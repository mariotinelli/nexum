#!/usr/bin/env python3
"""Validate append-only publication alignment records without remote access."""

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from uuid import UUID

sys.dont_write_bytecode = True

from render_publication import canonical_reference_path, check_projection, issue_snapshot
from validate_state import validate as validate_requirement
from artifact_paths import artifact_root, contained_path, relocated_path
from artifact_layout import approved_document


SHA256 = re.compile(r"^[a-f0-9]{64}$")
FILE_NAME = re.compile(r"^publication-alignment-([0-9a-fA-F-]{36})\.json$")
SECRET = re.compile(r"(?i)(authorization\s*:|bearer\s+|api[_ -]?key|token\s*[=:]|password\s*[=:])")
STATUSES = ("pending", "approved", "unknown", "completed")


def fail(message):
    raise ValueError(message)


def exact(value, keys, label):
    if not isinstance(value, dict) or set(value) != set(keys):
        fail(f"{label} has missing or unknown fields")


def text(value, label):
    if not isinstance(value, str) or not value.strip():
        fail(f"{label} must be non-empty text")
    return value


def timestamp(value, label):
    text(value, label)
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        fail(f"{label} requires a timezone")
    return parsed


def sha256(value, label):
    if not isinstance(value, str) or not SHA256.fullmatch(value):
        fail(f"{label} must be a lowercase SHA-256")
    return value


def identifier(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, str)) or str(value).strip() == "":
        fail(f"{label} must be an issue identifier")
    return value


def uuid(value, label):
    text(value, label)
    try:
        UUID(value)
    except ValueError as error:
        raise ValueError(f"{label} must be a UUID") from error
    return value


def relative_path(root, value, label):
    text(value, label)
    return relocated_path(contained_path(root, value))


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def description_hash(issue):
    return hashlib.sha256(issue["description"].encode("utf-8")).hexdigest()


def safe_strings(value, label="record"):
    if isinstance(value, dict):
        for key, entry in value.items():
            safe_strings(entry, f"{label}.{key}")
    elif isinstance(value, list):
        for index, entry in enumerate(value):
            safe_strings(entry, f"{label}[{index}]")
    elif isinstance(value, str) and SECRET.search(value):
        fail(f"{label} contains credential material")


def validate_legacy(state):
    if state.get("schema_version") != 1 or state.get("kind") != "publication-alignment":
        fail("unsupported publication alignment schema")
    identifier(state.get("issue_id"), "issue_id")
    text(state.get("canonical_state"), "canonical_state")
    if state.get("status") not in STATUSES:
        fail("legacy alignment has an invalid status")
    if not isinstance(state.get("lock"), dict) or not isinstance(state.get("attempts"), list) or not isinstance(state.get("observations"), list):
        fail("legacy alignment is incomplete")
    safe_strings(state)
    return state


def validate_status_history(state):
    history = state["status_history"]
    if not isinstance(history, list) or not history:
        fail("status_history must start at pending")
    allowed = {
        "pending": {"approved"},
        "approved": {"unknown", "completed"},
        "unknown": {"completed"},
        "completed": set(),
    }
    previous = None
    previous_at = None
    for index, entry in enumerate(history):
        exact(entry, {"status", "recorded_at"}, f"status_history[{index}]")
        status = entry["status"]
        if status not in STATUSES:
            fail(f"status_history[{index}] has an invalid status")
        recorded_at = timestamp(entry["recorded_at"], f"status_history[{index}].recorded_at")
        if index == 0 and status != "pending":
            fail("status_history must start at pending")
        if previous is not None and status not in allowed[previous]:
            fail("status_history contains an invalid transition")
        if previous_at is not None and recorded_at < previous_at:
            fail("status_history timestamps are out of order")
        previous, previous_at = status, recorded_at
    if state["status"] != history[-1]["status"]:
        fail("status must equal the latest status_history entry")


def validate_file_reference(root, value, label, required):
    exact(value, {"path", "sha256"}, label)
    path = relative_path(root, value["path"], f"{label}.path")
    digest = value["sha256"]
    if digest is None:
        if required:
            fail(f"{label}.sha256 is required")
        return path
    sha256(digest, f"{label}.sha256")
    if not path.is_file() or file_hash(path) != digest:
        fail(f"{label} file does not match its SHA-256")
    return path


