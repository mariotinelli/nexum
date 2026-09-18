#!/usr/bin/env python3
"""Select and persist Project Slices scope progress without remote access."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import sys
import tempfile
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any


class ContractError(ValueError):
    pass


STATUSES = {"waiting-requirements", "pending", "in-progress", "completed"}


def fail(message: str) -> None:
    raise ContractError(message)


def is_link_like(path: Path) -> bool:
    if path.is_symlink():
        return True
    try:
        attributes = os.lstat(path).st_file_attributes
    except (AttributeError, FileNotFoundError, OSError):
        return False
    return bool(attributes & 0x400)


def assert_safe_path(path: Path, *, file: bool = False) -> None:
    absolute = path.absolute()
    for current in (absolute, *absolute.parents):
        if current.exists() and is_link_like(current):
            fail(f"symlink or junction path component is not allowed: {current}")
    if file and (not path.is_file() or is_link_like(path)):
        fail(f"regular non-symlink file required: {path}")


def load_json(path: Path) -> dict[str, Any]:
    assert_safe_path(path, file=True)
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        fail(f"cannot read valid JSON from {path}: {error}")
    if not isinstance(value, dict):
        fail(f"{path} must contain a JSON object")
    return value


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def atomic_write(path: Path, content: bytes) -> None:
    assert_safe_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    assert_safe_path(path.parent)
    handle, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def require_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        fail(f"{label} must be non-empty text")
    return value.strip()


def require_timestamp(value: Any, label: str) -> str:
    text = require_text(value, label)
    try:
        datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        fail(f"{label} must be an ISO-8601 timestamp")
    return text


def contracts() -> tuple[Any, Any, Any, Any, Any, Any, Any]:
    package = Path(__file__).resolve().parents[1]
    project_flow = package.parent / "project-flow" / "scripts"
    if not project_flow.is_dir():
        fail("the packaged project-flow dependency is required")
    for directory in (project_flow, package / "scripts"):
        if str(directory) not in sys.path:
            sys.path.insert(0, str(directory))
    try:
        from catalog_contract import digest as catalog_digest
        import manage_publication as publication_contract
        import manage_dependencies as dependency_contract
        from manage_slices import validate_feature_approval, validate_state as validate_slices_state
        from validate_scope_state import validate as validate_scope_state
        from validate_state import validate as validate_requirement_state
    except ImportError as error:
        fail(f"cannot load packaged verification contracts: {error}")
    return (
        catalog_digest,
        validate_scope_state,
        validate_requirement_state,
        validate_feature_approval,
        validate_slices_state,
        publication_contract,
        dependency_contract,
    )


def contained(root: Path, value: Any, label: str) -> Path:
    relative = Path(require_text(value, label))
    if relative.is_absolute() or relative.anchor or ".." in relative.parts:
        fail(f"{label} must be a contained relative path")
    candidate = (root / relative).absolute()
    try:
        candidate.relative_to(root.absolute())
    except ValueError:
        fail(f"{label} escapes the harness root")
    assert_safe_path(candidate)
    return candidate


def scope_paths(scope_dir: Path) -> tuple[Path, Path]:
    scope_dir = scope_dir.absolute()
    assert_safe_path(scope_dir)
    if not scope_dir.is_dir() or scope_dir.parent.name != "scopes" or scope_dir.parent.parent.name != "harness":
        fail("scope directory must be docs/harness/scopes/<scope>")
    candidates = [scope_dir / ".flow" / "scope-state.json", scope_dir / "scope-state.json"]
    existing = [path for path in candidates if path.is_file()]
    if len(existing) != 1:
        fail("exactly one project-flow scope state is required")
    assert_safe_path(existing[0], file=True)
    return scope_dir, existing[0]


def approved_scope(scope_dir: Path) -> tuple[Path, Path, Path, dict[str, Any], str]:
    scope_dir, state_path = scope_paths(scope_dir)
    catalog_digest, validate_scope_state, _, _, _, _, _ = contracts()
    try:
        state = validate_scope_state(state_path)
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as error:
        fail(f"invalid project-flow scope: {error}")
    approvals = [
        approval for approval in state["approvals"]
        if approval.get("kind") == "complete-catalog-and-order" and approval.get("status") == "valid"
    ]
    if len(approvals) != 1 or approvals[0].get("subject_sha256") != catalog_digest(state):
        fail("scope requires one valid approval for the current complete catalog projection")
    return scope_dir, scope_dir.parent.parent, state_path, state, approvals[0]["subject_sha256"]


def progress_by_item(scope: dict[str, Any]) -> dict[str, dict[str, Any]]:
    progress = scope.get("item_progress")
    if not isinstance(progress, list):
        fail("scope item_progress is required")
    return {item["catalog_item_id"]: item for item in progress}


def mapped_path(harness: Path, value: Any, label: str) -> Path:
    text = require_text(value, label).replace("\\", "/")
    if text.startswith("docs/harness/"):
        return contained(harness.parent.parent, text, label)
    return contained(harness, text, label)


def feature_paths(harness: Path, item: dict[str, Any], progress: dict[str, Any]) -> tuple[Path, Path] | None:
    artifact_value = progress.get("artifact_path")
    state_value = progress.get("state_path")
    if artifact_value is None and state_value is None:
        return None
    if artifact_value is None or state_value is None:
        fail(f"catalog item {item['id']} has an incomplete Feature artifact mapping")
    artifact = mapped_path(harness, artifact_value, f"{item['id']} artifact_path")
    state_path = mapped_path(harness, state_value, f"{item['id']} state_path")
    if artifact.is_dir():
        artifact = artifact / "feature.md"
    if artifact.name != "feature.md" or not artifact.is_file() or not state_path.is_file():
        fail(f"catalog item {item['id']} does not map to real Feature artifacts")
    if artifact.parent not in state_path.parents:
        fail(f"catalog item {item['id']} Feature state belongs to another directory")
    return artifact.parent, state_path


def file_digest(path: Path) -> str:
    assert_safe_path(path, file=True)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def publication_evidence(
    feature_dir: Path,
    issue_id: int,
    requirement_sha256: str,
    validate_slices_state: Any,
    publication: Any,
    dependencies: Any,
) -> tuple[str, str | None, str, str | None]:
    publication_path = feature_dir / ".flow" / "slices-publication.json"
    slices_path = feature_dir / ".flow" / "slices-state.json"
    if not publication_path.exists():
        status = "in-progress" if slices_path.exists() else "pending"
        return status, None, "unknown", None
    state = load_json(publication_path)
    try:
        publication.validate_publication_state(state)
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as error:
        fail(f"invalid slicing publication for {feature_dir.name}: {error}")
    if state["status"] != "completed":
        return "in-progress", digest(state), "unknown", None
    readback = state.get("readback")
    current = state["revisions"][-1]
    recorded_slices = Path(current["slices_state_path"])
    if recorded_slices.absolute() != slices_path.absolute() or not slices_path.is_file():
        fail(f"slicing publication for {feature_dir.name} belongs to another Feature")
    if file_digest(slices_path) != current["slices_state_sha256"]:
        fail(f"slicing source changed for completed Feature {feature_dir.name}")
    slices = load_json(slices_path)
    try:
        validate_slices_state(slices)
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as error:
        fail(f"invalid approved slicing source for {feature_dir.name}: {error}")
    slicing_revision = slices["revisions"][-1]
    slicing_approvals = [
        approval for approval in slices["approvals"]
        if approval.get("status") == "valid" and approval.get("revision") == slicing_revision["number"]
    ]
    if slices["status"] != "approved" or len(slicing_approvals) != 1:
        fail(f"completed publication for {feature_dir.name} lacks its approved decomposition")
    if (
        current["slicing_revision"] != slicing_revision["number"]
        or current["slicing_approval_sha256"] != digest(slicing_approvals[0])
    ):
        fail(f"publication for {feature_dir.name} is not bound to its current decomposition approval")
    proposal_feature = slicing_revision["proposal"]["feature"]
    if proposal_feature["issue_id"] != issue_id:
        fail(f"slicing source for {feature_dir.name} has another parent identity")
    if proposal_feature["requirement_sha256"] != requirement_sha256:
        fail(f"slicing source for {feature_dir.name} uses another approved requirement")
    if current["parent_baseline"]["issue_id"] != issue_id:
        fail(f"publication for {feature_dir.name} has another parent identity")
    valid = [
        approval for approval in state["approvals"]
        if approval.get("status") == "valid"
        and approval.get("revision") == current["number"]
        and approval.get("publication_sha256") == current["publication_sha256"]
    ]
    expected_operations = {
        *(f"create:{child['key']}" for child in current["children"] if child.get("source") != "adopted"),
        *(f"relation:{relation['key']}" for relation in current["relations"]),
    }
    if (
        len(valid) != 1
        or not isinstance(readback, dict)
        or not readback.get("sha256")
        or set(state["operations"]) != expected_operations
        or any(operation.get("status") != "completed" for operation in state["operations"].values())
    ):
        fail(f"completed slicing publication for {feature_dir.name} lacks verified child routing evidence")
    readback_path = Path(readback.get("path", ""))
    work_dir = (feature_dir / ".work").absolute()
    try:
        readback_path.absolute().relative_to(work_dir)
    except ValueError:
        fail(f"publication readback for {feature_dir.name} is outside its temporary evidence area")
    if file_digest(readback_path) != readback["sha256"]:
        fail(f"publication readback for {feature_dir.name} is missing or changed")
    snapshot = load_json(readback_path)
    if set(snapshot) != {"parent", "children"}:
        fail(f"publication readback for {feature_dir.name} has an invalid shape")
    baseline = current["parent_baseline"]
    parent = snapshot["parent"]
    if (
        publication.positive_int(parent.get("id"), "parent.id") != issue_id
        or publication.named_id(parent, "status") != baseline["status_id"]
        or parent["status"].get("name") != baseline["status_name"]
    ):
        fail(f"publication readback for {feature_dir.name} changed the parent identity or status")
    children = snapshot["children"]
    review = current.get("existing_children_review")
    external_count = 0 if review is None else sum(item["disposition"] == "keep-external" for item in review["decisions"])
    if not isinstance(children, list) or len(children) != len(current["children"]) + external_count:
        fail(f"publication readback for {feature_dir.name} does not contain every child")
    by_id = {
        publication.positive_int(child.get("id"), "child.id"): child
        for child in children if isinstance(child, dict)
    }
    if len(by_id) != len(children):
        fail(f"publication readback for {feature_dir.name} has duplicate or invalid children")
    for child in current["children"]:
        description_path = Path(child["description_path"]).absolute()
        try:
            description_path.relative_to((feature_dir / "slices" / "descriptions").absolute())
        except ValueError:
            fail(f"publication child description for {feature_dir.name} is outside its canonical layout")
        remote_id = publication.child_remote_id(state, child["key"])
        if remote_id not in by_id:
            fail(f"publication readback for {feature_dir.name} is missing a routed child")
        publication.compare_issue(child, by_id[remote_id], baseline, current["native_fields"])
    for relation in current["relations"]:
        source_id, target_id = publication.relation_ids(state, relation)
        present_target, _ = publication.relation_present({"issue": by_id[target_id]}, source_id, target_id)
        present_source, _ = publication.relation_present({"issue": by_id[source_id]}, source_id, target_id)
        if not (present_target or present_source):
            fail(f"publication readback for {feature_dir.name} is missing an approved blocking edge")
    publication_digest = digest({
        "publication_sha256": current["publication_sha256"],
        "readback_sha256": readback["sha256"],
        "operations": {key: value.get("remote_id") for key, value in sorted(state["operations"].items())},
        **({"adopted_children": {child["key"]: child["remote_id"] for child in current["children"] if child.get("source") == "adopted"}} if any(child.get("source") == "adopted" for child in current["children"]) else {}),
    })
    has_external = any(
        item.get("external_blockers")
        for item in slicing_revision["proposal"]["slices"]
    )
    dependency_path = feature_dir / ".flow" / "slices-dependencies.json"
    if not has_external:
        return "completed", publication_digest, "not-required", None
    if not dependency_path.exists():
        return "completed", publication_digest, "pending", None
    dependency_state = load_json(dependency_path)
    try:
        dependencies.validate_state(dependency_state)
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as error:
        fail(f"invalid dependency routing for {feature_dir.name}: {error}")
    dependency_current = dependency_state["revisions"][-1]
    if (
        dependency_current["slices_state_path"] != str(slices_path.absolute())
        or dependency_current["slices_state_sha256"] != file_digest(slices_path)
        or dependency_current["publication_state_path"] != str(publication_path.absolute())
        or dependency_current["publication_sha256"] != current["publication_sha256"]
        or dependency_current["publication_readback_sha256"] != readback["sha256"]
    ):
        fail(f"dependency routing for {feature_dir.name} belongs to another child publication")
    if dependency_state["status"] == "completed":
        try:
            dependency_evidence = dependencies.completion_evidence(dependency_state)
        except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as error:
            fail(f"unverified dependency completion for {feature_dir.name}: {error}")
        return "completed", publication_digest, "ready", dependency_evidence
    return "completed", publication_digest, "refining", digest(dependency_state)


def inspect_scope(scope_dir: Path) -> dict[str, Any]:
    (
        scope_dir,
        harness,
        scope_path,
        scope,
        catalog_sha,
    ) = approved_scope(scope_dir)
    _, _, _, validate_feature, validate_slices_state, publication, dependencies = contracts()
    progress = progress_by_item(scope)
    catalog = {item["id"]: item for item in scope["catalog"]}
    ordered_ids = [item_id for item_id in scope["suggested_order"] if item_id in catalog]
    active_ids = {item_id for item_id, item in catalog.items() if item["lifecycle"] == "active"}
    if len(ordered_ids) != len(set(ordered_ids)) or set(ordered_ids) != active_ids:
        fail("approved catalog order does not cover every active catalog item exactly once")
    items = []
    for item_id in ordered_ids:
        item = catalog[item_id]
        if item["lifecycle"] != "active" or item["type"] != "Feature":
            continue
        mapped = feature_paths(harness, item, progress[item_id])
        record: dict[str, Any] = {
            "catalog_item_id": item_id,
            "position": item["suggested_position"],
            "title": item["delivery"]["title"],
            "status": "waiting-requirements",
            "feature_dir": None,
            "feature_state_path": None,
            "issue_id": None,
            "requirement_sha256": None,
            "publication_evidence_sha256": None,
            "dependency_status": "unknown",
            "dependency_evidence_sha256": None,
        }
        if mapped is None:
            items.append(record)
            continue
        feature_dir, feature_state_path = mapped
        requirement = load_json(feature_state_path)
        link = requirement.get("scope_item")
        linked_scope = None
        if isinstance(link, dict) and isinstance(link.get("state_path"), str):
            linked_scope = Path(os.path.abspath(feature_dir / link["state_path"]))
            assert_safe_path(linked_scope)
        if (
            requirement.get("mode") != "new-scope"
            or requirement.get("item_type") != "Feature"
            or not isinstance(link, dict)
            or link.get("catalog_item_id") != item_id
            or link.get("catalog_sha256") != catalog_sha
            or linked_scope != scope_path.absolute()
            or requirement.get("delivery") != item["delivery"]
        ):
            fail(f"Feature state for catalog item {item_id} has a stale scope identity")
        record["feature_dir"] = str(feature_dir.relative_to(harness)).replace("\\", "/")
        record["feature_state_path"] = str(feature_state_path.relative_to(harness)).replace("\\", "/")
        if requirement.get("phase") != "completed":
            items.append(record)
            continue
        try:
            _, checked_state, checked_requirement, approval, _ = validate_feature(feature_dir)
        except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as error:
            fail(f"completed Feature for catalog item {item_id} is not eligible: {error}")
        if checked_state.absolute() != feature_state_path.absolute():
            fail(f"catalog item {item_id} points to a stale Feature state path")
        if str(checked_requirement["redmine"]["issue_id"]) != str(progress[item_id].get("issue_id")):
            fail(f"catalog item {item_id} Redmine identity differs from its Feature")
        record["issue_id"] = checked_requirement["redmine"]["issue_id"]
        record["requirement_sha256"] = approval["subject_sha256"]
        record["status"], record["publication_evidence_sha256"], record["dependency_status"], record["dependency_evidence_sha256"] = publication_evidence(
            feature_dir,
            record["issue_id"],
            record["requirement_sha256"],
            validate_slices_state,
            publication,
            dependencies,
        )
        items.append(record)
    counts = {status: sum(item["status"] == status for item in items) for status in STATUSES}
    counts["sliced"] = counts["completed"]
    counts["total"] = len(items)
    return {
        "scope": {
            "directory": str(scope_dir),
            "state_path": str(scope_path.relative_to(scope_dir)).replace("\\", "/"),
            "internal_identity": scope["internal_identity"],
            "project_id": scope["redmine"]["project_id"],
            "catalog_sha256": catalog_sha,
        },
        "items": items,
        "progress": counts,
    }


def state_path_for(scope_dir: Path, supplied: str | None) -> Path:
    expected = scope_dir / ".flow" / "slices-scope-state.json"
    path = Path(supplied).absolute() if supplied else expected
    if path != expected:
        fail("scope slicing state must be .flow/slices-scope-state.json")
    return path


def next_item(items: list[dict[str, Any]], decided: set[str]) -> str | None:
    for item in items:
        if item["catalog_item_id"] not in decided and item["status"] in {"pending", "in-progress"}:
            return item["catalog_item_id"]
    return None


def snapshot(inspection: dict[str, Any], recorded_at: str) -> dict[str, Any]:
    projection = {"items": inspection["items"], "progress": inspection["progress"]}
    return {"recorded_at": recorded_at, "projection_sha256": digest(projection), **projection}


def validate_state(state: dict[str, Any], previous: dict[str, Any] | None = None) -> None:
    required = {"schema_version", "run_id", "scope", "status", "items", "progress", "current_item_id", "awaiting_decision_for", "observations", "continuation_decisions", "resumes", "started_by", "started_at", "completed_at"}
    if set(state) != required or state.get("schema_version") != 1:
        fail("scope slicing state has unknown or missing fields")
    try:
        uuid.UUID(state["run_id"])
    except (ValueError, TypeError, AttributeError):
        fail("scope slicing run_id must be a UUID")
    if state["status"] not in {"active", "paused", "completed"}:
        fail("scope slicing status is invalid")
    require_text(state["started_by"], "started_by")
    require_timestamp(state["started_at"], "started_at")
    if not isinstance(state["observations"], list) or not state["observations"]:
        fail("scope slicing state requires durable observations")
    latest = state["observations"][-1]
    if state["items"] != latest.get("items") or state["progress"] != latest.get("progress"):
        fail("current scope progress must match the latest durable observation")
    if latest.get("projection_sha256") != digest({"items": latest.get("items"), "progress": latest.get("progress")}):
        fail("scope progress observation hash differs")
    ids = [item.get("catalog_item_id") for item in state["items"]]
    if len(ids) != len(set(ids)) or any(item.get("status") not in STATUSES for item in state["items"]):
        fail("scope slicing items are invalid")
    expected_progress = {status: sum(item["status"] == status for item in state["items"]) for status in STATUSES}
    expected_progress.update(sliced=expected_progress["completed"], total=len(state["items"]))
    if state["progress"] != expected_progress:
        fail("scope slicing progress does not match its Feature observations")
    decisions = state["continuation_decisions"]
    if not isinstance(decisions, list) or len({item.get("after_item_id") for item in decisions}) != len(decisions):
        fail("each completed Feature requires at most one continuation decision")
    for decision in decisions:
        if decision.get("decision") not in {"continue", "stop"} or decision.get("after_item_id") not in ids:
            fail("scope continuation decision is invalid")
        require_text(decision.get("decided_by"), "continuation decided_by")
        require_timestamp(decision.get("decided_at"), "continuation decided_at")
        if decision.get("progress_sha256") not in {item.get("projection_sha256") for item in state["observations"]}:
            fail("continuation decision does not reference a durable progress observation")
    if not isinstance(state["resumes"], list):
        fail("scope resumes must be an array")
    for resume in state["resumes"]:
        if not isinstance(resume, dict) or set(resume) != {"resumed_by", "resumed_at"}:
            fail("scope resume record is invalid")
        require_text(resume["resumed_by"], "resumed_by")
        require_timestamp(resume["resumed_at"], "resumed_at")
    if state["status"] == "completed":
        if state["progress"]["sliced"] != state["progress"]["total"] or state["completed_at"] is None or state["awaiting_decision_for"] is not None:
            fail("scope completes only when every active Feature has verified routing")
        require_timestamp(state["completed_at"], "completed_at")
    elif state["completed_at"] is not None:
        fail("incomplete scope cannot have completed_at")
    if state["status"] == "paused" and state["current_item_id"] is not None:
        fail("paused scope cannot expose a current Feature")
    if state["awaiting_decision_for"] is not None:
        awaiting = next((item for item in state["items"] if item["catalog_item_id"] == state["awaiting_decision_for"]), None)
        if awaiting is None or awaiting["status"] != "completed" or state["current_item_id"] is not None:
            fail("scope can await a decision only for its just-completed Feature")
        if any(item["after_item_id"] == state["awaiting_decision_for"] for item in decisions):
            fail("scope cannot await an already-recorded continuation decision")
    if state["current_item_id"] is not None and state["current_item_id"] not in ids:
        fail("current Feature is not in the approved scope")
    if state["current_item_id"] is not None:
        current = next(item for item in state["items"] if item["catalog_item_id"] == state["current_item_id"])
        if current["status"] not in {"pending", "in-progress"} or any(decision["after_item_id"] == state["current_item_id"] for decision in decisions):
            fail("current Feature must be eligible and not previously processed")
    if previous is not None:
        if state["run_id"] != previous["run_id"] or state["scope"] != previous["scope"] or state["started_at"] != previous["started_at"] or state["started_by"] != previous["started_by"]:
            fail("scope slicing identity was rewritten")
        for field in ("observations", "continuation_decisions", "resumes"):
            if state[field][:len(previous[field])] != previous[field]:
                fail(f"scope slicing {field} history was rewritten")
        old_completed = {item["catalog_item_id"]: item["publication_evidence_sha256"] for item in previous["items"] if item["status"] == "completed"}
        current = {item["catalog_item_id"]: item for item in state["items"]}
        if any(current.get(item_id, {}).get("status") != "completed" or current[item_id].get("publication_evidence_sha256") != evidence for item_id, evidence in old_completed.items()):
            fail("verified completed Feature evidence was rewritten")


def reconcile(state: dict[str, Any], inspection: dict[str, Any], at: str) -> None:
    if state["scope"] != inspection["scope"]:
        fail("scope slicing state is bound to another approved catalog projection")
    previous_current = state["current_item_id"]
    candidate = snapshot(inspection, at)
    if candidate["projection_sha256"] != state["observations"][-1]["projection_sha256"]:
        state["observations"].append(candidate)
    state["items"] = candidate["items"]
    state["progress"] = candidate["progress"]
    decided = {item["after_item_id"] for item in state["continuation_decisions"]}
    current = next((item for item in state["items"] if item["catalog_item_id"] == previous_current), None)
    if current is not None and current["status"] == "completed" and previous_current not in decided:
        state["awaiting_decision_for"] = previous_current
        state["current_item_id"] = None
        state["status"] = "active"
        state["completed_at"] = None
    elif state["awaiting_decision_for"] is not None:
        state["current_item_id"] = None
        state["completed_at"] = None
    elif state["progress"]["sliced"] == state["progress"]["total"]:
        state["status"] = "completed"
        state["current_item_id"] = None
        state["completed_at"] = at
    elif state["status"] != "paused":
        state["status"] = "active"
        state["current_item_id"] = next_item(state["items"], decided)
        state["completed_at"] = None


def command_list(arguments: argparse.Namespace) -> None:
    harness = Path(arguments.harness).absolute()
    assert_safe_path(harness)
    scopes_dir = harness / "scopes"
    assert_safe_path(scopes_dir)
    if not scopes_dir.is_dir():
        fail("harness scopes directory does not exist")
    results = []
    skipped = []
    for child in sorted(scopes_dir.iterdir(), key=lambda path: path.name):
        if is_link_like(child):
            fail(f"scope discovery rejects symlink or junction: {child}")
        if not child.is_dir():
            continue
        try:
            inspection = inspect_scope(child)
        except (ContractError, OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as error:
            skipped.append({"directory": str(child), "reason": str(error)})
            continue
        if any(item["status"] in {"pending", "in-progress"} for item in inspection["items"]):
            results.append({"scope": inspection["scope"], "progress": inspection["progress"]})
    print(json.dumps({"scopes": results, "skipped": skipped}, ensure_ascii=False, sort_keys=True))


def command_start(arguments: argparse.Namespace) -> None:
    inspection = inspect_scope(Path(arguments.scope))
    scope_dir = Path(inspection["scope"]["directory"])
    path = state_path_for(scope_dir, arguments.state)
    if path.exists():
        fail("scope slicing state already exists; use refresh or resume")
    at = require_timestamp(arguments.at, "started_at")
    actor = require_text(arguments.actor, "started_by")
    first = snapshot(inspection, at)
    state = {
        "schema_version": 1,
        "run_id": str(uuid.uuid4()),
        "scope": inspection["scope"],
        "status": "active",
        "items": first["items"],
        "progress": first["progress"],
        "current_item_id": next_item(first["items"], set()),
        "awaiting_decision_for": None,
        "observations": [first],
        "continuation_decisions": [],
        "resumes": [],
        "started_by": actor,
        "started_at": at,
        "completed_at": None,
    }
    if state["progress"]["sliced"] == state["progress"]["total"]:
        state["status"] = "completed"
        state["current_item_id"] = None
        state["completed_at"] = at
    validate_state(state)
    atomic_write(path, canonical_bytes(state) + b"\n")
    print(json.dumps(state, ensure_ascii=False, sort_keys=True))


def command_refresh(arguments: argparse.Namespace) -> None:
    inspection = inspect_scope(Path(arguments.scope))
    scope_dir = Path(inspection["scope"]["directory"])
    path = state_path_for(scope_dir, arguments.state)
    state = load_json(path)
    validate_state(state)
    previous = copy.deepcopy(state)
    reconcile(state, inspection, require_timestamp(arguments.at, "recorded_at"))
    validate_state(state, previous)
    atomic_write(path, canonical_bytes(state) + b"\n")
    print(json.dumps(state, ensure_ascii=False, sort_keys=True))


def command_decide(arguments: argparse.Namespace) -> None:
    inspection = inspect_scope(Path(arguments.scope))
    scope_dir = Path(inspection["scope"]["directory"])
    path = state_path_for(scope_dir, arguments.state)
    state = load_json(path)
    validate_state(state)
    previous = copy.deepcopy(state)
    at = require_timestamp(arguments.at, "decided_at")
    reconcile(state, inspection, at)
    matches = [item for item in state["items"] if item["catalog_item_id"] == arguments.after_item]
    if len(matches) != 1 or matches[0]["status"] != "completed" or state["awaiting_decision_for"] != arguments.after_item:
        fail("continue or stop must answer the pending decision for the just-completed Feature")
    if any(item["after_item_id"] == arguments.after_item for item in state["continuation_decisions"]):
        fail("a continuation decision is already recorded for this Feature")
    state["continuation_decisions"].append({
        "after_item_id": arguments.after_item,
        "decision": arguments.decision,
        "progress_sha256": state["observations"][-1]["projection_sha256"],
        "decided_by": require_text(arguments.actor, "decided_by"),
        "decided_at": at,
    })
    state["awaiting_decision_for"] = None
    if state["progress"]["sliced"] == state["progress"]["total"]:
        state["status"] = "completed"
        state["current_item_id"] = None
        state["completed_at"] = at
    else:
        if arguments.decision == "stop":
            state["status"] = "paused"
            state["current_item_id"] = None
        else:
            decided = {item["after_item_id"] for item in state["continuation_decisions"]}
            state["status"] = "active"
            state["current_item_id"] = next_item(state["items"], decided)
    validate_state(state, previous)
    atomic_write(path, canonical_bytes(state) + b"\n")
    print(json.dumps(state, ensure_ascii=False, sort_keys=True))


def command_resume(arguments: argparse.Namespace) -> None:
    inspection = inspect_scope(Path(arguments.scope))
    scope_dir = Path(inspection["scope"]["directory"])
    path = state_path_for(scope_dir, arguments.state)
    state = load_json(path)
    validate_state(state)
    if state["status"] != "paused":
        fail("only a paused scope slicing run can resume")
    previous = copy.deepcopy(state)
    at = require_timestamp(arguments.at, "resumed_at")
    reconcile(state, inspection, at)
    state["resumes"].append({
        "resumed_by": require_text(arguments.actor, "resumed_by"),
        "resumed_at": at,
    })
    if state["status"] != "completed":
        decided = {item["after_item_id"] for item in state["continuation_decisions"]}
        state["status"] = "active"
        state["current_item_id"] = next_item(state["items"], decided)
    validate_state(state, previous)
    atomic_write(path, canonical_bytes(state) + b"\n")
    print(json.dumps(state, ensure_ascii=False, sort_keys=True))


def command_validate(arguments: argparse.Namespace) -> None:
    state = load_json(Path(arguments.state))
    previous = load_json(Path(arguments.previous)) if arguments.previous else None
    validate_state(state, previous)
    print("valid")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(required=True)
    listing = commands.add_parser("list")
    listing.add_argument("harness"); listing.set_defaults(run=command_list)
    start = commands.add_parser("start")
    start.add_argument("scope"); start.add_argument("--state"); start.add_argument("--actor", required=True); start.add_argument("--at", required=True); start.set_defaults(run=command_start)
    refresh = commands.add_parser("refresh")
    refresh.add_argument("scope"); refresh.add_argument("--state"); refresh.add_argument("--at", required=True); refresh.set_defaults(run=command_refresh)
    decide = commands.add_parser("decide")
    decide.add_argument("scope"); decide.add_argument("--state"); decide.add_argument("--after-item", required=True); decide.add_argument("--decision", choices=("continue", "stop"), required=True); decide.add_argument("--actor", required=True); decide.add_argument("--at", required=True); decide.set_defaults(run=command_decide)
    resume = commands.add_parser("resume")
    resume.add_argument("scope"); resume.add_argument("--state"); resume.add_argument("--actor", required=True); resume.add_argument("--at", required=True); resume.set_defaults(run=command_resume)
    validate = commands.add_parser("validate")
    validate.add_argument("state"); validate.add_argument("--previous"); validate.set_defaults(run=command_validate)
    return parser


def main() -> int:
    try:
        arguments = build_parser().parse_args()
        arguments.run(arguments)
    except (ContractError, OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as error:
        print(f"invalid: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
