#!/usr/bin/env python3
"""Prepare and reconcile Project Slices publication artifacts without remote access."""

from __future__ import annotations

import argparse
import copy
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

from manage_slices import (
    ContractError,
    atomic_write,
    assert_safe_write,
    canonical_bytes,
    contained_feature_path,
    digest,
    file_digest,
    load_json,
    reject_secrets,
    require_text,
    require_timestamp,
    validate_input_linkage,
    validate_state as validate_slices_state,
)


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


def optional_int(value: Any, label: str) -> int | None:
    if value is None:
        return None
    return positive_int(value, label)


def hours(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
        fail(f"{label} must be positive hours")
    return float(value)


def issue_object(snapshot: dict[str, Any]) -> dict[str, Any]:
    issue = snapshot.get("issue", snapshot)
    if not isinstance(issue, dict):
        fail("snapshot must contain an issue object")
    reject_secrets(issue, "issue snapshot")
    return issue


def feature_evidence_path(feature_dir: Path, value: Any, label: str) -> Path:
    path = Path(require_text(value, label)).absolute()
    try:
        relative = path.relative_to(feature_dir.absolute())
    except ValueError:
        fail(f"{label} must be inside the Feature directory")
    if not relative.parts or relative.parts[0] != ".work":
        fail(f"{label} must be disposable evidence under .work")
    return contained_feature_path(feature_dir, str(relative).replace("\\", "/"), label)


def current_evidence_path(current: dict[str, Any], value: Any, label: str) -> Path:
    return feature_evidence_path(Path(current["slices_state_path"]).parent.parent, value, label)


def named_id(issue: dict[str, Any], field: str, *, required: bool = True) -> int | None:
    value = issue.get(field)
    if value is None and not required:
        return None
    if isinstance(value, dict):
        value = value.get("id")
    return positive_int(value, f"issue.{field}")


def approved_source(path: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    state = load_json(path)
    validate_slices_state(state)
    if state["status"] != "approved":
        fail("publication requires an approved slicing revision")
    revision = state["revisions"][-1]
    approvals = [
        item for item in state["approvals"]
        if item["revision"] == revision["number"] and item["status"] == "valid"
    ]
    if len(approvals) != 1:
        fail("publication requires exactly one valid slicing approval")
    validate_input_linkage(path.parent.parent, revision["proposal"], path.parent / "slices-input-check.json")
    return state, revision, approvals[0]


def description_markdown(description: dict[str, Any], kind: str, parent_issue_id: int) -> str:
    if kind == "dev":
        lines = [
            "## Entrega", "", description["delivery"], "",
            "## Escopo e limites", "", description["limits"], "", "## Critérios de aceite", "",
        ]
        lines.extend(f"- {item['text']}" for item in description["criteria"])
        lines.extend(["", "## Dependências", "", description["dependencies"]])
        if description.get("technical_context"):
            lines.extend(["", "## Contexto técnico", "", description["technical_context"]])
        lines.extend(["", "## Referências", "", f"Item pai Redmine #{parent_issue_id}; regras/critérios {', '.join(description['traceability'])}.", ""])
        return "\n".join(lines)
    lines = [
        "## Objetivo", "", description["objective"], "",
        "## Jornadas integradas", "",
    ]
    lines.extend(f"- {item}" for item in description["integrated_journeys"])
    lines.extend(["", "## Regras e permissões", ""])
    lines.extend(f"- {item}" for item in description["rules_permissions"])
    lines.extend(["", "## Impactos relacionados", ""])
    lines.extend(f"- {item}" for item in description["related_impacts"])
    lines.extend(["", "## Critérios de conclusão", ""])
    lines.extend(f"- {item}" for item in description["completion_criteria"])
    lines.extend(["", "## Referências", "", f"Item pai Redmine #{parent_issue_id}; regras/critérios {', '.join(description['requirement_references'])}.", ""])
    return "\n".join(lines)


def validate_qa(qa: Any, feature_title: str, dev_keys: set[str], *, qa_only: bool) -> dict[str, Any]:
    qa = exact(qa, {"title", "estimate_hours", "blocked_by", "description"}, "qa")
    if qa["title"] != f"[QA] {feature_title}":
        fail("QA title must be [QA] followed by the full parent title")
    hours(qa["estimate_hours"], "qa.estimate_hours")
    blockers = qa["blocked_by"]
    if not isinstance(blockers, list) or len(blockers) != len(set(blockers)):
        fail("QA blocked_by must name unique required DEV children")
    if qa_only:
        if blockers:
            fail("QA-only publication cannot invent DEV blockers")
    elif not blockers:
        fail("QA blocked_by must name required DEV children outside QA-only mode")
    if any(item not in dev_keys for item in blockers):
        fail("QA blocked_by references an unknown DEV child")
    description = exact(qa["description"], {
        "objective", "integrated_journeys", "rules_permissions", "related_impacts",
        "completion_criteria", "requirement_references",
    }, "qa.description")
    require_text(description["objective"], "qa.description.objective")
    for field in ("integrated_journeys", "rules_permissions", "related_impacts", "completion_criteria", "requirement_references"):
        values = description[field]
        if not isinstance(values, list) or not values or any(not isinstance(item, str) or not item.strip() for item in values):
            fail(f"qa.description.{field} must contain non-empty text")
    reject_secrets(qa, "QA proposal")
    return qa


def validate_plan(plan: dict[str, Any], slices_path: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    required = {"source", "parent_snapshot", "metadata_snapshot", "native_fields", "qa"}
    if not isinstance(plan, dict) or not required.issubset(plan) or not set(plan).issubset(required | {"existing_children_review"}):
        fail("publication plan has missing or unknown fields")
    source = exact(plan["source"], {"slices_state_path", "slices_state_sha256"}, "source")
    if Path(source["slices_state_path"]).absolute() != slices_path.absolute():
        fail("plan source path differs from the approved slicing state")
    if source["slices_state_sha256"] != file_digest(slices_path):
        fail("plan source hash differs from the approved slicing state")
    _, revision, slicing_approval = approved_source(slices_path)
    feature_dir = slices_path.parent.parent
    parent_snapshot_path = feature_evidence_path(feature_dir, plan["parent_snapshot"], "parent_snapshot")
    parent = issue_object(load_json(parent_snapshot_path))
    feature = revision["proposal"]["feature"]
    if positive_int(parent.get("id"), "parent.id") != feature["issue_id"] or require_text(parent.get("subject"), "parent.subject") != feature["title"]:
        fail("parent snapshot differs from the approved Feature")
    parent_children = parent.get("children")
    if parent_children is not None and not isinstance(parent_children, list):
        fail("parent.children must be an array when present")
    if isinstance(parent_children, list) and parent_children and "existing_children_review" not in plan:
        fail("existing parent children require a complete tech-lead review before publication preview")
    native = exact(plan["native_fields"], {
        "project_id", "dev_tracker_id", "qa_tracker_id", "initial_status_id", "default_priority_id", "priority_override_id", "priority_override_reason",
    }, "native_fields")
    project_id = positive_int(native["project_id"], "native_fields.project_id")
    if named_id(parent, "project") != project_id:
        fail("publication must use the parent project")
    for field in ("dev_tracker_id", "qa_tracker_id", "initial_status_id", "default_priority_id"):
        positive_int(native[field], f"native_fields.{field}")
    if native["priority_override_id"] is not None or native["priority_override_reason"] is not None:
        fail("child priority is fixed as Normal and cannot be overridden")
    metadata_path = feature_evidence_path(feature_dir, plan["metadata_snapshot"], "metadata_snapshot")
    metadata = load_json(metadata_path)
    exact(metadata, {"trackers", "statuses", "priorities"}, "metadata snapshot")
    selected: dict[str, Any] = {"path": str(metadata_path.absolute()), "sha256": file_digest(metadata_path)}
    parent_tracker = parent.get("tracker")
    parent_tracker_name = require_text(parent_tracker.get("name") if isinstance(parent_tracker, dict) else None, "parent.tracker.name")
    if parent_tracker_name not in {"Feature", "Bug"}:
        fail("parent tracker must be Feature or Bug")
    expected_dev_tracker = "Task" if parent_tracker_name == "Feature" else "Bug"
    trackers = metadata["trackers"]
    if not isinstance(trackers, list):
        fail("confirmed trackers metadata must be an array")
    for expected_name, selected_field, output_field in (
        (expected_dev_tracker, "dev_tracker_id", "dev_tracker"),
        ("Deliverable", "qa_tracker_id", "qa_tracker"),
    ):
        matches = [item for item in trackers if isinstance(item, dict) and item.get("name") == expected_name]
        if len(matches) != 1:
            fail(f"tracker {expected_name} must exist exactly once in confirmed MCP metadata")
        tracker_id = positive_int(matches[0].get("id"), f"tracker {expected_name}.id")
        if native[selected_field] != tracker_id:
            fail(f"tracker contract requires DEV={expected_dev_tracker} and QA=Deliverable for a {parent_tracker_name} parent")
        selected[output_field] = {"id": tracker_id, "name": expected_name}
    for collection, expected_name, selected_field, output_field in (
        ("statuses", "New", "initial_status_id", "initial_status"),
        ("priorities", "Normal", "default_priority_id", "default_priority"),
    ):
        values = metadata[collection]
        matches = [item for item in values if isinstance(item, dict) and item.get("name") == expected_name] if isinstance(values, list) else []
        if len(matches) != 1:
            fail(f"{collection} value {expected_name} must exist exactly once in confirmed MCP metadata")
        selected_id = positive_int(matches[0].get("id"), f"{collection} {expected_name}.id")
        if native[selected_field] != selected_id:
            fail("child status and priority contract requires status=New and priority=Normal")
        selected[output_field] = {"id": selected_id, "name": expected_name}
    selected["parent_tracker"] = {"id": named_id(parent, "tracker"), "name": parent_tracker_name}
    selected["priority_override"] = None
    dev_keys = {f"dev-{item['number']}" for item in revision["proposal"]["slices"]}
    coverage = revision["proposal"]["coverage"]
    qa_only = not dev_keys and bool(coverage) and all(item["disposition"] == "existing" for item in coverage)
    if not dev_keys and not qa_only:
        fail("publication without DEV requires exhaustive existing-behavior coverage")
    qa = validate_qa(plan["qa"], feature["title"], dev_keys, qa_only=qa_only)
    reject_secrets(plan, "publication plan")
    return revision, slicing_approval, parent, selected


def child_attributes(child: dict[str, Any], native: dict[str, Any], parent: dict[str, Any]) -> dict[str, Any]:
    attributes: dict[str, Any] = {
        "project_id": native["project_id"],
        "parent_issue_id": parent["id"],
        "tracker_id": native["qa_tracker_id"] if child["kind"] == "qa" else native["dev_tracker_id"],
        "status_id": native["initial_status_id"],
        "subject": child["title"],
        "description": child["description"],
        "assigned_to_id": None,
        "start_date": None,
        "due_date": None,
        "estimated_hours": child["estimate_hours"],
    }
    attributes["priority_id"] = native["default_priority_id"]
    category_id = named_id(parent, "category", required=False)
    version_id = named_id(parent, "fixed_version", required=False)
    if category_id is not None:
        attributes["category_id"] = category_id
    if version_id is not None:
        attributes["fixed_version_id"] = version_id
    return attributes


def comparable_issue(issue: dict[str, Any]) -> dict[str, Any]:
    fields = {
        "project_id": named_id(issue, "project"),
        "parent_issue_id": named_id(issue, "parent"),
        "tracker_id": named_id(issue, "tracker"),
        "status_id": named_id(issue, "status"),
        "priority_id": named_id(issue, "priority"),
        "subject": require_text(issue.get("subject"), "existing child.subject"),
        "description": require_text(issue.get("description"), "existing child.description"),
        "estimated_hours": hours(issue.get("estimated_hours"), "existing child.estimated_hours"),
        "assigned_to_id": named_id(issue, "assigned_to", required=False),
        "start_date": issue.get("start_date") or None,
        "due_date": issue.get("due_date") or None,
        "category_id": named_id(issue, "category", required=False),
        "fixed_version_id": named_id(issue, "fixed_version", required=False),
    }
    relations = issue.get("relations")
    if not isinstance(relations, list):
        fail("existing child snapshot requires relations")
    return fields


def issue_fingerprint(issue: dict[str, Any]) -> dict[str, Any]:
    relations = issue.get("relations")
    if not isinstance(relations, list):
        fail("existing child snapshot requires relations")
    normalized_relations = sorted(
        [
            {
                "id": optional_int(item.get("id"), "relation.id"),
                "issue_id": positive_int(item.get("issue_id"), "relation.issue_id"),
                "issue_to_id": positive_int(item.get("issue_to_id"), "relation.issue_to_id"),
                "relation_type": require_text(item.get("relation_type"), "relation.relation_type"),
            }
            for item in relations if isinstance(item, dict)
        ],
        key=lambda item: (item["issue_id"], item["issue_to_id"], item["relation_type"], item["id"] or 0),
    )
    if len(normalized_relations) != len(relations):
        fail("existing child relations must be structured")
    return {"id": positive_int(issue.get("id"), "existing child.id"), **comparable_issue(issue), "relations": normalized_relations}


def external_issue_fingerprint(issue: dict[str, Any], project_id: int, parent_issue_id: int) -> dict[str, Any]:
    def loose_named(field: str) -> int | None:
        value = issue.get(field)
        if isinstance(value, dict):
            value = value.get("id")
        return optional_int(value, f"external child.{field}")

    observed_project = loose_named("project")
    observed_parent = loose_named("parent")
    if observed_project not in {None, project_id} or observed_parent not in {None, parent_issue_id}:
        fail("external child belongs to another project or parent")
    relations = issue.get("relations", [])
    if not isinstance(relations, list):
        fail("external child relations must be an array when present")
    normalized_relations = sorted(
        [
            {
                "id": optional_int(item.get("id"), "external relation.id"),
                "issue_id": positive_int(item.get("issue_id"), "external relation.issue_id"),
                "issue_to_id": positive_int(item.get("issue_to_id"), "external relation.issue_to_id"),
                "relation_type": require_text(item.get("relation_type"), "external relation.relation_type"),
            }
            for item in relations if isinstance(item, dict)
        ],
        key=lambda item: (item["issue_id"], item["issue_to_id"], item["relation_type"], item["id"] or 0),
    )
    if len(normalized_relations) != len(relations):
        fail("external child relations must be structured")
    return {
        "id": positive_int(issue.get("id"), "external child.id"), "project_id": observed_project,
        "parent_issue_id": observed_parent, "tracker_id": loose_named("tracker"), "status_id": loose_named("status"),
        "priority_id": loose_named("priority"), "category_id": loose_named("category"),
        "fixed_version_id": loose_named("fixed_version"), "assigned_to_id": loose_named("assigned_to"),
        "subject": issue.get("subject"), "description": issue.get("description"),
        "estimated_hours": issue.get("estimated_hours"), "start_date": issue.get("start_date"),
        "due_date": issue.get("due_date"), "relations": normalized_relations,
    }


def review_existing_children(plan: dict[str, Any], feature_dir: Path, parent: dict[str, Any], children: list[dict[str, Any]], native: dict[str, Any]) -> dict[str, Any] | None:
    review = plan.get("existing_children_review")
    if review is None:
        return None
    review = exact(review, {"snapshot", "decisions"}, "existing children review")
    snapshot_path = feature_evidence_path(feature_dir, review["snapshot"], "existing children snapshot")
    snapshot = load_json(snapshot_path)
    reject_secrets(snapshot, "existing children snapshot")
    exact(snapshot, {"project_id", "parent_issue_id", "status_scope", "complete", "pages", "total_count", "children"}, "existing children snapshot")
    if snapshot["project_id"] != native["project_id"] or snapshot["parent_issue_id"] != parent["id"] or snapshot["status_scope"] != "all" or snapshot["complete"] is not True:
        fail("existing children snapshot must completely cover the approved project and parent")
    discovered = snapshot["children"]
    if not isinstance(discovered, list):
        fail("existing children snapshot children must be an array")
    discovered_by_id: dict[int, dict[str, Any]] = {}
    for issue in discovered:
        if not isinstance(issue, dict):
            fail("existing child must be a full issue object")
        issue_id = positive_int(issue.get("id"), "existing child.id")
        if issue_id in discovered_by_id:
            fail("existing children snapshot contains duplicate IDs")
        discovered_by_id[issue_id] = issue
    pages = snapshot["pages"]
    if not isinstance(pages, list) or not pages or snapshot["total_count"] != len(discovered):
        fail("existing children snapshot requires complete paginated evidence")
    next_offset = 0
    observed = 0
    for page in pages:
        if not isinstance(page, dict) or set(page) != {"offset", "limit", "count"} or page["offset"] != next_offset or not isinstance(page["limit"], int) or page["limit"] < 1 or not isinstance(page["count"], int) or page["count"] < 0 or page["count"] > page["limit"]:
            fail("existing children snapshot requires complete paginated evidence")
        observed += page["count"]
        next_offset += page["count"]
    if observed != len(discovered):
        fail("existing children snapshot requires complete paginated evidence")
    parent_children = parent.get("children")
    if not isinstance(parent_children, list):
        fail("parent snapshot must include children before existing-child decisions")
    parent_ids = {positive_int(item.get("id"), "parent.children.id") for item in parent_children if isinstance(item, dict)}
    if parent_ids != set(discovered_by_id):
        fail("existing children snapshot does not match the parent's complete child list")
    decisions = review["decisions"]
    if not isinstance(decisions, list) or len(decisions) != len(discovered_by_id):
        fail("every discovered child requires exactly one tech-lead decision")
    children_by_key = {child["key"]: child for child in children}
    adopted_keys: set[str] = set()
    records: list[dict[str, Any]] = []
    for index, decision in enumerate(decisions):
        decision = exact(decision, {"issue_id", "disposition", "target_key", "accepted_divergences", "decided_by", "decided_at", "reason"}, f"existing child decision {index}")
        issue_id = positive_int(decision["issue_id"], "decision.issue_id")
        if issue_id not in discovered_by_id or any(item["issue_id"] == issue_id for item in records):
            fail("existing child decisions must uniquely cover discovered children")
        disposition = decision["disposition"]
        if disposition not in {"adopt", "keep-external"}:
            fail("existing child disposition must be adopt or keep-external")
        actor = require_text(decision["decided_by"], "decision.decided_by")
        decided_at = require_timestamp(decision["decided_at"], "decision.decided_at")
        reason = require_text(decision["reason"], "decision.reason")
        target_key = decision["target_key"]
        accepted_divergences = decision["accepted_divergences"]
        if not isinstance(accepted_divergences, list) or len(accepted_divergences) != len(set(accepted_divergences)) or any(not isinstance(item, str) for item in accepted_divergences):
            fail("decision.accepted_divergences must be a unique field list")
        issue = discovered_by_id[issue_id]
        if disposition == "adopt":
            if target_key not in children_by_key or target_key in adopted_keys:
                fail("adopted child must select one unique managed target")
            child = children_by_key[target_key]
            expected = child["attributes"]
            actual = comparable_issue(issue)
            comparable_expected = {
                "project_id": expected["project_id"], "parent_issue_id": expected["parent_issue_id"],
                "tracker_id": expected["tracker_id"], "status_id": expected["status_id"],
                "priority_id": expected.get("priority_id", native["default_priority_id"]),
                "subject": expected["subject"], "description": child["base_description"],
                "estimated_hours": float(expected["estimated_hours"]), "assigned_to_id": expected["assigned_to_id"],
                "start_date": expected["start_date"], "due_date": expected["due_date"],
                "category_id": expected.get("category_id"), "fixed_version_id": expected.get("fixed_version_id"),
            }
            if actual["project_id"] != comparable_expected["project_id"] or actual["parent_issue_id"] != comparable_expected["parent_issue_id"]:
                fail(f"existing child {issue_id} identity diverges from target {target_key}")
            divergences = sorted(field for field in actual if actual[field] != comparable_expected[field] and field not in {"project_id", "parent_issue_id"})
            if divergences != sorted(accepted_divergences):
                fail(f"existing child {issue_id} fields diverge from target {target_key} without matching approval: {', '.join(divergences) or 'none'}")
            child["source"] = "adopted"
            child["remote_id"] = issue_id
            child["title"] = actual["subject"]
            child["estimate_hours"] = actual["estimated_hours"]
            child["description"] = actual["description"]
            child["attributes"] = {
                "project_id": actual["project_id"], "parent_issue_id": actual["parent_issue_id"],
                "tracker_id": actual["tracker_id"], "status_id": actual["status_id"],
                "subject": actual["subject"], "description": actual["description"],
                "assigned_to_id": actual["assigned_to_id"], "start_date": actual["start_date"], "due_date": actual["due_date"],
                "estimated_hours": actual["estimated_hours"], "priority_id": actual["priority_id"],
                "category_id": actual["category_id"], "fixed_version_id": actual["fixed_version_id"],
            }
            child["payload_sha256"] = digest({"attributes": child["attributes"]})
            child["adoption_evidence"] = {"snapshot_path": str(snapshot_path.absolute()), "snapshot_sha256": file_digest(snapshot_path)}
            adopted_keys.add(target_key)
        elif target_key is not None or accepted_divergences:
            fail("a child kept external cannot select a managed target or accepted divergences")
        issue_hash = digest(issue_fingerprint(issue)) if disposition == "adopt" else digest(external_issue_fingerprint(issue, native["project_id"], parent["id"]))
        records.append({
            "issue_id": issue_id, "disposition": disposition, "target_key": target_key,
            "decided_by": actor, "decided_at": decided_at, "reason": reason,
            "accepted_divergences": accepted_divergences, "issue_sha256": issue_hash,
        })
    return {"snapshot_path": str(snapshot_path.absolute()), "snapshot_sha256": file_digest(snapshot_path), "decisions": records}


def publication_digest(revision: dict[str, Any]) -> str:
    value = {
        "parent_baseline": revision["parent_baseline"],
        "metadata_baseline": revision["metadata_baseline"],
        "native_fields": revision["native_fields"],
        "children": revision["children"],
        "relations": revision["relations"],
    }
    if "semantic_baseline" in revision:
        value["semantic_baseline"] = revision["semantic_baseline"]
    if "existing_children_review" in revision:
        value["existing_children_review"] = revision["existing_children_review"]
    return digest(value)


def validate_current_source(current: dict[str, Any]) -> None:
    source_path = Path(current["slices_state_path"])
    if file_digest(source_path) != current["slices_state_sha256"]:
        fail("approved slicing source changed after publication preview")
    _, revision, approval = approved_source(source_path)
    if revision["number"] != current["slicing_revision"] or digest(approval) != current["slicing_approval_sha256"]:
        fail("approved slicing source changed after publication preview")


def require_remote_authority(state: dict[str, Any]) -> None:
    if state["status"] not in {"approved", "publishing"}:
        fail("remote publication requires final tech-lead approval")
    validate_current_source(state["revisions"][-1])


def atomic_batch_write(files: dict[Path, bytes]) -> None:
    staged: dict[Path, str] = {}
    backups: dict[Path, bytes | None] = {}
    try:
        for path, content in files.items():
            assert_safe_write(path)
            path.parent.mkdir(parents=True, exist_ok=True)
            handle, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
            with os.fdopen(handle, "wb") as stream:
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
            staged[path] = temporary
            backups[path] = path.read_bytes() if path.is_file() else None
        for path, temporary in staged.items():
            os.replace(temporary, path)
    except BaseException:
        for path, previous in backups.items():
            try:
                if previous is None:
                    if path.is_file():
                        path.unlink()
                else:
                    atomic_write(path, previous)
            except OSError:
                pass
        raise
    finally:
        for temporary in staged.values():
            try:
                os.unlink(temporary)
            except FileNotFoundError:
                pass


def render_preview(revision: dict[str, Any], children: list[dict[str, Any]], relations: list[dict[str, Any]], native_fields: dict[str, Any], metadata: dict[str, Any], review: dict[str, Any] | None = None) -> str:
    feature = revision["proposal"]["feature"]
    native = children[0]["attributes"]
    priority = native_fields["default_priority_id"]
    lines = [
        f"# Publicação das filhas de {feature['title']}", "",
        f"Item pai Redmine: `{feature['issue_id']}`", "",
        "## Campos nativos aprovados", "",
        f"- Projeto: `{native['project_id']}`",
        f"- Pai nativo: `{native['parent_issue_id']}`",
        f"- Tracker da mãe: {metadata['parent_tracker']['name']} (`{metadata['parent_tracker']['id']}`)",
        f"- Tracker DEV: {metadata['dev_tracker']['name']} (`{native_fields['dev_tracker_id']}`)",
        f"- Tracker QA: {metadata['qa_tracker']['name']} (`{native_fields['qa_tracker_id']}`)",
        f"- Status inicial: {metadata['initial_status']['name']} (`{native['status_id']}`)",
        f"- Prioridade inicial: {metadata['default_priority']['name']} (`{priority}`, regra fixa)",
        f"- Categoria herdada: `{native.get('category_id')}`",
        f"- Versão herdada: `{native.get('fixed_version_id')}`",
        "- Responsável, início e vencimento: vazios", "",
        "## Campos nativos e descrições", "",
    ]
    for child in children:
        lines.extend([
            f"### {'#' + str(child['remote_id']) + ' — ' if child.get('remote_id') else ''}{child['title']}", "",
            f"- Chave interna: `{child['key']}`",
            f"- Tipo: {child['kind'].upper()}",
            *([f"- Origem: {'filha existente adotada' if child.get('source') == 'adopted' else 'nova filha a criar'}"] if review else []),
            *([f"- ID adotado: `{child['remote_id']}`"] if child.get("source") == "adopted" else []),
            f"- Estimativa: {child['estimate_hours']:g}h",
            f"- Payload SHA-256: `{child['payload_sha256']}`", "",
            child["description"], "",
        ])
    lines.extend(["## Bloqueios nativos", ""])
    children_by_key = {child["key"]: child for child in children}

    def child_label(key: str) -> str:
        child = children_by_key[key]
        identity = f"#{child['remote_id']} — " if child.get("remote_id") else ""
        return f"{identity}{child['title']}"

    if relations:
        lines.extend(f"- {child_label(item['source_key'])} bloqueia {child_label(item['target_key'])} (`blocks`)." for item in relations)
    else:
        lines.append("- Nenhum; a Feature possui cobertura existente integral e segue somente para QA.")
    if review:
        snapshot = load_json(Path(review["snapshot_path"]))
        titles = {issue["id"]: issue["subject"] for issue in snapshot["children"]}
        lines.extend(["", "## Filhas descobertas e decisões", ""])
        for decision in review["decisions"]:
            target_title = next((item["title"] for item in revision["proposal"]["slices"] if f"dev-{item['number']}" == decision["target_key"]), f"[QA] {feature['title']}")
            destination = f"adotar como {target_title} (chave interna `{decision['target_key']}`)" if decision["disposition"] == "adopt" else "manter fora do conjunto gerenciado"
            lines.append(f"- #{decision['issue_id']} — {titles[decision['issue_id']]}: {destination}; decisão de {decision['decided_by']} em {decision['decided_at']} — {decision['reason']}")
    return "\n".join(lines) + "\n"


def command_prepare(arguments: argparse.Namespace) -> None:
    state_path = Path(arguments.state)
    slices_path = Path(arguments.slices_state)
    plan = load_json(Path(arguments.plan))
    revision, slicing_approval, parent, metadata = validate_plan(plan, slices_path)
    feature_dir = slices_path.parent.parent
    state_path = contained_feature_path(feature_dir, str(Path(arguments.state).absolute().relative_to(feature_dir.absolute())).replace("\\", "/"), "publication state")
    preview_path = contained_feature_path(feature_dir, str(Path(arguments.preview).absolute().relative_to(feature_dir.absolute())).replace("\\", "/"), "publication preview")
    descriptions_dir = contained_feature_path(feature_dir, str(Path(arguments.descriptions_dir).absolute().relative_to(feature_dir.absolute())).replace("\\", "/"), "descriptions directory")
    if state_path != (feature_dir / ".flow" / "slices-publication.json").absolute():
        fail("publication state must use .flow/slices-publication.json")
    if preview_path != (feature_dir / "slices" / "publication.md").absolute() or descriptions_dir != (feature_dir / "slices" / "descriptions").absolute():
        fail("publication output must use the canonical slices layout")
    recorded_at = require_timestamp(arguments.at, "recorded_at")
    actor = require_text(arguments.actor, "recorded_by")
    reason = require_text(arguments.reason, "reason")
    native = plan["native_fields"]
    children: list[dict[str, Any]] = []
    for item in revision["proposal"]["slices"]:
        key = f"dev-{item['number']}"
        document = description_markdown(item["description"], "dev", parent["id"])
        identity = digest({"slices_state_sha256": file_digest(slices_path), "slicing_revision": revision["number"], "child_key": key})
        document += f"\n<!-- project-slices-child:{identity} -->\n"
        children.append({"key": key, "identity": identity, "kind": "dev", "title": item["title"], "estimate_hours": float(item["estimate_hours"]), "description": document, "base_description": document.removesuffix(f"\n<!-- project-slices-child:{identity} -->\n")})
    qa = plan["qa"]
    qa_identity = digest({"slices_state_sha256": file_digest(slices_path), "slicing_revision": revision["number"], "child_key": "qa"})
    qa_document = description_markdown(qa["description"], "qa", parent["id"]) + f"\n<!-- project-slices-child:{qa_identity} -->\n"
    children.append({"key": "qa", "identity": qa_identity, "kind": "qa", "title": qa["title"], "estimate_hours": float(qa["estimate_hours"]), "description": qa_document, "base_description": qa_document.removesuffix(f"\n<!-- project-slices-child:{qa_identity} -->\n")})
    for child in children:
        child["attributes"] = child_attributes(child, native, parent)
        child["payload_sha256"] = digest({"attributes": child["attributes"]})
        child["description_path"] = str((descriptions_dir / f"{child['key']}.md").absolute())
    review = review_existing_children(plan, feature_dir, parent, children, native)
    for child in children:
        child.pop("base_description", None)
    dev_relations = [
        {"key": f"blocks:dev-{blocker}:dev-{item['number']}", "source_key": f"dev-{blocker}", "target_key": f"dev-{item['number']}", "relation_type": "blocks"}
        for item in revision["proposal"]["slices"] for blocker in item["blocked_by"]
    ]
    relations = dev_relations + [
        {"key": f"blocks:{key}:qa", "source_key": key, "target_key": "qa", "relation_type": "blocks"}
        for key in qa["blocked_by"]
    ]
    revision_record = {
        "number": 1, "recorded_by": actor, "recorded_at": recorded_at, "reason": reason,
        "slices_state_path": str(slices_path.absolute()), "slices_state_sha256": file_digest(slices_path),
        "slicing_revision": revision["number"], "slicing_approval_sha256": digest(slicing_approval),
        "parent_baseline": {
            "path": str(Path(plan["parent_snapshot"]).absolute()), "sha256": file_digest(Path(plan["parent_snapshot"])),
            "issue_id": parent["id"], "project_id": native["project_id"],
            "status_id": named_id(parent, "status"), "status_name": require_text(parent["status"].get("name"), "parent.status.name"),
        },
        "metadata_baseline": metadata,
        "native_fields": copy.deepcopy(native), "children": children, "relations": relations,
        "semantic_baseline": copy.deepcopy(revision.get("semantic_baseline")),
    }
    if review is not None:
        revision_record["existing_children_review"] = review
    revision_record["publication_sha256"] = publication_digest(revision_record)
    if state_path.exists():
        state = load_json(state_path)
        validate_publication_state(state)
        if state["operations"]:
            fail("a publication with remote progress cannot be revised")
        for approval in state["approvals"]:
            if approval["status"] == "valid":
                approval["status"] = "invalidated"
        revision_record["number"] = len(state["revisions"]) + 1
        state["revisions"].append(revision_record)
        state["status"] = "prepared"
        state["status_history"].append({"status": "prepared", "recorded_at": recorded_at})
    else:
        state = {
            "schema_version": 1, "status": "prepared",
            "status_history": [{"status": "prepared", "recorded_at": recorded_at}],
            "revisions": [revision_record], "approvals": [], "operations": {}, "readback": None, "completed_at": None,
        }
    validate_publication_state(state, check_files=False)
    outputs = {Path(child["description_path"]): child["description"].encode("utf-8") for child in children}
    outputs[preview_path] = render_preview(revision, children, relations, native, metadata, review).encode("utf-8")
    outputs[state_path] = canonical_bytes(state) + b"\n"
    atomic_batch_write(outputs)
    print(json.dumps({"status": state["status"], "revision": revision_record["number"], "publication_sha256": revision_record["publication_sha256"]}))


def validate_publication_state(state: dict[str, Any], *, check_files: bool = True) -> None:
    exact(state, {"schema_version", "status", "status_history", "revisions", "approvals", "operations", "readback", "completed_at"}, "publication state")
    if state["schema_version"] != 1 or state["status"] not in {"prepared", "approved", "publishing", "completed"}:
        fail("unsupported publication state")
    if not isinstance(state["revisions"], list) or not state["revisions"]:
        fail("publication requires revision history")
    revision_fields = {
        "number", "recorded_by", "recorded_at", "reason", "slices_state_path", "slices_state_sha256",
        "slicing_revision", "slicing_approval_sha256", "parent_baseline", "metadata_baseline",
        "native_fields", "children", "relations", "publication_sha256",
    }
    for number, revision in enumerate(state["revisions"], start=1):
        optional = ({"existing_children_review"} if "existing_children_review" in revision else set())
        optional |= ({"semantic_baseline"} if "semantic_baseline" in revision else set())
        exact(revision, revision_fields | optional, f"publication revision {number}")
        if revision["number"] != number:
            fail("publication revision numbers must be contiguous")
        require_text(revision["recorded_by"], "revision.recorded_by")
        require_timestamp(revision["recorded_at"], "revision.recorded_at")
        require_text(revision["reason"], "revision.reason")
        baseline = revision.get("semantic_baseline")
        if "semantic_baseline" in revision and baseline is not None:
            if not isinstance(baseline, dict) or baseline.get("semantic_model_sha256") != digest(baseline.get("semantic_model")):
                fail("publication semantic baseline is invalid")
        if not isinstance(revision.get("children"), list) or not revision["children"]:
            fail("publication revision requires managed children")
        keys = [item.get("key") for item in revision["children"]]
        if keys.count("qa") != 1 or any(not isinstance(key, str) for key in keys) or len(keys) != len(set(keys)):
            fail("publication children require stable unique keys and exactly one QA")
        for child in revision["children"]:
            source = child.get("source", "create")
            if source not in {"create", "adopted"}:
                fail("child source must be create or adopted")
            if source == "adopted" and (not isinstance(child.get("remote_id"), int) or "adoption_evidence" not in child):
                fail("adopted child requires observed ID and evidence")
            if source == "create" and ("remote_id" in child or "adoption_evidence" in child):
                fail("new child cannot carry adoption evidence")
            if child["payload_sha256"] != digest({"attributes": child["attributes"]}):
                fail("child payload hash differs")
            expected_tracker = revision["native_fields"]["qa_tracker_id"] if child["kind"] == "qa" else revision["native_fields"]["dev_tracker_id"]
            if child["attributes"].get("tracker_id") != expected_tracker:
                fail("child tracker differs from the derived DEV/QA contract")
        relation_keys = set()
        for relation in revision["relations"]:
            if relation.get("relation_type") != "blocks" or relation.get("source_key") not in keys or relation.get("target_key") not in keys or relation.get("source_key") == relation.get("target_key") or relation.get("key") in relation_keys:
                fail("publication relation is invalid")
            relation_keys.add(relation["key"])
        review = revision.get("existing_children_review")
        if review is not None:
            exact(review, {"snapshot_path", "snapshot_sha256", "decisions"}, "existing children review")
            evidence_path = Path(review["snapshot_path"])
            if check_files and (not evidence_path.is_file() or file_digest(evidence_path) != review["snapshot_sha256"]):
                fail("existing children review evidence is missing or changed")
            if not isinstance(review["decisions"], list):
                fail("existing children review decisions must be an array")
            adopted = {child["key"]: child for child in revision["children"] if child.get("source") == "adopted"}
            adopted_decisions: dict[str, dict[str, Any]] = {}
            for decision in review["decisions"]:
                exact(decision, {"issue_id", "disposition", "target_key", "accepted_divergences", "decided_by", "decided_at", "reason", "issue_sha256"}, "existing child decision")
                require_text(decision["decided_by"], "existing child decision.decided_by")
                require_timestamp(decision["decided_at"], "existing child decision.decided_at")
                require_text(decision["reason"], "existing child decision.reason")
                if decision["disposition"] == "adopt":
                    adopted_decisions[decision["target_key"]] = decision
            if set(adopted_decisions) != set(adopted) or any(adopted[key]["remote_id"] != decision["issue_id"] for key, decision in adopted_decisions.items()):
                fail("adopted children differ from the approved existing-child decisions")
        if revision.get("publication_sha256") != publication_digest(revision):
            fail("publication content differs from its approved hash")
    current = state["revisions"][-1]
    for child in current["children"]:
        path = Path(child["description_path"])
        if check_files and (not path.is_file() or path.read_text(encoding="utf-8") != child["description"]):
            fail("individual child description differs from its revision")
    if not isinstance(state["operations"], dict):
        fail("operations must be an object")
    for approval in state["approvals"]:
        exact(approval, {"revision", "publication_sha256", "approved_by", "approved_at", "status"}, "publication approval")
        if not isinstance(approval["revision"], int) or approval["revision"] < 1 or approval["revision"] > len(state["revisions"]):
            fail("publication approval references an unknown revision")
        if approval["publication_sha256"] != state["revisions"][approval["revision"] - 1]["publication_sha256"] or approval["status"] not in {"valid", "invalidated"}:
            fail("publication approval differs from its revision")
        require_text(approval["approved_by"], "publication approval approved_by")
        require_timestamp(approval["approved_at"], "publication approval approved_at")
    valid_approvals = [item for item in state["approvals"] if item["status"] == "valid"]
    if state["status"] == "prepared" and valid_approvals:
        fail("prepared publication cannot retain a valid approval")
    if state["status"] != "prepared" and (len(valid_approvals) != 1 or valid_approvals[0]["revision"] != current["number"] or valid_approvals[0]["publication_sha256"] != current["publication_sha256"]):
        fail("remote publication requires final approval of the current content")
    if state["status"] == "completed" and (state["readback"] is None or state["completed_at"] is None):
        fail("completed publication requires readback evidence")
    reject_secrets(state, "publication state")


def command_approve(arguments: argparse.Namespace) -> None:
    path = Path(arguments.state)
    state = load_json(path)
    validate_publication_state(state)
    if state["status"] != "prepared":
        fail("only prepared publication content can be approved")
    current = state["revisions"][-1]
    validate_current_source(current)
    at = require_timestamp(arguments.at, "approved_at")
    state["approvals"].append({
        "revision": current["number"], "publication_sha256": current["publication_sha256"],
        "approved_by": require_text(arguments.actor, "approved_by"), "approved_at": at, "status": "valid",
    })
    state["status"] = "approved"
    state["status_history"].append({"status": "approved", "recorded_at": at})
    validate_publication_state(state)
    atomic_write(path, canonical_bytes(state) + b"\n")
    print(json.dumps({"status": "approved", "publication_sha256": current["publication_sha256"]}))


def operation(state: dict[str, Any], key: str, kind: str) -> dict[str, Any]:
    value = state["operations"].setdefault(key, {"kind": kind, "attempts": [], "observations": [], "status": "pending", "remote_id": None})
    if value["kind"] != kind:
        fail("operation key belongs to another operation kind")
    return value


def current_child(state: dict[str, Any], key: str) -> dict[str, Any]:
    matches = [item for item in state["revisions"][-1]["children"] if item["key"] == key]
    if len(matches) != 1:
        fail("unknown child key")
    return matches[0]


def check_retry(value: dict[str, Any]) -> None:
    if value["status"] == "completed":
        fail("completed operation must not be repeated")
    if value["attempts"] and value["attempts"][-1]["outcome"] in {"in-flight", "unknown"}:
        later = value["observations"][value["attempts"][-1].get("observations_before", 0):]
        if not later or later[-1]["outcome"] != "absent":
            fail("unknown outcome requires readback reconciliation before retry")


def command_begin_create(arguments: argparse.Namespace) -> None:
    path = Path(arguments.state)
    state = load_json(path)
    validate_publication_state(state)
    require_remote_authority(state)
    child = current_child(state, arguments.key)
    if child.get("source") == "adopted":
        fail("adopted child must not be sent to create")
    value = operation(state, f"create:{arguments.key}", "create")
    check_retry(value)
    attempted_at = require_timestamp(arguments.at, "attempted_at")
    attempt_id = len(value["attempts"]) + 1
    value["attempts"].append({
        "id": attempt_id, "attempted_at": attempted_at, "payload_sha256": child["payload_sha256"],
        "outcome": "in-flight", "observations_before": len(value["observations"]),
    })
    state["status"] = "publishing"
    state["status_history"].append({"status": "publishing", "recorded_at": attempted_at})
    atomic_write(path, canonical_bytes(state) + b"\n")
    print(json.dumps({"attempt_id": attempt_id, "attributes": child["attributes"]}, ensure_ascii=False))


def command_finish_create(arguments: argparse.Namespace) -> None:
    path = Path(arguments.state)
    state = load_json(path)
    validate_publication_state(state)
    child = current_child(state, arguments.key)
    value = operation(state, f"create:{arguments.key}", "create")
    if not value["attempts"] or value["attempts"][-1].get("id") != arguments.attempt or value["attempts"][-1]["outcome"] != "in-flight":
        fail("create result must finish the current in-flight attempt")
    entry = value["attempts"][-1]
    outcome = arguments.outcome
    if outcome == "completed":
        remote_id = positive_int(arguments.issue_id, "issue_id")
        value["remote_id"] = remote_id
        value["status"] = "completed"
    elif arguments.issue_id is not None:
        fail("only a completed create response may include issue_id")
    if entry["payload_sha256"] != child["payload_sha256"]:
        fail("in-flight create payload differs from approved content")
    entry["outcome"] = outcome
    entry["response_recorded_at"] = require_timestamp(arguments.at, "response_recorded_at")
    if outcome == "failed":
        entry["error_code"] = require_text(arguments.error_code, "error_code")
        entry["message"] = require_text(arguments.message, "message")
    validate_publication_state(state)
    atomic_write(path, canonical_bytes(state) + b"\n")


def compare_issue(child: dict[str, Any], issue: dict[str, Any], baseline: dict[str, Any], native: dict[str, Any]) -> None:
    expected = child["attributes"]
    comparisons = {
        "project": expected["project_id"], "parent": expected["parent_issue_id"], "tracker": expected["tracker_id"],
        "status": expected["status_id"], "priority": expected.get("priority_id", native["default_priority_id"]),
    }
    for field, expected_id in comparisons.items():
        if named_id(issue, field) != expected_id:
            fail(f"child {field} differs from approved native fields")
    for field in ("subject", "description"):
        if issue.get(field) != expected[field]:
            fail(f"child {field} differs from approved content")
    if float(issue.get("estimated_hours", 0)) != float(expected["estimated_hours"]):
        fail("child estimated_hours differs from approved estimate")
    if named_id(issue, "assigned_to", required=False) != expected.get("assigned_to_id") or (issue.get("start_date") or None) != expected.get("start_date") or (issue.get("due_date") or None) != expected.get("due_date"):
        fail("child assignee or dates differ from approved content")
    for remote_field, payload_field in (("category", "category_id"), ("fixed_version", "fixed_version_id")):
        expected_id = expected.get(payload_field)
        if named_id(issue, remote_field, required=False) != expected_id:
            fail(f"child {remote_field} does not inherit the parent value")


def command_observe_create(arguments: argparse.Namespace) -> None:
    path = Path(arguments.state)
    state = load_json(path)
    validate_publication_state(state)
    child = current_child(state, arguments.key)
    value = operation(state, f"create:{arguments.key}", "create")
    if not value["attempts"] or value["attempts"][-1]["outcome"] not in {"in-flight", "unknown"} or value["status"] == "completed":
        fail("create reconciliation requires a pending unknown attempt")
    snapshot_path = current_evidence_path(state["revisions"][-1], arguments.snapshot, "create reconciliation snapshot")
    snapshot = load_json(snapshot_path)
    reject_secrets(snapshot, "create reconciliation snapshot")
    exact(snapshot, {"project_id", "parent_issue_id", "identity", "status_scope", "pages", "total_count", "issues"}, "create reconciliation search")
    current = state["revisions"][-1]
    if snapshot["project_id"] != current["native_fields"]["project_id"] or snapshot["parent_issue_id"] != current["parent_baseline"]["issue_id"]:
        fail("create reconciliation search used the wrong project or parent")
    if snapshot["identity"] != child["identity"] or snapshot["status_scope"] != "all":
        fail("create reconciliation must search the stable identity across open and closed issues")
    issues = snapshot["issues"]
    pages = snapshot["pages"]
    complete_pages = isinstance(pages, list) and bool(pages)
    next_offset = 0
    observed_count = 0
    if complete_pages:
        for index, page in enumerate(pages):
            if not isinstance(page, dict) or set(page) != {"offset", "limit", "count"} or page["offset"] != next_offset or not isinstance(page["limit"], int) or page["limit"] < 1 or not isinstance(page["count"], int) or page["count"] < 0 or page["count"] > page["limit"]:
                complete_pages = False
                break
            observed_count += page["count"]
            next_offset += page["count"]
            if page["count"] < page["limit"] and index != len(pages) - 1:
                complete_pages = False
                break
    if not isinstance(issues, list) or not complete_pages or snapshot["total_count"] != len(issues) or observed_count != len(issues):
        fail("create reconciliation requires complete paginated search evidence")
    marker = f"<!-- project-slices-child:{child['identity']} -->"
    candidates = [item for item in issues if isinstance(item, dict) and marker in str(item.get("description", ""))]
    outcome = arguments.outcome
    remote_id = None
    if outcome == "matched":
        if len(candidates) != 1:
            fail("create reconciliation requires exactly one stable-identity candidate")
        issue = candidates[0]
        compare_issue(child, issue, current["parent_baseline"], current["native_fields"])
        remote_id = positive_int(issue.get("id"), "issue.id")
        value["remote_id"] = remote_id
        value["status"] = "completed"
    else:
        if candidates:
            fail("search snapshot contains a stable-identity candidate")
    observed_at = require_timestamp(arguments.at, "observed_at")
    value["observations"].append({"observed_at": observed_at, "outcome": outcome, "snapshot_path": str(snapshot_path.absolute()), "snapshot_sha256": file_digest(snapshot_path), "remote_id": remote_id})
    atomic_write(path, canonical_bytes(state) + b"\n")


def child_remote_id(state: dict[str, Any], key: str) -> int:
    child = current_child(state, key)
    if child.get("source") == "adopted":
        return positive_int(child.get("remote_id"), "adopted child remote_id")
    value = state["operations"].get(f"create:{key}")
    if not isinstance(value, dict) or value.get("status") != "completed":
        fail("remote child ID requires a reconciled create or adoption")
    return positive_int(value["remote_id"], "child remote_id")


def relation_ids(state: dict[str, Any], relation: dict[str, Any]) -> tuple[int, int]:
    ids = []
    for key in (relation["source_key"], relation["target_key"]):
        ids.append(child_remote_id(state, key))
    return ids[0], ids[1]


def current_relation(state: dict[str, Any], key: str) -> dict[str, Any]:
    matches = [item for item in state["revisions"][-1]["relations"] if item["key"] == key]
    if len(matches) != 1:
        fail("unknown relation key")
    return matches[0]


def command_begin_relation(arguments: argparse.Namespace) -> None:
    path = Path(arguments.state)
    state = load_json(path)
    validate_publication_state(state)
    require_remote_authority(state)
    relation = current_relation(state, arguments.key)
    source_id, target_id = relation_ids(state, relation)
    value = operation(state, f"relation:{arguments.key}", "relation")
    check_retry(value)
    payload = {"issue_id": source_id, "issue_to_id": target_id, "relation_type": "blocks"}
    attempted_at = require_timestamp(arguments.at, "attempted_at")
    attempt_id = len(value["attempts"]) + 1
    value["attempts"].append({"id": attempt_id, "attempted_at": attempted_at, "payload_sha256": digest(payload), "outcome": "in-flight", "observations_before": len(value["observations"])})
    state["status"] = "publishing"
    state["status_history"].append({"status": "publishing", "recorded_at": attempted_at})
    atomic_write(path, canonical_bytes(state) + b"\n")
    print(json.dumps({"attempt_id": attempt_id, **payload}))


def command_finish_relation(arguments: argparse.Namespace) -> None:
    path = Path(arguments.state)
    state = load_json(path)
    validate_publication_state(state)
    relation = current_relation(state, arguments.key)
    source_id, target_id = relation_ids(state, relation)
    value = operation(state, f"relation:{arguments.key}", "relation")
    if not value["attempts"] or value["attempts"][-1].get("id") != arguments.attempt or value["attempts"][-1]["outcome"] != "in-flight":
        fail("relation result must finish the current in-flight attempt")
    entry = value["attempts"][-1]
    payload = {"issue_id": source_id, "issue_to_id": target_id, "relation_type": "blocks"}
    if entry["payload_sha256"] != digest(payload):
        fail("in-flight relation payload differs from approved blockers")
    entry["outcome"] = arguments.outcome
    entry["response_recorded_at"] = require_timestamp(arguments.at, "response_recorded_at")
    if arguments.outcome == "completed":
        value["status"] = "completed"
        value["remote_id"] = optional_int(arguments.relation_id, "relation_id")
    elif arguments.relation_id is not None:
        fail("only a completed relation response may include relation_id")
    if arguments.outcome == "failed":
        entry["error_code"] = require_text(arguments.error_code, "error_code")
        entry["message"] = require_text(arguments.message, "message")
    atomic_write(path, canonical_bytes(state) + b"\n")


def relation_present(snapshot: dict[str, Any], source_id: int, target_id: int) -> tuple[bool, int | None]:
    issue = issue_object(snapshot)
    if positive_int(issue.get("id"), "relation readback issue.id") not in {source_id, target_id}:
        fail("relation readback belongs to an unrelated issue")
    relations = issue.get("relations")
    if not isinstance(relations, list):
        fail("relation reconciliation requires issue relations")
    for relation in relations:
        if not isinstance(relation, dict) or relation.get("relation_type") != "blocks":
            continue
        if relation.get("issue_id") == source_id and relation.get("issue_to_id") == target_id:
            return True, optional_int(relation.get("id"), "relation.id")
    return False, None


def command_observe_relation(arguments: argparse.Namespace) -> None:
    path = Path(arguments.state)
    state = load_json(path)
    validate_publication_state(state)
    relation = current_relation(state, arguments.key)
    source_id, target_id = relation_ids(state, relation)
    value = operation(state, f"relation:{arguments.key}", "relation")
    if not value["attempts"] or value["attempts"][-1]["outcome"] not in {"in-flight", "unknown"} or value["status"] == "completed":
        fail("relation reconciliation requires a pending unknown attempt")
    snapshot_path = current_evidence_path(state["revisions"][-1], arguments.snapshot, "relation reconciliation snapshot")
    snapshot = load_json(snapshot_path)
    present, relation_id = relation_present(snapshot, source_id, target_id)
    if (arguments.outcome == "matched") != present:
        fail("relation observation outcome differs from readback")
    if present:
        value["status"] = "completed"
        value["remote_id"] = relation_id
    value["observations"].append({"observed_at": require_timestamp(arguments.at, "observed_at"), "outcome": arguments.outcome, "snapshot_path": str(snapshot_path.absolute()), "snapshot_sha256": file_digest(snapshot_path), "remote_id": relation_id})
    atomic_write(path, canonical_bytes(state) + b"\n")


def command_complete(arguments: argparse.Namespace) -> None:
    path = Path(arguments.state)
    state = load_json(path)
    validate_publication_state(state)
    current = state["revisions"][-1]
    validate_current_source(current)
    for child in current["children"]:
        if child.get("source") == "adopted":
            continue
        value = state["operations"].get(f"create:{child['key']}")
        if not isinstance(value, dict) or value.get("status") != "completed":
            fail("all child creates must be reconciled before completion")
    for relation in current["relations"]:
        value = state["operations"].get(f"relation:{relation['key']}")
        if not isinstance(value, dict) or value.get("status") != "completed":
            fail("all blocked-by relations must be reconciled before completion")
    snapshot_path = current_evidence_path(current, arguments.readback, "publication readback")
    snapshot = load_json(snapshot_path)
    exact(snapshot, {"parent", "children"}, "publication readback")
    parent = snapshot["parent"]
    baseline = current["parent_baseline"]
    if positive_int(parent.get("id"), "parent.id") != baseline["issue_id"] or named_id(parent, "status") != baseline["status_id"] or parent["status"].get("name") != baseline["status_name"]:
        fail("parent execution status changed")
    children = snapshot["children"]
    review = current.get("existing_children_review")
    external_decisions = [] if review is None else [item for item in review["decisions"] if item["disposition"] == "keep-external"]
    expected_count = len(current["children"]) + len(external_decisions)
    if not isinstance(children, list) or len(children) != expected_count:
        fail("readback must contain every managed and reviewed external child exactly once")
    by_id = {positive_int(item.get("id"), "child.id"): item for item in children if isinstance(item, dict)}
    if len(by_id) != len(children):
        fail("readback child IDs must be unique")
    for child in current["children"]:
        remote_id = child_remote_id(state, child["key"])
        if remote_id not in by_id:
            fail("readback is missing a published child")
        compare_issue(child, by_id[remote_id], baseline, current["native_fields"])
    if review is not None:
        evidence_path = Path(review["snapshot_path"])
        if file_digest(evidence_path) != review["snapshot_sha256"]:
            fail("existing children evidence changed after approval")
        original = load_json(evidence_path)
        original_by_id = {item["id"]: item for item in original["children"]}
        for decision in review["decisions"]:
            if decision["disposition"] != "adopt":
                continue
            issue_id = decision["issue_id"]
            original_relations = original_by_id[issue_id].get("relations", [])
            current_relations = by_id[issue_id].get("relations", [])
            if any(relation not in current_relations for relation in original_relations):
                fail("adopted child lost a pre-existing relation")
        for decision in external_decisions:
            issue_id = decision["issue_id"]
            if issue_id not in by_id or digest(external_issue_fingerprint(by_id[issue_id], current["native_fields"]["project_id"], baseline["issue_id"])) != decision["issue_sha256"] or external_issue_fingerprint(by_id[issue_id], current["native_fields"]["project_id"], baseline["issue_id"]) != external_issue_fingerprint(original_by_id[issue_id], current["native_fields"]["project_id"], baseline["issue_id"]):
                fail("reviewed external child changed or disappeared from readback")
    for relation in current["relations"]:
        source_id, target_id = relation_ids(state, relation)
        target = by_id[target_id]
        source = by_id[source_id]
        present_target, _ = relation_present({"issue": target}, source_id, target_id)
        present_source, _ = relation_present({"issue": source}, source_id, target_id)
        if not (present_target or present_source):
            fail("readback is missing a required DEV blocks QA relation")
    completed_at = require_timestamp(arguments.at, "completed_at")
    state["readback"] = {"path": str(snapshot_path.absolute()), "sha256": file_digest(snapshot_path), "observed_at": completed_at}
    state["completed_at"] = completed_at
    state["status"] = "completed"
    state["status_history"].append({"status": "completed", "recorded_at": completed_at})
    validate_publication_state(state)
    atomic_write(path, canonical_bytes(state) + b"\n")
    print(json.dumps({"status": "completed", "child_ids": sorted(by_id)}))


def command_validate(arguments: argparse.Namespace) -> None:
    current = load_json(Path(arguments.state))
    validate_publication_state(current)
    if arguments.previous:
        previous = load_json(Path(arguments.previous))
        validate_publication_state(previous)
        if current["revisions"][:len(previous["revisions"])] != previous["revisions"]:
            fail("publication revision history is not append-only")
        if current["approvals"][:len(previous["approvals"])] != previous["approvals"] and not all(
            old == new or (old | {"status": "invalidated"}) == new
            for old, new in zip(previous["approvals"], current["approvals"])
        ):
            fail("publication approval history was rewritten")
        if current["status_history"][:len(previous["status_history"])] != previous["status_history"]:
            fail("publication status history was rewritten")
        for key, value in previous["operations"].items():
            if key not in current["operations"] or current["operations"][key]["observations"][:len(value["observations"])] != value["observations"]:
                fail("publication operation history was rewritten")
            old_attempts = value["attempts"]
            new_attempts = current["operations"][key]["attempts"]
            if len(new_attempts) < len(old_attempts) or new_attempts[:max(0, len(old_attempts) - 1)] != old_attempts[:-1]:
                fail("publication attempt history was rewritten")
            if old_attempts:
                old_last = old_attempts[-1]
                new_last = new_attempts[len(old_attempts) - 1]
                if new_last != old_last:
                    stable = {field: old_last[field] for field in ("id", "attempted_at", "payload_sha256", "observations_before")}
                    if old_last["outcome"] != "in-flight" or any(new_last.get(field) != expected for field, expected in stable.items()) or new_last.get("outcome") not in {"completed", "failed", "unknown"}:
                        fail("publication attempt history was rewritten")
        if previous["readback"] is not None and current["readback"] != previous["readback"]:
            fail("publication readback was rewritten")
    print("valid")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(required=True)
    prepare = commands.add_parser("prepare")
    prepare.add_argument("state"); prepare.add_argument("plan"); prepare.add_argument("--slices-state", required=True)
    prepare.add_argument("--preview", required=True); prepare.add_argument("--descriptions-dir", required=True)
    prepare.add_argument("--actor", required=True); prepare.add_argument("--at", required=True); prepare.add_argument("--reason", required=True)
    prepare.set_defaults(run=command_prepare)
    approve = commands.add_parser("approve")
    approve.add_argument("state"); approve.add_argument("--actor", required=True); approve.add_argument("--at", required=True); approve.set_defaults(run=command_approve)
    create = commands.add_parser("begin-create")
    create.add_argument("state"); create.add_argument("--key", required=True); create.add_argument("--at", required=True); create.set_defaults(run=command_begin_create)
    finish_create = commands.add_parser("finish-create")
    finish_create.add_argument("state"); finish_create.add_argument("--key", required=True); finish_create.add_argument("--attempt", type=int, required=True)
    finish_create.add_argument("--outcome", choices=("completed", "failed", "unknown"), required=True); finish_create.add_argument("--issue-id", type=int)
    finish_create.add_argument("--error-code"); finish_create.add_argument("--message"); finish_create.add_argument("--at", required=True); finish_create.set_defaults(run=command_finish_create)
    observe_create = commands.add_parser("observe-create")
    observe_create.add_argument("state"); observe_create.add_argument("--key", required=True); observe_create.add_argument("--outcome", choices=("matched", "absent"), required=True)
    observe_create.add_argument("--snapshot", required=True); observe_create.add_argument("--at", required=True); observe_create.set_defaults(run=command_observe_create)
    relation = commands.add_parser("begin-relation")
    relation.add_argument("state"); relation.add_argument("--key", required=True); relation.add_argument("--at", required=True); relation.set_defaults(run=command_begin_relation)
    finish_relation = commands.add_parser("finish-relation")
    finish_relation.add_argument("state"); finish_relation.add_argument("--key", required=True); finish_relation.add_argument("--attempt", type=int, required=True)
    finish_relation.add_argument("--outcome", choices=("completed", "failed", "unknown"), required=True); finish_relation.add_argument("--relation-id", type=int)
    finish_relation.add_argument("--error-code"); finish_relation.add_argument("--message"); finish_relation.add_argument("--at", required=True); finish_relation.set_defaults(run=command_finish_relation)
    observe_relation = commands.add_parser("observe-relation")
    observe_relation.add_argument("state"); observe_relation.add_argument("--key", required=True); observe_relation.add_argument("--outcome", choices=("matched", "absent"), required=True)
    observe_relation.add_argument("--snapshot", required=True); observe_relation.add_argument("--at", required=True); observe_relation.set_defaults(run=command_observe_relation)
    complete = commands.add_parser("complete")
    complete.add_argument("state"); complete.add_argument("--readback", required=True); complete.add_argument("--at", required=True); complete.set_defaults(run=command_complete)
    validate = commands.add_parser("validate")
    validate.add_argument("state"); validate.add_argument("--previous"); validate.set_defaults(run=command_validate)
    return parser


def main() -> int:
    try:
        arguments = build_parser().parse_args()
        arguments.run(arguments)
    except (ContractError, OSError, ValueError, TypeError, KeyError, json.JSONDecodeError, UnicodeDecodeError) as error:
        print(f"invalid: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
