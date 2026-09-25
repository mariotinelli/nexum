#!/usr/bin/env python3
"""Resume-safe executor for approved Ralph phases."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import signal
import subprocess
import sys
import time
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

sys.dont_write_bytecode = True

from ralph_runtime import EventSink, RuntimeFailure, TaskLock, atomic_json, evidence_digest, popen_group, sanitize, sanitize_text, normalized_failures, SECRET_KEYS, terminate_process_tree


class ExecutionError(RuntimeError):
    pass


class EffectError(ExecutionError):
    def __init__(self, message: str, reason: str = "failed") -> None:
        super().__init__(message)
        self.reason = reason


ACTIVE_PROCESS: subprocess.Popen[Any] | None = None
CANCELLED_SIGNAL: int | None = None
EVENTS: EventSink | None = None


def fail(message: str) -> None:
    raise ExecutionError(message)


def emit(event: str, **values: Any) -> None:
    if EVENTS is not None:
        EVENTS.emit(event, **values)


def run(command: list[str], repo: Path, *, capture: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=repo, capture_output=capture, text=True, encoding="utf-8", errors="replace", check=False)


def git(repo: Path, *arguments: str) -> str:
    result = run(["git", *arguments], repo)
    if result.returncode:
        fail("git command failed")
    return result.stdout.strip()


class Clock:
    def __init__(self) -> None:
        configured = os.environ.get("RALPH_CLOCK_VALUES")
        self.values = [int(value) for value in configured.split(",")] if configured else []

    def milliseconds(self) -> int:
        if self.values:
            return self.values.pop(0)
        return int(time.monotonic() * 1000)


def elapsed_ms(clock: Clock, started: int) -> int:
    return max(0, clock.milliseconds() - started)


def clean_status(repo: Path) -> str:
    lines = git(repo, "status", "--porcelain=v1", "--untracked-files=all").splitlines()
    return "\n".join(line for line in lines if not runtime_artifact(line[3:].strip('"')))


def runtime_artifact(relative: str) -> bool:
    normalized = relative.replace("\\", "/")
    return "/.flow/ralph/" in f"/{normalized}" or "/ralph.lock/" in f"/{normalized}/"


def working_snapshot(repo: Path) -> str:
    difference = subprocess.run(["git", "diff", "--binary", "HEAD"], cwd=repo, capture_output=True, check=False)
    if difference.returncode:
        fail("repository changes cannot be inspected")
    digest = hashlib.sha256(difference.stdout)
    untracked = git(repo, "ls-files", "--others", "--exclude-standard", "-z")
    for relative in sorted(path for path in untracked.split("\0") if path and not runtime_artifact(path)):
        path = repo / relative
        digest.update(relative.encode())
        if path.is_file() and not path.is_symlink():
            digest.update(path.read_bytes())
    return digest.hexdigest()


def load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exception:
        fail(f"{label} is missing or invalid: {exception}")
    if not isinstance(value, dict):
        fail(f"{label} must be an object")
    return value


def persist(state_path: Path, state: dict[str, Any], event: str, **details: Any) -> None:
    history = state["execution"].setdefault("history", [])
    history.append({"sequence": len(history) + 1, "event": event, "at": datetime.now(timezone.utc).isoformat(), **details})
    atomic_json(state_path, state)


def interrupt_for_test(point: str) -> None:
    if os.environ.get("RALPH_TEST_INTERRUPT_AT") == point:
        os._exit(97)


def approved_phases(state: dict[str, Any], planning: Path) -> list[tuple[dict[str, Any], str]]:
    revisions = state.get("revisions")
    if not isinstance(revisions, list) or not revisions:
        fail("approved planning has no revision")
    text = planning.read_text(encoding="utf-8")
    matches = list(re.finditer(r"^## Fase (\d+)\b.*$", text, re.MULTILINE))
    bodies: dict[int, str] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        bodies[int(match.group(1))] = text[match.start():end].rstrip() + "\n"
    selected = []
    for phase in revisions[-1].get("phases", []):
        number = int(phase["number"])
        body = bodies.get(number)
        if body is None or hashlib.sha256(body.encode()).hexdigest() != phase.get("sha256"):
            fail(f"approved phase {number} does not match planning.md")
        selected.append((phase, body))
    return selected


def runner_command(package: Path) -> list[str]:
    configured = os.environ.get("RALPH_AGENT_COMMAND_JSON")
    if configured:
        try:
            command = json.loads(configured)
        except json.JSONDecodeError:
            fail("RALPH_AGENT_COMMAND_JSON must be a JSON argv array")
        if not isinstance(command, list) or not command or not all(isinstance(item, str) and item for item in command):
            fail("RALPH_AGENT_COMMAND_JSON must be a non-empty JSON argv array")
        return command
    return [sys.executable, str(package / "scripts" / "run_codex.py")]


def render_prompt(template: Path, values: dict[str, str]) -> str:
    text = template.read_text(encoding="utf-8")
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    if re.search(r"\{\{[A-Z_]+\}\}", text):
        fail("agent prompt has an unresolved placeholder")
    return text


def gate_label(mode: str) -> str:
    return "Gate 1" if mode == "develop" else "integral validation" if mode == "validate-integral" else "Gate 2"


def validate_result(path: Path, mode: str) -> dict[str, Any]:
    label = gate_label(mode)
    value = load_json(path, f"{label} result")
    if mode == "develop":
        if set(value) != {"status", "summary", "files_changed", "checks"} or value.get("status") != "completed":
            fail(f"{label} returned an invalid structured completion")
        if any(not isinstance(value.get(field), list) or not all(isinstance(item, str) and item.strip() for item in value[field]) for field in ("files_changed", "checks")):
            fail(f"{label} result has invalid evidence")
    else:
        if set(value) != {"verdict", "summary", "evidence", "findings"} or value.get("verdict") not in ("approved", "rejected"):
            fail(f"{label} returned an invalid structured verdict")
        findings = value.get("findings")
        if not isinstance(findings, list) or any(not isinstance(item, dict) or set(item) != {"severity", "criterion", "evidence"} or item.get("severity") not in {"critical", "high", "medium", "low"} or any(not isinstance(item.get(field), str) or not item[field].strip() for field in ("criterion", "evidence")) for item in findings):
            fail(f"{label} result has invalid structured findings")
        if (value["verdict"] == "rejected") != bool(findings):
            fail(f"{label} findings must match its verdict")
        if not isinstance(value.get("evidence"), list) or not value["evidence"] or not all(isinstance(item, str) and item.strip() for item in value["evidence"]):
            fail(f"{label} result requires evidence")
    if not isinstance(value.get("summary"), str) or not value["summary"].strip():
        fail(f"{label} result requires a summary")
    return value


def communicate_process(process: subprocess.Popen[str], timeout_seconds: float | None) -> tuple[str, str, int]:
    global ACTIVE_PROCESS
    ACTIVE_PROCESS = process
    try:
        try:
            stdout, stderr = process.communicate(timeout=timeout_seconds)
        except subprocess.TimeoutExpired:
            terminate_process_tree(process)
            raise EffectError("effect timed out and its process tree was terminated", "timeout")
        if CANCELLED_SIGNAL is not None:
            raise EffectError(f"execution cancelled by signal {CANCELLED_SIGNAL}", "cancelled")
        return stdout or "", stderr or "", process.returncode
    finally:
        ACTIVE_PROCESS = None


def ensure_not_cancelled() -> None:
    if CANCELLED_SIGNAL is not None:
        raise EffectError(f"execution cancelled by signal {CANCELLED_SIGNAL}", "cancelled")


def invoke_agent(package: Path, repo: Path, mode: str, prompt: str, schema: Path, session_id: str, timeout_seconds: float) -> dict[str, Any]:
    if EVENTS is None:
        fail("operational event sink is unavailable")
    prefix = f"{mode}-{session_id}"
    prompt_path = EVENTS.private_file(f"{prefix}-prompt.md")
    result_path = EVENTS.private_file(f"{prefix}-result.json")
    stdout_path = EVENTS.private_file(f"{prefix}-stdout.log")
    stderr_path = EVENTS.private_file(f"{prefix}-stderr.log")
    prompt_path.write_text(sanitize_text(prompt), encoding="utf-8", newline="\n")
    # The runner's raw result is transient. Only sanitized evidence is retained.
    with tempfile.TemporaryDirectory(prefix="ralph-result-") as temporary:
        transient = Path(temporary) / "result.json"
        command = [*runner_command(package), "--mode", mode, "--prompt", str(prompt_path), "--schema", str(schema), "--result", str(transient), "--repo", str(repo)]
        environment = os.environ.copy()
        environment["RALPH_SESSION_ID"] = session_id
        process = popen_group(command, cwd=repo, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace", env=environment)
        try:
            stdout, stderr, returncode = communicate_process(process, timeout_seconds)
            stdout_path.write_text(sanitize_text(stdout), encoding="utf-8", newline="\n")
            stderr_path.write_text(sanitize_text(stderr), encoding="utf-8", newline="\n")
        finally:
            if transient.exists():
                try:
                    value = json.loads(transient.read_text(encoding="utf-8"))
                    def redact(item: Any) -> Any:
                        if isinstance(item, str): return sanitize_text(item)
                        if isinstance(item, list): return [redact(x) for x in item]
                        if isinstance(item, dict): return {k: "[REDACTED]" if SECRET_KEYS.search(str(k)) else redact(v) for k, v in item.items()}
                        return item
                    atomic_json(result_path, redact(value))
                except (ValueError, OSError):
                    result_path.write_text("{}", encoding="utf-8")
    interrupt_for_test(f"after-{mode}-effect")
    if returncode:
        raise EffectError(f"{gate_label(mode)} agent failed")
    return validate_result(result_path, mode)


def classify_test_failure(baseline: dict[str, Any], exit_code: int, failures: list[str]) -> str:
    baseline_failures = baseline.get("normalized_failures")
    if baseline.get("normalization_version") == 2 and baseline.get("result") == "red" and bool(failures) and baseline.get("exit_code") == exit_code and baseline_failures == failures:
        return "baseline-identical"
    if not failures or not isinstance(baseline_failures, list) or (baseline.get("result") == "red" and not baseline_failures):
        return "inconclusive"
    if baseline.get("result") == "green" or not set(failures) & set(baseline_failures):
        return "new"
    return "altered"


def focused_validation_report(name: str, findings: list[dict[str, str]]) -> str:
    lines = [f"Gate: {name}"]
    for finding in findings:
        lines.extend((f"- Severidade: {sanitize(finding['severity'])}", f"  Critério: {sanitize(finding['criterion'])}", f"  Evidência: {sanitize(finding['evidence'])}"))
    return "\n".join(lines)


def focused_test_report(classification: str, baseline: dict[str, Any], exit_code: int, failures: list[str]) -> str:
    lines = ["Gate: tests", f"Classificação: {classification}", f"Exit code atual: {exit_code}", f"Exit code do baseline: {baseline.get('exit_code')}", "Falhas atuais:"]
    lines.extend(f"- {failure}" for failure in failures or ["nenhuma linha conclusiva capturada"])
    lines.append("Falhas do baseline aprovado:")
    lines.extend(f"- {sanitize(str(failure))}" for failure in baseline.get("normalized_failures", []) or ["nenhuma falha registrada"])
    return "\n".join(lines)


def context_paths(repo: Path, state: dict[str, Any], planning: Path) -> str:
    issue = state["issue"]
    paths = [Path(issue["task_path"]), Path(issue["parent"]["requirement_path"]), planning]
    for category in ("instructions", "architecture", "adrs"):
        paths.extend(repo / item["path"] for item in state["inspection"][category])
    unique: list[str] = []
    for path in paths:
        relative = path.resolve().relative_to(repo.resolve()).as_posix()
        if relative not in unique:
            unique.append(relative)
    return "\n".join(f"- `{path}`" for path in unique)


def safe_title(value: str) -> str:
    return re.sub(r"[^\w .:/#-]+", "", value, flags=re.UNICODE).strip()[:80]


def gate_start(state_path: Path, state: dict[str, Any], record: dict[str, Any], name: str, before_snapshot: str, timeout_seconds: float | None, session_id: str | None = None) -> dict[str, Any]:
    ensure_not_cancelled()
    attempt = len([item for item in record["gates"] if item.get("name") == name]) + 1
    gate: dict[str, Any] = {"name": name, "status": "running", "attempt": attempt, "before_snapshot": before_snapshot, "before_head": record["base_commit"]}
    if timeout_seconds is not None:
        gate["timeout_seconds"] = timeout_seconds
    if session_id is not None:
        gate["session_id"] = session_id
    record["gates"].append(gate)
    persist(state_path, state, "effect-prepared", phase=record["number"], gate=name, session_id=session_id)
    emit("gate-started", phase=record["number"], gate=name, attempt=attempt, result="started", details={"session_id": session_id} if session_id else None)
    interrupt_for_test(f"before-{name}-effect")
    return gate


def gate_finish(state_path: Path, state: dict[str, Any], record: dict[str, Any], gate: dict[str, Any], status: str, duration_ms: int, repo: Path, **evidence: Any) -> None:
    gate.update({"status": status, "duration_ms": duration_ms, "after_snapshot": working_snapshot(repo), "after_head": git(repo, "rev-parse", "HEAD"), **evidence})
    persist(state_path, state, "effect-observed", phase=record["number"], gate=gate["name"], status=status)
    emit("gate-finished", phase=record["number"], gate=gate["name"], attempt=gate.get("attempt", "-"), duration_ms=duration_ms, result=status)


def uncertain_report(state_path: Path, state: dict[str, Any], repo: Path, record: dict[str, Any], gate: dict[str, Any], reason: str) -> None:
    evidence = {
        "phase": record["number"], "gate": gate["name"], "reason": sanitize(reason),
        "head": git(repo, "rev-parse", "HEAD"), "snapshot": working_snapshot(repo),
        "status": [sanitize(line) for line in clean_status(repo).splitlines()[:100]],
        "diff_stat": [sanitize(line) for line in run(["git", "diff", "--stat", "HEAD"], repo).stdout.splitlines()[:100]],
        "staged_diff_stat": [sanitize(line) for line in run(["git", "diff", "--cached", "--stat", "HEAD"], repo).stdout.splitlines()[:100]],
    }
    evidence["evidence_sha256"] = evidence_digest(evidence)
    report = state_path.parent / "ralph" / f"phase-{record['number']}-{gate['name']}-uncertain.json"
    atomic_json(report, evidence)
    gate["status"] = "uncertain"
    state["status"] = "execution-uncertain"
    state["execution"]["uncertain"] = {**evidence, "report_path": str(report), "expected_head": gate["before_head"]}
    persist(state_path, state, "uncertain-changes-observed", phase=record["number"], gate=gate["name"], evidence_sha256=evidence["evidence_sha256"])
    emit("gate-uncertain", phase=record["number"], gate=gate["name"], attempt=gate.get("attempt", "-"), result="interrupted", report_path=report)


def handle_interrupted_gate(state_path: Path, state: dict[str, Any], repo: Path, record: dict[str, Any], gate: dict[str, Any]) -> None:
    unchanged = git(repo, "rev-parse", "HEAD") == gate.get("before_head") and working_snapshot(repo) == gate.get("before_snapshot")
    if unchanged:
        gate["status"] = "interrupted"
        persist(state_path, state, "interrupted-effect-retryable", phase=record["number"], gate=gate["name"])
        return
    uncertain_report(state_path, state, repo, record, gate, "session ended without a durable result after repository changes")
    digest = state["execution"]["uncertain"]["evidence_sha256"]
    fail(f"alterações incertas preservadas; descarte exige --authorize-discard {digest} --authorized-by <ator>")


def resolve_uncertain(arguments: argparse.Namespace, state_path: Path, state: dict[str, Any], repo: Path) -> None:
    uncertain = state.get("execution", {}).get("uncertain")
    if not isinstance(uncertain, dict):
        return
    if working_snapshot(repo) != uncertain.get("snapshot") or git(repo, "rev-parse", "HEAD") != uncertain.get("head"):
        fail("a árvore mudou desde a evidência incerta; preserve o trabalho e faça nova decisão humana")
    if arguments.authorize_discard != uncertain.get("evidence_sha256") or not arguments.authorized_by:
        fail(f"alterações incertas preservadas; descarte exige --authorize-discard {uncertain.get('evidence_sha256')} --authorized-by <ator>")
    report_path = Path(uncertain["report_path"])
    report = load_json(report_path, "uncertain execution report")
    persist(state_path, state, "discard-authorized", evidence_sha256=uncertain["evidence_sha256"], authorized_by=sanitize(arguments.authorized_by))
    interrupt_for_test("before-uncertain-discard")
    if run(["git", "reset", "--hard", uncertain["expected_head"]], repo).returncode or run(["git", "clean", "-fd"], repo).returncode:
        fail("o descarte autorizado falhou; o trabalho foi preservado para intervenção manual")
    atomic_json(report_path, report)
    state["execution"].pop("uncertain", None)
    state["status"] = "ready"
    persist(state_path, state, "discard-completed", evidence_sha256=uncertain["evidence_sha256"])


def existing_phase_record(state: dict[str, Any], phase_number: int, base_commit: str) -> dict[str, Any]:
    records = state["execution"].setdefault("phases", [])
    matches = [record for record in records if record.get("number") == phase_number]
    if len(matches) > 1:
        fail(f"phase {phase_number} has duplicate execution state")
    if matches:
        return matches[0]
    record = {"number": phase_number, "base_commit": base_commit, "planning_sha256": state["revisions"][-1]["planning_sha256"], "gates": []}
    records.append(record)
    return record


def verified_phase_commit(repo: Path, state: dict[str, Any], record: dict[str, Any]) -> str | None:
    expected = record.get("commit")
    head = git(repo, "rev-parse", "HEAD")
    candidate = expected
    if candidate is None and head != record["base_commit"]:
        parent = run(["git", "rev-parse", f"{head}^"], repo)
        candidate = head if parent.returncode == 0 and parent.stdout.strip() == record["base_commit"] else None
    if not candidate:
        return None
    if run(["git", "merge-base", "--is-ancestor", candidate, "HEAD"], repo).returncode:
        fail(f"recorded commit for phase {record['number']} is not in HEAD history")
    message = git(repo, "show", "-s", "--format=%B", candidate)
    required = [f"DEV-Issue: #{state['issue']['id']}", f"Ralph-Phase: {record['number']}", f"Planning-SHA256: {record.get('planning_sha256', state['revisions'][-1]['planning_sha256'])}"]
    if not all(value in message for value in required) or git(repo, "rev-parse", f"{candidate}^") != record["base_commit"]:
        fail(f"HEAD does not prove the expected commit for phase {record['number']}")
    return candidate


def write_exhaustion_report(state_path: Path, state: dict[str, Any], record: dict[str, Any], gate_name: str, limit: int) -> Path:
    report_path = state_path.parent / "ralph" / f"phase-{record['number']}-{gate_name}-exhausted.json"
    rejected = [{key: gate[key] for key in ("name", "attempt", "status", "classification", "findings", "exit_code", "normalized_failures") if key in gate} for gate in record["gates"] if gate.get("name") == gate_name and gate.get("status") == "rejected"]
    atomic_json(report_path, {"phase": record["number"], "gate": gate_name, "rejection_limit": limit, "rejections": rejected, "resume_from": "development"})
    state["status"] = "execution-paused"
    state["execution"]["stop"] = {"reason": "rejection-limit-exhausted", "phase": record["number"], "gate": gate_name, "report_path": str(report_path)}
    persist(state_path, state, "execution-paused", phase=record["number"], gate=gate_name, reason="rejection-limit-exhausted")
    emit("rejection-limit", phase=record["number"], gate=gate_name, attempt=limit, result="rejected", report_path=report_path)
    return report_path


def write_final_summary(package: Path, state: dict[str, Any], outcome: str) -> Path | None:
    if EVENTS is None:
        return None
    records = state.get("execution", {}).get("phases", [])
    phases = [str(record.get("number")) for record in records]
    commits = [str(record["commit"]) for record in records if record.get("commit")]
    gates = [gate for record in records for gate in record.get("gates", [])]
    sessions = [str(gate["session_id"]) for gate in gates if gate.get("session_id")]
    rejections = [gate for gate in gates if gate.get("status") == "rejected"]
    tests = [gate for gate in gates if gate.get("name") == "tests"]
    ignored_baseline = [gate for gate in tests if gate.get("classification") == "baseline-identical"]
    values = {
        "OUTCOME": sanitize(outcome),
        "PHASES": ", ".join(phases) or "none",
        "COMMITS": ", ".join(commits) or "none",
        "SESSIONS": ", ".join(sessions) or "none",
        "REJECTIONS": str(len(rejections)),
        "TESTS": ", ".join(f"phase {record.get('number')}: {gate.get('status')} ({gate.get('classification', 'not-classified')})" for record in records for gate in record.get("gates", []) if gate.get("name") == "tests") or "none",
        "IGNORED_BASELINE": str(len(ignored_baseline)),
    }
    template = (package / "templates" / "final-summary.md").read_text(encoding="utf-8")
    for key, value in values.items():
        template = template.replace("{{" + key + "}}", value)
    path = EVENTS.private_file("final-summary.md")
    path.write_text(template, encoding="utf-8", newline="\n")
    categories = {
        "phases": values["PHASES"],
        "commits": values["COMMITS"],
        "sessions": values["SESSIONS"],
        "rejections": values["REJECTIONS"],
        "tests": values["TESTS"],
        "ignored-baseline": values["IGNORED_BASELINE"],
    }
    for category, value in categories.items():
        emit("summary", result=f"{category}:{value}", report_path=path)
    emit("developer-reminder", result="review full diff and test in browser when applicable", report_path=path)
    return path


def execute_phases(package: Path, repo: Path, state_path: Path, state: dict[str, Any], planning: Path, baseline: dict[str, Any], clock: Clock, arguments: argparse.Namespace) -> int:
    phases = approved_phases(state, planning)
    execution = state["execution"]
    execution["started_at"] = execution.get("started_at") or datetime.now(timezone.utc).isoformat()
    execution["base_commit"] = execution.get("base_commit") or git(repo, "rev-parse", "HEAD")
    execution["timeouts"] = {"development_seconds": arguments.dev_timeout_minutes * 60, "validation_seconds": arguments.validation_timeout_minutes * 60, "tests_seconds": arguments.tests_timeout_minutes * 60}
    persist(state_path, state, "execution-opened", base_commit=execution["base_commit"])
    context = context_paths(repo, state, planning)

    for index, (phase, phase_body) in enumerate(phases):
        phase_number = int(phase["number"])
        completed = phase_number in execution.setdefault("completed_phases", [])
        prior_commit = execution["base_commit"] if index == 0 else next((record.get("commit") for record in execution["phases"] if record.get("number") == int(phases[index - 1][0]["number"])), None)
        if not prior_commit:
            fail(f"phase {phase_number} cannot start before the previous phase commit")
        existing = next((item for item in execution["phases"] if item["number"] == phase_number), None)
        if existing is None:
            head = git(repo, "rev-parse", "HEAD")
            if run(["git", "merge-base", "--is-ancestor", prior_commit, head], repo).returncode:
                fail("previous phase commit is not an ancestor of the current planning base")
            prior_commit = head
        record = existing_phase_record(state, phase_number, prior_commit)
        record["max_gate_rejections"] = arguments.max_gate_rejections
        proven_commit = verified_phase_commit(repo, state, record)
        if proven_commit:
            record["commit"] = proven_commit
            if not completed:
                execution["completed_phases"].append(phase_number)
                persist(state_path, state, "existing-commit-recognized", phase=phase_number, commit=proven_commit)
            emit("phase-resumed", phase=phase_number, gate="commit", result="resumed", details={"commit": proven_commit})
            continue
        if completed:
            fail(f"state says phase {phase_number} completed but its commit cannot be proven")
        if git(repo, "rev-parse", "HEAD") != record["base_commit"]:
            fail(f"HEAD does not match resumable base for phase {phase_number}")
        execution["current_phase"] = phase_number
        state["status"] = "executing"
        persist(state_path, state, "phase-opened", phase=phase_number)
        emit("phase-started", phase=phase_number, result="started")

        for gate in record["gates"]:
            if gate.get("status") in {"running", "uncertain"}:
                handle_interrupted_gate(state_path, state, repo, record, gate)

        common = {"REPOSITORY": str(repo), "CONTEXT_PATHS": context, "PHASE": phase_body, "ISSUE_ID": str(state["issue"]["id"]), "PHASE_NUMBER": str(phase_number)}

        def count(name: str) -> int:
            return len([gate for gate in record["gates"] if gate.get("name") == name])

        def last_index(predicate: Callable[[dict[str, Any]], bool]) -> int:
            return max((i for i, gate in enumerate(record["gates"]) if predicate(gate)), default=-1)

        def latest_development() -> int:
            return last_index(lambda gate: gate.get("name") == "development" and gate.get("status") == "completed")

        def latest_rejection_after(index_: int) -> tuple[int, dict[str, Any]] | None:
            values = [(i, gate) for i, gate in enumerate(record["gates"]) if i > index_ and gate.get("status") == "rejected"]
            return values[-1] if values else None

        def develop(correction: tuple[str, str] | None = None) -> None:
            session_id = str(uuid.uuid4())
            before = working_snapshot(repo)
            if correction:
                source, report = correction
                record.setdefault("transitions", []).append({"from": source, "to": "development", "reason": f"correction attempt {count('development') + 1}"})
                for prior in record["gates"]:
                    if prior.get("name") in {"validation", "tests", "integral_validation"} and prior.get("status") == "approved":
                        prior.update({"status": "invalidated", "invalidated_by": session_id})
                prompt = render_prompt(package / "prompts" / "correct.md", {**common, "CORRECTION_REPORT": report})
            else:
                prompt = render_prompt(package / "prompts" / "develop.md", common)
            gate = gate_start(state_path, state, record, "development", before, arguments.dev_timeout_minutes * 60, session_id)
            gate["kind"] = "correction" if correction else "initial"
            atomic_json(state_path, state)
            started = clock.milliseconds()
            try:
                invoke_agent(package, repo, "develop", prompt, package / "schemas" / "development-result.schema.json", session_id, arguments.dev_timeout_minutes * 60)
            except (EffectError, ExecutionError) as exception:
                if working_snapshot(repo) != before:
                    uncertain_report(state_path, state, repo, record, gate, str(exception))
                else:
                    gate.update({"status": "interrupted", "failure": sanitize(str(exception))})
                    state["status"] = "execution-paused"
                    execution["stop"] = {"reason": getattr(exception, "reason", "agent-failure"), "phase": phase_number, "gate": "development"}
                    persist(state_path, state, "effect-interrupted", phase=phase_number, gate="development", reason=getattr(exception, "reason", "agent-failure"))
                raise
            if git(repo, "rev-parse", "HEAD") != record["base_commit"]:
                fail("Gate 1 must leave phase changes without a commit")
            if not clean_status(repo):
                fail("Gate 1 completed without repository changes")
            if correction and working_snapshot(repo) == before:
                fail("focused development completed without changing the phase")
            duration = elapsed_ms(clock, started)
            gate_finish(state_path, state, record, gate, "completed", duration, repo)

        def reject_or_exhaust(gate: dict[str, Any], gate_name: str, duration: int, **details: Any) -> None:
            prior_approval = last_index(lambda item: item.get("name") == gate_name and item.get("status") == "approved")
            rejection = len([item for i, item in enumerate(record["gates"]) if i > prior_approval and item.get("name") == gate_name and item.get("status") == "rejected"]) + 1
            gate_finish(state_path, state, record, gate, "rejected", duration, repo, rejection=rejection, **details)
            if rejection >= arguments.max_gate_rejections:
                report = write_exhaustion_report(state_path, state, record, gate_name, arguments.max_gate_rejections)
                fail(f"{gate_name} esgotou {arguments.max_gate_rejections} reprovações consecutivas na fase {phase_number}; relatório sanitizado: {report}")

        def validate(mode: str, gate_name: str) -> str | None:
            before = working_snapshot(repo)
            session_id = str(uuid.uuid4())
            gate = gate_start(state_path, state, record, gate_name, before, arguments.validation_timeout_minutes * 60, session_id)
            atomic_json(state_path, state)
            started = clock.milliseconds()
            try:
                result = invoke_agent(package, repo, mode, render_prompt(package / "prompts" / ("validate-integral.md" if mode == "validate-integral" else "validate.md"), {**common, "EXECUTION_BASE": execution["base_commit"]}), package / "schemas" / "validation-result.schema.json", session_id, arguments.validation_timeout_minutes * 60)
            except (EffectError, ExecutionError) as exception:
                if working_snapshot(repo) != before:
                    uncertain_report(state_path, state, repo, record, gate, str(exception))
                else:
                    gate.update({"status": "interrupted", "failure": sanitize(str(exception))})
                    state["status"] = "execution-paused"
                    execution["stop"] = {"reason": getattr(exception, "reason", "agent-failure"), "phase": phase_number, "gate": gate_name}
                    persist(state_path, state, "effect-interrupted", phase=phase_number, gate=gate_name, reason=getattr(exception, "reason", "agent-failure"))
                raise
            duration = elapsed_ms(clock, started)
            if working_snapshot(repo) != before:
                uncertain_report(state_path, state, repo, record, gate, f"{gate_label(mode)} mutated the repository")
                fail(f"{gate_label(mode)} mutated the repository")
            if result["verdict"] == "approved":
                gate_finish(state_path, state, record, gate, "approved", duration, repo, evidence=[sanitize(item) for item in result["evidence"]])
                return None
            findings = [{"severity": sanitize(item["severity"]), "criterion": sanitize(item["criterion"]), "evidence": sanitize(item["evidence"])} for item in result["findings"]]
            reject_or_exhaust(gate, gate_name, duration, findings=findings)
            return focused_validation_report(gate_name, findings)

        def test_suite() -> str | None:
            before = working_snapshot(repo)
            gate = gate_start(state_path, state, record, "tests", before, arguments.tests_timeout_minutes * 60)
            atomic_json(state_path, state)
            started = clock.milliseconds()
            if EVENTS is None:
                fail("operational event sink is unavailable")
            output_path = EVENTS.private_file(f"phase-{phase_number}-tests-{gate['attempt']}.log")
            with tempfile.TemporaryFile() as output:
                process = popen_group(baseline["command"], cwd=repo, shell=True, stdout=output, stderr=subprocess.STDOUT)
                try:
                    _, _, returncode = communicate_process(process, arguments.tests_timeout_minutes * 60)
                except EffectError as exception:
                    gate.update({"status": "interrupted", "failure": sanitize(str(exception))})
                    state["status"] = "execution-paused"
                    execution["stop"] = {"reason": exception.reason, "phase": phase_number, "gate": "tests"}
                    persist(state_path, state, "effect-interrupted", phase=phase_number, gate="tests", reason=exception.reason)
                    emit("gate-interrupted", phase=phase_number, gate="tests", attempt=gate["attempt"], result="interrupted")
                    raise
                finally:
                    output.seek(0)
                    output_path.write_text(sanitize_text(output.read().decode("utf-8", errors="replace")), encoding="utf-8", newline="\n")
            failures = normalized_failures(output_path.read_text(encoding="utf-8", errors="replace").splitlines(), returncode)
            if working_snapshot(repo) != before:
                uncertain_report(state_path, state, repo, record, gate, "test suite mutated the repository")
                fail("Gate 3 test suite mutated the repository")
            duration = elapsed_ms(clock, started)
            classification = classify_test_failure(baseline, returncode, failures)
            if returncode == 0 or classification == "baseline-identical":
                gate_finish(state_path, state, record, gate, "approved", duration, repo, classification="green" if returncode == 0 else classification, exit_code=returncode)
                interrupt_for_test("after-tests-effect")
                return None
            reject_or_exhaust(gate, "tests", duration, classification=classification, exit_code=returncode, normalized_failures=failures)
            interrupt_for_test("after-tests-effect")
            return focused_test_report(classification, baseline, returncode, failures)

        while True:
            development_index = latest_development()
            rejection = latest_rejection_after(development_index)
            if development_index < 0 or rejection:
                correction = None
                if rejection:
                    rejected = rejection[1]
                    correction = (rejected["name"], focused_validation_report(rejected["name"], rejected["findings"]) if "findings" in rejected else focused_test_report(rejected["classification"], baseline, rejected["exit_code"], rejected["normalized_failures"]))
                develop(correction)
                development_index = latest_development()
            current_snapshot = working_snapshot(repo)
            approved_validation = last_index(lambda gate: gate.get("name") == "validation" and gate.get("status") == "approved" and gate.get("after_snapshot") == current_snapshot)
            if approved_validation < development_index and validate("validate", "validation") is not None:
                continue
            approved_tests = last_index(lambda gate: gate.get("name") == "tests" and gate.get("status") == "approved" and gate.get("after_snapshot") == working_snapshot(repo))
            if approved_tests < latest_development() and test_suite() is not None:
                continue
            if index == len(phases) - 1:
                approved_integral = last_index(lambda gate: gate.get("name") == "integral_validation" and gate.get("status") == "approved" and gate.get("after_snapshot") == working_snapshot(repo))
                if approved_integral < latest_development() and validate("validate-integral", "integral_validation") is not None:
                    continue
            break

        approved_snapshot = working_snapshot(repo)
        commit_gate = next((gate for gate in reversed(record["gates"]) if gate.get("name") == "commit" and gate.get("status") in {"running", "operational-failure"}), None)
        if commit_gate is None:
            commit_gate = gate_start(state_path, state, record, "commit", approved_snapshot, None)
        elif commit_gate.get("before_snapshot") != approved_snapshot:
            fail("repository tree no longer matches the approved commit evidence")
        started = clock.milliseconds()
        ensure_not_cancelled()
        if run(["git", "add", "--all"], repo).returncode:
            commit_gate.update({"status": "operational-failure", "failure": "could not stage phase changes"})
            persist(state_path, state, "commit-failed", phase=phase_number, step="stage")
            fail("Gate 4 could not stage phase changes; work preserved for the developer")
        persist(state_path, state, "commit-staged", phase=phase_number, snapshot=working_snapshot(repo))
        interrupt_for_test("after-commit-stage")
        ensure_not_cancelled()
        if not git(repo, "diff", "--cached", "--name-only"):
            fail("Gate 4 has no phase changes to commit")
        subject = f"feat: complete DEV #{state['issue']['id']} phase {phase_number} - {safe_title(str(phase['title']))}"[:72].rstrip()
        trailers = f"DEV-Issue: #{state['issue']['id']}\nRalph-Phase: {phase_number}\nPlanning-SHA256: {state['revisions'][-1]['planning_sha256']}"
        interrupt_for_test("before-commit-effect")
        commit_process = popen_group(["git", "commit", "--no-verify", "-m", subject, "-m", trailers], cwd=repo, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
        _, _, commit_returncode = communicate_process(commit_process, None)
        interrupt_for_test("after-commit-effect")
        if commit_returncode:
            commit_gate.update({"status": "operational-failure", "failure": "git commit failed"})
            state["status"] = "execution-paused"
            execution["stop"] = {"reason": "commit-operational-failure", "phase": phase_number, "gate": "commit"}
            persist(state_path, state, "commit-failed", phase=phase_number, step="commit")
            fail("Gate 4 commit failed; staged work and evidence were preserved for the developer")
        commit = verified_phase_commit(repo, state, record)
        if commit is None or clean_status(repo):
            fail("Gate 4 did not leave exactly one clean phase commit")
        duration = elapsed_ms(clock, started)
        record["commit"] = commit
        execution["completed_phases"].append(phase_number)
        execution["current_phase"] = None
        execution.pop("stop", None)
        state["status"] = "ready"
        gate_finish(state_path, state, record, commit_gate, "completed", duration, repo, commit=commit)
        emit("phase-finished", phase=phase_number, gate="commit", attempt=commit_gate.get("attempt", 1), duration_ms=duration, result="completed", details={"commit": commit})
    return 0


def positive_timeout(value: str) -> float:
    try:
        parsed = float(value)
    except ValueError:
        raise argparse.ArgumentTypeError("timeout must be a positive number of minutes")
    if not parsed > 0 or parsed == float("inf"):
        raise argparse.ArgumentTypeError("timeout must be a positive finite number of minutes")
    return parsed


def signal_handler(signum: int, _frame: Any) -> None:
    global CANCELLED_SIGNAL
    CANCELLED_SIGNAL = signum
    if ACTIVE_PROCESS is not None:
        terminate_process_tree(ACTIVE_PROCESS)


def authority_is_current(state: dict[str, Any], planning: Path) -> bool:
    revision = state.get("revisions", [])[-1]
    current = hashlib.sha256(planning.read_bytes()).hexdigest()
    return current == revision.get("planning_sha256") and any(approval.get("status") == "valid" and approval.get("revision") == revision.get("number") and approval.get("planning_sha256") == current for approval in state.get("approvals", [])) and isinstance(state.get("handoff"), dict) and state["handoff"].get("planning_sha256") == current


def main() -> int:
    global EVENTS
    parser = argparse.ArgumentParser()
    parser.add_argument("planning")
    parser.add_argument("--state", required=True)
    parser.add_argument("--max-gate-rejections", type=int, default=3)
    parser.add_argument("--dev-timeout-minutes", type=positive_timeout, default=60.0)
    parser.add_argument("--validation-timeout-minutes", type=positive_timeout, default=30.0)
    parser.add_argument("--tests-timeout-minutes", type=positive_timeout, default=60.0)
    parser.add_argument("--authorize-discard")
    parser.add_argument("--authorized-by")
    parser.add_argument("--verbose", action="store_true")
    arguments = parser.parse_args()
    package = Path(__file__).resolve().parent.parent
    planning, state_path = Path(arguments.planning).resolve(), Path(arguments.state).resolve()
    preliminary = load_json(state_path, "plan-issue state")
    preliminary_repo = Path(preliminary.get("repository", {}).get("path", "")).resolve()
    git_directory = run(["git", "rev-parse", "--git-dir"], preliminary_repo)
    if git_directory.returncode:
        print("Ralph interrompido: preflight requires the approved repository root", file=sys.stderr)
        return 1
    lock_root = (preliminary_repo / git_directory.stdout.strip()).resolve() / "ralph-locks"
    EVENTS = EventSink(lock_root.parent, state_path, verbose=arguments.verbose)
    lock = TaskLock(state_path, lock_root)
    state: dict[str, Any] | None = None
    outcome = "failed"
    from manage_plan import evidence_current, accepted_baseline, ContractError
    try:
        if arguments.max_gate_rejections < 1:
            fail("--max-gate-rejections must be a positive integer")
        lock.acquire()
        for signum in (signal.SIGINT, signal.SIGTERM):
            signal.signal(signum, signal_handler)
        state = load_json(state_path, "plan-issue state")
        repo = Path(state.get("repository", {}).get("path", "")).resolve()
        if not repo.is_dir() or Path(git(repo, "rev-parse", "--show-toplevel")).resolve() != repo:
            fail("preflight requires the approved repository root")
        if not authority_is_current(state, planning):
            fail("preflight rejected planning authority")
        first_execution = not state.get("execution", {}).get("phases") and state.get("execution", {}).get("started_at") is None
        starting_revision = not any(record.get("planning_sha256") == state["revisions"][-1]["planning_sha256"] for record in state["execution"].get("phases", []))
        if (first_execution or starting_revision) and (clean_status(repo) or not evidence_current(state)):
            fail("preflight requires a clean worktree with unchanged inspected evidence")
        relative_state = state_path.relative_to(repo).as_posix()
        if git(repo, "ls-files", "--", relative_state):
            fail("runtime state must be untracked; preserve the file and remove it from the Git index")
        if run(["git", "check-ignore", "--quiet", "--", relative_state], repo).returncode:
            fail("runtime state must be ignored before execution")
        resolve_uncertain(arguments, state_path, state, repo)
        baseline = accepted_baseline(state)
        if not isinstance(baseline, dict) or baseline.get("result") not in {"green", "red"}:
            fail("preflight requires the approved baseline")
        if state.get("issue", {}).get("kind") != "DEV":
            fail("preflight requires canonical DEV identity")
        result = execute_phases(package, repo, state_path, state, planning, baseline, Clock(), arguments)
        outcome = "success"
        return result
    except (ExecutionError, RuntimeFailure, ContractError, KeyError, IndexError, ValueError, OSError) as exception:
        if state is not None and CANCELLED_SIGNAL is not None:
            try:
                state["status"] = "execution-cancelled"
                persist(state_path, state, "execution-cancelled", signal=CANCELLED_SIGNAL)
            except OSError:
                pass
        emit("execution-stopped", phase=state.get("execution", {}).get("current_phase", "-") if state else "-", result="failed", details={"reason": sanitize(str(exception))})
        print(f"Ralph interrompido: {sanitize(str(exception))}", file=sys.stderr)
        return 1
    finally:
        try:
            write_final_summary(package, state or preliminary, outcome)
        except OSError as exception:
            emit("summary-failed", result="failed", details={"reason": sanitize(str(exception))})
        lock.release()


if __name__ == "__main__":
    raise SystemExit(main())
