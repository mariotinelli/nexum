#!/usr/bin/env python3
"""Guard canonical DEV planning evidence and executable authority."""
from __future__ import annotations

import argparse, hashlib, json, os, re, shlex, subprocess, sys, tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

from ralph_runtime import normalized_failures

CATEGORIES = ("instructions", "architecture", "adrs", "conventions", "automations", "tests")
PLAN_SECTIONS = ("Identidade e fontes", "Objetivo", "Estado atual", "Escopo", "Arquitetura", "Estratégia", "Baseline", "Riscos")
PHASE_SECTIONS = ("Objetivo", "Dependências", "Mudanças esperadas", "Arquivos prováveis", "Limites", "Estratégia", "Aceite", "Verificação focada")
SECRET_KEYS = re.compile(r"api[_-]?key|authorization|password|secret|token|cookie", re.I)
SECRET_VALUES = re.compile(r"bearer\s+\S+|api[_-]?key\s*[:=]\s*\S+", re.I)

class ContractError(RuntimeError): pass
def fail(message: str) -> None: raise ContractError(message)
def digest(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()
def json_digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
def timestamp(value: str) -> datetime:
    try: parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError: fail(f"invalid ISO-8601 timestamp: {value}")
    if parsed.tzinfo is None: fail(f"timestamp requires an offset: {value}")
    return parsed
def reject_secrets(value: Any, label: str) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            if SECRET_KEYS.search(str(key)) and not (str(key) == "authorization_sha256" and isinstance(nested, str) and re.fullmatch(r"[a-f0-9]{64}", nested)): fail(f"{label} contains a secret-like field")
            reject_secrets(nested, label)
    elif isinstance(value, list):
        for nested in value: reject_secrets(nested, label)
    elif isinstance(value, str) and SECRET_VALUES.search(value): fail(f"{label} contains secret-like content")
def sanitized_line(value: str) -> str:
    value = SECRET_VALUES.sub("[REDACTED]", value.strip())
    return re.sub(r"(?i)(password|secret|token|cookie)\s*[:=]\s*\S+", r"\1=[REDACTED]", value)[:500]
def safe_file(path: Path, root: Path | None = None) -> Path:
    path = path.absolute()
    if path.is_symlink() or not path.is_file(): fail(f"required regular file is missing or unsafe: {path}")
    if root:
        try: path.resolve().relative_to(root.resolve())
        except ValueError: fail(f"inspection source is outside the repository: {path}")
        current = path.parent
        while current != root.absolute().parent:
            if current.is_symlink(): fail(f"required file has a symbolic-link parent: {path}")
            if current == root.absolute(): break
            current = current.parent
    return path
def assert_safe_write(path: Path) -> None:
    if path.exists() and (path.is_symlink() or not path.is_file()): fail(f"output is not a safe regular file: {path.absolute()}")
    parent = path.parent
    while parent != parent.parent:
        if parent.is_symlink() or (parent.exists() and not parent.is_dir()): fail(f"output parent is unsafe: {parent.absolute()}")
        parent = parent.parent
def atomic_json(path: Path, value: dict[str, Any]) -> None:
    assert_safe_write(path); path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2, sort_keys=True); stream.write("\n"); stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        try: os.unlink(temporary)
        except FileNotFoundError: pass
def load_json(path: Path, label: str) -> dict[str, Any]:
    value = json.loads(safe_file(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict): fail(f"{label} must be a JSON object")
    return value
def load_state(path: Path) -> dict[str, Any]:
    value = load_json(path, "plan-issue state")
    if value.get("schema_version") != 2: fail("unsupported plan-issue state")
    return value
def git_head(repo: Path) -> str:
    result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True, check=False)
    if result.returncode: fail("repository must have an inspected Git commit")
    return result.stdout.strip()
def code_fingerprint(repo: Path, dev_dir: Path, ignored: tuple[Path, ...] = ()) -> str:
    result = subprocess.run(["git", "ls-files", "-z"], cwd=repo, capture_output=True, check=False)
    if result.returncode: fail("repository tracked files cannot be inspected")
    records = []
    for raw in result.stdout.split(b"\0"):
        if not raw: continue
        relative = Path(os.fsdecode(raw)); path = repo / relative
        if any(path.absolute() == item.absolute() for item in ignored): continue
        try: path.absolute().relative_to(dev_dir.absolute())
        except ValueError: pass
        else: continue
        if path.is_file() and not path.is_symlink(): records.append((relative.as_posix(), digest(path)))
    return json_digest(records)

