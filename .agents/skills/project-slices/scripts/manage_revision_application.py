#!/usr/bin/env python3
"""Prepare and reconcile an approved localized revision application."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

from manage_slices import (
    ContractError,
    atomic_write,
    digest,
    file_digest,
    load_json,
    reject_secrets,
    require_text,
    require_timestamp,
)
import manage_change_review as change_review
import manage_publication as publication


TASK_ACTIONS = {"create", "update", "cancel"}
RELATION_ACTIONS = {"relation-add", "relation-remove"}
ALL_ACTIONS = TASK_ACTIONS | RELATION_ACTIONS


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


def evidence_path(feature_dir: Path, value: Any, label: str) -> Path:
    path = Path(require_text(value, label)).absolute()
    try:
        relative = path.relative_to((feature_dir / ".work").absolute())
    except ValueError:
        fail(f"{label} must be disposable evidence under the Feature .work directory")
    if ".." in relative.parts or not path.is_file() or path.is_symlink():
        fail(f"{label} must be a regular contained evidence file")
    return path


def issue_projection(issue: Any, label: str) -> dict[str, Any]:
    if not isinstance(issue, dict):
        fail(f"{label} must be an issue object")
    issue = copy.deepcopy(issue)
    for field, native in (("project_id", "project"), ("parent_issue_id", "parent"), ("tracker_id", "tracker"), ("status_id", "status")):
        if isinstance(issue.get(native), dict):
            native_id = issue[native].get("id")
            if field in issue and issue[field] != native_id:
                fail(f"{label} has conflicting {field}")
            issue[field] = native_id
    if "subject" not in issue and "title" in issue:
        issue["subject"] = issue["title"]
    for field in ("id", "project_id", "parent_issue_id"):
        if field == "parent_issue_id" and issue.get(field) is None:
            continue
        positive_int(issue.get(field), f"{label}.{field}")
    status = exact(issue.get("status"), {"id", "name"}, f"{label}.status")
    positive_int(status["id"], f"{label}.status.id")
    require_text(status["name"], f"{label}.status.name")
    for field in ("title", "description"):
        if field in issue and not isinstance(issue[field], str):
            fail(f"{label}.{field} must be text")
    return copy.deepcopy(issue)


def load_snapshot(feature_dir: Path, value: Any, label: str) -> tuple[Path, dict[str, Any]]:
    path = evidence_path(feature_dir, value, label)
    snapshot = load_json(path)
    exact(snapshot, {"parent", "tasks", "relations", "complete"}, label)
    if snapshot["complete"] is not True or not isinstance(snapshot["tasks"], list) or not isinstance(snapshot["relations"], list):
        fail(f"{label} must contain complete task and relation readback")
    snapshot["parent"] = issue_projection(snapshot["parent"], f"{label}.parent")
    ids: set[int] = set()
    for index, issue in enumerate(snapshot["tasks"]):
        snapshot["tasks"][index] = issue_projection(issue, f"{label}.tasks[{index}]")
        issue_id = issue["id"]
        if issue_id in ids:
            fail(f"{label} contains duplicate task ids")
        ids.add(issue_id)
    for index, relation in enumerate(snapshot["relations"]):
        exact(relation, {"id", "issue_id", "issue_to_id", "relation_type"}, f"{label}.relations[{index}]")
        for field in ("id", "issue_id", "issue_to_id"):
            positive_int(relation[field], f"{label}.relations[{index}].{field}")
        require_text(relation["relation_type"], f"{label}.relations[{index}].relation_type")
    reject_secrets(snapshot, label)
    return path, snapshot


def approved_review(path: Path, *, check_current: bool = True) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    state = load_json(path)
    change_review.validate_state(state, check_current=check_current)
    current = state["revisions"][-1]
    decisions = [item for item in state["decisions"] if item["revision"] == current["number"]]
    authorizations = [item for item in state["authorizations"] if item["revision"] == current["number"]]
    if state["status"] != "authorized" or len(decisions) != 1 or decisions[0]["decision"] != "approved" or len(authorizations) != 1:
        fail("revision application requires the current specifically approved and authorized change-review revision")
    authorization = authorizations[0]
    if authorization["review_sha256"] != current["review_sha256"]:
        fail("change-review authorization is stale or superseded")
    return state, current, authorization


def status_contract(value: Any) -> dict[str, dict[str, Any]]:
    statuses = exact(value, {"not_started", "in_progress", "completed", "cancelled"}, "status contract")
    seen: set[tuple[int, str]] = set()
    for state, status in statuses.items():
        exact(status, {"id", "name"}, f"status contract.{state}")
        pair = (positive_int(status["id"], f"status contract.{state}.id"), require_text(status["name"], f"status contract.{state}.name"))
        if pair in seen:
            fail("native status mappings must be distinct")
        seen.add(pair)
    return statuses


def status_kind(issue: dict[str, Any], statuses: dict[str, dict[str, Any]]) -> str:
    matches = [key for key, value in statuses.items() if issue["status"] == value]
    if len(matches) != 1:
        fail(f"task {issue['id']} current status has no exact native mapping")
    return matches[0]


def operation_digest(operation: dict[str, Any]) -> str:
    return digest({key: value for key, value in operation.items() if key != "operation_sha256"})


def validate_operation(raw: Any, tasks: dict[int, dict[str, Any]], relations: dict[int, dict[str, Any]], statuses: dict[str, dict[str, Any]], affected_tasks: set[str], affected_dependencies: set[str], parent_id: int, parent_project_id: int, review_sha256: str, published_tasks: dict[str, int] | None = None) -> dict[str, Any]:
    fields = {"key", "action", "impact_ids", "task_key", "issue_id", "relation_id", "attributes", "reason", "replacement_keys", "source_task_keys", "revision_sha256"}
    operation = exact(raw, fields, "revision operation")
    key = require_text(operation["key"], "operation.key")
    action = operation["action"]
    if action not in ALL_ACTIONS:
        fail(f"operation {key} has an unsupported action")
    if operation["revision_sha256"] != review_sha256:
        fail(f"operation {key} is not linked to the approved revision")
    impacts = operation["impact_ids"]
    if not isinstance(impacts, list) or not impacts or len(impacts) != len(set(impacts)):
        fail(f"operation {key} requires unique localized impact ids")
    allowed = affected_tasks if action in TASK_ACTIONS else affected_dependencies
    if set(impacts) - allowed:
        fail(f"operation {key} broadens the approved localized impact")
    attributes = operation["attributes"]
    if not isinstance(attributes, dict):
        fail(f"operation {key} attributes must be an object")
    reject_secrets(attributes, f"operation {key}")
    task_key = operation["task_key"]
    if task_key is not None:
        require_text(task_key, f"operation {key}.task_key")
    replacements = operation["replacement_keys"]
    sources = operation["source_task_keys"]
    if not isinstance(replacements, list) or len(replacements) != len(set(replacements)) or not isinstance(sources, list) or len(sources) != len(set(sources)):
        fail(f"operation {key} replacement/source keys must be unique arrays")
    for item in replacements + sources:
        require_text(item, f"operation {key} task reference")
    reason = operation["reason"]
    if action == "create":
        if operation["issue_id"] is not None or operation["relation_id"] is not None or task_key is None:
            fail(f"create operation {key} cannot reference an existing remote object")
        if not sources or set(sources) - affected_tasks:
            fail(f"create operation {key} must derive from affected approved tasks")
        required_attributes = {"project_id", "parent_issue_id", "tracker_id", "status_id", "subject", "description", "estimated_hours"}
        subject = require_text(attributes.get("subject"), f"operation {key}.attributes.subject")
        if not required_attributes <= set(attributes) or attributes.get("project_id") != parent_project_id or attributes.get("parent_issue_id") != parent_id or not subject.startswith(("[DEV] ", "[QA] ")) or not require_text(attributes.get("description"), f"operation {key}.attributes.description"):
            fail(f"create operation {key} violates title, description, or parent contracts")
        positive_int(attributes.get("tracker_id"), f"operation {key}.attributes.tracker_id")
        positive_int(attributes.get("status_id"), f"operation {key}.attributes.status_id")
        if isinstance(attributes.get("estimated_hours"), bool) or not isinstance(attributes.get("estimated_hours"), (int, float)) or attributes["estimated_hours"] <= 0:
            fail(f"create operation {key} requires a positive estimate")
        if review_sha256 not in attributes["description"]:
            fail(f"create operation {key} description must link the approved revision hash")
        require_text(reason, f"operation {key}.reason")
    elif action in {"update", "cancel"}:
        issue_id = positive_int(operation["issue_id"], f"operation {key}.issue_id")
        if issue_id not in tasks or task_key not in affected_tasks or operation["relation_id"] is not None:
            fail(f"operation {key} does not select an affected current task")
        if published_tasks is not None and published_tasks.get(task_key) != issue_id:
            fail(f"operation {key} remote id differs from the approved task")
        if tasks[issue_id]["project_id"] != parent_project_id or tasks[issue_id].get("parent_issue_id") != parent_id:
            fail(f"operation {key} belongs to another project or Feature")
        if task_key not in impacts:
            fail(f"operation {key} must include its target in the approved impact")
        if action == "update" and set(attributes) - {"subject", "description", "estimated_hours"}:
            fail("updates may only change approved task content and estimate")
        kind = status_kind(tasks[issue_id], statuses)
        if kind == "completed":
            fail(f"completed task {task_key} is immutable; represent added or corrected work as a new child task")
        if kind == "cancelled":
            fail(f"cancelled task {task_key} cannot be mutated")
        if action == "cancel":
            if kind != "not_started" or not replacements or not require_text(reason, f"operation {key}.reason"):
                fail(f"cancellation {key} requires a not-started task, reason, and replacement keys")
            if attributes != {"status_id": statuses["cancelled"]["id"]}:
                fail(f"cancellation {key} must use the exact native cancelled status id")
        elif not attributes or "status_id" in attributes or reason is not None or replacements or sources:
            fail(f"update operation {key} fields are invalid")
    else:
        if task_key is not None or operation["issue_id"] is not None or replacements or sources or not require_text(reason, f"operation {key}.reason"):
            fail(f"relation operation {key} fields are invalid")
        if set(attributes) != {"issue_id", "issue_to_id", "relation_type"} or attributes["relation_type"] != "blocks":
            fail(f"relation operation {key} must describe one native blocks edge")
        for endpoint in ("issue_id", "issue_to_id"):
            if action == "relation-add" and isinstance(attributes[endpoint], str):
                require_text(attributes[endpoint], f"operation {key}.{endpoint}")
            else:
                positive_int(attributes[endpoint], f"operation {key}.{endpoint}")
        if action == "relation-add" and operation["relation_id"] is not None:
            fail(f"relation add {key} cannot have an existing relation id")
        if action == "relation-remove":
            relation_id = positive_int(operation["relation_id"], f"operation {key}.relation_id")
            if relation_id not in relations or relations[relation_id] != {"id": relation_id, **attributes}:
                fail(f"relation remove {key} is not proven by the preview snapshot")
    return copy.deepcopy(operation)


def proposal_digest(revision: dict[str, Any]) -> str:
    return digest({key: revision[key] for key in ("change_review", "publication", "preview_snapshot", "status_metadata", "status_contract", "operations", "preservation")})


def validate_state(state: dict[str, Any], previous: dict[str, Any] | None = None, *, check_files: bool = True, check_authority: bool = True) -> None:
    state.setdefault("plan_approvals", [])
    exact(state, {"schema_version", "status", "status_history", "revisions", "approvals", "plan_approvals", "operations", "readback", "completed_at"}, "revision application state")
    reject_secrets(state, "revision application state")
    if state["schema_version"] != 1 or state["status"] not in {"prepared", "applying", "completed"}:
        fail("unsupported revision application state")
    if not isinstance(state["revisions"], list) or not state["revisions"]:
        fail("revision application requires revision history")
    revision_fields = {"number", "recorded_by", "recorded_at", "reason", "change_review", "publication", "preview_snapshot", "status_metadata", "status_contract", "operations", "preservation", "proposal_sha256"}
    for number, revision in enumerate(state["revisions"], start=1):
        exact(revision, revision_fields, f"application revision {number}")
        if revision["number"] != number or revision["proposal_sha256"] != proposal_digest(revision):
            fail("application revision identity or hash differs")
        require_text(revision["recorded_by"], "revision.recorded_by")
        require_timestamp(revision["recorded_at"], "revision.recorded_at")
        require_text(revision["reason"], "revision.reason")
        status_contract(revision["status_contract"])
        if not isinstance(revision["operations"], list) or not revision["operations"]:
            fail("application revision requires operations")
        keys = [item.get("key") for item in revision["operations"]]
        if len(keys) != len(set(keys)):
            fail("application operation keys must be unique")
        if check_files:
            for evidence in (revision["change_review"], revision["publication"], revision["preview_snapshot"], revision["status_metadata"]):
                if file_digest(Path(evidence["path"])) != evidence["sha256"]:
                    fail("application source evidence is stale or tampered")
            _review_state, current_review, current_authorization = approved_review(Path(revision["change_review"]["path"]), check_current=False)
            if current_review["number"] != revision["change_review"]["revision"] or current_review["review_sha256"] != revision["change_review"]["review_sha256"] or digest(current_authorization) != revision["change_review"]["authorization_sha256"]:
                fail("application change-review authority is stale or superseded")
            if check_authority and number == len(state["revisions"]) and state["status"] != "completed" and "source_path" in revision["change_review"]:
                _live_state, live_review, _live_authorization = approved_review(Path(revision["change_review"]["source_path"]))
                if live_review["review_sha256"] != current_review["review_sha256"]:
                    fail("application change-review authority is stale or superseded")
            publication_state = load_json(Path(revision["publication"]["path"]))
            publication.validate_publication_state(publication_state)
            if publication_state["status"] != "completed" or publication_state["revisions"][-1]["number"] != revision["publication"]["revision"]:
                fail("application publication source is no longer the completed baseline")
    if not isinstance(state["approvals"], list) or not isinstance(state["operations"], dict):
        fail("application approvals and operations are invalid")
    for approval in state["approvals"]:
        exact(approval, {"revision", "operation_key", "task_key", "task_snapshot_sha256", "operation_sha256", "approved_by", "approved_at", "reason"}, "task mutation approval")
        require_text(approval["approved_by"], "approval.approved_by")
        require_timestamp(approval["approved_at"], "approval.approved_at")
        require_text(approval["reason"], "approval.reason")
    for key, operation in state["operations"].items():
        exact(operation, {"kind", "attempts", "observations", "status", "remote_id"}, f"operation state {key}")
        if operation["kind"] not in ALL_ACTIONS or operation["status"] not in {"pending", "completed"} or not isinstance(operation["attempts"], list) or not isinstance(operation["observations"], list):
            fail(f"operation state {key} is invalid")
        if operation["status"] == "completed":
            positive_int(operation["remote_id"], f"operation {key}.remote_id")
        for number, attempt in enumerate(operation["attempts"], start=1):
            if attempt["id"] != number or attempt["outcome"] not in {"in-flight", "unknown", "failed", "completed"}:
                fail("operation attempt history is invalid")
        if check_files:
            for observation in operation["observations"]:
                if file_digest(Path(observation["path"])) != observation["sha256"]:
                    fail("operation observation evidence was changed")
    if previous is not None:
        if previous["revisions"] != state["revisions"][:len(previous["revisions"])] or previous["approvals"] != state["approvals"][:len(previous["approvals"])]:
            fail("application revision or approval history was rewritten")
        if previous.get("plan_approvals", []) != state["plan_approvals"][:len(previous.get("plan_approvals", []))] or previous["status_history"] != state["status_history"][:len(previous["status_history"])]:
            fail("application plan approval or status history was rewritten")
        for key, prior in previous["operations"].items():
            current = state["operations"].get(key)
            if current is None or len(current["attempts"]) < len(prior["attempts"]) or prior["observations"] != current["observations"][:len(prior["observations"])]:
                fail("application operation history was rewritten")
            for old, new in zip(prior["attempts"], current["attempts"]):
                if old != new and not (old["outcome"] == "in-flight" and new["outcome"] in {"unknown", "failed", "completed"} and all(new.get(field) == value for field, value in old.items() if field != "outcome")):
                    fail("application attempt history was rewritten")
            if prior["status"] == "completed" and (current["status"] != "completed" or current["remote_id"] != prior["remote_id"]):
                fail("completed operation identity was rewritten")
    approved_revisions: set[int] = set()
    for approval in state["plan_approvals"]:
        exact(approval, {"revision", "proposal_sha256", "approved_by", "approved_at"}, "plan approval")
        number = positive_int(approval["revision"], "plan approval revision")
        if number > len(state["revisions"]) or number in approved_revisions:
            fail("plan approval revision is unknown or duplicated")
        approved_revisions.add(number)
        revision = state["revisions"][approval["revision"] - 1]
        if approval["proposal_sha256"] != revision["proposal_sha256"] or approval["approved_by"] != revision["recorded_by"]:
            fail("plan approval differs from the preview or tech lead")
        require_timestamp(approval["approved_at"], "plan approved_at")


def render_preview(revision: dict[str, Any], tasks: dict[int, dict[str, Any]]) -> str:
    lines = ["# Aplicação da revisão aprovada", "", f"Revisão semântica: `{revision['change_review']['review_sha256']}`", "", "## Impacto concreto", ""]
    for item in revision["operations"]:
        current = tasks.get(item["issue_id"])
        status = "nova tarefa" if current is None else f"{current['status']['name']} (#{current['id']})"
        lines.extend([f"- **{item['key']}** — `{item['action']}` em {status}", f"  - Motivo: {item['reason'] or 'alteração localizada aprovada'}", f"  - Impactos: {', '.join(item['impact_ids'])}"])
        if item["replacement_keys"]:
            lines.append(f"  - Substituições: {', '.join(item['replacement_keys'])}")
        lines.extend(["", "```json", json.dumps(item["attributes"], ensure_ascii=False, indent=2), "```", ""])
    lines.extend(["", "Tarefas concluídas permanecem imutáveis. Relações e filhas fora do delta permanecem preservadas.", ""])
    return "\n".join(lines)


def command_prepare(arguments: argparse.Namespace) -> None:
    state_path = Path(arguments.state).absolute()
    feature_dir = state_path.parent.parent
    plan = load_json(Path(arguments.plan))
    exact(plan, {"preview_snapshot", "status_metadata", "status_contract", "operations"}, "application plan")
    review_path = Path(arguments.change_review).absolute()
    review_state, review, authorization = approved_review(review_path)
    publication_path = Path(arguments.publication_state).absolute()
    published = load_json(publication_path)
    publication.validate_publication_state(published)
    publication_revision = published["revisions"][-1]
    if published["status"] != "completed" or review["baseline"]["publication_state_path"] != str(publication_path) or review["baseline"]["publication_state_sha256"] != file_digest(publication_path):
        fail("revision application publication is stale or differs from the approved change review")
    snapshot_path, snapshot = load_snapshot(feature_dir, plan["preview_snapshot"], "preview snapshot")
    previous_state = load_json(state_path) if state_path.exists() else None
    if previous_state is not None:
        validate_state(previous_state, check_authority=False)
    metadata_path = evidence_path(feature_dir, plan["status_metadata"], "status metadata")
    metadata = load_json(metadata_path)
    statuses = status_contract(plan["status_contract"])
    available = {(item.get("id"), item.get("name")) for item in metadata.get("statuses", []) if isinstance(item, dict)}
    if any((value["id"], value["name"]) not in available for value in statuses.values()):
        fail("status contract is not proven by native metadata")
    parent_id = publication_revision["parent_baseline"]["issue_id"]
    if snapshot["parent"]["id"] != parent_id or snapshot["parent"]["project_id"] != publication_revision["parent_baseline"]["project_id"]:
        fail("preview snapshot belongs to another parent")
    tasks = {item["id"]: item for item in snapshot["tasks"]}
    relations = {item["id"]: item for item in snapshot["relations"]}
    affected_tasks = set(authorization["affected_task_keys"])
    affected_dependencies = {item["id"] for item in review["impact"]["affected_dependencies"]}
    lead = next(item["decided_by"] for item in review_state["decisions"] if item["revision"] == review["number"])
    if arguments.actor != lead:
        fail("only the tech lead may prepare the application")
    published_tasks = {item["key"]: item["remote_id"] for item in review["preservation"]["published_children"]}
    retained = {} if previous_state is None else {item["key"]: item for item in previous_state["revisions"][-1]["operations"] if previous_state["operations"].get(item["key"], {}).get("status") == "completed"}
    operations = []
    for item in plan["operations"]:
        if item["key"] in retained and retained[item["key"]] == item:
            operations.append(copy.deepcopy(item))
        else:
            operations.append(validate_operation(item, tasks, relations, statuses, affected_tasks, affected_dependencies, parent_id, snapshot["parent"]["project_id"], review["review_sha256"], published_tasks))
    keys = [item["key"] for item in operations]
    if len(keys) != len(set(keys)):
        fail("application operation keys must be unique")
    planned_task_keys = {item["task_key"] for item in operations if item["task_key"] is not None}
    created_keys = [item["task_key"] for item in operations if item["action"] == "create"]
    if len(created_keys) != len(set(created_keys)):
        fail("new task keys must be unique")
    for item in operations:
        if item["action"] == "cancel" and set(item["replacement_keys"]) - planned_task_keys:
            fail(f"cancellation {item['key']} references replacement tasks outside the approved plan")
        if item["action"] == "relation-add":
            for endpoint in ("issue_id", "issue_to_id"):
                value = item["attributes"][endpoint]
                if isinstance(value, str) and value not in planned_task_keys | set(published_tasks):
                    fail("relation references an unknown task key")
                if isinstance(value, int) and value not in published_tasks.values():
                    fail("relation endpoint is outside the published Feature")
        if item["action"] == "create" and item["task_key"] in published_tasks:
            fail("new task key already belongs to a published child")
    published_ids = {item["remote_id"] for item in review["preservation"]["published_children"] if item["remote_id"] is not None}
    present_ids = set(tasks)
    if not published_ids <= present_ids:
        fail("preview snapshot lost a published, adopted, or external child")
    evidence_dir = feature_dir / ".work" / "application-evidence"
    frozen_review = change_review.freeze_evidence(review_path, evidence_dir)
    snapshot_path = change_review.freeze_evidence(snapshot_path, evidence_dir)
    metadata_path = change_review.freeze_evidence(metadata_path, evidence_dir)
    revision = {
        "number": 1, "recorded_by": require_text(arguments.actor, "actor"), "recorded_at": require_timestamp(arguments.at, "recorded_at"), "reason": require_text(arguments.reason, "reason"),
        "change_review": {"path": str(frozen_review), "source_path": str(review_path), "sha256": file_digest(frozen_review), "revision": review["number"], "review_sha256": review["review_sha256"], "authorization_sha256": digest(authorization)},
        "publication": {"path": str(publication_path), "sha256": file_digest(publication_path), "revision": publication_revision["number"]},
        "preview_snapshot": {"path": str(snapshot_path), "sha256": file_digest(snapshot_path), "parent_status": copy.deepcopy(snapshot["parent"]["status"])},
        "status_metadata": {"path": str(metadata_path), "sha256": file_digest(metadata_path)}, "status_contract": statuses, "operations": operations,
        "preservation": {"task_ids": sorted(tasks), "relation_ids": sorted(relations), "published_child_ids": sorted(published_ids)},
    }
    revision["proposal_sha256"] = proposal_digest(revision)
    if state_path.exists():
        state = load_json(state_path); validate_state(state, check_authority=False)
        current = state["revisions"][-1]
        if current["proposal_sha256"] == revision["proposal_sha256"]:
            print(json.dumps({"status": state["status"], "revision": current["number"], "proposal_sha256": current["proposal_sha256"]})); return
        prior_operations = {item["key"]: item for item in current["operations"]}
        next_operations = {item["key"]: item for item in operations}
        for key, record in state["operations"].items():
            if record["attempts"] and record["attempts"][-1]["outcome"] in {"unknown", "in-flight"} and record["status"] != "completed" and not any(item.get("attempt_id") == record["attempts"][-1]["id"] for item in record["observations"]):
                fail("reconcile uncertain operations before preparing another revision")
            if key in next_operations and key not in prior_operations:
                fail("operation keys cannot be reused across application cycles")
            if key in next_operations and next_operations[key] != prior_operations[key]:
                fail("use a new operation key for a changed attempted intent")
            if state["status"] != "completed" and record["status"] == "completed" and key in prior_operations and key not in next_operations:
                fail("retain completed operations when revising a partial application")
        revision["number"] = len(state["revisions"]) + 1
        state["revisions"].append(revision)
        state["status"] = "prepared"
        state["readback"] = None; state["completed_at"] = None
    else:
        state = {"schema_version": 1, "status": "prepared", "status_history": [{"status": "prepared", "recorded_at": revision["recorded_at"]}], "revisions": [revision], "approvals": [], "operations": {}, "readback": None, "completed_at": None}
    validate_state(state)
    atomic_write(state_path, json.dumps(state, ensure_ascii=False, indent=2).encode() + b"\n")
    atomic_write(Path(arguments.preview), render_preview(revision, tasks).encode("utf-8"))
    print(json.dumps({"status": "prepared", "revision": revision["number"], "proposal_sha256": revision["proposal_sha256"]}))


def preview_snapshot(state: dict[str, Any]) -> dict[str, Any]:
    snapshot = load_json(Path(state["revisions"][-1]["preview_snapshot"]["path"]))
    snapshot["parent"] = issue_projection(snapshot["parent"], "preview parent")
    snapshot["tasks"] = [issue_projection(item, "preview task") for item in snapshot["tasks"]]
    return snapshot


def command_approve(arguments: argparse.Namespace) -> None:
    path = Path(arguments.state); state = load_json(path); validate_state(state)
    revision = state["revisions"][-1]
    if arguments.actor != revision["recorded_by"] or arguments.proposal_sha256 != revision["proposal_sha256"]:
        fail("approval must bind the exact preview hash and tech lead")
    if not any(item["revision"] == revision["number"] for item in state["plan_approvals"]):
        state["plan_approvals"].append({"revision": revision["number"], "proposal_sha256": revision["proposal_sha256"], "approved_by": arguments.actor, "approved_at": require_timestamp(arguments.at, "approved_at")})
    validate_state(state); atomic_write(path, json.dumps(state, ensure_ascii=False, indent=2).encode() + b"\n")
    print(json.dumps({"status": "approved", "proposal_sha256": revision["proposal_sha256"]}))


def current_operation(state: dict[str, Any], key: str) -> dict[str, Any]:
    result = next((item for item in state["revisions"][-1]["operations"] if item["key"] == key), None)
    if result is None:
        fail("unknown application operation key")
    return result


def fresh_snapshot(state_path: Path, state: dict[str, Any], operation: dict[str, Any], snapshot_value: str) -> tuple[Path, dict[str, Any], str | None]:
    path, snapshot = load_snapshot(state_path.parent.parent, snapshot_value, "current mutation snapshot")
    preview = preview_snapshot(state)
    if any(snapshot["parent"].get(field) != preview["parent"].get(field) for field in ("id", "project_id", "status")):
        fail("parent execution status changed since preview")
    issue_sha: str | None = None
    if operation["issue_id"] is not None:
        issue = next((item for item in snapshot["tasks"] if item["id"] == operation["issue_id"]), None)
        prior = next((item for item in preview["tasks"] if item["id"] == operation["issue_id"]), None)
        if issue is None or prior is None or issue != prior:
            fail("task changed since preview; reconcile and prepare a new application revision")
        issue_sha = digest(issue)
    return path, snapshot, issue_sha


def requires_approval(operation: dict[str, Any], state: dict[str, Any]) -> bool:
    if operation["action"] == "cancel":
        return True
    if operation["action"] != "update":
        return False
    preview = preview_snapshot(state)
    issue = next(item for item in preview["tasks"] if item["id"] == operation["issue_id"])
    return status_kind(issue, state["revisions"][-1]["status_contract"]) == "in_progress"


def command_approve_task(arguments: argparse.Namespace) -> None:
    path = Path(arguments.state); state = load_json(path); validate_state(state)
    operation = current_operation(state, arguments.key)
    if not requires_approval(operation, state):
        fail("this operation does not require task-specific approval")
    snapshot_path, _snapshot, issue_sha = fresh_snapshot(path, state, operation, arguments.snapshot)
    if arguments.actor != state["revisions"][-1]["recorded_by"]:
        fail("only the tech lead may approve the task-specific mutation")
    if any(item["operation_key"] == operation["key"] and item["revision"] == state["revisions"][-1]["number"] for item in state["approvals"]):
        fail("task-specific approval is already recorded")
    state["approvals"].append({"revision": state["revisions"][-1]["number"], "operation_key": operation["key"], "task_key": operation["task_key"], "task_snapshot_sha256": issue_sha, "operation_sha256": operation_digest(operation), "approved_by": arguments.actor, "approved_at": require_timestamp(arguments.at, "approved_at"), "reason": require_text(arguments.reason, "reason")})
    validate_state(state); atomic_write(path, json.dumps(state, ensure_ascii=False, indent=2).encode() + b"\n")
    print(json.dumps({"status": "approved", "operation_key": operation["key"], "snapshot_sha256": file_digest(snapshot_path)}))


def command_begin(arguments: argparse.Namespace) -> None:
    path = Path(arguments.state); state = load_json(path); validate_state(state)
    if state["status"] == "completed": fail("completed application cannot begin operations")
    operation = current_operation(state, arguments.key)
    _snapshot_path, _snapshot, issue_sha = fresh_snapshot(path, state, operation, arguments.snapshot)
    record = state["operations"].setdefault(operation["key"], {"kind": operation["action"], "attempts": [], "observations": [], "status": "pending", "remote_id": None})
    if record["status"] == "completed": fail("completed operation must not be duplicated")
    if record["attempts"] and record["attempts"][-1]["outcome"] in {"in-flight", "unknown"} and not any(item.get("attempt_id") == record["attempts"][-1]["id"] for item in record["observations"]):
        fail("uncertain operation requires observation before retry")
    if requires_approval(operation, state):
        approval = next((item for item in state["approvals"] if item["operation_key"] == operation["key"] and item["revision"] == state["revisions"][-1]["number"]), None)
        if approval is None or approval["task_snapshot_sha256"] != issue_sha or approval["operation_sha256"] != operation_digest(operation):
            fail("mutation requires task-specific tech-lead approval bound to the current snapshot")
    if not any(item["revision"] == state["revisions"][-1]["number"] for item in state["plan_approvals"]):
        fail("the exact application preview requires tech-lead approval")
    tool, payload = operation_payload(operation, state)
    if operation["action"] == "create":
        expected = payload["attributes"]
        if any(all(item.get(field) == expected[field] for field in ("project_id", "parent_issue_id", "subject")) for item in _snapshot["tasks"]):
            fail("a matching child already exists; reconcile before creating")
    elif operation["action"] == "relation-add":
        if any(all(item.get(field) == value for field, value in payload.items()) for item in _snapshot["relations"]):
            fail("a matching relation already exists; reconcile before creating")
    elif operation["action"] == "relation-remove":
        current_relation = next((item for item in _snapshot["relations"] if item["id"] == operation["relation_id"]), None)
        if current_relation != {"id": operation["relation_id"], **operation["attributes"]}:
            fail("relation changed since preview; reconcile before removing")
    attempt_id = len(record["attempts"]) + 1
    record["attempts"].append({"id": attempt_id, "started_at": require_timestamp(arguments.at, "started_at"), "outcome": "in-flight", "payload": copy.deepcopy(payload)})
    state["status"] = "applying"; state["status_history"].append({"status": "applying", "recorded_at": arguments.at})
    validate_state(state); atomic_write(path, json.dumps(state, ensure_ascii=False, indent=2).encode() + b"\n")
    print(json.dumps({"attempt_id": attempt_id, "tool": tool, "payload": payload}, ensure_ascii=False))


def resolve_task(value: Any, state: dict[str, Any]) -> int:
    if isinstance(value, int):
        return positive_int(value, "relation endpoint")
    current = state["revisions"][-1]
    operation = next((item for item in current["operations"] if item["task_key"] == value), None)
    if operation is not None:
        if operation["action"] != "create":
            return operation["issue_id"]
        record = state["operations"].get(operation["key"])
        if record is None or record["status"] != "completed":
            fail("replacement tasks and relation endpoints must be reconciled before use")
        return positive_int(record["remote_id"], "created task id")
    review = load_json(Path(current["change_review"]["path"]))["revisions"][-1]
    child = next((item for item in review["preservation"]["published_children"] if item["key"] == value), None)
    if child is None:
        fail("unknown published task reference")
    return positive_int(child["remote_id"], "published task id")


def operation_payload(operation: dict[str, Any], state: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    action = operation["action"]
    attributes = copy.deepcopy(operation["attributes"])
    if action == "create":
        marker = f"[project-slices-revision:{operation['revision_sha256']}:{operation['key']}]"
        attributes["description"] += "\n\n" + marker
        return "redmine_create_issue", {"attributes": attributes}
    if action in {"update", "cancel"}:
        if action == "cancel":
            replacements = [f"{key} (#{resolve_task(key, state)})" for key in operation["replacement_keys"]]
            attributes["notes"] = f"{operation['reason']} Replaced by: {', '.join(replacements)}. Revision: {operation['revision_sha256']}"
        return "redmine_update_issue", {"issue_id": operation["issue_id"], "changes": attributes}
    if action == "relation-add":
        for field in ("issue_id", "issue_to_id"):
            attributes[field] = resolve_task(attributes[field], state)
        return "redmine_create_relation", attributes
    return "redmine_delete_relation", {"relation_id": operation["relation_id"]}


def issue_matches(issue: dict[str, Any] | None, attributes: dict[str, Any]) -> bool:
    if issue is None:
        return False
    for field, value in attributes.items():
        if field == "notes":
            notes = [issue.get("notes", ""), *[item.get("notes", "") for item in issue.get("journals", [])]]
            if value not in notes:
                return False
        elif issue.get(field) != value:
            return False
    return True


def command_finish(arguments: argparse.Namespace) -> None:
    path = Path(arguments.state); state = load_json(path); validate_state(state, check_authority=False)
    operation = current_operation(state, arguments.key); record = state["operations"].get(operation["key"])
    if record is None or not record["attempts"] or record["attempts"][-1]["id"] != arguments.attempt or record["attempts"][-1]["outcome"] != "in-flight": fail("finish does not match the active attempt")
    if arguments.outcome == "completed" and operation["action"] in {"create", "relation-add"}: positive_int(arguments.remote_id, "remote_id")
    if arguments.outcome != "completed" and arguments.remote_id is not None: fail("only a completed create/add may record a remote id")
    if operation["action"] not in {"create", "relation-add"} and arguments.remote_id is not None:
        fail("only create/add operations accept a remote id")
    record["attempts"][-1].update({"outcome": arguments.outcome, "finished_at": require_timestamp(arguments.at, "finished_at"), "error_code": arguments.error_code, "message": arguments.message})
    if arguments.outcome == "completed": record["status"] = "completed"; record["remote_id"] = arguments.remote_id or operation["issue_id"] or operation["relation_id"]
    validate_state(state, check_authority=False); atomic_write(path, json.dumps(state, ensure_ascii=False, indent=2).encode() + b"\n")
    print(json.dumps({"status": record["status"], "outcome": arguments.outcome}))


def command_observe(arguments: argparse.Namespace) -> None:
    path = Path(arguments.state); state = load_json(path); validate_state(state, check_authority=False)
    operation = current_operation(state, arguments.key); record = state["operations"].get(operation["key"])
    if record is None or not record["attempts"] or record["attempts"][-1]["outcome"] not in {"in-flight", "unknown"}: fail("observation requires an uncertain operation")
    snapshot_path, snapshot = load_snapshot(path.parent.parent, arguments.snapshot, "operation observation snapshot")
    preview = preview_snapshot(state)
    if any(snapshot["parent"].get(field) != preview["parent"].get(field) for field in ("id", "project_id")):
        fail("operation reconciliation belongs to another parent")
    tasks = {item["id"]: item for item in snapshot["tasks"]}
    relations = {item["id"]: item for item in snapshot["relations"]}
    attempt_id = record["attempts"][-1]["id"]
    if record["status"] == "completed" or any(item.get("attempt_id") == attempt_id and item["outcome"] == arguments.outcome for item in record["observations"]):
        fail("this attempt already has a reconciliation observation")
    _tool, payload = operation_payload(operation, state)
    action = operation["action"]
    remote_id = arguments.remote_id
    completed = False
    if action in {"create", "relation-add"}:
        expected = payload["attributes"] if action == "create" else payload
        if action == "create":
            marker = f"[project-slices-revision:{operation['revision_sha256']}:{operation['key']}]"
            candidates = [item for item in tasks.values() if marker in item.get("description", "") or all(item.get(field) == expected[field] for field in ("project_id", "parent_issue_id", "subject"))]
            matches = [item for item in candidates if issue_matches(item, expected)]
        else:
            candidates = [item for item in relations.values() if all(item.get(field) == value for field, value in expected.items())]
            matches = candidates
        if len(candidates) > 1 or len(matches) != len(candidates):
            fail("ambiguous or changed remote result requires reconciliation")
        completed = len(matches) == 1
        if completed:
            if arguments.outcome != "matched" or remote_id != matches[0]["id"]:
                fail("operation observation outcome does not match the readback evidence")
        elif arguments.outcome != "absent" or remote_id is not None:
            fail("operation observation outcome does not match the readback evidence")
    elif action in {"update", "cancel"}:
        issue = tasks.get(operation["issue_id"])
        completed = issue_matches(issue, payload["changes"])
        prior = next((item for item in preview["tasks"] if item["id"] == operation["issue_id"]), None)
        if not completed and issue != prior:
            fail("changed remote task requires reconciliation; absence is not proven")
        if completed != (arguments.outcome == "matched") or remote_id is not None:
            fail("operation observation outcome does not match the readback evidence")
    else:
        completed = operation["relation_id"] not in relations
        if completed != (arguments.outcome == "absent") or remote_id is not None:
            fail("operation observation outcome does not match the readback evidence")
    snapshot_path = change_review.freeze_evidence(snapshot_path, path.parent.parent / ".work" / "application-evidence")
    observation = {"attempt_id": attempt_id, "outcome": arguments.outcome, "path": str(snapshot_path.absolute()), "sha256": file_digest(snapshot_path), "observed_at": require_timestamp(arguments.at, "observed_at"), "remote_id": remote_id}
    if completed:
        record["status"] = "completed"; record["remote_id"] = remote_id or operation["issue_id"] or operation["relation_id"]
    record["observations"].append(observation)
    validate_state(state, check_authority=False); atomic_write(path, json.dumps(state, ensure_ascii=False, indent=2).encode() + b"\n")
    print(json.dumps({"status": record["status"], "observation": arguments.outcome}))


def command_complete(arguments: argparse.Namespace) -> None:
    path = Path(arguments.state); state = load_json(path); validate_state(state)
    current = state["revisions"][-1]
    if not any(item["revision"] == current["number"] for item in state["plan_approvals"]):
        fail("completion requires approval of the current application preview")
    if any(state["operations"].get(item["key"], {}).get("status") != "completed" for item in current["operations"]): fail("all approved operations must be reconciled before completion")
    readback_path, readback = load_snapshot(path.parent.parent, arguments.readback, "final readback")
    preview = preview_snapshot(state)
    if any(readback["parent"].get(field) != preview["parent"].get(field) for field in ("id", "project_id", "status")): fail("final readback changed the parent identity or execution status")
    final_tasks = {item["id"]: item for item in readback["tasks"]}; final_relations = {item["id"]: item for item in readback["relations"]}
    operations = {item["key"]: item for item in current["operations"]}
    changed_task_ids = {item["issue_id"] for item in operations.values() if item["issue_id"] is not None}
    removed_relations = {item["relation_id"] for item in operations.values() if item["action"] == "relation-remove"}
    for issue in preview["tasks"]:
        if issue["id"] not in changed_task_ids and final_tasks.get(issue["id"]) != issue: fail("final readback lost or changed an unaffected/completed/adopted/external task")
    for relation in preview["relations"]:
        if relation["id"] not in removed_relations and final_relations.get(relation["id"]) != relation: fail("final readback lost or changed an unrelated relation")
    for key, operation in operations.items():
        record = state["operations"][key]
        if operation["action"] == "create":
            issue = final_tasks.get(record["remote_id"])
            if issue is None or not issue_matches(issue, operation_payload(operation, state)[1]["attributes"]): fail("final readback has a missing or wrong created task")
        elif operation["action"] == "update":
            issue = final_tasks.get(operation["issue_id"])
            if issue is None or not issue_matches(issue, operation["attributes"]): fail("final readback has a missing or wrong updated task")
        elif operation["action"] == "cancel":
            issue = final_tasks.get(operation["issue_id"])
            if not issue_matches(issue, operation_payload(operation, state)[1]["changes"]):
                fail("final readback lacks cancellation status, reason, or replacement IDs/keys")
        elif operation["action"] == "relation-add":
            relation = final_relations.get(record["remote_id"])
            if relation is None or any(relation.get(field) != value for field, value in operation_payload(operation, state)[1].items()): fail("final readback lacks an affected DEV/QA blocker")
        elif operation["relation_id"] in final_relations: fail("final readback still contains an approved removed relation")
    readback_path = change_review.freeze_evidence(readback_path, path.parent.parent / ".work" / "application-evidence")
    state["readback"] = {"path": str(readback_path.absolute()), "sha256": file_digest(readback_path), "observed_at": require_timestamp(arguments.at, "observed_at")}; state["completed_at"] = arguments.at; state["status"] = "completed"; state["status_history"].append({"status": "completed", "recorded_at": arguments.at, "readback": copy.deepcopy(state["readback"])})
    validate_state(state); atomic_write(path, json.dumps(state, ensure_ascii=False, indent=2).encode() + b"\n")
    print(json.dumps({"status": "completed", "readback_sha256": state["readback"]["sha256"]}))


def command_validate(arguments: argparse.Namespace) -> None:
    state = load_json(Path(arguments.state)); previous = load_json(Path(arguments.previous)) if arguments.previous else None
    validate_state(state, previous); print(json.dumps({"status": "valid", "workflow_status": state["status"], "revision": len(state["revisions"])}))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__); commands = parser.add_subparsers(dest="command", required=True)
    prepare = commands.add_parser("prepare"); prepare.add_argument("state"); prepare.add_argument("plan"); prepare.add_argument("--change-review", required=True); prepare.add_argument("--publication-state", required=True); prepare.add_argument("--preview", required=True); prepare.add_argument("--actor", required=True); prepare.add_argument("--at", required=True); prepare.add_argument("--reason", required=True); prepare.set_defaults(run=command_prepare)
    approve_plan = commands.add_parser("approve"); approve_plan.add_argument("state"); approve_plan.add_argument("--proposal-sha256", required=True); approve_plan.add_argument("--actor", required=True); approve_plan.add_argument("--at", required=True); approve_plan.set_defaults(run=command_approve)
    approve = commands.add_parser("approve-task"); approve.add_argument("state"); approve.add_argument("--key", required=True); approve.add_argument("--snapshot", required=True); approve.add_argument("--actor", required=True); approve.add_argument("--at", required=True); approve.add_argument("--reason", required=True); approve.set_defaults(run=command_approve_task)
    begin = commands.add_parser("begin"); begin.add_argument("state"); begin.add_argument("--key", required=True); begin.add_argument("--snapshot", required=True); begin.add_argument("--at", required=True); begin.set_defaults(run=command_begin)
    finish = commands.add_parser("finish"); finish.add_argument("state"); finish.add_argument("--key", required=True); finish.add_argument("--attempt", type=int, required=True); finish.add_argument("--outcome", choices=("completed", "failed", "unknown"), required=True); finish.add_argument("--remote-id", type=int); finish.add_argument("--error-code"); finish.add_argument("--message"); finish.add_argument("--at", required=True); finish.set_defaults(run=command_finish)
    observe = commands.add_parser("observe"); observe.add_argument("state"); observe.add_argument("--key", required=True); observe.add_argument("--outcome", choices=("matched", "absent"), required=True); observe.add_argument("--snapshot", required=True); observe.add_argument("--remote-id", type=int); observe.add_argument("--at", required=True); observe.set_defaults(run=command_observe)
    complete = commands.add_parser("complete"); complete.add_argument("state"); complete.add_argument("--readback", required=True); complete.add_argument("--at", required=True); complete.set_defaults(run=command_complete)
    validate = commands.add_parser("validate"); validate.add_argument("state"); validate.add_argument("--previous"); validate.set_defaults(run=command_validate)
    return parser


def main() -> int:
    try:
        arguments = build_parser().parse_args(); arguments.run(arguments); return 0
    except (ContractError, KeyError, TypeError) as error:
        print(f"invalid: {error}", file=sys.stderr); return 1


if __name__ == "__main__":
    raise SystemExit(main())
