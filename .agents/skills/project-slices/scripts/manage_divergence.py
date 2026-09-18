#!/usr/bin/env python3
"""Resolve material parent/slice divergences before child publication."""

from __future__ import annotations

import argparse
import copy
import json
import sys
import uuid
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

from manage_slices import (
    ContractError,
    atomic_write,
    canonical_bytes,
    digest,
    file_digest,
    load_json,
    reject_secrets,
    require_text,
    require_timestamp,
    validate_feature_approval,
)
from manage_publication import atomic_batch_write, named_id, positive_int


def fail(message: str) -> None:
    raise ContractError(message)


def exact(value: Any, fields: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != fields:
        fail(f"{label} has missing or unknown fields")
    return value


def evidence_path(feature_dir: Path, value: Any, label: str) -> Path:
    path = Path(require_text(value, label)).absolute()
    try:
        path.relative_to((feature_dir / ".work").absolute())
    except ValueError:
        fail(f"{label} must be disposable evidence under the Feature .work directory")
    if not path.is_file() or path.is_symlink():
        fail(f"{label} must be a regular evidence file")
    return path


def issue(snapshot: dict[str, Any]) -> dict[str, Any]:
    value = snapshot.get("issue", snapshot)
    if not isinstance(value, dict):
        fail("parent snapshot must contain an issue object")
    reject_secrets(value, "parent snapshot")
    return value


def managed_description(document: str, canonical: Path, approved_by: str, before: str) -> str:
    scripts = Path(__file__).resolve().parents[2] / "project-flow" / "scripts"
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    try:
        from render_publication import END, START, canonical_reference_path, projection
    except ImportError as error:
        fail(f"cannot load project-flow publication contract: {error}")
    if before.count(START) != 1 or before.count(END) != 1 or before.index(START) > before.index(END):
        fail("parent baseline requires exactly one ordered managed delimiter pair")
    start = before.index(START) + len(START)
    end = before.index(END)
    projected = projection(document, "Feature", canonical_reference_path(canonical), approved_by)
    return before[:start] + projected + before[end:]


def correction_digest(revision: dict[str, Any]) -> str:
    return digest({
        "source": revision["source"],
        "parent_baseline": revision["parent_baseline"],
        "proposed_document": revision["proposed_document"],
        "proposal_evidence": revision["proposal_evidence"],
        "divergences": revision["divergences"],
        "impact": revision["impact"],
        "remote_payload": revision["remote_payload"],
    })


def validate_state(state: dict[str, Any], previous: dict[str, Any] | None = None, *, check_files: bool = True) -> None:
    exact(state, {
        "schema_version", "status", "status_history", "revisions", "decisions",
        "local_alignments", "operation", "readback", "completed_at",
    }, "divergence state")
    statuses = {"pending", "rejected", "approved", "local-aligned", "aligning", "completed"}
    if state["schema_version"] != 1 or state["status"] not in statuses:
        fail("unsupported divergence state")
    if not isinstance(state["status_history"], list) or not state["status_history"]:
        fail("divergence status history is invalid")
    for entry in state["status_history"]:
        exact(entry, {"status", "recorded_at"}, "divergence status history entry")
        if entry["status"] not in statuses:
            fail("divergence status history contains an invalid status")
        require_timestamp(entry["recorded_at"], "status history recorded_at")
    if not isinstance(state["revisions"], list) or not state["revisions"]:
        fail("divergence state requires revision history")
    for number, revision in enumerate(state["revisions"], start=1):
        exact(revision, {
            "number", "recorded_by", "recorded_at", "reason", "source", "parent_baseline",
            "proposed_document", "proposal_evidence", "divergences", "impact", "remote_payload",
            "correction_sha256",
        }, f"divergence revision {number}")
        if revision["number"] != number or revision["correction_sha256"] != correction_digest(revision):
            fail("divergence revision identity or hash differs")
        require_text(revision["recorded_by"], "revision.recorded_by")
        require_timestamp(revision["recorded_at"], "revision.recorded_at")
        require_text(revision["reason"], "revision.reason")
        exact(revision["source"], {"artifact_path", "artifact_sha256", "state_path", "state_sha256", "approval_sha256"}, "source")
        exact(revision["parent_baseline"], {"path", "sha256", "issue_id", "subject", "description_sha256", "status", "relations", "preserved_fields"}, "parent_baseline")
        exact(revision["proposed_document"], {"content", "sha256"}, "proposed_document")
        if revision["proposed_document"]["sha256"] != digest(revision["proposed_document"]["content"]):
            fail("proposed canonical document hash differs")
        if not isinstance(revision["divergences"], list) or not revision["divergences"]:
            fail("material divergence requires at least one exact correction")
        affected: set[str] = set()
        for value in revision["divergences"]:
            exact(value, {"id", "kind", "approved", "proposed", "impact", "affected_children"}, "material divergence")
            for field in ("id", "kind", "approved", "proposed", "impact"):
                require_text(value[field], f"material divergence.{field}")
            children = value["affected_children"]
            if not isinstance(children, list) or not children or any(not isinstance(item, str) or not item.strip() for item in children):
                fail("material divergence must name every affected child")
            affected.update(children)
        exact(revision["impact"], {"affected_children", "publication_effect"}, "impact")
        if sorted(revision["impact"]["affected_children"]) != sorted(affected):
            fail("correction impact must exactly cover affected children")
        require_text(revision["impact"]["publication_effect"], "impact.publication_effect")
        payload = exact(revision["remote_payload"], {"issue_id", "changes"}, "remote_payload")
        exact(payload["changes"], {"description"}, "remote_payload.changes")
        positive_int(payload["issue_id"], "remote_payload.issue_id")
        require_text(payload["changes"]["description"], "remote_payload.changes.description")
        if check_files:
            for key, hash_key in (("artifact_path", "artifact_sha256"), ("state_path", "state_sha256")):
                path = Path(revision["source"][key])
                if not path.is_file() or file_digest(path) != revision["source"][hash_key]:
                    if number == len(state["revisions"]) and state["status"] in {"pending", "approved", "rejected"}:
                        fail("approved parent source changed before correction alignment")
            for evidence in (revision["parent_baseline"], revision["proposal_evidence"]):
                evidence_file = Path(evidence["path"])
                if not evidence_file.is_file() or file_digest(evidence_file) != evidence["sha256"]:
                    fail("correction evidence changed after preview")
    decisions = state["decisions"]
    if not isinstance(decisions, list):
        fail("divergence decisions must be an array")
    for decision in decisions:
        exact(decision, {"revision", "correction_sha256", "decision", "decided_by", "decided_at", "reason", "role"}, "divergence decision")
        if decision["role"] != "tech-lead" or decision["decision"] not in {"approved", "rejected"}:
            fail("material correction decision belongs exclusively to the tech lead")
        if decision["revision"] < 1 or decision["revision"] > len(state["revisions"]):
            fail("divergence decision references an unknown revision")
        if decision["correction_sha256"] != state["revisions"][decision["revision"] - 1]["correction_sha256"]:
            fail("divergence decision is not bound to its correction")
        require_text(decision["decided_by"], "decision.decided_by")
        require_timestamp(decision["decided_at"], "decision.decided_at")
        require_text(decision["reason"], "decision.reason")
    current = state["revisions"][-1]
    current_decisions = [item for item in decisions if item["revision"] == current["number"]]
    if state["status"] == "pending" and current_decisions:
        fail("pending correction cannot already contain a decision")
    if state["status"] != "pending" and len(current_decisions) != 1:
        fail("resolved correction requires exactly one current tech-lead decision")
    if state["status"] == "rejected" and current_decisions[0]["decision"] != "rejected":
        fail("rejected correction requires a rejection decision")
    if state["status"] not in {"pending", "rejected"} and current_decisions[0]["decision"] != "approved":
        fail("correction alignment requires an approved decision")
    if not isinstance(state["local_alignments"], list) or len(state["local_alignments"]) > 1:
        fail("local correction alignment history is invalid")
    if state["status"] in {"local-aligned", "aligning", "completed"} and len(state["local_alignments"]) != 1:
        fail("remote alignment requires verified local canonical alignment")
    operation = state["operation"]
    if operation is not None:
        exact(operation, {"kind", "payload_sha256", "attempts", "observations", "status"}, "parent update operation")
        if operation["kind"] != "update-parent" or operation["payload_sha256"] != digest(current["remote_payload"]):
            fail("parent update operation differs from the approved correction")
        if operation["status"] not in {"pending", "completed"}:
            fail("parent update operation status is invalid")
    if state["status"] == "completed" and (operation is None or operation["status"] != "completed" or not isinstance(state["readback"], dict) or state["completed_at"] is None):
        fail("completed correction requires verified remote-parent readback")
    if isinstance(state["readback"], dict):
        readback_path = Path(state["readback"]["snapshot_path"])
        if not readback_path.is_file() or file_digest(readback_path) != state["readback"]["snapshot_sha256"]:
            fail("remote-parent readback evidence is missing or changed")
    reject_secrets(state, "divergence state")
    if previous is not None:
        validate_state(previous, check_files=False)
        for field in ("revisions", "decisions", "local_alignments", "status_history"):
            if state[field][:len(previous[field])] != previous[field]:
                fail(f"divergence {field} history was rewritten")
        old_operation = previous["operation"]
        if old_operation is not None:
            if state["operation"] is None:
                fail("parent update operation was removed")
            if state["operation"]["kind"] != old_operation["kind"] or state["operation"]["payload_sha256"] != old_operation["payload_sha256"]:
                fail("parent update identity was rewritten")
            if state["operation"]["observations"][:len(old_operation["observations"])] != old_operation["observations"]:
                fail("parent update observation history was rewritten")
            old_attempts = old_operation["attempts"]
            new_attempts = state["operation"]["attempts"]
            if len(new_attempts) < len(old_attempts) or new_attempts[:max(0, len(old_attempts) - 1)] != old_attempts[:-1]:
                fail("parent update attempt history was rewritten")
            if old_attempts and new_attempts[len(old_attempts) - 1] != old_attempts[-1]:
                old_last = old_attempts[-1]
                new_last = new_attempts[len(old_attempts) - 1]
                stable = {field: old_last[field] for field in ("id", "attempted_at", "payload_sha256")}
                if old_last["outcome"] != "in-flight" or any(new_last.get(field) != value for field, value in stable.items()) or new_last.get("outcome") not in {"completed", "failed", "unknown"}:
                    fail("parent update attempt history was rewritten")
            if old_operation["status"] == "completed" and state["operation"] != old_operation:
                fail("completed parent update operation was rewritten")
        if previous["readback"] is not None and state["readback"] != previous["readback"]:
            fail("remote-parent readback was rewritten")


def command_prepare(arguments: argparse.Namespace) -> None:
    feature_dir = Path(arguments.feature_dir).absolute()
    canonical, state_path, feature_state, approval, canonical_content = validate_feature_approval(feature_dir, permit_divergence=True)
    plan_path = evidence_path(feature_dir, arguments.plan, "divergence plan")
    plan = load_json(plan_path)
    exact(plan, {"proposed_document", "parent_snapshot", "proposal_evidence", "divergences", "impact"}, "divergence plan")
    proposed_path = evidence_path(feature_dir, plan["proposed_document"], "proposed document")
    proposed_content = proposed_path.read_text(encoding="utf-8")
    if not proposed_content.startswith(canonical_content.decode("utf-8").splitlines()[0] + "\n"):
        fail("correction cannot silently change the approved parent title")
    parent_path = evidence_path(feature_dir, plan["parent_snapshot"], "parent snapshot")
    parent = issue(load_json(parent_path))
    issue_id = positive_int(parent.get("id", parent.get("issue_id")), "parent issue id")
    if issue_id != feature_state["redmine"]["issue_id"]:
        fail("parent baseline belongs to another issue")
    title = proposed_content.splitlines()[0].removeprefix("# ").strip()
    if parent.get("subject") != title:
        fail("parent baseline subject differs from the canonical Feature")
    before_description = require_text(parent.get("description"), "parent.description")
    actor = require_text(arguments.actor, "recorded_by")
    payload = {"issue_id": issue_id, "changes": {"description": managed_description(proposed_content, canonical, actor, before_description)}}
    divergences = plan["divergences"]
    if any(item.get("kind") == "api-expansion" for item in divergences if isinstance(item, dict)):
        evidence = load_json(evidence_path(feature_dir, plan["proposal_evidence"], "proposal evidence"))
        slices = evidence.get("slices", [])
        if not any(isinstance(item, dict) and item.get("api_delivery") is True for item in slices):
            fail("API expansion evidence does not contain an API child proposal")
    proposal_path = evidence_path(feature_dir, plan["proposal_evidence"], "proposal evidence")
    revision = {
        "number": 1,
        "recorded_by": actor,
        "recorded_at": require_timestamp(arguments.at, "recorded_at"),
        "reason": require_text(arguments.reason, "reason"),
        "source": {
            "artifact_path": str(canonical), "artifact_sha256": file_digest(canonical),
            "state_path": str(state_path), "state_sha256": file_digest(state_path),
            "approval_sha256": digest(approval),
        },
        "parent_baseline": {
            "path": str(parent_path), "sha256": file_digest(parent_path), "issue_id": issue_id,
            "subject": title, "description_sha256": digest(before_description),
            "status": copy.deepcopy(parent.get("status")), "relations": copy.deepcopy(parent.get("relations", [])),
            "preserved_fields": {key: copy.deepcopy(value) for key, value in parent.items() if key != "description"},
        },
        "proposed_document": {"content": proposed_content, "sha256": digest(proposed_content)},
        "proposal_evidence": {"path": str(proposal_path), "sha256": file_digest(proposal_path)},
        "divergences": copy.deepcopy(divergences), "impact": copy.deepcopy(plan["impact"]),
        "remote_payload": payload,
    }
    revision["correction_sha256"] = correction_digest(revision)
    output = Path(arguments.state).absolute()
    if output != (feature_dir / ".flow" / "slices-divergence.json").absolute():
        fail("divergence state must use .flow/slices-divergence.json")
    if output.exists():
        state = load_json(output)
        validate_state(state)
        if state["operation"] is not None or state["local_alignments"]:
            fail("a correction with alignment progress cannot be revised")
        revision["number"] = len(state["revisions"]) + 1
        state["revisions"].append(revision)
        state["status"] = "pending"
        state["status_history"].append({"status": "pending", "recorded_at": revision["recorded_at"]})
    else:
        state = {
            "schema_version": 1, "status": "pending",
            "status_history": [{"status": "pending", "recorded_at": revision["recorded_at"]}],
            "revisions": [revision], "decisions": [], "local_alignments": [],
            "operation": None, "readback": None, "completed_at": None,
        }
    validate_state(state)
    lines = [
        f"# Correção proposta para {title}", "", f"Hash: `{revision['correction_sha256']}`", "",
        "## Divergências materiais", "",
    ]
    for item in divergences:
        lines.extend([
            f"### {item['id']} — {item['kind']}", "", f"- Aprovado: {item['approved']}",
            f"- Correção proposta: {item['proposed']}", f"- Impacto: {item['impact']}",
            f"- Filhas afetadas: {', '.join(item['affected_children'])}", "",
        ])
    lines.extend(["## Efeito na publicação", "", plan["impact"]["publication_effect"], "", "## Descrição remota resultante", "", payload["changes"]["description"]])
    preview = Path(arguments.preview).absolute()
    if preview != (feature_dir / "slices" / "divergence.md").absolute():
        fail("divergence preview must use slices/divergence.md")
    atomic_batch_write({output: canonical_bytes(state) + b"\n", preview: ("\n".join(lines).rstrip() + "\n").encode("utf-8")})
    print(json.dumps({"status": "pending", "revision": revision["number"], "correction_sha256": revision["correction_sha256"]}))


def command_decide(arguments: argparse.Namespace) -> None:
    path = Path(arguments.state)
    state = load_json(path)
    validate_state(state)
    if state["status"] != "pending":
        fail("only a pending material correction can receive a decision")
    current = state["revisions"][-1]
    decision = arguments.decision
    at = require_timestamp(arguments.at, "decided_at")
    state["decisions"].append({
        "revision": current["number"], "correction_sha256": current["correction_sha256"],
        "decision": decision, "decided_by": require_text(arguments.actor, "decided_by"),
        "decided_at": at, "reason": require_text(arguments.reason, "reason"), "role": "tech-lead",
    })
    state["status"] = decision
    state["status_history"].append({"status": decision, "recorded_at": at})
    validate_state(state)
    atomic_write(path, canonical_bytes(state) + b"\n")
    print(json.dumps({"status": decision, "correction_sha256": current["correction_sha256"]}))


def updated_feature_state(current: dict[str, Any], new_sha: str, actor: str, at: str, reason: str) -> dict[str, Any]:
    result = copy.deepcopy(current)
    approvals = result.get("approvals", [])
    valid = [item for item in approvals if item.get("kind") == "requirement" and item.get("status") == "valid"]
    if len(valid) != 1:
        fail("local alignment requires exactly one prior valid requirement approval")
    old = valid[0]
    full = "id" in old
    old["status"] = "invalidated"
    if full:
        old["invalidated_at"] = at
        old["invalidated_reason"] = reason
        approval = {
            "id": str(uuid.uuid4()), "kind": "requirement", "subject_sha256": new_sha,
            "approved_by": actor, "approved_at": at, "status": "valid",
        }
    else:
        approval = {"kind": "requirement", "status": "valid", "subject_sha256": new_sha, "approved_by": actor}
    approvals.append(approval)
    return result


def command_apply_local(arguments: argparse.Namespace) -> None:
    path = Path(arguments.state)
    state = load_json(path)
    validate_state(state)
    if state["status"] in {"local-aligned", "aligning", "completed"}:
        print(json.dumps({"status": "local-aligned", **state["local_alignments"][0]}))
        return
    if state["status"] != "approved":
        fail("local canonical correction requires the current tech-lead approval")
    current = state["revisions"][-1]
    source = current["source"]
    artifact = Path(source["artifact_path"])
    feature_state_path = Path(source["state_path"])
    if file_digest(artifact) != source["artifact_sha256"] or file_digest(feature_state_path) != source["state_sha256"]:
        fail("approved parent source changed before local correction")
    feature_state = load_json(feature_state_path)
    decision = state["decisions"][-1]
    content = current["proposed_document"]["content"].encode("utf-8")
    new_sha = __import__("hashlib").sha256(content).hexdigest()
    new_feature_state = updated_feature_state(feature_state, new_sha, decision["decided_by"], decision["decided_at"], decision["reason"])
    scripts = Path(__file__).resolve().parents[2] / "project-flow" / "scripts"
    if set(feature_state) >= {"run_id", "completed_phases", "remote_operations"}:
        if str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        from validate_state import validate, validate_transition
        validate_transition(validate(feature_state_path), new_feature_state)
    state_copy = copy.deepcopy(state)
    aligned_at = require_timestamp(arguments.at, "aligned_at")
    state_copy["local_alignments"].append({
        "revision": current["number"], "correction_sha256": current["correction_sha256"],
        "artifact_before_sha256": source["artifact_sha256"], "artifact_after_sha256": new_sha,
        "state_before_sha256": source["state_sha256"], "state_after_sha256": digest(new_feature_state),
        "requirement_approval_sha256": digest(new_feature_state["approvals"][-1]), "aligned_at": aligned_at,
    })
    state_copy["status"] = "local-aligned"
    state_copy["status_history"].append({"status": "local-aligned", "recorded_at": aligned_at})
    validate_state(state_copy, check_files=False)
    atomic_batch_write({artifact: content, feature_state_path: json.dumps(new_feature_state, ensure_ascii=False, indent=2).encode("utf-8") + b"\n", path: canonical_bytes(state_copy) + b"\n"})
    print(json.dumps({"status": "local-aligned", **state_copy["local_alignments"][0]}))


def local_is_current(state: dict[str, Any]) -> None:
    current = state["revisions"][-1]
    alignment = state["local_alignments"][0]
    artifact = Path(current["source"]["artifact_path"])
    feature_state_path = Path(current["source"]["state_path"])
    if file_digest(artifact) != alignment["artifact_after_sha256"]:
        fail("corrected canonical artifact changed after local alignment")
    feature_state = load_json(feature_state_path)
    approvals = [item for item in feature_state.get("approvals", []) if item.get("kind") == "requirement" and item.get("status") == "valid"]
    if len(approvals) != 1 or digest(approvals[0]) != alignment["requirement_approval_sha256"]:
        fail("corrected canonical approval changed after local alignment")


def command_begin_update(arguments: argparse.Namespace) -> None:
    path = Path(arguments.state)
    state = load_json(path)
    validate_state(state, check_files=False)
    if state["status"] == "completed":
        fail("completed parent update must not be duplicated")
    if state["status"] not in {"local-aligned", "aligning"}:
        fail("parent update requires approved and verified local alignment")
    local_is_current(state)
    current = state["revisions"][-1]
    operation = state["operation"]
    if operation is None:
        operation = {"kind": "update-parent", "payload_sha256": digest(current["remote_payload"]), "attempts": [], "observations": [], "status": "pending"}
        state["operation"] = operation
    if operation["status"] == "completed":
        fail("completed parent update must not be duplicated")
    if operation["attempts"] and operation["attempts"][-1]["outcome"] in {"in-flight", "unknown"}:
        observations = operation["observations"]
        if not observations or observations[-1]["outcome"] != "baseline" or observations[-1]["attempt_id"] != operation["attempts"][-1]["id"]:
            fail("uncertain parent update requires baseline readback before retry")
    at = require_timestamp(arguments.at, "attempted_at")
    attempt = {"id": len(operation["attempts"]) + 1, "attempted_at": at, "payload_sha256": operation["payload_sha256"], "outcome": "in-flight"}
    operation["attempts"].append(attempt)
    state["status"] = "aligning"
    state["status_history"].append({"status": "aligning", "recorded_at": at})
    atomic_write(path, canonical_bytes(state) + b"\n")
    print(json.dumps({"attempt_id": attempt["id"], "tool": "redmine_update_issue", "payload": current["remote_payload"]}, ensure_ascii=False))


def command_finish_update(arguments: argparse.Namespace) -> None:
    path = Path(arguments.state)
    state = load_json(path)
    validate_state(state, check_files=False)
    operation = state["operation"]
    if operation is None or not operation["attempts"] or operation["attempts"][-1]["id"] != arguments.attempt or operation["attempts"][-1]["outcome"] != "in-flight":
        fail("parent update result must finish the current in-flight attempt")
    attempt = operation["attempts"][-1]
    attempt["outcome"] = arguments.outcome
    attempt["finished_at"] = require_timestamp(arguments.at, "finished_at")
    if arguments.outcome == "failed":
        attempt["error_code"] = require_text(arguments.error_code, "error_code")
        attempt["message"] = require_text(arguments.message, "message")
    atomic_write(path, canonical_bytes(state) + b"\n")


def compare_parent(state: dict[str, Any], snapshot: dict[str, Any]) -> str:
    current = state["revisions"][-1]
    observed = issue(snapshot)
    baseline = current["parent_baseline"]
    if positive_int(observed.get("id", observed.get("issue_id")), "readback issue id") != baseline["issue_id"]:
        fail("parent readback belongs to another issue")
    observed_preserved = {key: observed.get(key) for key in baseline["preserved_fields"]}
    if observed_preserved != baseline["preserved_fields"] or observed.get("subject") != baseline["subject"] or observed.get("status") != baseline["status"] or observed.get("relations", []) != baseline["relations"]:
        fail("parent readback changed unrelated content, execution status, or relations")
    description = require_text(observed.get("description"), "readback description")
    if description == current["remote_payload"]["changes"]["description"]:
        return "matched"
    if digest(description) == baseline["description_sha256"]:
        return "baseline"
    fail("parent readback diverges from both approved correction and pre-write baseline")


def command_observe_update(arguments: argparse.Namespace) -> None:
    path = Path(arguments.state)
    state = load_json(path)
    validate_state(state, check_files=False)
    operation = state["operation"]
    if operation is None or not operation["attempts"] or operation["attempts"][-1]["outcome"] not in {"in-flight", "unknown", "completed"}:
        fail("parent update readback requires an attempted operation")
    snapshot_path = evidence_path(path.parent.parent, arguments.snapshot, "parent update readback")
    observed = load_json(snapshot_path)
    outcome = compare_parent(state, observed)
    if outcome != arguments.outcome:
        fail("parent update observation outcome differs from exact readback")
    operation["observations"].append({
        "attempt_id": operation["attempts"][-1]["id"], "outcome": outcome,
        "observed_at": require_timestamp(arguments.at, "observed_at"),
        "snapshot_path": str(snapshot_path), "snapshot_sha256": file_digest(snapshot_path),
    })
    if outcome == "matched":
        operation["status"] = "completed"
        state["readback"] = operation["observations"][-1]
        state["completed_at"] = operation["observations"][-1]["observed_at"]
        state["status"] = "completed"
        state["status_history"].append({"status": "completed", "recorded_at": state["completed_at"]})
    validate_state(state, check_files=False)
    atomic_write(path, canonical_bytes(state) + b"\n")
    print(json.dumps({"status": state["status"], "outcome": outcome}))


def command_validate(arguments: argparse.Namespace) -> None:
    state = load_json(Path(arguments.state))
    previous = load_json(Path(arguments.previous)) if arguments.previous else None
    validate_state(state, previous, check_files=state["status"] in {"pending", "approved", "rejected"})
    if state["status"] in {"local-aligned", "aligning", "completed"}:
        local_is_current(state)
    print("valid")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(required=True)
    prepare = commands.add_parser("prepare")
    prepare.add_argument("state"); prepare.add_argument("plan"); prepare.add_argument("--feature-dir", required=True); prepare.add_argument("--preview", required=True)
    prepare.add_argument("--actor", required=True); prepare.add_argument("--at", required=True); prepare.add_argument("--reason", required=True); prepare.set_defaults(run=command_prepare)
    decide = commands.add_parser("decide")
    decide.add_argument("state"); decide.add_argument("--decision", choices=("approved", "rejected"), required=True); decide.add_argument("--actor", required=True); decide.add_argument("--at", required=True); decide.add_argument("--reason", required=True); decide.set_defaults(run=command_decide)
    local = commands.add_parser("apply-local")
    local.add_argument("state"); local.add_argument("--at", required=True); local.set_defaults(run=command_apply_local)
    begin = commands.add_parser("begin-update")
    begin.add_argument("state"); begin.add_argument("--at", required=True); begin.set_defaults(run=command_begin_update)
    finish = commands.add_parser("finish-update")
    finish.add_argument("state"); finish.add_argument("--attempt", type=int, required=True); finish.add_argument("--outcome", choices=("completed", "failed", "unknown"), required=True); finish.add_argument("--error-code"); finish.add_argument("--message"); finish.add_argument("--at", required=True); finish.set_defaults(run=command_finish_update)
    observe = commands.add_parser("observe-update")
    observe.add_argument("state"); observe.add_argument("--outcome", choices=("matched", "baseline"), required=True); observe.add_argument("--snapshot", required=True); observe.add_argument("--at", required=True); observe.set_defaults(run=command_observe_update)
    validate = commands.add_parser("validate")
    validate.add_argument("state"); validate.add_argument("--previous"); validate.set_defaults(run=command_validate)
    return parser


def main() -> int:
    try:
        arguments = build_parser().parse_args()
        arguments.run(arguments)
        return 0
    except (ContractError, OSError, ValueError, TypeError, KeyError, json.JSONDecodeError, UnicodeDecodeError) as error:
        print(f"invalid: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