def parse_task(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    patterns = [r"^# (.+)$", r"^- Redmine: `?#(\d+)`?\s*$", r"^- Tipo: `?([A-Za-z]+)`?\s*$", r"^- Tracker: (.+?) \(`?(\d+)`?\)\s*$", r"^- Item pai: `?#(\d+)`?\s*$"]
    found = [re.search(pattern, text, re.MULTILINE) for pattern in patterns]
    description = re.search(r"^## Descri(?:ção|Ã§Ã£o)\s*\n+(.*)(?=\n## Rela(?:\u00e7\u00f5es|\u00c3\u00a7\u00c3\u00b5es)\s*\n)", text, re.MULTILINE | re.DOTALL)
    if not all(found) or not description: fail("task.md does not satisfy the canonical child contract")
    return {"title": found[0].group(1).strip(), "id": int(found[1].group(1)), "kind": found[2].group(1).upper(),
            "tracker_name": found[3].group(1).strip(), "tracker_id": int(found[3].group(2)), "parent_id": int(found[4].group(1)), "description": description.group(1).strip()}
def nested_id(value: Any, label: str) -> int:
    if isinstance(value, dict): value = value.get("id")
    if isinstance(value, bool) or not isinstance(value, int) or value < 1: fail(f"{label} is missing or invalid")
    return value
def origin_contract(path: Path, task: Path, issue_id: int) -> dict[str, Any]:
    origin = load_json(path, "canonical origin"); reject_secrets(origin, "canonical origin")
    if origin.get("status") == "completed" and isinstance(origin.get("artifact_updates"), list):
        pointer = origin.get("revisions", [{}])[-1].get("publication", {})
        publication_path = safe_file(Path(str(pointer.get("path", ""))))
        if digest(publication_path) != pointer.get("sha256"): fail("canonical publication evidence changed")
        publication = load_json(publication_path, "canonical publication")
        artifacts = {item["remote_id"]: item for item in publication.get("artifacts", [])}
        seen = set()
        for update in origin["artifact_updates"]:
            number = update.get("revision")
            if not isinstance(number, int) or number in seen or not 1 <= number <= len(origin["revisions"]): fail("invalid canonical update revision")
            seen.add(number)
            for item in update["items"]:
                prior = artifacts.get(item["remote_id"])
                if item.get("previous_sha256") != (prior["sha256"] if prior else None): fail("canonical update history diverges")
                if prior and any(prior[k] != item[k] for k in ("path", "kind")): fail("canonical update changes task identity")
                artifacts[item["remote_id"]] = item
        if len(origin["revisions"]) not in seen: fail("canonical application lacks completed artifact readback")
        origin = {**publication, "artifacts": list(artifacts.values())}
    if origin.get("status") != "completed" or not isinstance(origin.get("artifacts"), list): fail("canonical origin is missing or incomplete")
    matches = [x for x in origin["artifacts"] if isinstance(x, dict) and x.get("remote_id") == issue_id]
    if len(matches) != 1: fail("task is externally managed or absent from the canonical origin")
    artifact = matches[0]
    if artifact.get("kind") != "dev": fail("only a canonical DEV can be planned")
    if Path(str(artifact.get("path"))).absolute() != task.absolute() or artifact.get("sha256") != digest(task): fail("task.md diverges from its canonical origin")
    source = origin
    if not isinstance(origin.get("revisions"), list):
        pointer = origin.get("source", {}).get("path") if isinstance(origin.get("source"), dict) else None
        if not isinstance(pointer, str): fail("canonical origin lacks its publication source")
        source = load_json(Path(pointer), "legacy canonical source")
    revision = source.get("revisions", [None])[-1]
    if not isinstance(revision, dict): fail("canonical origin lacks its publication revision")
    project_id = nested_id(revision.get("native_fields", {}).get("project_id"), "origin project")
    parent_id = nested_id(revision.get("parent_baseline", {}).get("issue_id"), "origin parent")
    return {"path": str(path.absolute()), "sha256": digest(path), "project_id": project_id, "parent_id": parent_id}
def remote_contract(path: Path, local: dict[str, Any], origin: dict[str, Any]) -> dict[str, Any]:
    snapshot = load_json(path, "sanitized Redmine readback"); reject_secrets(snapshot, "sanitized Redmine readback")
    if set(snapshot) != {"parent", "child"} or not all(isinstance(snapshot[x], dict) for x in snapshot): fail("sanitized Redmine readback must contain exactly parent and child")
    parent, child = snapshot["parent"], snapshot["child"]
    remote = (nested_id(child.get("id"), "remote child id"), nested_id(child.get("parent"), "remote child parent"), nested_id(child.get("project"), "remote child project"), nested_id(parent.get("id"), "remote parent id"), nested_id(parent.get("project"), "remote parent project"), nested_id(child.get("tracker"), "remote tracker"), child.get("subject"), str(child.get("description", "")).strip())
    expected = (local["id"], local["parent_id"], origin["project_id"], origin["parent_id"], origin["project_id"], local["tracker_id"], local["title"], local["description"])
    if remote != expected:
        labels = ("child id", "parent id", "child project", "parent readback id", "parent project", "tracker", "title", "description")
        differences = ", ".join(label for label, actual, wanted in zip(labels, remote, expected) if actual != wanted)
        fail(f"task.md, canonical parent, origin state, and Redmine readback diverge in: {differences}")
    evidence_sha = json_digest(remote)
    return {"path": str(path.absolute()), "sha256": evidence_sha, "evidence_sha256": evidence_sha}

def invalidate(state: dict[str, Any], reason: str, at: str | None = None) -> None:
    for approval in state["approvals"]:
        if approval.get("status") == "valid":
            approval.update({"status": "invalidated", "invalidated_reason": reason})
            if at: approval["invalidated_at"] = at
    state["handoff"] = None
def evidence_current(state: dict[str, Any]) -> bool:
    repo, issue = Path(state["repository"]["path"]), state["issue"]
    if subprocess.run(["git", "merge-base", "--is-ancestor", state["repository"]["inspected_commit"], "HEAD"], cwd=repo, capture_output=True).returncode: return False
    ignored = (Path(state["alignment"]["origin"]["path"]), Path(state["alignment"]["remote"]["path"]))
    if code_fingerprint(repo, Path(issue["task_path"]).parent, ignored) != state["repository"]["code_fingerprint"]: return False
    if digest(Path(issue["task_path"])) != issue["task_sha256"] or digest(Path(issue["parent"]["requirement_path"])) != issue["parent"]["requirement_sha256"]: return False
    origin = state["alignment"]["origin"]
    if digest(Path(origin["path"])) != origin["sha256"]: return False
    local = parse_task(Path(issue["task_path"]))
    try: remote = remote_contract(Path(state["alignment"]["remote"]["path"]), local, origin)
    except ContractError: return False
    if remote["evidence_sha256"] != state["alignment"]["remote"]["evidence_sha256"]: return False
    return all(digest(repo / item["path"]) == item["sha256"] for values in state["inspection"].values() for item in values)
def require_evidence(state_path: Path, state: dict[str, Any]) -> None:
    if evidence_current(state): return
    invalidate(state, "relevant inspected evidence changed"); state["status"] = "evidence-stale"; atomic_json(state_path, state)
    fail("relevant inspected code or canonical evidence changed; baseline and planning authority were invalidated")

def command_prepare(a: argparse.Namespace) -> None:
    repo = Path(a.repo).absolute()
    if git_head(repo) != a.inspected_commit: fail("inspected commit does not match repository HEAD")
    candidates = [p for kind in ("features", "bugs") for p in (repo / "docs" / "harness" / kind).glob(f"*/tasks/*-{a.issue_id}-*/task.md") if p.is_file() and not p.is_symlink()]
    if len(candidates) != 1: fail(f"issue #{a.issue_id} must resolve to exactly one canonical task.md")
    task, local = safe_file(candidates[0], repo), parse_task(candidates[0])
    if local["kind"] != "DEV" or not task.parent.name.startswith(f"dev-{a.issue_id}-"): fail("only a canonical DEV can be planned; QA and Study are ineligible")
    if local["id"] != a.issue_id: fail("canonical task identity is inconsistent")
    parent_dir = task.parent.parent.parent; collection = parent_dir.parent.name
    parent_kind = "Feature" if collection == "features" else "Bug" if collection == "bugs" else None
    if not parent_kind or not re.match(rf"^{local['parent_id']}-", parent_dir.name): fail("canonical DEV parent identity is inconsistent")
    requirement = safe_file(parent_dir / ("feature.md" if parent_kind == "Feature" else "bug.md"), repo)
    origin = origin_contract(safe_file(Path(a.origin_state)), task, a.issue_id)
    if origin["parent_id"] != local["parent_id"]: fail("canonical origin belongs to another parent")
    remote = remote_contract(safe_file(Path(a.remote_readback)), local, origin)
    manifest = load_json(Path(a.inspection_manifest), "inspection manifest")
    if set(manifest) != set(CATEGORIES): fail("inspection manifest must contain exactly the six required categories")
    inspection = {}
    for category in CATEGORIES:
        if not isinstance(manifest[category], list) or not manifest[category]: fail(f"inspection category must not be empty: {category}")
        inspection[category] = []
        for value in manifest[category]:
            if not isinstance(value, str): fail(f"inspection path must be text: {category}")
            source = safe_file(repo / value, repo); inspection[category].append({"path": source.relative_to(repo).as_posix(), "sha256": digest(source)})
    state_path = Path(a.state).absolute()
    if state_path != (task.parent / ".flow" / "plan-issue.json").absolute(): fail("state must be <canonical-dev>/.flow/plan-issue.json")
    candidate = {"schema_version": 2, "status": "prepared", "repository": {"path": str(repo), "inspected_commit": a.inspected_commit, "code_fingerprint": code_fingerprint(repo, task.parent, (Path(a.origin_state), Path(a.remote_readback)))},
        "issue": {"id": local["id"], "kind": "DEV", "task_path": str(task), "task_sha256": digest(task), "project_id": origin["project_id"], "parent": {"id": local["parent_id"], "kind": parent_kind, "requirement_path": str(requirement), "requirement_sha256": digest(requirement)}},
        "alignment": {"origin": origin, "remote": remote}, "inspection": inspection, "baselines": [], "baseline_approvals": [], "revisions": [], "approvals": [], "execution": {"started_at": None, "current_phase": None, "completed_phases": [], "phases": []}, "handoff": None}
    if state_path.exists():
        existing = load_state(state_path)
        keys = ("repository", "issue", "alignment", "inspection")
        if any(existing.get(k) != candidate[k] for k in keys):
            if existing["issue"]["id"] != local["id"] or existing["issue"]["task_path"] != str(task): fail("canonical task identity cannot change")
            execution = existing["execution"]
            if execution.get("uncertain") or any(not record.get("commit") for record in execution.get("phases", [])):
                fail("finish or resolve the active phase before refreshing planning evidence")
            from execute_phase import verified_phase_commit
            for record in execution.get("phases", []): verified_phase_commit(repo, existing, record)
            existing.setdefault("evidence_history", []).append({k: existing[k] for k in keys})
            for k in keys: existing[k] = candidate[k]
            invalidate(existing, "canonical evidence refreshed; new baseline and approval required")
            existing["status"] = "prepared"
            atomic_json(state_path, existing)
    else: atomic_json(state_path, candidate)
    ignore_path = task.parent / ".gitignore"
    assert_safe_write(ignore_path)
    ignore = ignore_path.read_text(encoding="utf-8") if ignore_path.exists() else ""
    if "/.flow/" not in ignore.splitlines():
        ignore_path.write_text(ignore.rstrip() + "\n/.flow/\n", encoding="utf-8", newline="\n")
    print(state_path)

def evidence_identity(state: dict[str, Any]) -> str:
    return json_digest({key: state[key] for key in ("repository", "issue", "alignment", "inspection")})

def baseline_hash(value: dict[str, Any]) -> str:
    return json_digest({k: value[k] for k in ("number", "command", "inspected_commit", "duration_ms", "result", "exit_code", "normalized_failures", "normalization_version", "inspection_sha256")})
def command_baseline(a: argparse.Namespace) -> None:
    state_path = Path(a.state).absolute(); state = load_state(state_path); require_evidence(state_path, state)
    started, finished = timestamp(a.started_at), timestamp(a.finished_at); duration = int((finished - started).total_seconds() * 1000)
    if duration < 0: fail("baseline duration cannot be negative")
    with tempfile.NamedTemporaryFile(prefix="plan-issue-baseline-", suffix=".log", delete=False) as output: output_path = Path(output.name)
    try:
        with output_path.open("wb") as output: result = subprocess.run(a.command, cwd=state["repository"]["path"], shell=True, stdout=output, stderr=subprocess.STDOUT, check=False)
        lines = output_path.read_text(encoding="utf-8", errors="replace").splitlines()
        failures = normalized_failures(lines, result.returncode)
    finally: output_path.unlink(missing_ok=True)
    baseline = {"number": len(state["baselines"]) + 1, "command": sanitized_line(a.command), "inspected_commit": state["repository"]["inspected_commit"], "started_at": a.started_at, "finished_at": a.finished_at, "duration_ms": duration, "result": "green" if result.returncode == 0 else "red", "exit_code": result.returncode, "normalized_failures": failures}
    baseline.update({"normalization_version": 2, "inspection_sha256": evidence_identity(state)})
    baseline["evidence_sha256"] = baseline_hash(baseline); state["baselines"].append(baseline); invalidate(state, "new baseline recorded")
    state["status"] = "baselined" if result.returncode == 0 else "baseline-awaiting-approval"; atomic_json(state_path, state)
    if result.returncode: fail("canonical baseline is red and requires explicit developer approval")
def command_approve_baseline(a: argparse.Namespace) -> None:
    state_path = Path(a.state).absolute(); state = load_state(state_path); require_evidence(state_path, state); timestamp(a.at)
    if not a.actor.strip(): fail("baseline approval actor is required")
    if not state["baselines"] or state["baselines"][-1]["result"] != "red": fail("the current baseline is not red")
    baseline = state["baselines"][-1]; state["baseline_approvals"].append({"baseline_number": baseline["number"], "baseline_sha256": baseline["evidence_sha256"], "approved_by": a.actor.strip(), "approved_at": a.at}); state["status"] = "baselined"; atomic_json(state_path, state)
def accepted_baseline(state: dict[str, Any]) -> dict[str, Any]:
    if not state["baselines"]: fail("a canonical baseline is required before planning")
    baseline = state["baselines"][-1]
    if baseline.get("normalization_version") != 2 or baseline.get("inspection_sha256") != evidence_identity(state): fail("a fresh baseline is required for the refreshed evidence")
    if baseline["result"] == "green": return baseline
    if not any(x["baseline_number"] == baseline["number"] and x["baseline_sha256"] == baseline["evidence_sha256"] for x in state["baseline_approvals"]): fail("red baseline failures require explicit developer approval")
    return baseline

def parse_planning(path: Path, expected: Path) -> tuple[str, list[dict[str, Any]]]:
    if path.absolute() != expected.absolute(): fail("the sole planning artifact must be <canonical-dev>/planning.md")
    text = safe_file(path).read_text(encoding="utf-8"); headings = re.findall(r"^## (.+)$", text, re.MULTILINE)
    if headings[:len(PLAN_SECTIONS)] != list(PLAN_SECTIONS): fail("planning.md is missing or reorders required sections")
    matches = list(re.finditer(r"^## Fase (\d+) — (.+)$", text, re.MULTILINE)); numbers = [int(x.group(1)) for x in matches]
    if not matches or numbers != sorted(set(numbers)): fail("planning.md phases must have unique increasing numbers")
    phases = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text); body = text[match.start():end].rstrip() + "\n"
        if re.findall(r"^### (.+)$", body, re.MULTILINE) != list(PHASE_SECTIONS): fail(f"Fase {match.group(1)} does not satisfy the phase contract")
        for section in PHASE_SECTIONS:
            content = re.search(rf"^### {re.escape(section)}\s*\n+(.*?)(?=\n### |\Z)", body, re.MULTILINE | re.DOTALL)
            if not content or not content.group(1).strip(): fail(f"Fase {match.group(1)} has an empty {section}")
        phases.append({"number": int(match.group(1)), "title": match.group(2).strip(), "sha256": hashlib.sha256(body.encode()).hexdigest()})
    return digest(path), phases
