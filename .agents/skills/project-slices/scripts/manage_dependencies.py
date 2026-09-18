#!/usr/bin/env python3
"""Prepare and reconcile cross-Feature slice blockers without remote access."""

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
    assert_safe_read,
    canonical_bytes,
    digest,
    file_digest,
    load_json,
    reject_secrets,
    require_text,
    require_timestamp,
    validate_state as validate_slices_state,
)
import manage_publication as publication


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
    if ".." in relative.parts:
        fail(f"{label} must be a regular contained evidence file")
    assert_safe_read(path)
    return path


def approved_sources(slices_path: Path, publication_path: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    slices, slicing_revision, slicing_approval = publication.approved_source(slices_path)
    published = load_json(publication_path)
    publication.validate_publication_state(published)
    current = published["revisions"][-1]
    valid = [
        item for item in published["approvals"]
        if item["status"] == "valid" and item["revision"] == current["number"]
    ]
    if published["status"] != "completed" or len(valid) != 1 or not isinstance(published.get("readback"), dict):
        fail("dependency routing requires completed and read-back child publication")
    publication.validate_current_source(current)
    readback_path = Path(published["readback"]["path"])
    if file_digest(readback_path) != published["readback"]["sha256"]:
        fail("verified child publication readback is missing or changed")
    if current["slices_state_path"] != str(slices_path.absolute()) or current["slices_state_sha256"] != file_digest(slices_path):
        fail("child publication is not bound to the current slicing state")
    if current["slicing_revision"] != slicing_revision["number"] or current["slicing_approval_sha256"] != digest(slicing_approval):
        fail("child publication is not bound to the current slicing approval")
    return slicing_revision, published, current


def graph_snapshot(feature_dir: Path, value: Any) -> tuple[Path, dict[str, Any]]:
    path = evidence_path(feature_dir, value, "graph_snapshot")
    graph = load_json(path)
    exact(graph, {"project_id", "scope", "complete", "issues", "relations"}, "relevant graph snapshot")
    positive_int(graph["project_id"], "graph project_id")
    if graph["scope"] != "relevant-blocking-graph" or graph["complete"] is not True:
        fail("dependency decisions require a complete relevant blocking graph")
    if not isinstance(graph["issues"], list) or not isinstance(graph["relations"], list):
        fail("relevant graph issues and relations must be arrays")
    issue_ids: set[int] = set()
    for index, issue in enumerate(graph["issues"]):
        exact(issue, {"id", "parent_issue_id", "title"}, f"graph issue {index}")
        issue_id = positive_int(issue["id"], f"graph issue {index}.id")
        if issue_id in issue_ids:
            fail("relevant graph contains duplicate issues")
        issue_ids.add(issue_id)
        if issue["parent_issue_id"] is not None:
            positive_int(issue["parent_issue_id"], f"graph issue {index}.parent_issue_id")
        require_text(issue["title"], f"graph issue {index}.title")
    relation_ids: set[int] = set()
    for index, relation in enumerate(graph["relations"]):
        exact(relation, {"id", "issue_id", "issue_to_id", "relation_type"}, f"graph relation {index}")
        relation_id = positive_int(relation["id"], f"graph relation {index}.id")
        if relation_id in relation_ids:
            fail("relevant graph contains duplicate relation ids")
        relation_ids.add(relation_id)
        positive_int(relation["issue_id"], f"graph relation {index}.issue_id")
        positive_int(relation["issue_to_id"], f"graph relation {index}.issue_to_id")
        require_text(relation["relation_type"], f"graph relation {index}.relation_type")
    reject_secrets(graph, "relevant graph snapshot")
    return path, graph


def external_blockers(slicing_revision: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    result: dict[tuple[str, str], dict[str, Any]] = {}
    for item in slicing_revision["proposal"]["slices"]:
        target_key = f"dev-{item['number']}"
        for blocker in item.get("external_blockers", []):
            identity = (target_key, blocker["key"])
            if identity in result:
                fail("external blocker keys must be unique within each target slice")
            result[identity] = blocker
    return result


def child_ids(published: dict[str, Any], current: dict[str, Any]) -> dict[str, int]:
    result: dict[str, int] = {}
    for child in current["children"]:
        if child.get("source") == "adopted":
            result[child["key"]] = positive_int(child.get("remote_id"), "adopted child id")
            continue
        operation = published["operations"].get(f"create:{child['key']}")
        if not isinstance(operation, dict) or operation.get("status") != "completed":
            fail("every dependency target requires a reconciled child id")
        result[child["key"]] = positive_int(operation.get("remote_id"), "published child id")
    return result


def owned_provisionals(state: dict[str, Any] | None) -> dict[tuple[str, str], dict[str, Any]]:
    result: dict[tuple[str, str], dict[str, Any]] = {}
    if state is None:
        return result
    for revision in state["revisions"]:
        for change in revision["changes"]:
            if change["action"] != "add" or not change["provisional"]:
                continue
            operation = state["operations"].get(f"r{revision['number']}:{change['key']}")
            if isinstance(operation, dict) and operation.get("status") == "completed":
                result[(change["target_key"], change["dependency_key"])] = {
                    **change,
                    "relation_id": operation["remote_id"],
                }
    for revision in state["revisions"]:
        for change in revision["changes"]:
            if change["action"] == "remove":
                operation = state["operations"].get(f"r{revision['number']}:{change['key']}")
                if isinstance(operation, dict) and operation.get("status") == "completed":
                    result.pop((change["target_key"], change["dependency_key"]), None)
    return result


def active_owned(state: dict[str, Any] | None) -> dict[tuple[str, str], list[dict[str, Any]]]:
    result: dict[tuple[str, str], list[dict[str, Any]]] = {}
    if state is None:
        return result
    for revision in state["revisions"]:
        for change in revision["changes"]:
            operation = state["operations"].get(f"r{revision['number']}:{change['key']}")
            if not isinstance(operation, dict) or operation.get("status") != "completed":
                continue
            identity = (change["target_key"], change["dependency_key"])
            if change["action"] == "add":
                result.setdefault(identity, []).append({**change, "remote_id": operation["remote_id"]})
            else:
                result[identity] = [item for item in result.get(identity, []) if item["remote_id"] != change["relation_id"]]
    return result


def assert_acyclic(relations: list[dict[str, Any]], changes: list[dict[str, Any]]) -> None:
    removed = {change["relation_id"] for change in changes if change["action"] == "remove"}
    edges = {
        (item["issue_id"], item["issue_to_id"])
        for item in relations if item["relation_type"] == "blocks" and item["id"] not in removed
    }
    edges.update((item["source_issue_id"], item["target_issue_id"]) for item in changes if item["action"] == "add")
    if any(source == target for source, target in edges):
        fail("dependency proposal introduces a self-cycle")
    graph: dict[int, set[int]] = {}
    for source, target in edges:
        graph.setdefault(source, set()).add(target)
    visiting: set[int] = set()
    visited: set[int] = set()

    def visit(node: int) -> None:
        if node in visiting:
            fail("dependency proposal creates a cycle in the relevant graph")
        if node in visited:
            return
        visiting.add(node)
        for target in graph.get(node, set()):
            visit(target)
        visiting.remove(node)
        visited.add(node)

    for node in graph:
        visit(node)


def proposal_digest(revision: dict[str, Any]) -> str:
    return digest({
        key: revision[key]
        for key in (
            "slices_state_sha256", "slicing_revision", "slicing_approval_sha256",
            "publication_sha256", "publication_readback_sha256", "graph_snapshot",
            "changes", "coverage",
        )
    })


def validate_state(state: dict[str, Any], previous: dict[str, Any] | None = None) -> None:
    exact(state, {"schema_version", "status", "status_history", "revisions", "approvals", "operations", "completion_history", "readback", "completed_at"}, "dependency state")
    if state["schema_version"] != 1 or state["status"] not in {"prepared", "approved", "applying", "completed"}:
        fail("unsupported dependency state")
    if not isinstance(state["revisions"], list) or not state["revisions"]:
        fail("dependency state requires revision history")
    revision_fields = {
        "number", "recorded_by", "recorded_at", "reason", "slices_state_path", "slices_state_sha256",
        "slicing_revision", "slicing_approval_sha256", "publication_state_path", "publication_sha256",
        "publication_readback_sha256", "graph_snapshot", "changes", "coverage", "proposal_sha256",
    }
    for number, revision in enumerate(state["revisions"], start=1):
        exact(revision, revision_fields, f"dependency revision {number}")
        if revision["number"] != number or revision["proposal_sha256"] != proposal_digest(revision):
            fail("dependency revision identity or hash differs")
        require_text(revision["recorded_by"], "dependency revision recorded_by")
        require_timestamp(revision["recorded_at"], "dependency revision recorded_at")
        require_text(revision["reason"], "dependency revision reason")
        if not isinstance(revision["changes"], list) or not revision["changes"]:
            fail("dependency revision requires at least one change")
        if not isinstance(revision["coverage"], list) or not revision["coverage"]:
            fail("dependency revision requires complete external blocker coverage")
        keys: set[str] = set()
        for change in revision["changes"]:
            exact(change, {"key", "action", "dependency_key", "source_issue_id", "target_key", "target_issue_id", "relation_id", "provisional", "capability", "blocking_reason"}, "dependency change")
            key = require_text(change["key"], "dependency change key")
            if key in keys or change["action"] not in {"add", "remove"}:
                fail("dependency change keys and actions are invalid")
            keys.add(key)
            positive_int(change["source_issue_id"], "dependency source_issue_id")
            positive_int(change["target_issue_id"], "dependency target_issue_id")
            require_text(change["dependency_key"], "dependency_key")
            require_text(change["target_key"], "target_key")
            require_text(change["capability"], "capability")
            require_text(change["blocking_reason"], "blocking_reason")
            if not isinstance(change["provisional"], bool):
                fail("dependency provisional flag must be boolean")
            if change["action"] == "add" and change["relation_id"] is not None:
                fail("a relation add cannot have a prior relation id")
            if change["action"] == "remove":
                positive_int(change["relation_id"], "removed relation_id")
                if not change["provisional"]:
                    fail("only an exact provisional project-slices relation may be removed")
    current = state["revisions"][-1]
    for approval in state["approvals"]:
        exact(approval, {"revision", "proposal_sha256", "approved_by", "approved_at", "status"}, "dependency approval")
        if approval["revision"] < 1 or approval["revision"] > len(state["revisions"]) or approval["proposal_sha256"] != state["revisions"][approval["revision"] - 1]["proposal_sha256"] or approval["status"] not in {"valid", "invalidated"}:
            fail("dependency approval differs from its revision")
        require_text(approval["approved_by"], "dependency approved_by")
        require_timestamp(approval["approved_at"], "dependency approved_at")
    valid = [item for item in state["approvals"] if item["status"] == "valid"]
    if state["status"] == "prepared" and valid:
        fail("prepared dependencies cannot retain an approval")
    if state["status"] != "prepared" and (len(valid) != 1 or valid[0]["revision"] != current["number"] or valid[0]["proposal_sha256"] != current["proposal_sha256"]):
        fail("dependency mutations require approval of the current proposal")
    expected_operations = {
        f"r{revision['number']}:{change['key']}"
        for revision in state["revisions"] for change in revision["changes"]
    }
    if not isinstance(state["operations"], dict) or not set(state["operations"]).issubset(expected_operations):
        fail("dependency operations contain an unknown change")
    for operation in state["operations"].values():
        exact(operation, {"kind", "attempts", "observations", "status", "remote_id"}, "dependency operation")
        if operation["kind"] not in {"add", "remove"} or operation["status"] not in {"pending", "completed"}:
            fail("dependency operation is invalid")
    if state["status"] == "completed" and (not isinstance(state["readback"], dict) or state["completed_at"] is None):
        fail("completed dependencies require readback evidence")
    if not isinstance(state["completion_history"], list):
        fail("dependency completion history must be an array")
    for completion in state["completion_history"]:
        exact(completion, {"revision", "proposal_sha256", "readback", "completed_at"}, "dependency completion")
        if completion["revision"] < 1 or completion["revision"] > len(state["revisions"]) or completion["proposal_sha256"] != state["revisions"][completion["revision"] - 1]["proposal_sha256"]:
            fail("dependency completion differs from its revision")
        require_timestamp(completion["completed_at"], "dependency completion completed_at")
    reject_secrets(state, "dependency state")
    if previous is not None:
        validate_state(previous)
        for field in ("revisions", "status_history", "completion_history"):
            if state[field][:len(previous[field])] != previous[field]:
                fail(f"dependency {field} history was rewritten")
        if len(state["approvals"]) < len(previous["approvals"]):
            fail("dependency approval history was removed")
        for index, old in enumerate(previous["approvals"]):
            new = state["approvals"][index]
            if new != old and not (old["status"] == "valid" and new == {**old, "status": "invalidated"}):
                fail("dependency approval history was rewritten")
        for key, old in previous["operations"].items():
            if key not in state["operations"] or state["operations"][key]["observations"][:len(old["observations"])] != old["observations"]:
                fail("dependency operation history was rewritten")
            new = state["operations"][key]
            if len(new["attempts"]) < len(old["attempts"]):
                fail("dependency attempt history was removed")
            for index, old_attempt in enumerate(old["attempts"]):
                new_attempt = new["attempts"][index]
                if new_attempt != old_attempt:
                    stable = {field: old_attempt[field] for field in ("id", "attempted_at", "payload_sha256", "observations_before")}
                    if old_attempt["outcome"] != "in-flight" or any(new_attempt.get(field) != value for field, value in stable.items()) or new_attempt.get("outcome") not in {"completed", "failed", "unknown"}:
                        fail("dependency attempt history was rewritten")
            if old["status"] == "completed" and new != old:
                fail("completed dependency operation was rewritten")


def validate_current_sources(current: dict[str, Any]) -> None:
    slices_path = Path(current["slices_state_path"])
    publication_path = Path(current["publication_state_path"])
    slicing_revision, published, publication_revision = approved_sources(slices_path, publication_path)
    slicing_approval = next(item for item in load_json(slices_path)["approvals"] if item["status"] == "valid")
    if current["slices_state_sha256"] != file_digest(slices_path) or current["slicing_revision"] != slicing_revision["number"] or current["slicing_approval_sha256"] != digest(slicing_approval):
        fail("approved slicing evidence changed after dependency preview")
    if current["publication_sha256"] != publication_revision["publication_sha256"] or current["publication_readback_sha256"] != published["readback"]["sha256"]:
        fail("verified child publication changed after dependency preview")
    graph_path = Path(current["graph_snapshot"]["path"])
    if file_digest(graph_path) != current["graph_snapshot"]["sha256"]:
        fail("relevant graph evidence changed after dependency preview")


def completion_evidence(state: dict[str, Any]) -> str:
    validate_state(state)
    if state["status"] != "completed":
        fail("dependency routing is not completed")
    current = state["revisions"][-1]
    validate_current_sources(current)
    for change in current["changes"]:
        if state["operations"].get(f"r{current['number']}:{change['key']}", {}).get("status") != "completed":
            fail("completed dependency routing has an unreconciled operation")
    feature_dir = Path(current["slices_state_path"]).parent.parent
    readback_path, readback = graph_snapshot(feature_dir, state["readback"]["path"])
    if file_digest(readback_path) != state["readback"]["sha256"]:
        fail("dependency completion readback is missing or changed")
    baseline = load_json(Path(current["graph_snapshot"]["path"]))
    if readback["project_id"] != baseline["project_id"]:
        fail("dependency completion readback belongs to another project")
    removed = {item["relation_id"] for item in current["changes"] if item["action"] == "remove"}
    by_id = {item["id"]: item for item in readback["relations"]}
    if any(relation["id"] not in removed and by_id.get(relation["id"]) != relation for relation in baseline["relations"]):
        fail("dependency completion readback changed an unrelated relation")
    for change in current["changes"]:
        present = relation_match(readback, change)
        if (change["action"] == "add" and not present) or (change["action"] == "remove" and present):
            fail("dependency completion readback differs from the approved delta")
    for coverage in current["coverage"]:
        for source in coverage["sources"]:
            if not any(
                relation["relation_type"] == "blocks"
                and relation["issue_id"] == source
                and relation["issue_to_id"] == coverage["target_issue_id"]
                for relation in readback["relations"]
            ):
                fail("dependency completion readback is missing covered external blockers")
    assert_acyclic(readback["relations"], [])
    return digest({
        "proposal_sha256": current["proposal_sha256"],
        "readback_sha256": state["readback"]["sha256"],
        "operations": {key: value.get("remote_id") for key, value in sorted(state["operations"].items())},
    })


def command_prepare(arguments: argparse.Namespace) -> None:
    state_path = Path(arguments.state).absolute()
    slices_path = Path(arguments.slices_state).absolute()
    publication_path = Path(arguments.publication_state).absolute()
    feature_dir = slices_path.parent.parent
    if state_path != (feature_dir / ".flow" / "slices-dependencies.json").absolute():
        fail("dependency state must use .flow/slices-dependencies.json")
    if publication_path != (feature_dir / ".flow" / "slices-publication.json").absolute():
        fail("dependency routing must use the canonical child publication state")
    slicing_revision, published, publication_revision = approved_sources(slices_path, publication_path)
    blockers = external_blockers(slicing_revision)
    children = child_ids(published, publication_revision)
    plan = load_json(Path(arguments.plan))
    exact(plan, {"graph_snapshot", "changes"}, "dependency plan")
    graph_path, graph = graph_snapshot(feature_dir, plan["graph_snapshot"])
    if graph["project_id"] != publication_revision["native_fields"]["project_id"]:
        fail("dependency graph belongs to another project")
    existing = load_json(state_path) if state_path.exists() else None
    if existing is not None:
        validate_state(existing)
        current_number = existing["revisions"][-1]["number"]
        current_operations = [key for key in existing["operations"] if key.startswith(f"r{current_number}:")]
        if existing["status"] not in {"prepared", "approved", "completed"} or (existing["status"] in {"prepared", "approved"} and current_operations):
            fail("finish or reconcile the current dependency mutation before preparing another")
    owned = owned_provisionals(existing)
    issue_by_id = {item["id"]: item for item in graph["issues"]}
    graph_relations = {item["id"]: item for item in graph["relations"]}
    changes: list[dict[str, Any]] = []
    for index, candidate in enumerate(plan["changes"] if isinstance(plan["changes"], list) else []):
        candidate = exact(candidate, {"key", "action", "dependency_key", "source_issue_id", "target_key", "relation_id"}, f"plan change {index}")
        target_key = require_text(candidate["target_key"], f"plan change {index}.target_key")
        dependency_key = require_text(candidate["dependency_key"], f"plan change {index}.dependency_key")
        descriptor = blockers.get((target_key, dependency_key))
        if descriptor is None or target_key not in children:
            fail("dependency change is not declared by the approved target slice")
        source_id = positive_int(candidate["source_issue_id"], "source_issue_id")
        action = candidate["action"]
        if action not in {"add", "remove"}:
            fail("dependency change action must be add or remove")
        provisional = source_id == descriptor["feature_issue_id"]
        if children[target_key] not in issue_by_id or descriptor["feature_issue_id"] not in issue_by_id:
            fail("complete graph evidence must include the target child and external Feature")
        if action == "add":
            if candidate["relation_id"] is not None:
                fail("relation add cannot provide relation_id")
            if provisional:
                if descriptor["source_slice_issue_id"] is not None:
                    fail("a specific approved slice cannot be replaced by a provisional Feature blocker")
                if any(issue["parent_issue_id"] == descriptor["feature_issue_id"] for issue in graph["issues"]):
                    fail("a provisional blocker is allowed only when no external Feature slices are available")
            else:
                issue = issue_by_id.get(source_id)
                if issue is None or issue["parent_issue_id"] != descriptor["feature_issue_id"]:
                    fail("specific blocker must be a graph-observed child of the approved external Feature")
                if descriptor["source_slice_issue_id"] is not None and source_id != descriptor["source_slice_issue_id"]:
                    fail("specific blocker differs from the approved external slice")
        else:
            relation_id = positive_int(candidate["relation_id"], "relation_id")
            controlled = owned.get((target_key, dependency_key))
            remote = graph_relations.get(relation_id)
            if controlled is None or controlled["relation_id"] != relation_id or controlled["source_issue_id"] != source_id:
                fail("only the exact completed provisional project-slices relation may be removed")
            if remote != {"id": relation_id, "issue_id": source_id, "issue_to_id": children[target_key], "relation_type": "blocks"}:
                fail("provisional removal does not match current graph evidence")
            provisional = True
        changes.append({
            "key": require_text(candidate["key"], "change key"), "action": action,
            "dependency_key": dependency_key, "source_issue_id": source_id,
            "target_key": target_key, "target_issue_id": children[target_key],
            "relation_id": candidate["relation_id"], "provisional": provisional,
            "capability": descriptor["capability"], "blocking_reason": descriptor["blocking_reason"],
        })
    if not changes:
        fail("dependency plan requires at least one change")
    pairs = [(item["source_issue_id"], item["target_issue_id"]) for item in changes if item["action"] == "add"]
    if len(pairs) != len(set(pairs)) or any(
        item["relation_type"] == "blocks" and (item["issue_id"], item["issue_to_id"]) in pairs
        for item in graph["relations"]
    ):
        fail("dependency proposal duplicates an existing or proposed blocking relation")
    for removal in (item for item in changes if item["action"] == "remove"):
        if not any(item["action"] == "add" and item["dependency_key"] == removal["dependency_key"] and item["target_key"] == removal["target_key"] and not item["provisional"] for item in changes):
            fail("provisional removal requires a specific replacement in the same proposal")
    assert_acyclic(graph["relations"], changes)
    effective = active_owned(existing)
    removal_ids = {item["relation_id"] for item in changes if item["action"] == "remove"}
    graph_by_id = {item["id"]: item for item in graph["relations"]}
    for values in effective.values():
        for active in values:
            if active["remote_id"] not in removal_ids and graph_by_id.get(active["remote_id"]) != {
                "id": active["remote_id"], "issue_id": active["source_issue_id"],
                "issue_to_id": active["target_issue_id"], "relation_type": "blocks",
            }:
                fail("current graph is missing a previously completed project-slices blocker")
    for change in changes:
        identity = (change["target_key"], change["dependency_key"])
        if change["action"] == "add":
            effective.setdefault(identity, []).append(change)
        else:
            effective[identity] = [item for item in effective.get(identity, []) if item.get("remote_id") != change["relation_id"]]
    if set(effective) != set(blockers) or any(not values for values in effective.values()):
        fail("dependency proposal must cover every approved external blocker")
    coverage = [
        {
            "target_key": target_key,
            "target_issue_id": children[target_key],
            "dependency_key": dependency_key,
            "sources": sorted({item["source_issue_id"] for item in effective[(target_key, dependency_key)]}),
            "mode": "provisional" if all(item["provisional"] for item in effective[(target_key, dependency_key)]) else "specific",
        }
        for target_key, dependency_key in sorted(blockers)
    ]
    slicing_state = load_json(slices_path)
    slicing_approval = next(item for item in slicing_state["approvals"] if item["status"] == "valid")
    number = len(existing["revisions"]) + 1 if existing else 1
    revision = {
        "number": number, "recorded_by": require_text(arguments.actor, "recorded_by"),
        "recorded_at": require_timestamp(arguments.at, "recorded_at"), "reason": require_text(arguments.reason, "reason"),
        "slices_state_path": str(slices_path), "slices_state_sha256": file_digest(slices_path),
        "slicing_revision": slicing_revision["number"], "slicing_approval_sha256": digest(slicing_approval),
        "publication_state_path": str(publication_path), "publication_sha256": publication_revision["publication_sha256"],
        "publication_readback_sha256": published["readback"]["sha256"],
        "graph_snapshot": {"path": str(graph_path), "sha256": file_digest(graph_path)}, "changes": changes, "coverage": coverage,
    }
    revision["proposal_sha256"] = proposal_digest(revision)
    if existing:
        state = copy.deepcopy(existing)
        for approval in state["approvals"]:
            if approval["status"] == "valid":
                approval["status"] = "invalidated"
        state["revisions"].append(revision)
        state["status"] = "prepared"
        state["status_history"].append({"status": "prepared", "recorded_at": revision["recorded_at"]})
        state["readback"] = None
        state["completed_at"] = None
    else:
        state = {"schema_version": 1, "status": "prepared", "status_history": [{"status": "prepared", "recorded_at": revision["recorded_at"]}], "revisions": [revision], "approvals": [], "operations": {}, "completion_history": [], "readback": None, "completed_at": None}
    validate_state(state)
    atomic_write(state_path, canonical_bytes(state) + b"\n")
    print(json.dumps({"status": "prepared", "revision": number, "proposal_sha256": revision["proposal_sha256"], "changes": changes}, ensure_ascii=False))


def command_approve(arguments: argparse.Namespace) -> None:
    path = Path(arguments.state)
    state = load_json(path)
    validate_state(state)
    if state["status"] != "prepared":
        fail("only the current prepared dependency proposal can be approved")
    current = state["revisions"][-1]
    validate_current_sources(current)
    at = require_timestamp(arguments.at, "approved_at")
    state["approvals"].append({"revision": current["number"], "proposal_sha256": current["proposal_sha256"], "approved_by": require_text(arguments.actor, "approved_by"), "approved_at": at, "status": "valid"})
    state["status"] = "approved"
    state["status_history"].append({"status": "approved", "recorded_at": at})
    validate_state(state)
    atomic_write(path, canonical_bytes(state) + b"\n")
    print(json.dumps({"status": "approved", "proposal_sha256": current["proposal_sha256"]}))


def current_change(state: dict[str, Any], key: str) -> tuple[dict[str, Any], str]:
    current = state["revisions"][-1]
    matches = [item for item in current["changes"] if item["key"] == key]
    if len(matches) != 1:
        fail("unknown current dependency change key")
    return matches[0], f"r{current['number']}:{key}"


def operation(state: dict[str, Any], key: str, kind: str) -> dict[str, Any]:
    value = state["operations"].setdefault(key, {"kind": kind, "attempts": [], "observations": [], "status": "pending", "remote_id": None})
    if value["kind"] != kind:
        fail("dependency operation kind differs")
    return value


def check_retry(value: dict[str, Any], kind: str) -> None:
    if value["status"] == "completed":
        fail("completed dependency operation must not be repeated")
    if value["attempts"] and value["attempts"][-1]["outcome"] in {"in-flight", "unknown"}:
        later = value["observations"][value["attempts"][-1]["observations_before"]:]
        retry_outcome = "absent" if kind == "add" else "matched"
        if not later or later[-1]["outcome"] != retry_outcome:
            fail("ambiguous dependency operation requires readback before retry")


def command_begin(arguments: argparse.Namespace) -> None:
    path = Path(arguments.state)
    state = load_json(path)
    validate_state(state)
    if state["status"] not in {"approved", "applying"}:
        fail("dependency mutation requires current tech-lead approval")
    current = state["revisions"][-1]
    validate_current_sources(current)
    change, operation_key = current_change(state, arguments.key)
    if change["action"] == "remove":
        pending_adds = [
            item for item in current["changes"] if item["action"] == "add"
            and state["operations"].get(f"r{current['number']}:{item['key']}", {}).get("status") != "completed"
        ]
        if pending_adds:
            fail("specific replacement relations must complete before provisional removal")
    value = operation(state, operation_key, change["action"])
    check_retry(value, change["action"])
    payload = ({"issue_id": change["source_issue_id"], "issue_to_id": change["target_issue_id"], "relation_type": "blocks"} if change["action"] == "add" else {"relation_id": change["relation_id"]})
    attempted_at = require_timestamp(arguments.at, "attempted_at")
    attempt = len(value["attempts"]) + 1
    value["attempts"].append({"id": attempt, "attempted_at": attempted_at, "payload_sha256": digest(payload), "outcome": "in-flight", "observations_before": len(value["observations"])})
    state["status"] = "applying"
    state["status_history"].append({"status": "applying", "recorded_at": attempted_at})
    atomic_write(path, canonical_bytes(state) + b"\n")
    print(json.dumps({"attempt_id": attempt, "tool": "redmine_create_relation" if change["action"] == "add" else "redmine_delete_relation", **payload}))


def command_finish(arguments: argparse.Namespace) -> None:
    path = Path(arguments.state)
    state = load_json(path)
    validate_state(state)
    change, operation_key = current_change(state, arguments.key)
    value = operation(state, operation_key, change["action"])
    if not value["attempts"] or value["attempts"][-1]["id"] != arguments.attempt or value["attempts"][-1]["outcome"] != "in-flight":
        fail("dependency result must finish the current in-flight attempt")
    entry = value["attempts"][-1]
    entry["outcome"] = arguments.outcome
    entry["response_recorded_at"] = require_timestamp(arguments.at, "response_recorded_at")
    if arguments.outcome == "completed":
        if change["action"] == "add":
            value["remote_id"] = positive_int(arguments.relation_id, "relation_id")
        elif arguments.relation_id is not None:
            fail("completed removal does not accept another relation id")
        value["status"] = "completed"
    elif arguments.relation_id is not None:
        fail("only a completed add may record relation_id")
    if arguments.outcome == "failed":
        entry["error_code"] = require_text(arguments.error_code, "error_code")
        entry["message"] = require_text(arguments.message, "message")
    validate_state(state)
    atomic_write(path, canonical_bytes(state) + b"\n")


def relation_match(graph: dict[str, Any], change: dict[str, Any]) -> bool:
    return any(
        item["id"] == change["relation_id"] and item["issue_id"] == change["source_issue_id"] and item["issue_to_id"] == change["target_issue_id"] and item["relation_type"] == "blocks"
        if change["action"] == "remove" else
        item["issue_id"] == change["source_issue_id"] and item["issue_to_id"] == change["target_issue_id"] and item["relation_type"] == "blocks"
        for item in graph["relations"]
    )


def command_observe(arguments: argparse.Namespace) -> None:
    path = Path(arguments.state)
    state = load_json(path)
    validate_state(state)
    change, operation_key = current_change(state, arguments.key)
    value = operation(state, operation_key, change["action"])
    if not value["attempts"] or value["attempts"][-1]["outcome"] not in {"in-flight", "unknown"} or value["status"] == "completed":
        fail("dependency reconciliation requires a pending ambiguous attempt")
    feature_dir = Path(state["revisions"][-1]["slices_state_path"]).parent.parent
    snapshot_path, graph = graph_snapshot(feature_dir, arguments.snapshot)
    current = state["revisions"][-1]
    if graph["project_id"] != load_json(Path(current["graph_snapshot"]["path"]))["project_id"]:
        fail("dependency reconciliation graph belongs to another project")
    issue_ids = {item["id"] for item in graph["issues"]}
    if change["source_issue_id"] not in issue_ids or change["target_issue_id"] not in issue_ids:
        fail("dependency reconciliation graph omits the operation endpoints")
    present = relation_match(graph, change)
    if (arguments.outcome == "matched") != present:
        fail("dependency observation outcome differs from readback")
    if (change["action"] == "add" and present) or (change["action"] == "remove" and not present):
        value["status"] = "completed"
        if change["action"] == "add":
            matches = [item for item in graph["relations"] if item["relation_type"] == "blocks" and item["issue_id"] == change["source_issue_id"] and item["issue_to_id"] == change["target_issue_id"]]
            value["remote_id"] = matches[0]["id"]
    value["observations"].append({"observed_at": require_timestamp(arguments.at, "observed_at"), "outcome": arguments.outcome, "snapshot_path": str(snapshot_path), "snapshot_sha256": file_digest(snapshot_path)})
    atomic_write(path, canonical_bytes(state) + b"\n")


def command_complete(arguments: argparse.Namespace) -> None:
    path = Path(arguments.state)
    state = load_json(path)
    validate_state(state)
    current = state["revisions"][-1]
    validate_current_sources(current)
    for change in current["changes"]:
        if state["operations"].get(f"r{current['number']}:{change['key']}", {}).get("status") != "completed":
            fail("every approved dependency change must be reconciled before completion")
    feature_dir = Path(current["slices_state_path"]).parent.parent
    readback_path, readback = graph_snapshot(feature_dir, arguments.readback)
    baseline = load_json(Path(current["graph_snapshot"]["path"]))
    if readback["project_id"] != baseline["project_id"]:
        fail("dependency readback belongs to another project")
    assert_acyclic(readback["relations"], [])
    removed = {item["relation_id"] for item in current["changes"] if item["action"] == "remove"}
    by_id = {item["id"]: item for item in readback["relations"]}
    for relation in baseline["relations"]:
        if relation["id"] not in removed and by_id.get(relation["id"]) != relation:
            fail("dependency readback changed or removed an unrelated native relation")
    for change in current["changes"]:
        present = relation_match(readback, change)
        if change["action"] == "add" and not present:
            fail("dependency readback is missing an approved specific or provisional relation")
        if change["action"] == "remove" and present:
            fail("dependency readback still contains the exact removed provisional relation")
    for coverage in current["coverage"]:
        for source in coverage["sources"]:
            if not any(
                relation["relation_type"] == "blocks"
                and relation["issue_id"] == source
                and relation["issue_to_id"] == coverage["target_issue_id"]
                for relation in readback["relations"]
            ):
                fail("dependency readback is missing covered external blockers")
    completed_at = require_timestamp(arguments.at, "completed_at")
    state["readback"] = {"path": str(readback_path), "sha256": file_digest(readback_path), "observed_at": completed_at}
    state["completed_at"] = completed_at
    state["status"] = "completed"
    state["status_history"].append({"status": "completed", "recorded_at": completed_at})
    state["completion_history"].append({"revision": current["number"], "proposal_sha256": current["proposal_sha256"], "readback": copy.deepcopy(state["readback"]), "completed_at": completed_at})
    validate_state(state)
    atomic_write(path, canonical_bytes(state) + b"\n")
    print(json.dumps({"status": "completed", "revision": current["number"]}))


def command_validate(arguments: argparse.Namespace) -> None:
    state = load_json(Path(arguments.state))
    previous = load_json(Path(arguments.previous)) if arguments.previous else None
    validate_state(state, previous)
    print("valid")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(required=True)
    prepare = commands.add_parser("prepare")
    prepare.add_argument("state"); prepare.add_argument("plan"); prepare.add_argument("--slices-state", required=True); prepare.add_argument("--publication-state", required=True)
    prepare.add_argument("--actor", required=True); prepare.add_argument("--at", required=True); prepare.add_argument("--reason", required=True); prepare.set_defaults(run=command_prepare)
    approve = commands.add_parser("approve")
    approve.add_argument("state"); approve.add_argument("--actor", required=True); approve.add_argument("--at", required=True); approve.set_defaults(run=command_approve)
    begin = commands.add_parser("begin")
    begin.add_argument("state"); begin.add_argument("--key", required=True); begin.add_argument("--at", required=True); begin.set_defaults(run=command_begin)
    finish = commands.add_parser("finish")
    finish.add_argument("state"); finish.add_argument("--key", required=True); finish.add_argument("--attempt", type=int, required=True); finish.add_argument("--outcome", choices=("completed", "failed", "unknown"), required=True)
    finish.add_argument("--relation-id", type=int); finish.add_argument("--error-code"); finish.add_argument("--message"); finish.add_argument("--at", required=True); finish.set_defaults(run=command_finish)
    observe = commands.add_parser("observe")
    observe.add_argument("state"); observe.add_argument("--key", required=True); observe.add_argument("--outcome", choices=("matched", "absent"), required=True); observe.add_argument("--snapshot", required=True); observe.add_argument("--at", required=True); observe.set_defaults(run=command_observe)
    complete = commands.add_parser("complete")
    complete.add_argument("state"); complete.add_argument("--readback", required=True); complete.add_argument("--at", required=True); complete.set_defaults(run=command_complete)
    validate = commands.add_parser("validate")
    validate.add_argument("state"); validate.add_argument("--previous"); validate.set_defaults(run=command_validate)
    return parser


def main() -> int:
    try:
        arguments = build_parser().parse_args()
        arguments.run(arguments)
        return 0
    except (ContractError, OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as error:
        print(f"invalid: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
