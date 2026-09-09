#!/usr/bin/env python3
"""Validate new-scope state and append-only transitions without network access."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from validate_state import validate_source


PHASES_V1 = ("mode-confirmed", "inputs-normalized", "repository-analyzed", "catalog-proposed", "catalog-approved", "first-item-started", "first-item-completed")
PHASES_V2 = ("mode-confirmed", "inputs-normalized", "repository-analyzed", "catalog-proposed", "catalog-approved", "items-processing", "relations-reconciled", "scope-approved", "completed")


def fail(message: str) -> None:
    raise ValueError(message)


def text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        fail(f"{label} must be non-empty text")
    return value


def timestamp(value: object, label: str) -> None:
    parsed = datetime.fromisoformat(text(value, label).replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        fail(f"{label} must include a timezone")


def require_keys(value: dict[str, Any], required: set[str], label: str) -> None:
    missing = required - value.keys()
    if missing:
        fail(f"{label} missing: {', '.join(sorted(missing))}")


def phase_position(state: dict[str, Any], phases: tuple[str, ...]) -> tuple[list[str], str]:
    completed = state["completed_phases"]
    if not isinstance(completed, list) or completed != list(phases[:len(completed)]):
        fail("completed_phases must be a contiguous ordered prefix")
    expected = phases[len(completed)] if len(completed) < len(phases) else phases[-1]
    if state["phase"] != "paused" and state["phase"] != expected:
        fail(f"phase must be the first incomplete phase: {expected}")
    return completed, expected


def validate_catalog(state: dict[str, Any], version: int) -> dict[str, dict[str, Any]]:
    catalog = state["catalog"]
    if not isinstance(catalog, list) or not catalog:
        fail("catalog must contain every classified candidate")
    base = {"id", "type", "name", "human_objective", "actors", "observable_result_or_deviation", "evidence", "dependencies", "separation_reason", "suggested_position", "status"}
    required = base | ({"candidate_ids", "lifecycle"} if version == 2 else set())
    items: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(catalog):
        if not isinstance(item, dict):
            fail(f"catalog[{index}] must be an object")
        require_keys(item, required, f"catalog[{index}]")
        if item.keys() != required:
            fail(f"catalog[{index}] has unknown keys")
        item_id = text(item["id"], f"catalog[{index}].id")
        if item_id in items:
            fail(f"duplicate catalog item id: {item_id}")
        if item["type"] not in {"Feature", "Bug"}:
            fail(f"catalog[{index}].type must be Feature or Bug")
        for field in ("name", "human_objective", "observable_result_or_deviation", "separation_reason"):
            text(item[field], f"catalog[{index}].{field}")
        for field in ("actors", "evidence", "dependencies"):
            values = item[field]
            if not isinstance(values, list) or (field != "dependencies" and not values) or len(values) != len(set(values)):
                fail(f"catalog[{index}].{field} is invalid")
            for value in values:
                text(value, f"catalog[{index}].{field}")
        if version == 1 and item["status"] not in {"catalogued", "first-item-started", "first-item-completed"}:
            fail(f"catalog[{index}].status is invalid")
        if version == 2:
            if item["status"] not in {"pending", "in-progress", "blocked", "completed", "retired"}:
                fail(f"catalog[{index}].status is invalid")
            if item["lifecycle"] not in {"active", "retired"} or (item["status"] == "retired") != (item["lifecycle"] == "retired"):
                fail(f"catalog[{index}] lifecycle and status disagree")
            candidates = item["candidate_ids"]
            if not isinstance(candidates, list) or not candidates or len(candidates) != len(set(candidates)):
                fail(f"catalog[{index}].candidate_ids is invalid")
        items[item_id] = item

    active = {item_id: item for item_id, item in items.items() if version == 1 or item["lifecycle"] == "active"}
    order = state["suggested_order"]
    if not isinstance(order, list) or len(order) != len(active) or set(order) != set(active):
        fail("suggested_order must contain every active catalog item exactly once")
    for position, item_id in enumerate(order, 1):
        if active[item_id]["suggested_position"] != position:
            fail("suggested_position must match suggested_order")

    expected_edges = {(item_id, dependency) for item_id, item in active.items() for dependency in item["dependencies"]}
    for item_id, dependency in expected_edges:
        if dependency not in active or dependency == item_id:
            fail(f"invalid active catalog dependency: {item_id} -> {dependency}")
    graph = state["dependency_graph"]
    if not isinstance(graph, list):
        fail("dependency_graph must be an array")
    actual_edges: set[tuple[str, str]] = set()
    for index, edge in enumerate(graph):
        if not isinstance(edge, dict) or edge.keys() != {"item", "blocked_by"}:
            fail(f"dependency_graph[{index}] is invalid")
        pair = (text(edge["item"], "edge.item"), text(edge["blocked_by"], "edge.blocked_by"))
        if pair in actual_edges:
            fail("dependency_graph contains a duplicate edge")
        actual_edges.add(pair)
    if actual_edges != expected_edges:
        fail("dependency_graph must exactly match direct active catalog dependencies")
    positions = {item_id: index for index, item_id in enumerate(order)}
    for item_id, dependency in actual_edges:
        if positions[dependency] >= positions[item_id]:
            fail("suggested_order is not topological")

    def reachable(start: str, target: str, skipped: tuple[str, str]) -> bool:
        frontier, visited = [start], set()
        while frontier:
            node = frontier.pop()
            if node == target:
                return True
            if node in visited:
                continue
            visited.add(node)
            frontier.extend(dep for item, dep in actual_edges if item == node and (item, dep) != skipped)
        return False

    for edge in actual_edges:
        if reachable(edge[0], edge[1], edge):
            fail(f"dependency_graph contains a redundant transitive edge: {edge[0]} -> {edge[1]}")
    remaining, done, groups = set(active), set(), []
    while remaining:
        ready = [item_id for item_id in order if item_id in remaining and set(active[item_id]["dependencies"]) <= done]
        if not ready:
            fail("dependency_graph contains a cycle")
        groups.append(ready)
        done.update(ready)
        remaining.difference_update(ready)
    if state.get("parallel_ready_groups") != groups:
        fail("parallel_ready_groups must expose independent items without false blockers")
    return items


def validate_common(state: dict[str, Any], path: Path) -> None:
    uuid.UUID(text(state["run_id"], "run_id"))
    uuid.UUID(text(state["internal_identity"], "internal_identity"))
    identity = state["identity"]
    if not isinstance(identity, dict):
        fail("identity must be an object")
    text(identity.get("display_name"), "identity.display_name")
    timestamp(identity.get("confirmed_at"), "identity.confirmed_at")
    repository = state["repository"]
    if not isinstance(repository, dict) or set(repository) != {"stack", "vocabulary", "exclusions"}:
        fail("repository is invalid")
    sources = state["sources"]
    if not isinstance(sources, list) or not sources:
        fail("sources must be a non-empty array")
    source_ids = set()
    for index, source in enumerate(sources):
        source_id, _ = validate_source(source, index, path)
        if source_id in source_ids:
            fail(f"duplicate source id: {source_id}")
        source_ids.add(source_id)
    lock = state["lock"]
    item_key = text(lock.get("item_key") if isinstance(lock, dict) else None, "lock.item_key")
    uuid.UUID(text(lock.get("lock_id"), "lock.lock_id"))
    expected = f"docs/harness/.locks/{hashlib.sha256(item_key.encode('utf-8')).hexdigest()}.lock.json"
    if lock.get("path") != expected:
        fail("lock.path does not match item_key")
    timestamp(lock.get("acquired_at"), "lock.acquired_at")


def validate_approvals_and_pauses(state: dict[str, Any]) -> int:
    if not isinstance(state["approvals"], list) or not isinstance(state["pauses"], list):
        fail("approvals and pauses must be arrays")
    ids, valid_catalog = set(), 0
    for index, approval in enumerate(state["approvals"]):
        approval_id = text(approval.get("id") if isinstance(approval, dict) else None, f"approvals[{index}].id")
        if approval_id in ids:
            fail(f"duplicate approval id: {approval_id}")
        ids.add(approval_id)
        if approval.get("kind") not in {"complete-catalog-and-order", "scope-completion"} or approval.get("status") not in {"valid", "invalidated"}:
            fail(f"approvals[{index}] is invalid")
        digest = approval.get("subject_sha256")
        if not isinstance(digest, str) or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            fail(f"approvals[{index}].subject_sha256 is invalid")
        text(approval.get("approved_by"), f"approvals[{index}].approved_by")
        timestamp(approval.get("approved_at"), f"approvals[{index}].approved_at")
        valid_catalog += approval["kind"] == "complete-catalog-and-order" and approval["status"] == "valid"
    open_pauses = 0
    for index, pause in enumerate(state["pauses"]):
        if not isinstance(pause, dict) or pause.get("status") not in {"paused", "resumed"} or pause.get("kind") not in {"catalog-change", "decision-deferred", "third-party-question", "voluntary-stop", "functional-gap"}:
            fail(f"pauses[{index}] is invalid")
        text(pause.get("id"), f"pauses[{index}].id")
        text(pause.get("reason"), f"pauses[{index}].reason")
        text(pause.get("resume_condition"), f"pauses[{index}].resume_condition")
        timestamp(pause.get("paused_at"), f"pauses[{index}].paused_at")
        open_pauses += pause["status"] == "paused"
    if state["phase"] == "paused" and (open_pauses != 1 or state["pauses"][-1]["status"] != "paused"):
        fail("paused phase requires exactly one open latest pause")
    if state["phase"] != "paused" and open_pauses:
        fail("an open pause requires phase paused")
    return valid_catalog


def validate_v1(state: dict[str, Any], path: Path) -> dict[str, Any]:
    required = {"schema_version", "run_id", "internal_identity", "mode", "phase", "completed_phases", "identity", "redmine", "sources", "repository", "catalog", "dependency_graph", "parallel_ready_groups", "suggested_order", "approvals", "pauses", "lock"}
    require_keys(state, required, "state")
    if state.keys() - (required | {"first_item"}):
        fail("state has unknown keys")
    completed, expected = phase_position(state, PHASES_V1)
    validate_common(state, path)
    if "repository-analyzed" in completed and (not state["repository"]["stack"] or not state["repository"]["exclusions"]):
        fail("repository-analyzed requires stack and exclusions")
    if "inputs-normalized" in completed and any(source.get("status") == "unreadable" for source in state["sources"]):
        fail("normalized phases cannot contain unreadable sources")
    valid_catalog = validate_approvals_and_pauses(state)
    items: dict[str, dict[str, Any]] = {}
    if "catalog-proposed" in completed:
        items = validate_catalog(state, 1)
    catalog_change_pause = state["phase"] == "paused" and state["pauses"] and state["pauses"][-1].get("kind") == "catalog-change"
    if ("catalog-approved" in completed or expected in {"first-item-started", "first-item-completed"}) and not catalog_change_pause and valid_catalog != 1:
        fail("catalog-approved requires exactly one valid complete catalog approval")
    if expected in {"first-item-started", "first-item-completed"} or "first-item-started" in completed:
        first = state.get("first_item")
        if not isinstance(first, dict) or first.get("catalog_item_id") != state["suggested_order"][0]:
            fail("first_item must be the first approved item")
        started = [item["id"] for item in state["catalog"] if item["status"] in {"first-item-started", "first-item-completed"}]
        if started != [first["catalog_item_id"]]:
            fail("exactly the first catalog item may be started")
        timestamp(first.get("interview_started_at"), "first_item.interview_started_at")
        if expected == "first-item-completed" or "first-item-completed" in completed:
            if first.get("requirement_phase") != "completed" or items[first["catalog_item_id"]]["status"] != "first-item-completed":
                fail("first-item-completed requires a completed requirement state")
            timestamp(first.get("completed_at"), "first_item.completed_at")
    return state


def validate_v2(state: dict[str, Any], path: Path) -> dict[str, Any]:
    required = {"schema_version", "run_id", "internal_identity", "mode", "phase", "completed_phases", "identity", "redmine", "sources", "source_allocation", "repository", "candidates", "catalog", "dependency_graph", "parallel_ready_groups", "suggested_order", "approvals", "pauses", "lock", "item_progress", "continuation_decisions", "catalog_changes", "relations", "validations", "final_summary"}
    require_keys(state, required, "state")
    if state.keys() != required:
        fail("state has unknown keys")
    completed, expected = phase_position(state, PHASES_V2)
    validate_common(state, path)
    valid_catalog = validate_approvals_and_pauses(state)
    if "repository-analyzed" in completed and (not state["repository"]["stack"] or not state["repository"]["exclusions"]):
        fail("repository-analyzed requires stack and exclusions")
    if "inputs-normalized" in completed and any(source.get("status") == "unreadable" for source in state["sources"]):
        fail("normalized phases cannot contain unreadable sources")
    if "catalog-proposed" not in completed:
        for field in ("candidates", "catalog", "dependency_graph", "parallel_ready_groups", "suggested_order", "item_progress", "continuation_decisions", "catalog_changes", "relations", "validations"):
            if not isinstance(state[field], list):
                fail(f"{field} must be an array")
        return state
    items = validate_catalog(state, 2)

    candidates = state["candidates"]
    if not isinstance(candidates, list) or not candidates:
        fail("candidates must account for every observed delivery candidate")
    candidate_ids, undecided = set(), []
    for index, candidate in enumerate(candidates):
        if not isinstance(candidate, dict) or candidate.keys() != {"id", "status", "catalog_item_ids", "rationale"}:
            fail(f"candidates[{index}] is invalid")
        candidate_id = text(candidate["id"], f"candidates[{index}].id")
        if candidate_id in candidate_ids:
            fail(f"duplicate candidate id: {candidate_id}")
        candidate_ids.add(candidate_id)
        if candidate["status"] not in {"decided", "undecided"}:
            fail(f"candidates[{index}].status is invalid")
        if candidate["status"] == "undecided":
            undecided.append(candidate_id)
        if not isinstance(candidate["catalog_item_ids"], list) or any(item_id not in items for item_id in candidate["catalog_item_ids"]):
            fail(f"candidates[{index}].catalog_item_ids is invalid")
        text(candidate["rationale"], f"candidates[{index}].rationale")
    if {candidate for item in items.values() for candidate in item["candidate_ids"]} != candidate_ids:
        fail("catalog candidate_ids must account for every candidate")
    catalog_change_pause = state["phase"] == "paused" and state["pauses"] and state["pauses"][-1].get("kind") == "catalog-change"
    if ("catalog-approved" in completed or expected in {"items-processing", "relations-reconciled", "scope-approved", "completed"}) and not catalog_change_pause and (valid_catalog != 1 or undecided):
        fail("catalog-approved requires exactly one valid approval and no undecided candidate")

    allocation = state["source_allocation"]
    if not isinstance(allocation, list) or not allocation:
        fail("source_allocation must be a non-empty array")
    allocated_ids, scope_source_ids = set(), {source["id"] for source in state["sources"]}
    for index, entry in enumerate(allocation):
        if not isinstance(entry, dict) or entry.keys() != {"source_id", "ownership", "item_ids", "path"}:
            fail(f"source_allocation[{index}] is invalid")
        source_id = text(entry["source_id"], f"source_allocation[{index}].source_id")
        if source_id in allocated_ids:
            fail(f"source is allocated more than once: {source_id}")
        allocated_ids.add(source_id)
        item_ids = entry["item_ids"]
        if not isinstance(item_ids, list) or not item_ids or any(item_id not in items for item_id in item_ids):
            fail(f"source_allocation[{index}].item_ids is invalid")
        source_path = text(entry["path"], f"source_allocation[{index}].path")
        if entry["ownership"] == "scope-shared":
            if source_id not in scope_source_ids or len(item_ids) < 2 or not source_path.startswith("sources/"):
                fail("shared sources must exist once in the scope and belong to multiple items")
        elif entry["ownership"] == "item-exclusive":
            if source_id in scope_source_ids or len(item_ids) != 1 or "/sources/" not in source_path:
                fail("exclusive sources must exist once under their owning item")
        else:
            fail(f"source_allocation[{index}].ownership is invalid")
    evidence_ids = {source_id for item in items.values() for source_id in item["evidence"]}
    if allocated_ids != evidence_ids:
        fail("source_allocation must cover every catalog evidence source exactly once")
    shared_ids = {entry["source_id"] for entry in allocation if entry["ownership"] == "scope-shared"}
    if scope_source_ids != shared_ids:
        fail("scope sources must contain exactly the shared source allocations")

    progress = state["item_progress"]
    if not isinstance(progress, list):
        fail("item_progress must be an array")
    progress_by_id = {}
    progress_keys = {"catalog_item_id", "status", "issue_id", "artifact_path", "state_path", "requirement_phase", "functional_gaps", "reconciliation_status", "started_at", "completed_at"}
    for index, record in enumerate(progress):
        if not isinstance(record, dict) or record.keys() != progress_keys:
            fail(f"item_progress[{index}] is invalid")
        item_id = record["catalog_item_id"]
        if item_id not in items or item_id in progress_by_id or record["status"] != items[item_id]["status"]:
            fail(f"item_progress[{index}] has unknown, duplicate, or mismatched item")
        gaps = record["functional_gaps"]
        if not isinstance(gaps, list):
            fail(f"item_progress[{index}].functional_gaps is invalid")
        for gap in gaps:
            if not isinstance(gap, dict) or gap.get("status") not in {"open", "resolved"}:
                fail(f"item_progress[{index}] has an invalid functional gap")
            text(gap.get("id"), "functional_gap.id")
            text(gap.get("description"), "functional_gap.description")
        if record["status"] == "completed":
            if record["requirement_phase"] != "completed" or record["reconciliation_status"] != "completed":
                fail("completed item requires completed requirement and reconciliation")
            for key in ("issue_id", "artifact_path", "state_path", "started_at", "completed_at"):
                if record[key] is None:
                    fail(f"completed item requires {key}")
            timestamp(record["started_at"], "item_progress.started_at")
            timestamp(record["completed_at"], "item_progress.completed_at")
        progress_by_id[item_id] = record
    if set(progress_by_id) != set(items):
        fail("item_progress must retain every active or retired catalog item")

    order, incomplete_seen = state["suggested_order"], False
    for position, item_id in enumerate(order):
        record = progress_by_id[item_id]
        if incomplete_seen and record["status"] != "pending":
            fail("only the first incomplete item in approved order may start")
        if record["status"] != "completed":
            incomplete_seen = True
        if any(gap["status"] == "open" for gap in record["functional_gaps"]):
            if any(progress_by_id[later]["status"] != "pending" for later in order[position + 1:]):
                fail("an open functional gap blocks the next item and later flows")

    decisions, decision_by_item = state["continuation_decisions"], {}
    if not isinstance(decisions, list):
        fail("continuation_decisions must be an array")
    for index, decision in enumerate(decisions):
        if not isinstance(decision, dict) or decision.keys() != {"after_item_id", "decision", "decided_by", "decided_at"}:
            fail(f"continuation_decisions[{index}] is invalid")
        item_id = decision["after_item_id"]
        if item_id in decision_by_item or item_id not in progress_by_id or progress_by_id[item_id]["status"] != "completed":
            fail("continuation decision must follow one completed item exactly once")
        if decision["decision"] not in {"continue", "stop", "finish"}:
            fail(f"continuation_decisions[{index}].decision is invalid")
        text(decision["decided_by"], f"continuation_decisions[{index}].decided_by")
        timestamp(decision["decided_at"], f"continuation_decisions[{index}].decided_at")
        decision_by_item[item_id] = decision["decision"]
    for index, item_id in enumerate(order):
        if progress_by_id[item_id]["status"] == "completed" and item_id not in decision_by_item:
            fail("every completed item requires a durable continue, stop, or finish decision")
        if index + 1 < len(order) and progress_by_id[order[index + 1]]["status"] != "pending" and decision_by_item.get(item_id) != "continue":
            fail("starting the next item requires an explicit continue decision")
    if decisions and decisions[-1]["decision"] == "stop" and state["phase"] != "paused":
        fail("a stop decision must preserve progress in a voluntary-stop pause")

    relations, relation_pairs, relation_keys = state["relations"], set(), set()
    if not isinstance(relations, list):
        fail("relations must be an array")
    relation_fields = {"stable_key", "from_item_id", "to_item_id", "relation_type", "from_issue_id", "to_issue_id", "status", "approval_id", "reconciliation_status", "completed_at"}
    for index, relation in enumerate(relations):
        if not isinstance(relation, dict) or relation.keys() != relation_fields:
            fail(f"relations[{index}] is invalid")
        key = text(relation["stable_key"], f"relations[{index}].stable_key")
        if key in relation_keys:
            fail(f"duplicate relation stable key: {key}")
        relation_keys.add(key)
        pair = (relation["from_item_id"], relation["to_item_id"])
        relation_pairs.add(pair)
        if pair[0] not in items or pair[1] not in items or relation["relation_type"] != "blocks":
            fail("relation must use native blocks and reference known items")
        from_issue, to_issue = progress_by_id[pair[0]]["issue_id"], progress_by_id[pair[1]]["issue_id"]
        if from_issue is not None and to_issue is not None:
            if relation["from_issue_id"] != from_issue or relation["to_issue_id"] != to_issue:
                fail("relation issue IDs must match item progress")
            if relation["status"] != "completed" or relation["reconciliation_status"] != "completed":
                fail("a native relation must be published and reconciled when both issue IDs exist")
            text(relation["approval_id"], f"relations[{index}].approval_id")
            timestamp(relation["completed_at"], f"relations[{index}].completed_at")
    if relation_pairs != {(edge["blocked_by"], edge["item"]) for edge in state["dependency_graph"]}:
        fail("relations must exactly project the active dependency graph")

    changes = state["catalog_changes"]
    if not isinstance(changes, list):
        fail("catalog_changes must be an array")
    change_fields = {"id", "kind", "affected_item_ids", "source_allocation_impact", "graph_impact", "order_impact", "preserved_issue_ids", "artifact_paths", "approved_by", "approved_at"}
    for index, change in enumerate(changes):
        if not isinstance(change, dict) or change.keys() != change_fields or change["kind"] not in {"split", "merge", "add", "remove", "retype", "dependency", "reorder"}:
            fail(f"catalog_changes[{index}] is invalid")
        if not isinstance(change["preserved_issue_ids"], list):
            fail("catalog changes must record every preserved existing issue")

    validations = state["validations"]
    if not isinstance(validations, list):
        fail("validations must be an array")
    passed_items = {entry.get("item_id") for entry in validations if isinstance(entry, dict) and entry.get("status") == "passed" and entry.get("kind") == "requirement-state"}
    scope_validation = any(isinstance(entry, dict) and entry.get("status") == "passed" and entry.get("kind") == "scope-state" for entry in validations)
    all_complete = all(progress_by_id[item_id]["status"] == "completed" for item_id in order)
    no_open_gaps = not any(gap["status"] == "open" for record in progress for gap in record["functional_gaps"])
    all_relations = all(relation["status"] == "completed" and relation["reconciliation_status"] == "completed" for relation in relations)
    if expected in {"relations-reconciled", "scope-approved", "completed"} or "items-processing" in completed:
        if not all_complete or not no_open_gaps or undecided or set(order) - passed_items:
            fail("items-processing completes only after every item, gap, candidate, reconciliation, and validation is complete")
    if expected in {"scope-approved", "completed"} or "relations-reconciled" in completed:
        if not all_relations:
            fail("relations-reconciled requires every native relation reconciled")
    if expected == "completed" or "scope-approved" in completed:
        summary = state["final_summary"]
        summary_keys = {"issues", "relations", "artifacts", "approvals", "validations", "next_recommendation"}
        final_approvals = [a for a in state["approvals"] if a["kind"] == "scope-completion" and a["status"] == "valid"]
        if not isinstance(summary, dict) or summary.keys() != summary_keys or not all(summary[key] for key in summary_keys):
            fail("final summary must list issues, relations, artifacts, approvals, validations, and next recommendation")
        if len(final_approvals) != 1 or not scope_validation:
            fail("scope completion requires one final approval and a passed scope validation")
    return state


def validate(path: Path) -> dict[str, Any]:
    state = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(state, dict) or state.get("mode") != "new-scope":
        fail("scope state must be a new-scope object")
    if state.get("schema_version") == 1:
        return validate_v1(state, path)
    if state.get("schema_version") == 2:
        return validate_v2(state, path)
    fail("unsupported scope schema_version")


def validate_transition(previous: dict[str, Any], current: dict[str, Any]) -> None:
    if previous["schema_version"] == 1 and current["schema_version"] == 2:
        first = previous.get("first_item")
        if first and not any(record.get("catalog_item_id") == first["catalog_item_id"] and record.get("issue_id") == first["issue_id"] for record in current["item_progress"]):
            fail("v1 migration must preserve the completed first item and issue")
        return
    if current["schema_version"] != previous["schema_version"]:
        fail("unsupported scope schema migration")
    for key in ("schema_version", "run_id", "internal_identity", "mode", "identity", "redmine"):
        if current[key] != previous[key]:
            fail(f"transition changed immutable field: {key}")
    phases = PHASES_V1 if current["schema_version"] == 1 else PHASES_V2
    old_completed, new_completed = previous["completed_phases"], current["completed_phases"]
    if new_completed not in (old_completed, list(phases[:len(old_completed) + 1])):
        fail("transition skipped, reordered, or reversed completed phases")
    if previous["phase"] == "paused" and new_completed != old_completed:
        fail("cannot complete a phase while paused")
    old_approvals = {entry["id"]: entry for entry in previous["approvals"]}
    new_approvals = {entry["id"]: entry for entry in current["approvals"]}
    for approval_id, old in old_approvals.items():
        if approval_id not in new_approvals:
            fail(f"transition removed approval: {approval_id}")
        new = new_approvals[approval_id]
        if new != old and not (old["status"] == "valid" and new.get("status") == "invalidated"):
            fail(f"transition rewrote approval: {approval_id}")
    old_pauses, new_pauses = previous["pauses"], current["pauses"]
    if previous["phase"] != "paused" and current["phase"] == "paused":
        if len(new_pauses) != len(old_pauses) + 1 or new_pauses[:-1] != old_pauses:
            fail("pause must append exactly one history record")
    elif previous["phase"] == "paused" and current["phase"] != "paused":
        if len(new_pauses) != len(old_pauses) or new_pauses[:-1] != old_pauses[:-1] or new_pauses[-1].get("status") != "resumed":
            fail("resume must resolve only the latest pause")
    elif new_pauses != old_pauses:
        fail("ordinary transition cannot rewrite pause history")
    if current["schema_version"] == 2:
        for collection, key in (("continuation_decisions", "after_item_id"), ("catalog_changes", "id"), ("relations", "stable_key"), ("item_progress", "catalog_item_id")):
            old_ids = {entry[key] for entry in previous[collection]}
            new_ids = {entry[key] for entry in current[collection]}
            if not old_ids <= new_ids:
                fail(f"transition removed {collection} history")
        for collection, key in (("continuation_decisions", "after_item_id"), ("catalog_changes", "id")):
            old_by_id = {entry[key]: entry for entry in previous[collection]}
            new_by_id = {entry[key]: entry for entry in current[collection]}
            if any(new_by_id[entry_id] != entry for entry_id, entry in old_by_id.items()):
                fail(f"transition rewrote {collection} history")
        old_issues = {entry["catalog_item_id"]: entry["issue_id"] for entry in previous["item_progress"] if entry["issue_id"] is not None}
        new_issues = {entry["catalog_item_id"]: entry["issue_id"] for entry in current["item_progress"] if entry["issue_id"] is not None}
        if any(new_issues.get(item_id) != issue_id for item_id, issue_id in old_issues.items()):
            fail("transition removed or rewrote an existing issue")
    catalog_fields = ("catalog", "dependency_graph", "parallel_ready_groups", "suggested_order")
    previous_catalog_approvals = [approval for approval in previous["approvals"] if approval["kind"] == "complete-catalog-and-order"]
    if previous_catalog_approvals and any(current[field] != previous[field] for field in catalog_fields):
        if current["phase"] != "paused" or not current["pauses"] or current["pauses"][-1].get("kind") != "catalog-change":
            fail("catalog changes must pause with their impact recorded")
        if current["schema_version"] == 2 and len(current["catalog_changes"]) != len(previous["catalog_changes"]) + 1:
            fail("catalog changes must append one approved change record")
        old_valid = {approval["id"] for approval in previous_catalog_approvals if approval["status"] == "valid"}
        current_by_id = {approval["id"]: approval for approval in current["approvals"]}
        if any(current_by_id.get(approval_id, {}).get("status") != "invalidated" for approval_id in old_valid):
            fail("catalog changes must invalidate the prior complete approval")
        if current["schema_version"] == 2:
            old_progress = previous["item_progress"]
            old_issue_ids = {entry["issue_id"] for entry in old_progress if entry["issue_id"] is not None}
            old_artifacts = {entry["artifact_path"] for entry in old_progress if entry["artifact_path"] is not None}
            change = current["catalog_changes"][-1]
            if not old_issue_ids <= set(change["preserved_issue_ids"]) or not old_artifacts <= set(change["artifact_paths"]):
                fail("catalog change record must preserve every existing issue and artifact")


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