def current_revision(state: dict[str, Any]) -> dict[str, Any]:
    if not state["revisions"]: fail("planning.md has not been recorded")
    return state["revisions"][-1]
def command_record(a: argparse.Namespace) -> None:
    state_path = Path(a.state).absolute(); state = load_state(state_path); require_evidence(state_path, state); baseline = accepted_baseline(state); timestamp(a.at)
    planning = Path(a.planning).absolute(); planning_sha, phases = parse_planning(planning, Path(state["issue"]["task_path"]).parent / "planning.md")
    previous = state["revisions"][-1] if state["revisions"] else None
    if previous:
        previous_by = {x["number"]: x for x in previous["phases"]}; current_by = {x["number"]: x for x in phases}; completed = set(state["execution"]["completed_phases"])
        for number in completed:
            if number not in current_by or current_by[number]["sha256"] != previous_by[number]["sha256"]: fail(f"completed phase {number} must be preserved byte-for-byte")
        historical = {x["number"] for revision in state["revisions"] for x in revision["phases"]}; new = set(current_by) - set(previous_by)
        if (historical - set(previous_by)) & set(current_by): fail("a retired phase number cannot be reused")
        if new and min(new) <= max(historical): fail("new phases must continue after the highest historical phase number")
        if state["execution"]["started_at"] is not None:
            approval = state["execution"].get("impact_approval")
            if not isinstance(approval, dict) or approval.get("for_planning_sha256") != planning_sha: fail("replanning after Ralph starts requires explicit approval of the pending-work impact")
    state["revisions"].append({"number": len(state["revisions"]) + 1, "planning_path": str(planning), "planning_sha256": planning_sha, "recorded_at": a.at, "reason": a.reason, "baseline_number": baseline["number"], "baseline_sha256": baseline["evidence_sha256"], "phases": phases})
    invalidate(state, "planning revision recorded", a.at); state["status"] = "draft"; atomic_json(state_path, state)