def validate_v2(state, path):
    fields = {
        "schema_version", "kind", "alignment_id", "status", "status_history", "issue", "canonical",
        "lock", "baseline", "preview", "payload", "approval", "attempts", "observations", "readback", "completed_at",
    }
    exact(state, fields, "alignment")
    if state["schema_version"] != 2 or state["kind"] != "publication-alignment":
        fail("unsupported publication alignment schema")
    match = FILE_NAME.fullmatch(path.name)
    uuid(state["alignment_id"], "alignment_id")
    if not match or UUID(match.group(1)) != UUID(state["alignment_id"]):
        fail("v2 filename must be publication-alignment-<alignment_id>.json")
    validate_status_history(state)
    root = artifact_root(path)

    exact(state["issue"], {"issue_id", "subject"}, "issue")
    issue_id = identifier(state["issue"]["issue_id"], "issue.issue_id")
    text(state["issue"]["subject"], "issue.subject")

    exact(state["canonical"], {"state_path", "document_path", "approval_id", "sha256"}, "canonical")
    state_path = relative_path(root, state["canonical"]["state_path"], "canonical.state_path")
    document_path = relative_path(root, state["canonical"]["document_path"], "canonical.document_path")
    approval_id = text(state["canonical"]["approval_id"], "canonical.approval_id")
    canonical_sha = sha256(state["canonical"]["sha256"], "canonical.sha256")
    document_bytes = approved_document(document_path, canonical_sha)
    requirement = validate_requirement(state_path)
    if requirement["phase"] != "completed" or str(requirement["redmine"]["issue_id"]) != str(issue_id):
        fail("alignment requires the completed state for the same issue")
    approvals = [approval for approval in requirement["approvals"] if approval["id"] == approval_id and approval["kind"] == "requirement" and approval["status"] == "valid" and approval["subject_sha256"] == canonical_sha]
    if len(approvals) != 1:
        fail("canonical approval does not match the approved document")
    if document_path.name != f"{requirement['item_type'].lower()}.md":
        fail("canonical document name differs from the requirement type")

    lock_fields = {"item_key", "lock_id", "path", "acquired_at", "released_at", "release_reason"}
    exact(state["lock"], lock_fields, "lock")
    text(state["lock"]["item_key"], "lock.item_key")
    uuid(state["lock"]["lock_id"], "lock.lock_id")
    relative_path(root, state["lock"]["path"], "lock.path")
    timestamp(state["lock"]["acquired_at"], "lock.acquired_at")

    baseline_fields = {"path", "sha256", "description_sha256", "captured_at", "sanitized", "status", "relations"}
    exact(state["baseline"], baseline_fields, "baseline")
    baseline_path = relative_path(root, state["baseline"]["path"], "baseline.path")
    baseline_sha = sha256(state["baseline"]["sha256"], "baseline.sha256")
    sha256(state["baseline"]["description_sha256"], "baseline.description_sha256")
    timestamp(state["baseline"]["captured_at"], "baseline.captured_at")
    if state["baseline"]["sanitized"] is not True or not isinstance(state["baseline"]["relations"], list):
        fail("baseline must be sanitized and include relations")
    if not baseline_path.is_file() or file_hash(baseline_path) != baseline_sha:
        fail("baseline file does not match its SHA-256")
    baseline = issue_snapshot(json.loads(baseline_path.read_text(encoding="utf-8")))
    if str(baseline["id"]) != str(issue_id) or baseline["subject"] != state["issue"]["subject"]:
        fail("baseline belongs to another issue or title")
    if "status" not in baseline or "relations" not in baseline:
        fail("baseline snapshot must include status and relations")
    if baseline["status"] != state["baseline"]["status"] or baseline["relations"] != state["baseline"]["relations"]:
        fail("baseline metadata differs from its sanitized snapshot")
    if description_hash(baseline) != state["baseline"]["description_sha256"]:
        fail("baseline description hash differs")

    ready = state["status"] != "pending"
    preview_path = validate_file_reference(root, state["preview"], "preview", ready)
    payload_path = validate_file_reference(root, state["payload"], "payload", ready)
    payload = None
    if ready:
        payload = json.loads(payload_path.read_text(encoding="utf-8"))
        if set(payload) != {"issue_id", "changes"} or set(payload["changes"]) != {"description"}:
            fail("payload may contain only issue_id and changes.description")
        if str(payload["issue_id"]) != str(issue_id) or not isinstance(payload["changes"]["description"], str):
            fail("payload identity or description is invalid")
        if preview_path.read_bytes().decode("utf-8") != payload["changes"]["description"]:
            fail("preview differs from the exact payload description")

    if state["status"] == "pending":
        if state["approval"] is not None or state["attempts"] or state["observations"] or state["readback"] is not None or state["completed_at"] is not None:
            fail("pending alignment cannot claim approval, attempts, observations, readback or completion")
    else:
        approval_fields = {"id", "kind", "subject_sha256", "approved_by", "approved_at", "status"}
        exact(state["approval"], approval_fields, "approval")
        for field in ("id", "approved_by"):
            text(state["approval"][field], f"approval.{field}")
        timestamp(state["approval"]["approved_at"], "approval.approved_at")
        if state["approval"]["kind"] != "publish-payload" or state["approval"]["status"] != "valid" or state["approval"]["subject_sha256"] != state["payload"]["sha256"]:
            fail("payload approval must match the exact payload SHA-256")

    attempt_ids = set()
    latest_unknown = None
    for index, attempt in enumerate(state["attempts"]):
        required_attempt = {"id", "attempted_at", "payload_sha256", "outcome"}
        optional_attempt = {"response_received_at", "error_code", "sanitized_message"}
        if not isinstance(attempt, dict) or not required_attempt <= set(attempt) or set(attempt) - required_attempt - optional_attempt:
            fail(f"attempts[{index}] has missing or unknown fields")
        attempt_id = text(attempt["id"], f"attempts[{index}].id")
        if attempt_id in attempt_ids:
            fail("attempt IDs must be unique")
        attempt_ids.add(attempt_id)
        attempted_at = timestamp(attempt["attempted_at"], f"attempts[{index}].attempted_at")
        if attempt["payload_sha256"] != state["payload"]["sha256"] or attempt["outcome"] not in {"failed", "unknown", "completed"}:
            fail("every attempt must use the approved payload and a known outcome")
        if "response_received_at" in attempt:
            timestamp(attempt["response_received_at"], f"attempts[{index}].response_received_at")
        if attempt["outcome"] == "failed" and not {"error_code", "sanitized_message"} <= set(attempt):
            fail("failed attempt requires a sanitized error")
        if latest_unknown is not None:
            proofs = [observation for observation in state["observations"] if observation.get("kind") == "readback" and observation.get("outcome") == "absent" and observation.get("payload_sha256") == state["payload"]["sha256"] and timestamp(observation["observed_at"], "observation.observed_at") <= attempted_at and timestamp(observation["observed_at"], "observation.observed_at") >= latest_unknown]
            if not proofs:
                fail("retry after unknown outcome requires a readback proving absence")
            latest_unknown = None
        if attempt["outcome"] == "unknown":
            latest_unknown = attempted_at

    observation_ids = set()
    for index, observation in enumerate(state["observations"]):
        required_observation = {"id", "observed_at", "kind", "outcome", "summary"}
        optional_observation = {"description_sha256", "payload_sha256"}
        if not isinstance(observation, dict) or not required_observation <= set(observation) or set(observation) - required_observation - optional_observation:
            fail(f"observations[{index}] has missing or unknown fields")
        observation_id = text(observation["id"], f"observations[{index}].id")
        if observation_id in observation_ids:
            fail("observation IDs must be unique")
        observation_ids.add(observation_id)
        timestamp(observation["observed_at"], f"observations[{index}].observed_at")
        if observation["kind"] not in {"response", "readback"} or observation["outcome"] not in {"failed", "unknown", "absent", "diverged", "matched", "completed"}:
            fail("observation kind or outcome is invalid")
        text(observation["summary"], f"observations[{index}].summary")
        if "description_sha256" in observation:
            sha256(observation["description_sha256"], f"observations[{index}].description_sha256")
        if "payload_sha256" in observation:
            sha256(observation["payload_sha256"], f"observations[{index}].payload_sha256")
        if observation["outcome"] == "absent" and observation.get("payload_sha256") != state["payload"]["sha256"]:
            fail("absence observation must identify the approved payload")

    if state["status"] == "unknown" and not state["attempts"]:
        fail("unknown status requires an unknown attempt")
    if state["status"] == "unknown" and state["attempts"][-1]["outcome"] != "unknown":
        fail("unknown status must reflect the latest attempt")

    if state["status"] != "completed":
        if state["readback"] is not None or state["completed_at"] is not None or state["lock"]["released_at"] is not None or state["lock"]["release_reason"] is not None:
            fail("incomplete alignment cannot claim readback, completion or lock release")
    else:
        readback_fields = {"path", "sha256", "observed_at", "issue_id", "description_sha256", "payload_reconciled", "functional_projection", "unmanaged_content_preserved", "status_preserved", "relations_preserved"}
        exact(state["readback"], readback_fields, "readback")
        readback_path = relative_path(root, state["readback"]["path"], "readback.path")
        readback_sha = sha256(state["readback"]["sha256"], "readback.sha256")
        timestamp(state["readback"]["observed_at"], "readback.observed_at")
        identifier(state["readback"]["issue_id"], "readback.issue_id")
        if str(state["readback"]["issue_id"]) != str(issue_id):
            fail("readback belongs to another issue")
        if not readback_path.is_file() or file_hash(readback_path) != readback_sha:
            fail("readback file does not match its SHA-256")
        current = issue_snapshot(json.loads(readback_path.read_text(encoding="utf-8")), baseline["subject"])
        if description_hash(current) != state["readback"]["description_sha256"]:
            fail("readback description hash differs")
        check_projection(document_bytes.decode("utf-8"), requirement["item_type"], canonical_reference_path(document_path), approvals[0]["approved_by"], baseline, current)
        if current["description"] != payload["changes"]["description"]:
            fail("readback does not match the approved payload")
        completion_checks = (
            state["readback"]["payload_reconciled"] is True,
            state["readback"]["functional_projection"] == "passed",
            state["readback"]["unmanaged_content_preserved"] is True,
            state["readback"]["status_preserved"] is True,
            state["readback"]["relations_preserved"] is True,
        )
        if not all(completion_checks):
            fail("completed alignment requires all readback checks")
        completed_at = timestamp(state["completed_at"], "completed_at")
        released_at = timestamp(state["lock"]["released_at"], "lock.released_at")
        text(state["lock"]["release_reason"], "lock.release_reason")
        if released_at < completed_at:
            fail("lock release cannot precede verified completion")

    safe_strings(state)
    return state


