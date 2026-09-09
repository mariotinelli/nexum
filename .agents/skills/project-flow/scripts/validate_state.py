#!/usr/bin/env python3
"""Validate sourced Feature/Bug state and append-only transitions without network access."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any


PHASES = (
    "mode-confirmed",
    "inputs-normalized",
    "repository-analyzed",
    "item-ready",
    "item-created",
    "interviewing",
    "requirement-proposed",
    "requirement-approved",
    "redmine-synchronized",
    "completed",
)
OPERATION_STATUSES = {"pending", "approved", "completed", "unknown"}
ITEM_TYPES = {"Feature", "Bug"}
SOURCE_STATUSES = {"normalized", "unreadable", "removed"}
RECONCILIATION_STATUSES = {"not-applicable", "pending", "completed"}
SOURCE_ID_CHARACTERS = set("abcdefghijklmnopqrstuvwxyz0123456789-")
SOURCE_FILE_CHARACTERS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-")
PAUSE_KINDS = {"decision-deferred", "third-party-question", "voluntary-stop"}
SECRET_MARKERS = ("api_key", "apikey", "authorization:", "bearer ", "x-redmine-api-key", "password", "session_path")


def fail(message: str) -> None:
    raise ValueError(message)


def require_object(value: object, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        fail(f"{label} must be an object")
    return value


def require_list(value: object, label: str) -> list[Any]:
    if not isinstance(value, list):
        fail(f"{label} must be an array")
    return value


def require_keys(value: dict[str, Any], keys: set[str], label: str) -> None:
    missing = keys - value.keys()
    if missing:
        fail(f"{label} missing: {', '.join(sorted(missing))}")


def allow_keys(value: dict[str, Any], keys: set[str], label: str) -> None:
    extra = value.keys() - keys
    if extra:
        fail(f"{label} has unknown keys: {', '.join(sorted(extra))}")


def require_text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        fail(f"{label} must be non-empty text")
    return value


def require_timestamp(value: object, label: str) -> None:
    text = require_text(value, label)
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        fail(f"{label} must be an ISO 8601 date-time")
    if parsed.tzinfo is None:
        fail(f"{label} must include a timezone")


def require_uuid(value: object, label: str) -> None:
    try:
        uuid.UUID(require_text(value, label))
    except ValueError:
        fail(f"{label} must be a UUID")


def unique_ids(records: list[Any], label: str) -> None:
    ids: set[str] = set()
    for index, record_value in enumerate(records):
        record = require_object(record_value, f"{label}[{index}]")
        record_id = require_text(record.get("id"), f"{label}[{index}].id")
        if record_id in ids:
            fail(f"{label} contains duplicate id: {record_id}")
        ids.add(record_id)


def validate_sha256(value: object, label: str) -> None:
    if not isinstance(value, str) or len(value) != 64 or any(character not in "0123456789abcdef" for character in value):
        fail(f"{label} must be a lowercase SHA-256")


def validate_operation(value: object, label: str, *, relation: bool = False) -> str:
    operation = require_object(value, label)
    common = {"status", "payload_sha256", "approved_by", "approved_at", "completed_at", "observation_id", "attempts"}
    relation_keys = {"key", "relation_type", "source_issue_id", "target_issue_id"}
    allow_keys(operation, common | (relation_keys if relation else set()), label)
    if relation:
        require_keys(operation, relation_keys, label)
        require_text(operation["key"], f"{label}.key")
        require_text(operation["relation_type"], f"{label}.relation_type")
    status = operation.get("status")
    if status not in OPERATION_STATUSES:
        fail(f"{label}.status is invalid")
    if status in {"approved", "completed", "unknown"}:
        require_text(operation.get("approved_by"), f"{label}.approved_by")
        require_timestamp(operation.get("approved_at"), f"{label}.approved_at")
        if "payload_sha256" in operation:
            validate_sha256(operation["payload_sha256"], f"{label}.payload_sha256")
    if status == "completed":
        require_timestamp(operation.get("completed_at"), f"{label}.completed_at")
    attempts = require_list(operation.get("attempts", []), f"{label}.attempts")
    unique_ids(attempts, f"{label}.attempts")
    for index, attempt_value in enumerate(attempts):
        attempt_label = f"{label}.attempts[{index}]"
        attempt = require_object(attempt_value, attempt_label)
        attempt_keys = {"id", "attempted_at", "outcome", "error_code", "sanitized_message"}
        require_keys(attempt, {"id", "attempted_at", "outcome"}, attempt_label)
        allow_keys(attempt, attempt_keys, attempt_label)
        require_timestamp(attempt["attempted_at"], f"{attempt_label}.attempted_at")
        if attempt["outcome"] not in {"completed", "failed", "unknown"}:
            fail(f"{attempt_label}.outcome is invalid")
        if attempt["outcome"] == "failed":
            code = require_text(attempt.get("error_code"), f"{attempt_label}.error_code")
            message = require_text(attempt.get("sanitized_message"), f"{attempt_label}.sanitized_message")
            if any(character not in "abcdefghijklmnopqrstuvwxyz0123456789._-" for character in code):
                fail(f"{attempt_label}.error_code is invalid")
            if any(marker in message.lower() for marker in SECRET_MARKERS):
                fail(f"{attempt_label}.sanitized_message contains credential material")
        elif {"error_code", "sanitized_message"} & attempt.keys():
            fail(f"{attempt_label} error metadata requires failed outcome")
    return str(status)


def validate_source(source: object, index: int, state_path: Path) -> tuple[str, str]:
    label = f"sources[{index}]"
    if not isinstance(source, dict):
        fail(f"{label} must be an object")
    common_keys = {"id", "name", "type", "origin", "status", "decision_reconciliation"}
    normalized_keys = {
        "path",
        "original_sha256",
        "hash_unavailable_reason",
        "normalized_sha256",
        "extraction_method",
        "fully_read",
    }
    unreadable_keys = {"diagnostic"}
    removed_keys = {"removed_by", "removed_at", "removal_reason"}
    all_keys = common_keys | normalized_keys | unreadable_keys | removed_keys
    require_keys(source, common_keys, label)
    allow_keys(source, all_keys, label)
    source_id = require_text(source["id"], f"{label}.id")
    if source_id[0] not in SOURCE_ID_CHARACTERS - {"-"} or any(character not in SOURCE_ID_CHARACTERS for character in source_id):
        fail(f"{label}.id is invalid")
    for key in ("name", "type", "origin"):
        require_text(source[key], f"{label}.{key}")
    status = source["status"]
    if status not in SOURCE_STATUSES:
        fail(f"{label}.status is invalid")
    reconciliation = source["decision_reconciliation"]
    if reconciliation not in RECONCILIATION_STATUSES:
        fail(f"{label}.decision_reconciliation is invalid")

    if status == "normalized":
        require_keys(source, normalized_keys, label)
        if source.keys() & (unreadable_keys | removed_keys):
            fail(f"{label} normalized source has status-specific keys")
        relative_path = require_text(source["path"], f"{label}.path")
        normalized_path = Path(relative_path)
        local_source = len(normalized_path.parts) == 2 and normalized_path.parts[0] == "sources"
        shared_scope_source = (
            len(normalized_path.parts) == 6
            and normalized_path.parts[:3] == ("..", "..", "scopes")
            and normalized_path.parts[4] == "sources"
            and all(character in SOURCE_FILE_CHARACTERS for character in normalized_path.parts[3])
        )
        if normalized_path.is_absolute() or not (local_source or shared_scope_source) or normalized_path.suffix != ".md" or any(character not in SOURCE_FILE_CHARACTERS for character in normalized_path.name):
            fail(f"{label}.path must be a safe local or shared-scope Markdown source path")
        original_sha256 = source["original_sha256"]
        unavailable_reason = source["hash_unavailable_reason"]
        if original_sha256 is None:
            require_text(unavailable_reason, f"{label}.hash_unavailable_reason")
        elif not isinstance(original_sha256, str) or len(original_sha256) != 64 or any(character not in "0123456789abcdef" for character in original_sha256):
            fail(f"{label}.original_sha256 is invalid")
        elif unavailable_reason is not None:
            fail(f"{label}.hash_unavailable_reason requires a null original_sha256")
        if source["fully_read"] is not True:
            fail(f"{label}.fully_read must be true")
        extraction_method = require_text(source["extraction_method"], f"{label}.extraction_method")
        source_path = state_path.parent / normalized_path
        if not source_path.is_file() or source_path.is_symlink() or source_path.parent.is_symlink():
            fail(f"normalized source file not found or is a symlink: {source_path}")
        digest = hashlib.sha256(source_path.read_bytes()).hexdigest()
        if digest != source["normalized_sha256"]:
            fail(f"{label}.normalized_sha256 does not match")
        body = source_path.read_text(encoding="utf-8")
        original_label = original_sha256 or f"not applicable — {unavailable_reason}"
        hash_line = f"- Original SHA-256: `{original_label}`" if original_sha256 else f"- Original SHA-256: {original_label}"
        expected_header = "\n".join((
            f"# Source: {source['name']}",
            "",
            f"- Source ID: `{source_id}`",
            f"- Type: {source['type']}",
            f"- Origin: {source['origin']}",
            hash_line,
            f"- Extraction: {extraction_method}",
            "",
            "## Extracted content",
            "",
        ))
        if not body.startswith(expected_header):
            fail(f"{label} normalized Markdown metadata does not match state")
        return source_id, relative_path

    if status == "unreadable":
        require_keys(source, unreadable_keys, label)
        if source.keys() & (normalized_keys | removed_keys):
            fail(f"{label} unreadable source has status-specific keys")
        require_text(source["diagnostic"], f"{label}.diagnostic")
        if reconciliation != "pending":
            fail(f"{label} unreadable source reconciliation must be pending")
        return source_id, ""

    require_keys(source, removed_keys, label)
    if source.keys() & (normalized_keys | unreadable_keys):
        fail(f"{label} removed source has status-specific keys")
    for key in removed_keys:
        require_text(source[key], f"{label}.{key}")
    if reconciliation == "pending":
        fail(f"{label} removed source reconciliation cannot be pending")
    return source_id, ""


def validate_history(state: dict[str, Any]) -> None:
    decisions = require_list(state["decisions"], "decisions")
    approvals = require_list(state["approvals"], "approvals")
    questions = require_list(state["deferred_questions"], "deferred_questions")
    pauses = require_list(state["pauses"], "pauses")
    for label, records in (("decisions", decisions), ("approvals", approvals), ("deferred_questions", questions), ("pauses", pauses)):
        unique_ids(records, label)

    for index, value in enumerate(decisions):
        label = f"decisions[{index}]"
        decision = require_object(value, label)
        keys = {"id", "statement", "decided_by", "decided_at", "status", "reopened_at", "reopened_reason"}
        require_keys(decision, {"id", "statement", "decided_by", "decided_at", "status"}, label)
        allow_keys(decision, keys, label)
        for key in ("statement", "decided_by"):
            require_text(decision[key], f"{label}.{key}")
        require_timestamp(decision["decided_at"], f"{label}.decided_at")
        if decision["status"] == "reopened":
            require_timestamp(decision.get("reopened_at"), f"{label}.reopened_at")
            require_text(decision.get("reopened_reason"), f"{label}.reopened_reason")
        elif decision["status"] != "valid" or {"reopened_at", "reopened_reason"} & decision.keys():
            fail(f"{label} has invalid status metadata")

    for index, value in enumerate(approvals):
        label = f"approvals[{index}]"
        approval = require_object(value, label)
        keys = {"id", "kind", "subject_sha256", "approved_by", "approved_at", "status", "invalidated_at", "invalidated_reason"}
        require_keys(approval, {"id", "kind", "subject_sha256", "approved_by", "approved_at", "status"}, label)
        allow_keys(approval, keys, label)
        if approval["kind"] not in {"create-payload", "requirement", "publish-payload", "relation-payload", "abandonment-payload"}:
            fail(f"{label}.kind is invalid")
        if not isinstance(approval["subject_sha256"], str) or len(approval["subject_sha256"]) != 64 or any(character not in "0123456789abcdef" for character in approval["subject_sha256"]):
            fail(f"{label}.subject_sha256 is invalid")
        require_text(approval["approved_by"], f"{label}.approved_by")
        require_timestamp(approval["approved_at"], f"{label}.approved_at")
        if approval["status"] == "invalidated":
            require_timestamp(approval.get("invalidated_at"), f"{label}.invalidated_at")
            require_text(approval.get("invalidated_reason"), f"{label}.invalidated_reason")
        elif approval["status"] != "valid" or {"invalidated_at", "invalidated_reason"} & approval.keys():
            fail(f"{label} has invalid status metadata")

    pending = 0
    for index, value in enumerate(questions):
        label = f"deferred_questions[{index}]"
        question = require_object(value, label)
        keys = {"id", "question", "responsible_role", "reason", "blocked_decisions", "status", "asked_at", "resolution"}
        require_keys(question, {"id", "question", "responsible_role", "reason", "blocked_decisions", "status", "asked_at"}, label)
        allow_keys(question, keys, label)
        for key in ("question", "responsible_role", "reason"):
            require_text(question[key], f"{label}.{key}")
        blocked = require_list(question["blocked_decisions"], f"{label}.blocked_decisions")
        if not blocked or len(blocked) != len(set(blocked)) or any(not isinstance(item, str) or not item.strip() for item in blocked):
            fail(f"{label}.blocked_decisions must contain unique decision ids")
        require_timestamp(question["asked_at"], f"{label}.asked_at")
        if question["status"] == "pending":
            pending += 1
            if "resolution" in question:
                fail(f"{label} pending question cannot have a resolution")
        elif question["status"] == "resolved":
            resolution = require_object(question.get("resolution"), f"{label}.resolution")
            require_keys(resolution, {"answer", "source", "resolved_at"}, f"{label}.resolution")
            allow_keys(resolution, {"answer", "source", "resolved_at"}, f"{label}.resolution")
            require_text(resolution["answer"], f"{label}.resolution.answer")
            require_text(resolution["source"], f"{label}.resolution.source")
            require_timestamp(resolution["resolved_at"], f"{label}.resolution.resolved_at")
        else:
            fail(f"{label}.status is invalid")

    open_pauses = 0
    for index, value in enumerate(pauses):
        label = f"pauses[{index}]"
        pause = require_object(value, label)
        keys = {"id", "status", "kind", "previous_phase", "resume_phase", "reason", "resume_condition", "paused_at", "resumed_at", "resume_evidence"}
        require_keys(pause, {"id", "status", "kind", "previous_phase", "resume_phase", "reason", "resume_condition", "paused_at"}, label)
        allow_keys(pause, keys, label)
        if pause["kind"] not in PAUSE_KINDS:
            fail(f"{label}.kind is invalid")
        if pause["previous_phase"] not in PHASES or pause["resume_phase"] not in PHASES:
            fail(f"{label} has an invalid phase")
        for key in ("reason", "resume_condition"):
            require_text(pause[key], f"{label}.{key}")
        require_timestamp(pause["paused_at"], f"{label}.paused_at")
        if pause["status"] == "paused":
            open_pauses += 1
            if {"resumed_at", "resume_evidence"} & pause.keys():
                fail(f"{label} paused record cannot have resume metadata")
        elif pause["status"] == "resumed":
            require_timestamp(pause.get("resumed_at"), f"{label}.resumed_at")
            require_text(pause.get("resume_evidence"), f"{label}.resume_evidence")
        else:
            fail(f"{label}.status is invalid")

    if state["phase"] == "paused":
        if open_pauses != 1 or not pauses or pauses[-1]["status"] != "paused":
            fail("paused phase requires exactly one open latest pause")
        if pauses[-1]["kind"] != "voluntary-stop" and pending == 0:
            fail("decision or third-party pause requires a pending deferred question")
    elif open_pauses:
        fail("an open pause requires phase paused")

    if pending:
        completed = state["completed_phases"]
        if "requirement-approved" in completed or "redmine-synchronized" in completed or "completed" in completed:
            fail("pending deferred questions block approval and later phases")
        if any(item["kind"] == "requirement" and item["status"] == "valid" for item in approvals):
            fail("pending deferred questions conflict with a valid requirement approval")


def validate(path: Path) -> dict[str, Any]:
    state = json.loads(path.read_text(encoding="utf-8"))
    state = require_object(state, "state")
    decision_keys = {"classification", "similarity"}
    required = {"schema_version", "run_id", "internal_identity", "mode", "item_type", "phase", "completed_phases", "identity", "redmine", "sources", "repository", "decisions", "approvals", "deferred_questions", "pauses", "lock", "remote_operations"}
    reconciliation_keys = {"remote_observations", "requirement_divergences"}
    allow = required | reconciliation_keys | {"classification", "similarity"}
    require_keys(state, required, "state")
    allow_keys(state, allow, "state")
    if state["schema_version"] not in {2, 3}:
        fail(f"unsupported schema_version: {state['schema_version']!r}; expected 2 or 3")
    if state["schema_version"] == 3:
        require_keys(state, reconciliation_keys, "schema v3 state")
    if state["mode"] not in {"new-issue", "new-scope"} or state["item_type"] not in ITEM_TYPES:
        fail("only new-issue or new-scope Feature or Bug state is supported")
    require_uuid(state["run_id"], "run_id")
    require_uuid(state["internal_identity"], "internal_identity")

    completed = require_list(state["completed_phases"], "completed_phases")
    if completed != list(PHASES[:len(completed)]):
        fail("completed_phases must be a contiguous ordered prefix")
    expected_phase = PHASES[len(completed)] if len(completed) < len(PHASES) else "completed"
    if state["phase"] != "paused" and state["phase"] != expected_phase:
        fail(f"phase must be the first incomplete phase: {expected_phase}")
    identity = require_object(state["identity"], "identity")
    require_keys(identity, {"redmine_user_id", "display_name", "confirmed_at"}, "identity")
    allow_keys(identity, {"redmine_user_id", "display_name", "confirmed_at"}, "identity")
    require_text(identity["display_name"], "identity.display_name")
    require_timestamp(identity["confirmed_at"], "identity.confirmed_at")

    if "item-ready" in completed or expected_phase == "item-ready":
        require_keys(state, decision_keys, "state at item-ready or later")

    classification = state.get("classification")
    if classification is not None:
        if not isinstance(classification, dict):
            fail("classification must be an object")
        classification_keys = {"suggested_type", "rationale", "confirmed_type", "confirmed_by", "confirmed_at"}
        require_keys(classification, classification_keys, "classification")
        allow_keys(classification, classification_keys, "classification")
        if classification["suggested_type"] not in ITEM_TYPES or classification["confirmed_type"] not in ITEM_TYPES:
            fail("classification type is invalid")
        if classification["confirmed_type"] != state["item_type"]:
            fail("classification.confirmed_type must match item_type")
        if not isinstance(classification["rationale"], str) or not classification["rationale"].strip():
            fail("classification.rationale must not be empty")

    similarity = state.get("similarity")
    if similarity is not None and not isinstance(similarity, dict):
        fail("similarity must be an object")
    if isinstance(similarity, dict):
        similarity_keys = {"searched_at", "candidates", "decision", "existing_issue_id", "confirmed_by", "confirmed_at"}
        required_similarity_keys = similarity_keys - {"existing_issue_id"}
        require_keys(similarity, required_similarity_keys, "similarity")
        allow_keys(similarity, similarity_keys, "similarity")
        if not isinstance(similarity["candidates"], list):
            fail("similarity.candidates must be an array")
        candidate_keys = {"issue_id", "title", "status", "reason"}
        for index, candidate in enumerate(similarity["candidates"]):
            if not isinstance(candidate, dict):
                fail(f"similarity.candidates[{index}] must be an object")
            require_keys(candidate, candidate_keys, f"similarity.candidates[{index}]")
            allow_keys(candidate, candidate_keys, f"similarity.candidates[{index}]")
        if similarity["decision"] not in {"new-demand", "existing-demand"}:
            fail("similarity.decision is invalid")
        if similarity["decision"] == "existing-demand" and "existing_issue_id" not in similarity:
            fail("existing similarity decision requires existing_issue_id")
        candidate_ids = {str(candidate["issue_id"]) for candidate in similarity["candidates"]}
        if similarity["decision"] == "existing-demand" and str(similarity["existing_issue_id"]) not in candidate_ids:
            fail("existing_issue_id must identify a presented similarity candidate")
        if similarity["decision"] == "new-demand" and "existing_issue_id" in similarity:
            fail("new demand cannot identify an existing issue")

    redmine = require_object(state["redmine"], "redmine")
    redmine_keys = {"project_id", "project_name", "tracker_id", "tracker_name", "initial_status_id", "initial_status_name", "approved_status_id", "approved_status_name", "mapping_confirmations", "category", "issue_id"}
    require_keys(redmine, redmine_keys - {"issue_id", "category"}, "redmine")
    allow_keys(redmine, redmine_keys, "redmine")
    if not isinstance(redmine["mapping_confirmations"], list):
        fail("redmine.mapping_confirmations must be an array")
    for index, confirmation in enumerate(redmine["mapping_confirmations"]):
        if not isinstance(confirmation, dict):
            fail(f"redmine.mapping_confirmations[{index}] must be an object")
        confirmation_keys = {"kind", "selected_id", "selected_name", "confirmed_by", "confirmed_at"}
        require_keys(confirmation, confirmation_keys, f"redmine.mapping_confirmations[{index}]")
        allow_keys(confirmation, confirmation_keys, f"redmine.mapping_confirmations[{index}]")
        if confirmation["kind"] not in {"tracker", "initial-status", "approved-status"}:
            fail(f"redmine.mapping_confirmations[{index}].kind is invalid")
    category = redmine.get("category")
    if category is not None:
        if not isinstance(category, dict):
            fail("redmine.category must be an attributed decision object")
        category_keys = {"id", "name", "confirmed_by", "confirmed_at"}
        require_keys(category, category_keys, "redmine.category")
        allow_keys(category, category_keys, "redmine.category")
    require_text(redmine["project_name"], "redmine.project_name")
    require_text(redmine["tracker_name"], "redmine.tracker_name")
    require_text(redmine["initial_status_name"], "redmine.initial_status_name")
    if category is not None:
        require_text(category["confirmed_by"], "redmine.category.confirmed_by")
        require_timestamp(category["confirmed_at"], "redmine.category.confirmed_at")

    lock = require_object(state["lock"], "lock")
    lock_keys = {"item_key", "lock_id", "path", "acquired_at", "recovered_from", "recovery_reason"}
    require_keys(lock, {"item_key", "lock_id", "path", "acquired_at"}, "lock")
    allow_keys(lock, lock_keys, "lock")
    require_text(lock["item_key"], "lock.item_key")
    require_uuid(lock["lock_id"], "lock.lock_id")
    digest = hashlib.sha256(lock["item_key"].encode("utf-8")).hexdigest()
    if lock["path"] != f"docs/harness/.locks/{digest}.lock.json":
        fail("lock.path does not match item_key")
    require_timestamp(lock["acquired_at"], "lock.acquired_at")
    if "recovered_from" in lock:
        require_uuid(lock["recovered_from"], "lock.recovered_from")
        require_text(lock.get("recovery_reason"), "lock.recovery_reason")
    elif "recovery_reason" in lock:
        fail("lock.recovery_reason requires recovered_from")

    operations = require_object(state["remote_operations"], "remote_operations")
    require_keys(operations, {"create", "publish"}, "remote_operations")
    allow_keys(operations, {"create", "publish", "relations"}, "remote_operations")
    if state["schema_version"] == 3:
        require_keys(operations, {"relations"}, "schema v3 remote_operations")
    create_status = validate_operation(operations["create"], "remote_operations.create")
    publish_status = validate_operation(operations["publish"], "remote_operations.publish")
    relation_operations = require_list(operations.get("relations", []), "remote_operations.relations")
    if [relation.get("key") for relation in relation_operations if isinstance(relation, dict)] != sorted(relation.get("key") for relation in relation_operations if isinstance(relation, dict)):
        fail("remote relation operations must use stable key order")
    relation_keys: set[str] = set()
    for index, relation in enumerate(relation_operations):
        validate_operation(relation, f"remote_operations.relations[{index}]", relation=True)
        relation_key = relation["key"]
        if relation_key in relation_keys:
            fail(f"duplicate relation operation key: {relation_key}")
        relation_keys.add(relation_key)
    if state["schema_version"] == 3:
        for name, operation in (("create", operations["create"]), ("publish", operations["publish"])):
            if operation["status"] in {"approved", "completed", "unknown"} and "payload_sha256" not in operation:
                fail(f"schema v3 remote operation {name} requires payload_sha256")
            if operation["status"] == "completed" and (not operation.get("attempts") or "observation_id" not in operation):
                fail(f"schema v3 completed remote operation {name} requires an attempt and observation")
        for relation in relation_operations:
            if relation["status"] in {"approved", "completed", "unknown"} and "payload_sha256" not in relation:
                fail(f"schema v3 relation operation {relation['key']} requires payload_sha256")
            if relation["status"] == "completed" and (not relation.get("attempts") or "observation_id" not in relation):
                fail(f"schema v3 completed relation operation {relation['key']} requires an attempt and observation")
    if create_status in {"approved", "completed"} and category is None:
        fail("approved create operation requires a confirmed category decision")

    if isinstance(similarity, dict) and similarity["decision"] == "existing-demand":
        if state["phase"] != "item-ready":
            fail("existing demand must stop at item-ready")
        if create_status != "pending" or publish_status != "pending" or "issue_id" in redmine:
            fail("existing demand cannot contain a remote mutation")
    if "item-created" in completed and (create_status != "completed" or not isinstance(redmine.get("issue_id"), int)):
        fail("completed item-created phase requires completed create and integer issue_id")
    if create_status == "completed" and not isinstance(redmine.get("issue_id"), int):
        fail("completed create requires an integer issue_id")
    if "redmine-synchronized" in completed and publish_status != "completed":
        fail("completed redmine-synchronized phase requires completed publish")
    if "redmine-synchronized" in completed and any(relation["status"] != "completed" for relation in relation_operations):
        fail("completed redmine-synchronized phase requires completed relations")
    if publish_status == "completed" and create_status != "completed":
        fail("publish cannot complete before create")
    if publish_status in {"approved", "unknown", "completed"} and create_status != "completed":
        fail("publication cannot start before create is durably completed")
    if any(relation["status"] in {"unknown", "completed"} for relation in relation_operations) and publish_status != "completed":
        fail("relation mutations cannot start before publication is durably completed")

    observations = require_list(state.get("remote_observations", []), "remote_observations")
    unique_ids(observations, "remote_observations")
    observation_ids: set[str] = set()
    for index, observation_value in enumerate(observations):
        label = f"remote_observations[{index}]"
        observation = require_object(observation_value, label)
        keys = {"id", "operation_key", "observed_at", "outcome", "remote_sha256", "summary"}
        require_keys(observation, {"id", "operation_key", "observed_at", "outcome", "summary"}, label)
        allow_keys(observation, keys, label)
        observation_ids.add(require_text(observation["id"], f"{label}.id"))
        require_text(observation["operation_key"], f"{label}.operation_key")
        require_timestamp(observation["observed_at"], f"{label}.observed_at")
        require_text(observation["summary"], f"{label}.summary")
        if observation["outcome"] not in {"matched", "absent", "diverged", "ambiguous"}:
            fail(f"{label}.outcome is invalid")
        if "remote_sha256" in observation:
            validate_sha256(observation["remote_sha256"], f"{label}.remote_sha256")
    for name, operation in [("create", operations["create"]), ("publish", operations["publish"]), *[(relation["key"], relation) for relation in relation_operations]]:
        if "observation_id" in operation and operation["observation_id"] not in observation_ids:
            fail(f"remote operation {name} references an unknown observation")
        if "observation_id" in operation:
            observation = next(item for item in observations if item["id"] == operation["observation_id"])
            if observation["operation_key"] != name:
                fail(f"remote operation {name} references another operation's observation")

    divergences = require_list(state.get("requirement_divergences", []), "requirement_divergences")
    unique_ids(divergences, "requirement_divergences")
    for index, divergence_value in enumerate(divergences):
        label = f"requirement_divergences[{index}]"
        divergence = require_object(divergence_value, label)
        keys = {"id", "observed_at", "remote_sha256", "summary", "status", "decided_by", "decided_at", "decision_reason"}
        require_keys(divergence, {"id", "observed_at", "remote_sha256", "summary", "status"}, label)
        allow_keys(divergence, keys, label)
        require_timestamp(divergence["observed_at"], f"{label}.observed_at")
        validate_sha256(divergence["remote_sha256"], f"{label}.remote_sha256")
        require_text(divergence["summary"], f"{label}.summary")
        if divergence["status"] == "pending":
            if {"decided_by", "decided_at", "decision_reason"} & divergence.keys():
                fail(f"{label} pending divergence cannot contain a decision")
        elif divergence["status"] in {"accepted", "rejected"}:
            require_text(divergence.get("decided_by"), f"{label}.decided_by")
            require_timestamp(divergence.get("decided_at"), f"{label}.decided_at")
            require_text(divergence.get("decision_reason"), f"{label}.decision_reason")
        else:
            fail(f"{label}.status is invalid")
    if any(divergence["status"] == "pending" for divergence in divergences) and publish_status in {"approved", "completed"}:
        fail("pending requirement divergence blocks publication")
    if publish_status in {"approved", "completed", "unknown"} and "requirement-approved" not in completed:
        fail("publication requires an approved canonical requirement")

    sources = state["sources"]
    if not isinstance(sources, list) or not sources:
        fail("sources must be a non-empty array")
    source_ids: set[str] = set()
    source_paths: set[str] = set()
    normalized_count = 0
    for index, source in enumerate(sources):
        source_id, source_path = validate_source(source, index, path)
        if source_id in source_ids:
            fail(f"duplicate source id: {source_id}")
        source_ids.add(source_id)
        if source_path:
            if source_path in source_paths:
                fail(f"duplicate normalized source path: {source_path}")
            source_paths.add(source_path)
            normalized_count += 1
    if "inputs-normalized" in completed:
        if any(source["status"] == "unreadable" for source in sources):
            fail("normalized phases cannot contain unreadable sources")
        if normalized_count == 0:
            fail("normalized phases require at least one retained source")
    if "interviewing" in completed and any(source["decision_reconciliation"] == "pending" for source in sources):
        fail("requirement phases cannot contain pending evidence reconciliation")

    repository = state["repository"]
    if not isinstance(repository, dict):
        fail("repository must be an object")
    repository_keys = {"stack", "vocabulary", "exclusions"}
    require_keys(repository, repository_keys, "repository")
    allow_keys(repository, repository_keys, "repository")
    if not all(isinstance(repository[key], list) for key in repository_keys):
        fail("repository fields must be arrays")
    for key in ("stack", "exclusions"):
        for index, value in enumerate(repository[key]):
            require_text(value, f"repository.{key}[{index}]")
    for index, entry in enumerate(repository["vocabulary"]):
        label = f"repository.vocabulary[{index}]"
        if not isinstance(entry, dict):
            fail(f"{label} must be an object")
        require_keys(entry, {"term", "evidence_paths"}, label)
        allow_keys(entry, {"term", "evidence_paths"}, label)
        require_text(entry["term"], f"{label}.term")
        if not isinstance(entry["evidence_paths"], list) or not entry["evidence_paths"]:
            fail(f"{label}.evidence_paths must be a non-empty array")
        for evidence_index, evidence_path in enumerate(entry["evidence_paths"]):
            require_text(evidence_path, f"{label}.evidence_paths[{evidence_index}]")
    if "repository-analyzed" in completed and (not repository["stack"] or not repository["exclusions"]):
        fail("repository-analyzed phases require stack and exclusions")

    validate_history(state)
    if state["phase"] == "paused" and state["pauses"][-1]["resume_phase"] != expected_phase:
        fail(f"pause must resume at first incomplete phase: {expected_phase}")
    return state


def records_by_id(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {record["id"]: record for record in records}


def validate_append_only(previous: dict[str, Any], current: dict[str, Any], field: str, allowed_change: tuple[str, str, set[str]]) -> None:
    old_records = records_by_id(previous[field])
    new_records = records_by_id(current[field])
    for record_id, old in old_records.items():
        if record_id not in new_records:
            fail(f"transition removed {field} record: {record_id}")
        new = new_records[record_id]
        if new == old:
            continue
        old_status, new_status, added = allowed_change
        if old.get("status") != old_status or new.get("status") != new_status:
            fail(f"transition rewrote {field} record: {record_id}")
        preserved = {key: value for key, value in new.items() if key not in added}
        original = {key: value for key, value in old.items() if key != "status"}
        if preserved != original:
            fail(f"transition altered history in {field} record: {record_id}")


def validate_sources_transition(previous: dict[str, Any], current: dict[str, Any]) -> None:
    old_sources = records_by_id(previous["sources"])
    new_sources = records_by_id(current["sources"])
    immutable_keys = {"id", "name", "type", "origin"}

    for source_id, old in old_sources.items():
        if source_id not in new_sources:
            fail(f"transition removed sources record: {source_id}")
        new = new_sources[source_id]
        if any(new.get(key) != old.get(key) for key in immutable_keys):
            fail(f"transition changed source identity: {source_id}")
        if new == old:
            continue
        if old["status"] == "removed":
            fail(f"transition rewrote removed source: {source_id}")
        if old["status"] == "normalized" and new["status"] == "normalized":
            old_reconciliation = old["decision_reconciliation"]
            new_reconciliation = new["decision_reconciliation"]
            preserved = {key: value for key, value in new.items() if key != "decision_reconciliation"}
            original = {key: value for key, value in old.items() if key != "decision_reconciliation"}
            if preserved != original or (old_reconciliation, new_reconciliation) != ("pending", "completed"):
                fail(f"transition rewrote normalized source: {source_id}")
            continue
        if old["status"] == "unreadable" and new["status"] in {"normalized", "removed"}:
            continue
        if new["status"] == "removed":
            continue
        fail(f"transition has invalid source status change: {source_id}")


def validate_operation_transition(old: dict[str, Any], new: dict[str, Any], name: str, observations: dict[str, dict[str, Any]]) -> None:
    if old["status"] == "completed" and new != old:
        fail(f"completed remote operation {name} is immutable")
    allowed = {
        "pending": {"pending", "approved"},
        "approved": {"approved", "completed", "unknown"},
        "completed": {"completed"},
        "unknown": {"unknown", "approved", "completed"},
    }
    if new["status"] not in allowed[old["status"]]:
        fail(f"remote operation {name} has impossible status transition")
    for key, value in old.items():
        if key in {"status", "attempts", "observation_id", "completed_at"}:
            continue
        if new.get(key) != value:
            fail(f"remote operation {name} rewrote {key}")
    old_attempts = old.get("attempts", [])
    new_attempts = new.get("attempts", [])
    if new_attempts[:len(old_attempts)] != old_attempts:
        fail(f"remote operation {name} rewrote attempt history")
    if old["status"] == "unknown" and new["status"] != "unknown":
        observation = observations.get(new.get("observation_id", ""))
        expected = "matched" if new["status"] == "completed" else "absent"
        if observation is None or observation["operation_key"] != name or observation["outcome"] != expected:
            fail(f"remote operation {name} requires a {expected} reconciliation observation")


def validate_transition(previous: dict[str, Any], current: dict[str, Any]) -> None:
    for key in ("schema_version", "run_id", "internal_identity", "mode", "item_type"):
        if current[key] != previous[key]:
            fail(f"transition changed immutable field: {key}")
    old_lock = previous["lock"]
    new_lock = current["lock"]
    if new_lock["item_key"] != old_lock["item_key"]:
        fail("transition changed immutable lock item_key")
    if new_lock["lock_id"] == old_lock["lock_id"]:
        if new_lock != old_lock:
            fail("transition changed lock metadata without recovery")
    elif new_lock.get("recovered_from") != old_lock["lock_id"]:
            fail("transition changed lock without an exact recovery record")
    if current["identity"] != previous["identity"]:
        fail("transition changed confirmed identity")
    for key, value in previous["redmine"].items():
        if key != "issue_id" and current["redmine"].get(key) != value:
            fail(f"transition changed confirmed Redmine context: {key}")

    old_completed = previous["completed_phases"]
    new_completed = current["completed_phases"]
    if new_completed not in (old_completed, list(PHASES[:len(old_completed) + 1])):
        fail("transition skipped, reordered, or reversed completed phases")
    if previous["phase"] == "paused" and new_completed != old_completed:
        fail("cannot complete a phase while paused")

    validate_append_only(previous, current, "decisions", ("valid", "reopened", {"status", "reopened_at", "reopened_reason"}))
    validate_append_only(previous, current, "approvals", ("valid", "invalidated", {"status", "invalidated_at", "invalidated_reason"}))
    validate_append_only(previous, current, "deferred_questions", ("pending", "resolved", {"status", "resolution"}))
    validate_sources_transition(previous, current)
    old_observations = previous.get("remote_observations", [])
    new_observations = current.get("remote_observations", [])
    if new_observations[:len(old_observations)] != old_observations:
        fail("transition rewrote remote observation history")
    old_divergences = records_by_id(previous.get("requirement_divergences", []))
    new_divergences = records_by_id(current.get("requirement_divergences", []))
    for divergence_id, old in old_divergences.items():
        if divergence_id not in new_divergences:
            fail(f"transition removed requirement divergence: {divergence_id}")
        new = new_divergences[divergence_id]
        if new == old:
            continue
        preserved = {key: value for key, value in new.items() if key not in {"status", "decided_by", "decided_at", "decision_reason"}}
        original = {key: value for key, value in old.items() if key != "status"}
        if old["status"] != "pending" or new["status"] not in {"accepted", "rejected"} or preserved != original:
            fail(f"transition rewrote requirement divergence: {divergence_id}")

    old_pauses = previous["pauses"]
    new_pauses = current["pauses"]
    if previous["phase"] == "paused":
        if len(new_pauses) != len(old_pauses):
            fail("resume cannot add or remove pause history")
        if current["phase"] == "paused":
            if new_pauses != old_pauses:
                fail("work during a pause cannot rewrite the pause record")
        else:
            for old, new in zip(old_pauses[:-1], new_pauses[:-1]):
                if old != new:
                    fail("resume rewrote earlier pause history")
            old_last = old_pauses[-1]
            new_last = new_pauses[-1]
            preserved = {key: value for key, value in new_last.items() if key not in {"status", "resumed_at", "resume_evidence"}}
            original = {key: value for key, value in old_last.items() if key != "status"}
            if old_last["status"] != "paused" or new_last["status"] != "resumed" or preserved != original:
                fail("resume must only resolve the latest pause")
            if current["phase"] != old_last["resume_phase"]:
                fail("resume must continue at the recorded first incomplete phase")
    elif current["phase"] == "paused":
        if len(old_completed) == len(PHASES):
            fail("a completed run cannot be paused")
        if len(new_pauses) != len(old_pauses) + 1 or new_pauses[:-1] != old_pauses:
            fail("pause must append exactly one history record")
        if new_pauses[-1]["previous_phase"] != previous["phase"]:
            fail("pause previous_phase does not match prior state")
    elif new_pauses != old_pauses:
        fail("ordinary transition cannot change pause history")

    if (previous["phase"] == "paused" or current["phase"] == "paused") and current["remote_operations"] != previous["remote_operations"]:
        fail("pause and resume transitions cannot mutate remote operations")
    observations = records_by_id(current.get("remote_observations", []))
    changed_operations: list[str] = []
    for name in ("create", "publish"):
        if previous["remote_operations"][name] != current["remote_operations"][name]:
            changed_operations.append(name)
        validate_operation_transition(previous["remote_operations"][name], current["remote_operations"][name], name, observations)
    old_relations = {relation["key"]: relation for relation in previous["remote_operations"].get("relations", [])}
    new_relations = {relation["key"]: relation for relation in current["remote_operations"].get("relations", [])}
    for relation_key, old in old_relations.items():
        if relation_key not in new_relations:
            fail(f"transition removed relation operation: {relation_key}")
        new = new_relations[relation_key]
        for key in ("key", "relation_type", "source_issue_id", "target_issue_id"):
            if new[key] != old[key]:
                fail(f"transition changed relation identity: {relation_key}")
        if old != new:
            changed_operations.append(relation_key)
        validate_operation_transition(old, new, relation_key, observations)
    if len(changed_operations) > 1:
        fail("persist each remote operation separately before advancing")
    if changed_operations and new_completed != old_completed:
        fail("persist a remote operation before advancing its phase")
    old_issue = previous["redmine"].get("issue_id")
    if old_issue is not None and current["redmine"].get("issue_id") != old_issue:
        fail("transition changed recorded issue_id")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("state", type=Path)
    parser.add_argument("--previous", type=Path)
    args = parser.parse_args()
    try:
        current = validate(args.state)
        if args.previous is not None:
            validate_transition(validate(args.previous), current)
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as error:
        print(f"invalid: {error}", file=sys.stderr)
        return 1
    print("valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