def command_observe_execution(a: argparse.Namespace) -> None:
    state_path = Path(a.state).absolute(); state = load_state(state_path); timestamp(a.at); known = {x["number"] for x in current_revision(state)["phases"]}; completed = sorted(set(a.completed_phase))
    if not set(completed).issubset(known): fail("completed phases must belong to the current planning revision")
    if not set(state["execution"]["completed_phases"]).issubset(completed): fail("completed phase observations are append-only")
    state["execution"].update({"started_at": state["execution"]["started_at"] or a.at, "completed_phases": completed, "observed_at": a.at}); state["execution"].pop("impact_approval", None); atomic_json(state_path, state)
def command_approve_impact(a: argparse.Namespace) -> None:
    state_path = Path(a.state).absolute(); state = load_state(state_path); timestamp(a.at)
    if state["execution"]["started_at"] is None: fail("Ralph has not started")
    planning = safe_file(Path(current_revision(state)["planning_path"])); current = digest(planning)
    if current == current_revision(state)["planning_sha256"]: fail("pending-work impact approval is only required for a changed plan")
    if not a.actor.strip() or not a.impact.strip(): fail("impact approval requires actor and impact")
    state["execution"]["impact_approval"] = {"for_planning_sha256": current, "approved_by": a.actor.strip(), "approved_at": a.at, "impact": sanitized_line(a.impact)}; atomic_json(state_path, state)
