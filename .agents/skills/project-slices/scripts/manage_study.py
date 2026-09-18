#!/usr/bin/env python3
"""Prepare, publish, and resume an exceptional Project Slices Study locally."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

from manage_slices import (
    ContractError,
    semantic_baseline,
    atomic_write,
    canonical_bytes,
    contained_feature_path,
    digest,
    file_digest,
    load_json,
    reject_secrets,
    require_text,
    require_timestamp,
    validate_feature_approval,
    validate_input_linkage,
    validate_proposal,
    validate_state as validate_slices_state,
)
from manage_publication import atomic_batch_write


def fail(message: str) -> None:
    raise ContractError(message)


def exact(value: Any, fields: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != fields:
        fail(f"{label} has missing or unknown fields")
    return value


def positive_int(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        fail(f"{label} must be a positive integer")
    return value


def hours(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
        fail(f"{label} must be positive hours")
    return float(value)


def named_id(issue: dict[str, Any], field: str, *, required: bool = True) -> int | None:
    value = issue.get(field)
    if value is None and not required:
        return None
    if isinstance(value, dict):
        value = value.get("id")
    return positive_int(value, f"issue.{field}")


def issue_object(snapshot: dict[str, Any]) -> dict[str, Any]:
    issue = snapshot.get("issue", snapshot)
    if not isinstance(issue, dict):
        fail("snapshot must contain an issue object")
    reject_secrets(issue, "issue snapshot")
    return issue


def evidence_path(feature_dir: Path, value: Any, label: str) -> Path:
    path = Path(require_text(value, label)).absolute()
    try:
        relative = path.relative_to(feature_dir.absolute())
    except ValueError:
        fail(f"{label} must be inside the Feature directory")
    if not relative.parts or relative.parts[0] != ".work":
        fail(f"{label} must be disposable evidence under .work")
    return contained_feature_path(feature_dir, str(relative).replace("\\", "/"), label)


def study_digest(revision: dict[str, Any]) -> str:
    return digest({
        "input_check_path": revision["input_check_path"],
        "input_check_sha256": revision["input_check_sha256"],
        "parent_baseline": revision["parent_baseline"],
        "metadata_baseline": revision["metadata_baseline"],
        "native_fields": revision["native_fields"],
        "study": revision["study"],
    })


def result_digest(result: dict[str, Any]) -> str:
    return digest({key: value for key, value in result.items() if key != "result_sha256"})


def validate_revision(revision: dict[str, Any], number: int, *, check_files: bool) -> None:
    exact(revision, {
        "number", "recorded_by", "recorded_at", "reason", "input_check_path",
        "input_check_sha256", "parent_baseline", "metadata_baseline", "native_fields",
        "study", "publication_sha256",
    }, f"study revision {number}")
    if revision["number"] != number:
        fail("Study revision numbers must be contiguous")
    require_text(revision["recorded_by"], "study revision.recorded_by")
    require_timestamp(revision["recorded_at"], "study revision.recorded_at")
    require_text(revision["reason"], "study revision.reason")
    input_path = Path(require_text(revision["input_check_path"], "study revision.input_check_path"))
    if check_files and file_digest(input_path) != revision["input_check_sha256"]:
        fail("Study input check changed after preview")
    for field in ("parent_baseline", "metadata_baseline"):
        baseline = revision[field]
        if not isinstance(baseline, dict) or "path" not in baseline or "sha256" not in baseline:
            fail(f"Study {field} is invalid")
        if check_files and file_digest(Path(baseline["path"])) != baseline["sha256"]:
            fail(f"Study {field} evidence changed after preview")
    study = exact(revision["study"], {
        "identity", "subject", "title", "question", "expected_result", "effort_limit",
        "estimate_hours", "description", "description_path", "attributes", "payload_sha256",
    }, "study")
    for field in ("identity", "subject", "title", "question", "expected_result", "effort_limit", "description", "description_path", "payload_sha256"):
        require_text(study[field], f"study.{field}")
    hours(study["estimate_hours"], "study.estimate_hours")
    if study["payload_sha256"] != digest({"attributes": study["attributes"]}):
        fail("Study payload differs from its hash")
    description_path = Path(study["description_path"])
    if check_files and description_path.read_text(encoding="utf-8") != study["description"]:
        fail("Study description changed after preview")
    if revision["publication_sha256"] != study_digest(revision):
        fail("Study preview differs from its hash")


def validate_operation(operation: Any) -> None:
    operation = exact(operation, {"kind", "attempts", "observations", "status", "remote_id"}, "Study create operation")
    if operation["kind"] != "create" or operation["status"] not in {"pending", "completed"}:
        fail("Study create operation is invalid")
    if not isinstance(operation["attempts"], list) or not isinstance(operation["observations"], list):
        fail("Study create history must be arrays")
    for number, attempt in enumerate(operation["attempts"], start=1):
        exact(attempt, {"id", "attempted_at", "payload_sha256", "outcome", "finished_at"}, "Study create attempt")
        if attempt["id"] != number or attempt["outcome"] not in {"in-flight", "completed", "failed", "unknown"}:
            fail("Study create attempt is invalid")
        require_timestamp(attempt["attempted_at"], "Study create attempted_at")
        require_text(attempt["payload_sha256"], "Study create payload_sha256")
        if attempt["outcome"] == "in-flight":
            if attempt["finished_at"] is not None or number != len(operation["attempts"]):
                fail("only the latest Study create attempt may remain in-flight")
        else:
            require_timestamp(attempt["finished_at"], "Study create finished_at")
    for observation in operation["observations"]:
        exact(observation, {"outcome", "observed_at", "snapshot_path", "snapshot_sha256", "remote_id"}, "Study create observation")
        if observation["outcome"] not in {"matched", "absent"}:
            fail("Study create observation is invalid")
        require_timestamp(observation["observed_at"], "Study observation observed_at")
    if operation["status"] == "completed":
        positive_int(operation["remote_id"], "Study remote_id")
    elif operation["remote_id"] is not None:
        fail("pending Study create cannot have a remote ID")


def validate_state(state: dict[str, Any], *, check_files: bool = True, previous: dict[str, Any] | None = None) -> None:
    exact(state, {
        "schema_version", "status", "status_history", "revisions", "approvals",
        "operation", "result_history", "resumptions",
    }, "Study state")
    statuses = {"prepared", "approved", "publishing", "awaiting-result", "result-recorded", "resumed"}
    if state["schema_version"] != 1 or state["status"] not in statuses:
        fail("unsupported Study state")
    if not isinstance(state["revisions"], list) or not state["revisions"]:
        fail("Study state requires revision history")
    for number, revision in enumerate(state["revisions"], start=1):
        validate_revision(revision, number, check_files=check_files and number == len(state["revisions"]))
    current = state["revisions"][-1]
    if not isinstance(state["status_history"], list) or not state["status_history"]:
        fail("Study status history is required")
    for entry in state["status_history"]:
        exact(entry, {"status", "recorded_at"}, "Study status history entry")
        if entry["status"] not in statuses:
            fail("Study status history is invalid")
        require_timestamp(entry["recorded_at"], "Study status history recorded_at")
    valid_approvals = []
    if not isinstance(state["approvals"], list):
        fail("Study approvals must be an array")
    for approval in state["approvals"]:
        exact(approval, {"revision", "publication_sha256", "approved_by", "approved_at", "role", "status"}, "Study approval")
        revision_number = positive_int(approval["revision"], "Study approval revision")
        if revision_number > len(state["revisions"]) or approval["publication_sha256"] != state["revisions"][revision_number - 1]["publication_sha256"]:
            fail("Study approval differs from its revision")
        if approval["role"] != "tech-lead" or approval["status"] not in {"valid", "invalidated"}:
            fail("Study publication requires a specific tech-lead approval")
        require_text(approval["approved_by"], "Study approval approved_by")
        require_timestamp(approval["approved_at"], "Study approval approved_at")
        if approval["status"] == "valid":
            valid_approvals.append(approval)
    if state["status"] == "prepared":
        if valid_approvals:
            fail("prepared Study cannot retain a valid approval")
    elif len(valid_approvals) != 1 or valid_approvals[0]["revision"] != current["number"]:
        fail("Study publication requires a specific tech-lead approval of the current preview")
    if state["operation"] is not None:
        validate_operation(state["operation"])
    if state["status"] in {"awaiting-result", "result-recorded", "resumed"}:
        if state["operation"] is None or state["operation"]["status"] != "completed":
            fail("Study result flow requires a reconciled remote Study ID")
    if not isinstance(state["result_history"], list) or len(state["result_history"]) > 1:
        fail("Study has at most one immutable result")
    for result in state["result_history"]:
        exact(result, {
            "study_revision", "study_publication_sha256", "study_remote_id", "question",
            "expected_result", "effort_limit", "result", "source", "authored_by", "authored_at",
            "recorded_by", "recorded_at", "source_path", "source_sha256", "result_sha256",
        }, "Study result")
        if result["study_revision"] != current["number"] or result["study_publication_sha256"] != current["publication_sha256"]:
            fail("Study result is stale for the current preview")
        if result["study_remote_id"] != state["operation"]["remote_id"]:
            fail("Study result references another remote Study")
        if result["question"] != current["study"]["question"] or result["expected_result"] != current["study"]["expected_result"] or result["effort_limit"] != current["study"]["effort_limit"]:
            fail("Study result is not bound to the approved question and bounds")
        exact(result["source"], {"kind", "reference"}, "Study result source")
        for field in ("result", "authored_by", "recorded_by"):
            require_text(result[field], f"Study result {field}")
        require_text(result["source"]["kind"], "Study result source.kind")
        require_text(result["source"]["reference"], "Study result source.reference")
        require_timestamp(result["authored_at"], "Study result authored_at")
        require_timestamp(result["recorded_at"], "Study result recorded_at")
        if result["result_sha256"] != result_digest(result):
            fail("Study result differs from its bound hash")
        source_path = Path(result["source_path"])
        if check_files and file_digest(source_path) != result["source_sha256"]:
            fail("Study result source changed after recording")
    if state["status"] in {"result-recorded", "resumed"} and len(state["result_history"]) != 1:
        fail("Study result status requires explicit result evidence")
    if not isinstance(state["resumptions"], list) or len(state["resumptions"]) > 1:
        fail("Study can open one bound slicing revision")
    if state["status"] == "resumed" and len(state["resumptions"]) != 1:
        fail("resumed Study requires slicing revision evidence")
    reject_secrets(state, "Study state")
    if previous is not None:
        validate_state(previous, check_files=False)
        if state["revisions"][:len(previous["revisions"])] != previous["revisions"]:
            fail("Study revisions are append-only")
        for field in ("status_history", "result_history", "resumptions"):
            if state[field][:len(previous[field])] != previous[field]:
                fail(f"Study {field} is append-only")
        if previous["operation"] is not None:
            current_operation = state["operation"]
            if current_operation is None:
                fail("Study create operation cannot be removed")
            if current_operation["attempts"][:len(previous["operation"]["attempts"])] != previous["operation"]["attempts"] or current_operation["observations"][:len(previous["operation"]["observations"])] != previous["operation"]["observations"]:
                fail("Study create history is append-only")
        if len(state["approvals"]) < len(previous["approvals"]):
            fail("Study approvals cannot be removed")
        for index, old in enumerate(previous["approvals"]):
            current_approval = state["approvals"][index]
            if current_approval != old and not (old["status"] == "valid" and current_approval == {**old, "status": "invalidated"}):
                fail("Study approval history is append-only except valid-to-invalidated status")


def input_feature(input_path: Path) -> tuple[Path, dict[str, Any], str, int]:
    input_check = load_json(input_path)
    exact(input_check, {
        "status", "feature_path", "state_path", "issue_id", "requirement_sha256",
        "remote_snapshot_sha256", "checked_at",
    }, "input check")
    if input_check["status"] != "ready":
        fail("Study requires a ready input check")
    feature_dir = input_path.parent.parent
    canonical, _, state, approval, content = validate_feature_approval(feature_dir)
    if canonical.absolute() != Path(input_check["feature_path"]).absolute() or state["redmine"]["issue_id"] != input_check["issue_id"] or approval["subject_sha256"] != input_check["requirement_sha256"]:
        fail("Study input check is stale for the approved parent")
    title = content.decode("utf-8").splitlines()[0].removeprefix("# ").strip()
    return feature_dir, input_check, title, state["redmine"]["issue_id"]


def render_description(title: str, question: str, expected_result: str, effort_limit: str) -> str:
    return "\n".join([
        f"# {title}", "", "## Pergunta técnica", "", question, "",
        "## Resultado esperado", "", expected_result, "", "## Limite de esforço", "", effort_limit, "",
    ])


def child_attributes(study: dict[str, Any], native: dict[str, Any], parent: dict[str, Any]) -> dict[str, Any]:
    attributes: dict[str, Any] = {
        "project_id": native["project_id"], "parent_issue_id": parent["id"],
        "tracker_id": native["dev_tracker_id"], "status_id": native["initial_status_id"],
        "subject": study["title"], "description": study["description"],
        "assigned_to_id": None, "start_date": None, "due_date": None,
        "estimated_hours": study["estimate_hours"],
    }
    attributes["priority_id"] = native["default_priority_id"]
    category_id = named_id(parent, "category", required=False)
    version_id = named_id(parent, "fixed_version", required=False)
    if category_id is not None:
        attributes["category_id"] = category_id
    if version_id is not None:
        attributes["fixed_version_id"] = version_id
    return attributes


def command_prepare(arguments: argparse.Namespace) -> None:
    state_path = Path(arguments.state)
    input_path = Path(arguments.input_check)
    feature_dir, input_check, feature_title, issue_id = input_feature(input_path)
    if state_path.absolute() != (feature_dir / ".flow" / "slices-study.json").absolute():
        fail("Study state must use .flow/slices-study.json")
    preview_path = Path(arguments.preview)
    if preview_path.absolute() != (feature_dir / "slices" / "study.md").absolute():
        fail("Study preview must use slices/study.md")
    plan = load_json(Path(arguments.plan))
    exact(plan, {"source", "parent_snapshot", "metadata_snapshot", "native_fields", "study"}, "Study plan")
    source = exact(plan["source"], {"input_check_path", "input_check_sha256"}, "Study source")
    if Path(source["input_check_path"]).absolute() != input_path.absolute() or source["input_check_sha256"] != file_digest(input_path):
        fail("Study plan source differs from the checked parent")
    parent_path = evidence_path(feature_dir, plan["parent_snapshot"], "parent snapshot")
    parent = issue_object(load_json(parent_path))
    if positive_int(parent.get("id"), "parent.id") != issue_id or require_text(parent.get("subject"), "parent.subject") != feature_title:
        fail("Study parent snapshot differs from the approved parent")
    native = exact(plan["native_fields"], {
        "project_id", "dev_tracker_id", "initial_status_id", "default_priority_id",
        "priority_override_id", "priority_override_reason",
    }, "native fields")
    if named_id(parent, "project") != positive_int(native["project_id"], "native_fields.project_id"):
        fail("Study must use the parent project")
    for field in ("dev_tracker_id", "initial_status_id", "default_priority_id"):
        positive_int(native[field], f"native_fields.{field}")
    if native["priority_override_id"] is not None or native["priority_override_reason"] is not None:
        fail("Study priority is fixed as Normal and cannot be overridden")
    metadata_path = evidence_path(feature_dir, plan["metadata_snapshot"], "metadata snapshot")
    metadata = load_json(metadata_path)
    exact(metadata, {"trackers", "statuses", "priorities"}, "metadata snapshot")
    parent_tracker = parent.get("tracker")
    parent_tracker_name = require_text(parent_tracker.get("name") if isinstance(parent_tracker, dict) else None, "parent.tracker.name")
    expected_dev_tracker = "Task" if parent_tracker_name == "Feature" else "Bug" if parent_tracker_name == "Bug" else None
    if expected_dev_tracker is None:
        fail("Study parent tracker must be Feature or Bug")
    trackers = metadata["trackers"]
    tracker_matches = [item for item in trackers if isinstance(item, dict) and item.get("name") == expected_dev_tracker] if isinstance(trackers, list) else []
    if len(tracker_matches) != 1:
        fail(f"Study tracker {expected_dev_tracker} must exist exactly once in confirmed MCP metadata")
    if positive_int(tracker_matches[0].get("id"), f"tracker {expected_dev_tracker}.id") != native["dev_tracker_id"]:
        fail(f"Study DEV tracker must be {expected_dev_tracker} for a {parent_tracker_name} parent")
    selections = (("statuses", "New", "initial_status_id"), ("priorities", "Normal", "default_priority_id"))
    for collection, expected_name, field in selections:
        matches = [item for item in metadata[collection] if isinstance(item, dict) and item.get("name") == expected_name] if isinstance(metadata[collection], list) else []
        if len(matches) != 1:
            fail(f"Study {collection} value {expected_name} must exist exactly once in confirmed MCP metadata")
        if positive_int(matches[0].get("id"), f"{collection} {expected_name}.id") != native[field]:
            fail("Study status and priority contract requires status=New and priority=Normal")
    study_plan = exact(plan["study"], {"subject", "question", "expected_result", "effort_limit", "estimate_hours"}, "Study")
    subject = require_text(study_plan["subject"], "study.subject").strip()
    question = require_text(study_plan["question"], "study.question")
    expected_result = require_text(study_plan["expected_result"], "study.expected_result")
    effort_limit = require_text(study_plan["effort_limit"], "study.effort_limit")
    estimate = hours(study_plan["estimate_hours"], "study.estimate_hours")
    title = f"[DEV] {feature_title} - Estudo: {subject}"
    identity = digest({"feature_issue_id": issue_id, "requirement_sha256": input_check["requirement_sha256"], "subject": subject})
    description = render_description(title, question, expected_result, effort_limit)
    description += f"\n<!-- project-slices-study:{identity} -->\n"
    description_path = feature_dir / "slices" / "descriptions" / "study.md"
    study = {
        "identity": identity, "subject": subject, "title": title, "question": question,
        "expected_result": expected_result, "effort_limit": effort_limit, "estimate_hours": estimate,
        "description": description, "description_path": str(description_path.absolute()),
    }
    study["attributes"] = child_attributes(study, native, parent)
    study["payload_sha256"] = digest({"attributes": study["attributes"]})
    recorded_at = require_timestamp(arguments.at, "recorded_at")
    revision = {
        "number": 1, "recorded_by": require_text(arguments.actor, "recorded_by"),
        "recorded_at": recorded_at, "reason": require_text(arguments.reason, "reason"),
        "input_check_path": str(input_path.absolute()), "input_check_sha256": file_digest(input_path),
        "parent_baseline": {"path": str(parent_path.absolute()), "sha256": file_digest(parent_path), "issue_id": issue_id, "project_id": native["project_id"]},
        "metadata_baseline": {"path": str(metadata_path.absolute()), "sha256": file_digest(metadata_path)},
        "native_fields": copy.deepcopy(native), "study": study,
    }
    revision["publication_sha256"] = study_digest(revision)
    if state_path.exists():
        state = load_json(state_path)
        validate_state(state)
        if state["operation"] is not None:
            fail("a Study with remote publication progress cannot be revised")
        for approval in state["approvals"]:
            if approval["status"] == "valid":
                approval["status"] = "invalidated"
        revision["number"] = len(state["revisions"]) + 1
        state["revisions"].append(revision)
        state["status"] = "prepared"
        state["status_history"].append({"status": "prepared", "recorded_at": recorded_at})
    else:
        state = {
            "schema_version": 1, "status": "prepared",
            "status_history": [{"status": "prepared", "recorded_at": recorded_at}],
            "revisions": [revision], "approvals": [], "operation": None,
            "result_history": [], "resumptions": [],
        }
    validate_state(state, check_files=False)
    preview = "\n".join([
        f"# Previa excepcional de Study para {feature_title}", "",
        "A publicacao deste Study nao conclui o fatiamento nem o item pai.", "",
        f"Hash da previa: `{revision['publication_sha256']}`", "", description,
    ])
    atomic_batch_write({
        description_path: description.encode("utf-8"),
        preview_path: preview.encode("utf-8"),
        state_path: canonical_bytes(state) + b"\n",
    })
    print(json.dumps({"status": "prepared", "revision": revision["number"], "publication_sha256": revision["publication_sha256"]}))


def command_approve(arguments: argparse.Namespace) -> None:
    path = Path(arguments.state)
    state = load_json(path)
    validate_state(state)
    if state["status"] != "prepared":
        fail("only a prepared Study preview can receive tech-lead approval")
    current = state["revisions"][-1]
    at = require_timestamp(arguments.at, "approved_at")
    state["approvals"].append({
        "revision": current["number"], "publication_sha256": current["publication_sha256"],
        "approved_by": require_text(arguments.actor, "approved_by"), "approved_at": at,
        "role": "tech-lead", "status": "valid",
    })
    state["status"] = "approved"
    state["status_history"].append({"status": "approved", "recorded_at": at})
    validate_state(state)
    atomic_write(path, canonical_bytes(state) + b"\n")
    print(json.dumps({"status": "approved", "publication_sha256": current["publication_sha256"]}))


def command_begin_create(arguments: argparse.Namespace) -> None:
    path = Path(arguments.state)
    state = load_json(path)
    validate_state(state)
    operation = state["operation"]
    if operation is not None and operation["status"] == "completed":
        fail("published Study must reuse its recorded remote ID")
    if state["status"] not in {"approved", "publishing"}:
        fail("Study publication requires specific tech-lead approval")
    if operation is None:
        operation = {"kind": "create", "attempts": [], "observations": [], "status": "pending", "remote_id": None}
        state["operation"] = operation
    if operation["attempts"] and operation["attempts"][-1]["outcome"] in {"in-flight", "unknown"}:
        fail("uncertain Study create requires reconciliation before retry")
    current = state["revisions"][-1]
    at = require_timestamp(arguments.at, "attempted_at")
    attempt_id = len(operation["attempts"]) + 1
    operation["attempts"].append({"id": attempt_id, "attempted_at": at, "payload_sha256": current["study"]["payload_sha256"], "outcome": "in-flight", "finished_at": None})
    state["status"] = "publishing"
    state["status_history"].append({"status": "publishing", "recorded_at": at})
    validate_state(state)
    atomic_write(path, canonical_bytes(state) + b"\n")
    print(json.dumps({"attempt_id": attempt_id, "attributes": current["study"]["attributes"]}, ensure_ascii=False))


def command_finish_create(arguments: argparse.Namespace) -> None:
    path = Path(arguments.state)
    state = load_json(path)
    validate_state(state)
    operation = state["operation"]
    if operation is None or not operation["attempts"]:
        fail("Study create has no in-flight attempt")
    attempt_id = positive_int(arguments.attempt, "attempt")
    attempt = operation["attempts"][-1]
    if attempt["id"] != attempt_id or attempt["outcome"] != "in-flight":
        fail("Study create attempt is not the current in-flight attempt")
    outcome = arguments.outcome
    if outcome not in {"completed", "failed", "unknown"}:
        fail("Study create outcome is invalid")
    attempt["outcome"] = outcome
    attempt["finished_at"] = require_timestamp(arguments.at, "finished_at")
    if outcome == "completed":
        operation["remote_id"] = positive_int(arguments.issue_id, "issue_id")
        operation["status"] = "completed"
        state["status"] = "awaiting-result"
        state["status_history"].append({"status": "awaiting-result", "recorded_at": attempt["finished_at"]})
    elif arguments.issue_id is not None:
        fail("only a completed Study create can record issue_id")
    validate_state(state)
    atomic_write(path, canonical_bytes(state) + b"\n")
    print(json.dumps({"status": state["status"], "remote_id": operation["remote_id"]}))


def compare_issue(study: dict[str, Any], issue: dict[str, Any], default_priority_id: int) -> None:
    attributes = study["attributes"]
    expected = {
        "project_id": named_id(issue, "project"), "parent_issue_id": named_id(issue, "parent"),
        "tracker_id": named_id(issue, "tracker"), "status_id": named_id(issue, "status"),
        "subject": issue.get("subject"), "description": issue.get("description"),
        "estimated_hours": float(issue.get("estimated_hours")),
        "priority_id": named_id(issue, "priority"),
    }
    for key in ("project_id", "parent_issue_id", "tracker_id", "status_id", "subject", "description", "estimated_hours"):
        if expected[key] != attributes[key]:
            fail("reconciled Study differs from the approved preview")
    if expected["priority_id"] != attributes.get("priority_id", default_priority_id):
        fail("reconciled Study priority differs from the approved preview")


def command_observe_create(arguments: argparse.Namespace) -> None:
    path = Path(arguments.state)
    state = load_json(path)
    validate_state(state)
    operation = state["operation"]
    if operation is None or not operation["attempts"] or operation["attempts"][-1]["outcome"] not in {"in-flight", "unknown"} or operation["status"] == "completed":
        fail("Study create does not require reconciliation")
    feature_dir = path.parent.parent
    snapshot_path = evidence_path(feature_dir, arguments.snapshot, "Study reconciliation snapshot")
    snapshot = load_json(snapshot_path)
    exact(snapshot, {"project_id", "parent_issue_id", "identity", "status_scope", "pages", "total_count", "issues"}, "Study reconciliation search")
    current = state["revisions"][-1]
    study = current["study"]
    attributes = study["attributes"]
    if snapshot["project_id"] != attributes["project_id"] or snapshot["parent_issue_id"] != attributes["parent_issue_id"] or snapshot["identity"] != study["identity"] or snapshot["status_scope"] != "all":
        fail("Study reconciliation search is not bound to the approved identity")
    issues = snapshot["issues"]
    pages = snapshot["pages"]
    if not isinstance(issues, list) or not isinstance(pages, list) or not pages or snapshot["total_count"] != len(issues) or sum(page.get("count", -1) for page in pages if isinstance(page, dict)) != len(issues):
        fail("Study reconciliation requires complete paginated evidence")
    marker = f"<!-- project-slices-study:{study['identity']} -->"
    matches = [issue for issue in issues if isinstance(issue, dict) and marker in str(issue.get("description", ""))]
    outcome = arguments.outcome
    if outcome == "matched":
        if len(matches) != 1:
            fail("Study reconciliation requires exactly one identity match")
        compare_issue(study, matches[0], current["native_fields"]["default_priority_id"])
        remote_id = positive_int(matches[0].get("id"), "reconciled Study id")
        operation["status"] = "completed"
        operation["remote_id"] = remote_id
        state["status"] = "awaiting-result"
        state["status_history"].append({"status": "awaiting-result", "recorded_at": require_timestamp(arguments.at, "observed_at")})
    elif outcome == "absent":
        if matches:
            fail("Study reconciliation snapshot contains the approved identity")
        remote_id = None
    else:
        fail("Study observation outcome is invalid")
    operation["observations"].append({"outcome": outcome, "observed_at": require_timestamp(arguments.at, "observed_at"), "snapshot_path": str(snapshot_path), "snapshot_sha256": file_digest(snapshot_path), "remote_id": remote_id})
    validate_state(state)
    atomic_write(path, canonical_bytes(state) + b"\n")
    print(json.dumps({"status": state["status"], "remote_id": remote_id}))


def command_record_result(arguments: argparse.Namespace) -> None:
    path = Path(arguments.state)
    state = load_json(path)
    validate_state(state)
    if state["status"] != "awaiting-result":
        fail("Study result can be recorded only after reconciled publication")
    source_path = evidence_path(path.parent.parent, arguments.result, "Study result source")
    source = load_json(source_path)
    exact(source, {"study_remote_id", "result", "source", "authored_by", "authored_at"}, "Study result source")
    remote_id = state["operation"]["remote_id"]
    if positive_int(source["study_remote_id"], "Study result study_remote_id") != remote_id:
        fail("Study result references another remote Study")
    source_reference = exact(source["source"], {"kind", "reference"}, "Study result source attribution")
    require_text(source_reference["kind"], "Study result source.kind")
    require_text(source_reference["reference"], "Study result source.reference")
    current = state["revisions"][-1]
    result = {
        "study_revision": current["number"], "study_publication_sha256": current["publication_sha256"],
        "study_remote_id": remote_id, "question": current["study"]["question"],
        "expected_result": current["study"]["expected_result"], "effort_limit": current["study"]["effort_limit"],
        "result": require_text(source["result"], "Study result"), "source": copy.deepcopy(source_reference),
        "authored_by": require_text(source["authored_by"], "Study result authored_by"),
        "authored_at": require_timestamp(source["authored_at"], "Study result authored_at"),
        "recorded_by": require_text(arguments.actor, "Study result recorded_by"),
        "recorded_at": require_timestamp(arguments.at, "Study result recorded_at"),
        "source_path": str(source_path), "source_sha256": file_digest(source_path),
    }
    result["result_sha256"] = result_digest(result)
    state["result_history"].append(result)
    state["status"] = "result-recorded"
    state["status_history"].append({"status": "result-recorded", "recorded_at": result["recorded_at"]})
    validate_state(state)
    atomic_write(path, canonical_bytes(state) + b"\n")
    print(json.dumps({"status": "result-recorded", "study_remote_id": remote_id, "result_sha256": result["result_sha256"]}))


def proposal_evidence(state_path: Path, state: dict[str, Any]) -> dict[str, Any]:
    result = state["result_history"][0]
    return {
        "study_state_path": str(state_path.absolute()), "study_revision": result["study_revision"],
        "study_publication_sha256": result["study_publication_sha256"], "study_remote_id": result["study_remote_id"],
        "question": result["question"], "expected_result": result["expected_result"], "effort_limit": result["effort_limit"],
        "result": result["result"], "source": copy.deepcopy(result["source"]),
        "authored_by": result["authored_by"], "authored_at": result["authored_at"],
        "recorded_by": result["recorded_by"], "recorded_at": result["recorded_at"],
        "result_sha256": result["result_sha256"],
    }


def command_resume(arguments: argparse.Namespace) -> None:
    study_path = Path(arguments.state)
    state = load_json(study_path)
    validate_state(state)
    if state["status"] == "resumed":
        slices_state = load_json(Path(arguments.slices_state))
        validate_slices_state(slices_state)
        resumption = state["resumptions"][0]
        if slices_state["current_revision"] != resumption["slicing_revision"] or slices_state["revisions"][-1]["proposal_sha256"] != resumption["proposal_sha256"]:
            fail("resumed slicing proposal changed after Study evidence was incorporated")
        print(json.dumps({"status": "resumed", **state["resumptions"][0]}))
        return
    if state["status"] != "result-recorded":
        fail("slicing remains in progress: the published Study has no explicit result")
    proposal_path = Path(arguments.proposal)
    proposal = load_json(proposal_path)
    evidence = proposal_evidence(study_path, state)
    existing = proposal.get("study_evidence", [])
    if not isinstance(existing, list) or any(item.get("study_remote_id") == evidence["study_remote_id"] for item in existing if isinstance(item, dict)):
        fail("candidate proposal contains stale or duplicate Study evidence")
    proposal["study_evidence"] = [*existing, evidence]
    validate_proposal(proposal)
    slices_path = Path(arguments.slices_state)
    input_path = Path(arguments.input_check)
    feature_dir = study_path.parent.parent
    if proposal_path.absolute() != (feature_dir / ".work" / "slices-proposal.json").absolute() or slices_path.absolute() != (feature_dir / ".flow" / "slices-state.json").absolute() or input_path.absolute() != (feature_dir / ".flow" / "slices-input-check.json").absolute():
        fail("Study resume must use the canonical proposal, slicing state, and input check paths")
    validate_input_linkage(feature_dir, proposal, input_path)
    if slices_path.exists():
        slices_state = load_json(slices_path)
        validate_slices_state(slices_state)
        slices_state = copy.deepcopy(slices_state)
        for approval in slices_state["approvals"]:
            if approval["status"] == "valid":
                approval["status"] = "invalidated"
    else:
        slices_state = {"schema_version": 1, "status": "proposed", "current_revision": 0, "revisions": [], "approvals": []}
    at = require_timestamp(arguments.at, "resumed_at")
    revision_number = len(slices_state["revisions"]) + 1
    proposal_sha = digest(proposal)
    slices_state["revisions"].append({
        "number": revision_number, "recorded_by": require_text(arguments.actor, "resumed_by"),
        "recorded_at": at, "reason": require_text(arguments.reason, "reason"),
        "proposal_sha256": proposal_sha, "proposal": proposal,
        "semantic_baseline": semantic_baseline(proposal),
    })
    slices_state["current_revision"] = revision_number
    slices_state["status"] = "proposed"
    validate_slices_state(slices_state)
    resumption = {"slicing_revision": revision_number, "proposal_sha256": proposal_sha, "resumed_by": arguments.actor, "resumed_at": at}
    state["resumptions"].append(resumption)
    state["status"] = "resumed"
    state["status_history"].append({"status": "resumed", "recorded_at": at})
    validate_state(state)
    atomic_batch_write({
        proposal_path: json.dumps(proposal, ensure_ascii=False, indent=2).encode("utf-8") + b"\n",
        slices_path: json.dumps(slices_state, ensure_ascii=False, indent=2).encode("utf-8") + b"\n",
        study_path: canonical_bytes(state) + b"\n",
    })
    print(json.dumps({"status": "proposed", "study_remote_id": evidence["study_remote_id"], **resumption}))


def command_validate(arguments: argparse.Namespace) -> None:
    state = load_json(Path(arguments.state))
    previous = load_json(Path(arguments.previous)) if arguments.previous else None
    validate_state(state, previous=previous)
    print(json.dumps({"status": "valid", "workflow_status": state["status"], "study_remote_id": state["operation"]["remote_id"] if state["operation"] else None}))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    prepare = commands.add_parser("prepare")
    prepare.add_argument("state"); prepare.add_argument("plan"); prepare.add_argument("--input-check", required=True); prepare.add_argument("--preview", required=True); prepare.add_argument("--actor", required=True); prepare.add_argument("--at", required=True); prepare.add_argument("--reason", required=True); prepare.set_defaults(run=command_prepare)
    approve = commands.add_parser("approve")
    approve.add_argument("state"); approve.add_argument("--actor", required=True); approve.add_argument("--at", required=True); approve.set_defaults(run=command_approve)
    begin = commands.add_parser("begin-create")
    begin.add_argument("state"); begin.add_argument("--at", required=True); begin.set_defaults(run=command_begin_create)
    finish = commands.add_parser("finish-create")
    finish.add_argument("state"); finish.add_argument("--attempt", type=int, required=True); finish.add_argument("--outcome", required=True); finish.add_argument("--issue-id", type=int); finish.add_argument("--at", required=True); finish.set_defaults(run=command_finish_create)
    observe = commands.add_parser("observe-create")
    observe.add_argument("state"); observe.add_argument("--outcome", required=True); observe.add_argument("--snapshot", required=True); observe.add_argument("--at", required=True); observe.set_defaults(run=command_observe_create)
    result = commands.add_parser("record-result")
    result.add_argument("state"); result.add_argument("--result", required=True); result.add_argument("--actor", required=True); result.add_argument("--at", required=True); result.set_defaults(run=command_record_result)
    resume = commands.add_parser("resume")
    resume.add_argument("state"); resume.add_argument("proposal"); resume.add_argument("--slices-state", required=True); resume.add_argument("--input-check", required=True); resume.add_argument("--actor", required=True); resume.add_argument("--at", required=True); resume.add_argument("--reason", required=True); resume.set_defaults(run=command_resume)
    validate = commands.add_parser("validate")
    validate.add_argument("state"); validate.add_argument("--previous"); validate.set_defaults(run=command_validate)
    return parser


def main() -> int:
    try:
        arguments = build_parser().parse_args()
        arguments.run(arguments)
        return 0
    except (ContractError, OSError, ValueError, KeyError, UnicodeDecodeError) as error:
        print(f"error: {error}", file=__import__("sys").stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
