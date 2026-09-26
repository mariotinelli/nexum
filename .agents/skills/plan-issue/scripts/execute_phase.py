#!/usr/bin/env python3
"""Execute planning.md phases with four gates and minimal resumable state."""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import signal
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True
from ralph_runtime import EventSink, RuntimeFailure, TaskLock, atomic_json, popen_group, sanitize, sanitize_text, SECRET_KEYS, terminate_process_tree


class ExecutionError(RuntimeError):
    pass


EVENTS: EventSink | None = None
ACTIVE_PROCESS: subprocess.Popen[Any] | None = None
CANCELLED = False


def fail(message: str) -> None:
    raise ExecutionError(message)


def run(command: list[str], repo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=repo, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)


def git(repo: Path, *arguments: str) -> str:
    result = run(["git", *arguments], repo)
    if result.returncode:
        fail(sanitize(result.stderr or result.stdout or f"git {' '.join(arguments)} failed"))
    return result.stdout.strip()


def repository_for(planning: Path) -> Path:
    result = subprocess.run(["git", "-C", str(planning.parent), "rev-parse", "--show-toplevel"], capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    if result.returncode:
        fail("planning.md must be inside a Git repository")
    return Path(result.stdout.strip()).resolve()


def parse_planning(planning: Path) -> tuple[str, list[tuple[int, str, str]]]:
    if planning.name != "planning.md" or not planning.is_file() or planning.is_symlink():
        fail("expected an existing planning.md file")
    text = planning.read_text(encoding="utf-8")
    baseline = re.search(r"^## Baseline\s*$\n(.*?)(?=^## |\Z)", text, re.MULTILINE | re.DOTALL)
    if not baseline:
        fail("planning.md must contain a Baseline section")
    commands = re.findall(r"```(?:sh|bash|shell)?\s*\n(.*?)```", baseline.group(1), re.DOTALL | re.IGNORECASE)
    if len(commands) != 1 or not commands[0].strip():
        fail("Baseline must contain exactly one fenced test command")
    matches = list(re.finditer(r"^## Fase (\d+)\s+[—-]\s+(.+?)\s*$", text, re.MULTILINE))
    if not matches:
        fail("planning.md must contain at least one phase")
    phases: list[tuple[int, str, str]] = []
    for index, match in enumerate(matches):
        number = int(match.group(1))
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[match.start():end].strip()
        if len(body.splitlines()) < 2:
            fail(f"Fase {number} must not be empty")
        phases.append((number, match.group(2).strip(), body))
    numbers = [phase[0] for phase in phases]
    if numbers != sorted(set(numbers)):
        fail("phase numbers must be unique and increasing")
    return commands[0].strip(), phases


def task_context(repo: Path, planning: Path) -> str:
    paths = [planning]
    candidates = [planning.parent / "task.md", planning.parent.parent.parent / "feature.md", planning.parent.parent.parent / "bug.md", repo / "AGENTS.md"]
    current = planning.parent
    while current != repo and repo in current.parents:
        candidates.append(current / "AGENTS.md")
        current = current.parent
    for candidate in candidates:
        if candidate.is_file() and candidate not in paths:
            paths.append(candidate)
    return "\n".join(f"- `{path.relative_to(repo).as_posix()}`" for path in paths)


def state_path_for(planning: Path) -> Path:
    return planning.parent / ".flow" / "ralph-state.json"


def load_state(path: Path, planning: Path) -> dict[str, Any]:
    if not path.exists():
        return {"version": 1, "planning": str(planning), "current_phase": None, "current_gate": None, "completed_phases": [], "phase_commits": {}}
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exception:
        fail(f"invalid Ralph state; delete {path} to restart: {exception}")
    if not isinstance(state, dict) or state.get("version") != 1 or Path(str(state.get("planning", ""))).resolve() != planning:
        fail(f"Ralph state belongs to another planning; delete {path} to restart")
    if not isinstance(state.get("completed_phases"), list) or not isinstance(state.get("phase_commits"), dict):
        fail(f"invalid Ralph state; delete {path} to restart")
    return state


def save_state(path: Path, state: dict[str, Any], **updates: Any) -> None:
    state.update(updates)
    atomic_json(path, state)


def worktree_changes(repo: Path) -> str:
    return git(repo, "status", "--porcelain=v1", "--untracked-files=all")


def render(template: Path, values: dict[str, str]) -> str:
    text = template.read_text(encoding="utf-8")
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def runner_command(package: Path) -> list[str]:
    configured = os.environ.get("RALPH_AGENT_COMMAND_JSON")
    if configured:
        try:
            value = json.loads(configured)
        except ValueError:
            fail("RALPH_AGENT_COMMAND_JSON must be a JSON argv array")
        if not isinstance(value, list) or not value or not all(isinstance(item, str) and item for item in value):
            fail("RALPH_AGENT_COMMAND_JSON must be a non-empty JSON argv array")
        return value
    return [sys.executable, str(package / "scripts" / "run_codex.py")]


def communicate(process: subprocess.Popen[Any], timeout: float) -> tuple[str, str, int]:
    global ACTIVE_PROCESS
    ACTIVE_PROCESS = process
    try:
        try:
            stdout, stderr = process.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            terminate_process_tree(process)
            stdout, stderr = process.communicate()
            raise ExecutionError(f"process timed out after {timeout:g} seconds")
        if CANCELLED:
            raise ExecutionError("execution cancelled")
        return stdout or "", stderr or "", process.returncode
    finally:
        ACTIVE_PROCESS = None


def extract_error(stderr: str) -> str:
    fallback = ""
    for line in reversed(stderr.splitlines()):
        candidate = line.strip()
        if candidate.startswith("ERROR:"):
            try:
                value = json.loads(candidate.removeprefix("ERROR:").strip())
                error = value.get("error") if isinstance(value, dict) else None
                message = error.get("message") if isinstance(error, dict) else None
                if isinstance(message, str) and message.strip():
                    return sanitize(message)
            except ValueError:
                pass
        if not fallback and re.search(r"(?:error|failed|fatal)", candidate, re.IGNORECASE):
            fallback = sanitize(candidate)
    return fallback or "the agent process exited without a result"


def redact_result(value: Any) -> Any:
    if isinstance(value, str):
        return sanitize_text(value)
    if isinstance(value, list):
        return [redact_result(item) for item in value]
    if isinstance(value, dict):
        return {key: "[REDACTED]" if SECRET_KEYS.search(str(key)) else redact_result(item) for key, item in value.items()}
    return value


def invoke_agent(package: Path, repo: Path, mode: str, prompt: str, schema: Path, phase: int, timeout: float) -> dict[str, Any]:
    if EVENTS is None:
        fail("runtime log is unavailable")
    session = str(uuid.uuid4())
    prefix = f"phase-{phase}-{mode}-{session}"
    prompt_path = EVENTS.private_file(f"{prefix}-prompt.md")
    stdout_path = EVENTS.private_file(f"{prefix}-stdout.log")
    stderr_path = EVENTS.private_file(f"{prefix}-stderr.log")
    prompt_path.write_text(sanitize_text(prompt), encoding="utf-8", newline="\n")
    with tempfile.TemporaryDirectory(prefix="ralph-result-") as directory:
        result_path = Path(directory) / "result.json"
        command = [*runner_command(package), "--mode", mode, "--prompt", str(prompt_path), "--schema", str(schema), "--result", str(result_path), "--repo", str(repo)]
        environment = os.environ.copy()
        environment["RALPH_SESSION_ID"] = session
        process = popen_group(command, cwd=repo, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace", env=environment)
        stdout, stderr, returncode = communicate(process, timeout)
        stdout_path.write_text(sanitize_text(stdout), encoding="utf-8", newline="\n")
        stderr_path.write_text(sanitize_text(stderr), encoding="utf-8", newline="\n")
        if returncode:
            gate = "Gate 1" if mode == "develop" else "Gate 2"
            fail(f"{gate} falhou: {extract_error(stderr)}. Diagnóstico: {stderr_path}")
        try:
            result = json.loads(result_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            fail(f"agent returned no valid JSON. Diagnóstico: {stderr_path}")
        return redact_result(result)


def validate_result(result: dict[str, Any], mode: str) -> None:
    if mode == "develop":
        if result.get("status") != "completed":
            fail("development agent did not finish the phase")
    elif result.get("verdict") not in {"approved", "rejected"} or not isinstance(result.get("findings"), list):
        fail("validation agent returned an invalid result")


def validation_report(result: dict[str, Any]) -> str:
    lines = []
    for finding in result.get("findings", []):
        if isinstance(finding, dict):
            lines.append(f"- {finding.get('severity', 'unknown')}: {finding.get('criterion', 'criterion')} — {finding.get('evidence', 'no evidence')}")
    return "\n".join(lines) or str(result.get("summary", "validation rejected without details"))


def run_tests(repo: Path, command: str, phase: int, timeout: float) -> tuple[bool, str, Path]:
    if EVENTS is None:
        fail("runtime log is unavailable")
    output_path = EVENTS.private_file(f"phase-{phase}-tests.log")
    with output_path.open("w+", encoding="utf-8", newline="\n") as output:
        process = popen_group(command, cwd=repo, shell=True, stdout=output, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")
        _, _, returncode = communicate(process, timeout)
        output.seek(0)
        content = sanitize_text(output.read())
        output.seek(0)
        output.truncate()
        output.write(content)
    lines = [line for line in content.splitlines() if line.strip()]
    return returncode == 0, "\n".join(lines[-80:]) or f"test command exited with code {returncode}", output_path


def emit(event: str, **values: Any) -> None:
    if EVENTS is not None:
        EVENTS.emit(event, **values)


def gate_started(phase: int, gate: str, attempt: int) -> float:
    emit("gate-started", phase=phase, gate=gate, attempt=attempt, result="started")
    return time.monotonic()


def gate_finished(phase: int, gate: str, attempt: int, result: str, started: float, **details: Any) -> None:
    emit("gate-finished", phase=phase, gate=gate, attempt=attempt, duration_ms=int((time.monotonic() - started) * 1000), result=result, details=details or None)


def positive(value: str) -> float:
    try:
        parsed = float(value)
    except ValueError:
        raise argparse.ArgumentTypeError("must be a number")
    if not math.isfinite(parsed) or parsed <= 0:
        raise argparse.ArgumentTypeError("must be a positive finite number")
    return parsed


def signal_handler(_signum: int, _frame: Any) -> None:
    global CANCELLED
    CANCELLED = True
    if ACTIVE_PROCESS is not None:
        terminate_process_tree(ACTIVE_PROCESS)


def execute(arguments: argparse.Namespace) -> int:
    global EVENTS
    planning = Path(arguments.planning).resolve()
    suite, phases = parse_planning(planning)
    repo = repository_for(planning)
    package = Path(__file__).resolve().parent.parent
    state_path = state_path_for(planning)
    state_relative = state_path.relative_to(repo).as_posix()
    if run(["git", "check-ignore", "--quiet", "--", state_relative], repo).returncode:
        fail(f"add /.flow/ to {planning.parent / '.gitignore'} before running Ralph")
    state = load_state(state_path, planning)
    git_dir = Path(git(repo, "rev-parse", "--git-dir"))
    git_dir = git_dir if git_dir.is_absolute() else (repo / git_dir).resolve()
    EVENTS = EventSink(git_dir, state_path, verbose=arguments.verbose)
    lock = TaskLock(state_path, git_dir / "ralph-locks")
    lock.acquire()
    try:
        for signum in (signal.SIGINT, signal.SIGTERM):
            signal.signal(signum, signal_handler)
        known = {number for number, _, _ in phases}
        state["completed_phases"] = [number for number in state["completed_phases"] if number in known]
        context = task_context(repo, planning)
        for number, title, body in phases:
            if number in state["completed_phases"]:
                continue
            if state.get("current_phase") == number and state.get("current_gate") == "commit" and not worktree_changes(repo):
                state["completed_phases"].append(number)
                state["phase_commits"][str(number)] = git(repo, "rev-parse", "HEAD")
                save_state(state_path, state, current_phase=None, current_gate=None)
                emit("phase-resumed", phase=number, gate="commit", result="resumed")
                continue
            if worktree_changes(repo) and state.get("current_phase") != number:
                fail("worktree has changes unrelated to the resumable phase; commit or discard them before Ralph")
            save_state(state_path, state, current_phase=number, current_gate="development")
            emit("phase-started", phase=number, result="started")
            correction = str(state.get("last_failure", "")).strip()
            for attempt in range(1, arguments.max_attempts + 1):
                started = gate_started(number, "development", attempt)
                template = package / "prompts" / ("correct.md" if correction else "develop.md")
                values = {"REPOSITORY": str(repo), "CONTEXT_PATHS": context, "PHASE": body, "PHASE_NUMBER": str(number), "CORRECTION_REPORT": correction}
                result = invoke_agent(package, repo, "develop", render(template, values), package / "schemas" / "development-result.schema.json", number, arguments.dev_timeout_minutes * 60)
                validate_result(result, "develop")
                if not worktree_changes(repo):
                    fail("Gate 1 finished without repository changes")
                gate_finished(number, "development", attempt, "completed", started)

                save_state(state_path, state, current_gate="validation")
                started = gate_started(number, "validation", attempt)
                before = worktree_changes(repo)
                validation = invoke_agent(package, repo, "validate", render(package / "prompts" / "validate.md", values), package / "schemas" / "validation-result.schema.json", number, arguments.validation_timeout_minutes * 60)
                validate_result(validation, "validate")
                if worktree_changes(repo) != before:
                    fail("Gate 2 modified the repository")
                if validation["verdict"] == "rejected":
                    correction = validation_report(validation)
                    save_state(state_path, state, current_gate="development", last_failure=correction)
                    gate_finished(number, "validation", attempt, "rejected", started, findings=validation.get("findings", []))
                    if attempt == arguments.max_attempts:
                        fail(f"Gate 2 rejected phase {number} {attempt} times; changes were preserved")
                    continue
                gate_finished(number, "validation", attempt, "approved", started)

                save_state(state_path, state, current_gate="tests")
                started = gate_started(number, "tests", attempt)
                passed, report, report_path = run_tests(repo, suite, number, arguments.tests_timeout_minutes * 60)
                if not passed:
                    correction = f"A suíte completa falhou. Corrija estas falhas:\n\n{report}"
                    save_state(state_path, state, current_gate="development", last_failure=correction)
                    gate_finished(number, "tests", attempt, "rejected", started, normalized_failures=[report])
                    if attempt == arguments.max_attempts:
                        fail(f"Gate 3 failed phase {number} {attempt} times. Diagnóstico: {report_path}")
                    continue
                gate_finished(number, "tests", attempt, "approved", started)

                save_state(state_path, state, current_gate="commit")
                started = gate_started(number, "commit", attempt)
                staged = run(["git", "add", "--all"], repo)
                if staged.returncode:
                    fail("Gate 4 could not stage phase changes")
                if not git(repo, "diff", "--cached", "--name-only"):
                    fail("Gate 4 has no changes to commit")
                committed = run(["git", "commit", "--no-verify", "-m", f"feat: complete phase {number} - {title}"[:72].rstrip()], repo)
                if committed.returncode:
                    fail(f"Gate 4 commit failed: {sanitize(committed.stderr or committed.stdout)}")
                commit = git(repo, "rev-parse", "HEAD")
                state["completed_phases"].append(number)
                state["phase_commits"][str(number)] = commit
                state.pop("last_failure", None)
                save_state(state_path, state, current_phase=None, current_gate=None)
                gate_finished(number, "commit", attempt, "completed", started, commit=commit)
                emit("phase-finished", phase=number, gate="commit", attempt=attempt, result="completed")
                break
        emit("developer-reminder", result="success")
        return 0
    finally:
        lock.release()


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser()
    value.add_argument("planning")
    value.add_argument("--max-attempts", type=int, default=3)
    value.add_argument("--dev-timeout-minutes", type=positive, default=60.0)
    value.add_argument("--validation-timeout-minutes", type=positive, default=30.0)
    value.add_argument("--tests-timeout-minutes", type=positive, default=60.0)
    value.add_argument("--verbose", action="store_true")
    return value


def main() -> int:
    arguments = parser().parse_args()
    if arguments.max_attempts < 1:
        print("Ralph interrompido: --max-attempts must be a positive integer", file=sys.stderr)
        return 1
    try:
        return execute(arguments)
    except (ExecutionError, RuntimeFailure, OSError, KeyError, IndexError, ValueError) as exception:
        print(f"Ralph interrompido: {sanitize(str(exception))}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