def current_artifact(state_path: Path, state: dict[str, Any]) -> tuple[Path, str, dict[str, Any]]:
    revision = current_revision(state); planning = safe_file(Path(revision["planning_path"])); current = digest(planning)
    if current != revision["planning_sha256"]:
        invalidate(state, "planning.md changed"); state["status"] = "draft-changed"; atomic_json(state_path, state); fail("planning.md changed; exact-hash approval was invalidated")
    return planning, current, revision
def command_approve(a: argparse.Namespace) -> None:
    state_path = Path(a.state).absolute(); state = load_state(state_path); require_evidence(state_path, state); planning, current, revision = current_artifact(state_path, state); parse_planning(planning, Path(state["issue"]["task_path"]).parent / "planning.md"); timestamp(a.at); accepted_baseline(state)
    if not a.actor.strip(): fail("approval actor is required")
    state["approvals"].append({"revision": revision["number"], "planning_sha256": current, "approved_by": a.actor.strip(), "approved_at": a.at, "status": "valid"}); state["handoff"] = None; state["status"] = "approved"; atomic_json(state_path, state)
def approved_artifact(state_path: Path, state: dict[str, Any]) -> tuple[Path, str]:
    require_evidence(state_path, state); accepted_baseline(state); planning, current, revision = current_artifact(state_path, state)
    if not any(x["status"] == "valid" and x["revision"] == revision["number"] and x["planning_sha256"] == current for x in state["approvals"]): fail("planning.md requires explicit approval of its exact current hash")
    return planning, current