def validate(path):
    path = relocated_path(path)
    artifact_root(path)
    state = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(state, dict):
        fail("publication alignment must be an object")
    if state.get("schema_version") == 1:
        return validate_legacy(state)
    return validate_v2(state, path)


def validate_transition(previous, current):
    if previous.get("schema_version") == 1 or current.get("schema_version") == 1:
        fail("legacy publication alignment records are read-only")
    if previous["alignment_id"] != current["alignment_id"] or previous["issue"] != current["issue"] or previous["canonical"] != current["canonical"] or previous["baseline"] != current["baseline"]:
        fail("alignment transition changed immutable identity or evidence")
    if previous["status"] == "completed" and current != previous:
        fail("completed publication alignment is immutable")
    if current["status_history"][:len(previous["status_history"])] != previous["status_history"]:
        fail("transition rewrote status history")
    for collection in ("attempts", "observations"):
        if current[collection][:len(previous[collection])] != previous[collection]:
            fail(f"transition rewrote {collection} history")
    for field in ("preview", "payload"):
        if previous[field]["path"] != current[field]["path"] or previous[field]["sha256"] not in {None, current[field]["sha256"]}:
            fail(f"transition changed approved {field} evidence")
    if previous["approval"] is not None and current["approval"] != previous["approval"]:
        fail("transition rewrote payload approval")
    old_lock = previous["lock"]
    new_lock = current["lock"]
    for field in ("item_key", "lock_id", "path", "acquired_at"):
        if new_lock[field] != old_lock[field]:
            fail("transition changed lock ownership history")
    if old_lock["released_at"] is not None and new_lock != old_lock:
        fail("transition rewrote lock release")
    if len(current["status_history"]) > len(previous["status_history"]) + 1:
        fail("transition appended more than one status")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("alignment", type=Path)
    parser.add_argument("--previous", type=Path)
    args = parser.parse_args()
    try:
        current = validate(args.alignment)
        if args.previous is not None:
            previous = validate(args.previous)
            validate_transition(previous, current)
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError, UnicodeDecodeError) as error:
        print(f"invalid: {error}", file=sys.stderr)
        return 1
    print("valid legacy (read-only)" if current["schema_version"] == 1 else "valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