def handoff_command(state_path: Path, planning: Path) -> str:
    ralph = safe_file(Path(__file__).resolve().parent.parent / "ralph.sh"); return f"bash {shlex.quote(str(ralph))} execute {shlex.quote(str(planning))} --state {shlex.quote(str(state_path))}"
def command_handoff(a: argparse.Namespace) -> None:
    state_path = Path(a.state).absolute(); state = load_state(state_path); planning, current = approved_artifact(state_path, state); command = handoff_command(state_path, planning); state["handoff"] = {"planning_sha256": current, "command": command, "commit": "manual"}; state["status"] = "ready"; atomic_json(state_path, state); print(command)
def command_verify(a: argparse.Namespace) -> None:
    state_path = Path(a.state).absolute(); state = load_state(state_path); planning, current = approved_artifact(state_path, state)
    if planning.absolute() != Path(a.planning).absolute(): fail("Ralph planning path differs from the approved artifact")
    if not isinstance(state.get("handoff"), dict) or state["handoff"].get("planning_sha256") != current: fail("Ralph requires the recorded approved handoff")
    print(f"approved planning verified: {current}")

def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(); commands = root.add_subparsers(dest="command", required=True)
    p = commands.add_parser("prepare"); p.add_argument("repo"); p.add_argument("issue_id", type=int); p.add_argument("--state", required=True); p.add_argument("--inspection-manifest", required=True); p.add_argument("--inspected-commit", required=True); p.add_argument("--origin-state", required=True); p.add_argument("--remote-readback", required=True); p.set_defaults(run=command_prepare)
    p = commands.add_parser("baseline"); p.add_argument("state"); p.add_argument("--command", required=True); p.add_argument("--started-at", required=True); p.add_argument("--finished-at", required=True); p.set_defaults(run=command_baseline)
    p = commands.add_parser("approve-baseline"); p.add_argument("state"); p.add_argument("--actor", required=True); p.add_argument("--at", required=True); p.set_defaults(run=command_approve_baseline)
    p = commands.add_parser("record"); p.add_argument("state"); p.add_argument("planning"); p.add_argument("--at", required=True); p.add_argument("--reason", required=True); p.set_defaults(run=command_record)
    p = commands.add_parser("observe-execution"); p.add_argument("state"); p.add_argument("--at", required=True); p.add_argument("--completed-phase", action="append", type=int, default=[]); p.set_defaults(run=command_observe_execution)
    p = commands.add_parser("approve-impact"); p.add_argument("state"); p.add_argument("--actor", required=True); p.add_argument("--at", required=True); p.add_argument("--impact", required=True); p.set_defaults(run=command_approve_impact)
    p = commands.add_parser("approve"); p.add_argument("state"); p.add_argument("--actor", required=True); p.add_argument("--at", required=True); p.set_defaults(run=command_approve)
    p = commands.add_parser("handoff"); p.add_argument("state"); p.set_defaults(run=command_handoff)
    p = commands.add_parser("verify-execution"); p.add_argument("state"); p.add_argument("planning"); p.set_defaults(run=command_verify)
    return root
def main() -> int:
    try: a = parser().parse_args(); a.run(a); return 0
    except (ContractError, json.JSONDecodeError, OSError, KeyError, IndexError) as exception: print(str(exception), file=sys.stderr); return 1
if __name__ == "__main__": raise SystemExit(main())
