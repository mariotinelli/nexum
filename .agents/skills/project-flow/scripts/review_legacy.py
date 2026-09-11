"""Validate explicit enrichment without discarding legacy execution history."""


def preserved(old, new, label):
    if isinstance(old, dict):
        if not isinstance(new, dict):
            raise ValueError(f"legacy review lost {label}")
        for key, value in old.items():
            if key not in new:
                raise ValueError(f"legacy review lost {label}.{key}")
            preserved(value, new[key], f"{label}.{key}")
    elif isinstance(old, list):
        if not isinstance(new, list) or new[:len(old)] != old:
            raise ValueError(f"legacy review rewrote {label}")
    elif old != new:
        raise ValueError(f"legacy review rewrote {label}")


def validate_scope_revision(previous, current, draft=False):
    """Revised product decisions retain an exact snapshot of their previous state."""
    snapshot = current.get("legacy_review", {})
    if set(snapshot) != {"previous_state", "reason"} or snapshot["previous_state"] != previous:
        raise ValueError("legacy revision must retain the exact previous state")
    if not isinstance(snapshot["reason"], str) or not snapshot["reason"].strip():
        raise ValueError("legacy revision requires a reason")
    if current["phase"] != "paused" or not current["pauses"] or current["pauses"][-1].get("kind") != "catalog-change":
        raise ValueError("legacy revision requires a catalog-change pause")
    mutable = {
        "schema_version", "approvals", "catalog", "phase", "completed_phases", "first_item",
        "dependency_graph", "parallel_ready_groups", "suggested_order", "candidates",
        "source_allocation", "item_progress", "relations",
    }
    for key, value in previous.items():
        if key not in mutable:
            preserved(value, current.get(key), key)
    items = {item["id"]: item for item in current["catalog"]}
    previous_progress = {record["catalog_item_id"]: record for record in previous.get("item_progress", [])}
    for old in previous["catalog"]:
        new = items.get(old["id"])
        if new is None or new["type"] != old["type"]:
            raise ValueError("legacy revision must retain every item ID and type")
        if old.get("lifecycle") == "retired" and new["lifecycle"] != "retired":
            raise ValueError("legacy revision cannot reactivate a retired item")
        if old.get("lifecycle") != "retired" and new["lifecycle"] == "retired":
            progress = previous_progress.get(old["id"], {})
            retained = ("issue_id", "artifact_path", "state_path", "requirement_phase", "started_at", "completed_at")
            if old.get("status") != "pending" or progress.get("status") != "pending" or any(progress.get(field) is not None for field in retained):
                raise ValueError("only unstarted, unpublished catalog items can be retired by legacy review")
        if new["lifecycle"] == "retired":
            for key, value in old.items():
                if key not in {"status", "lifecycle"}:
                    preserved(value, new.get(key), f"retired item {old['id']}.{key}")
    for collection, key in (("candidates", "id"), ("source_allocation", "source_id")):
        if not {record[key] for record in previous.get(collection, [])} <= {record[key] for record in current[collection]}:
            raise ValueError(f"legacy revision lost {collection} identities")
    progress = {record["catalog_item_id"]: record for record in current["item_progress"]}
    for old in previous.get("item_progress", []):
        new = progress.get(old["catalog_item_id"], {})
        for key, value in old.items():
            if key != "status":
                preserved(value, new.get(key), f"item progress {old['catalog_item_id']}.{key}")
        if new.get("status") != old["status"] and new.get("status") != "retired":
            raise ValueError("legacy revision cannot advance or reset item progress")
    validate_relation_history(previous.get("relations", []), current["relations"])
    if not draft and len(current["catalog_changes"]) <= len(previous.get("catalog_changes", [])):
        raise ValueError("legacy revision requires an attributed catalog change")


def validate_relation_history(previous, current, allow_progress=False):
    relations = {relation["stable_key"]: relation for relation in current}
    for old in previous:
        new = relations.get(old["stable_key"])
        if new == old:
            continue
        if allow_progress and old["status"] == "planned" and new and new["status"] in {"planned", "completed"}:
            identity = ("stable_key", "from_item_id", "to_item_id", "relation_type")
            endpoints = ("from_issue_id", "to_issue_id", "approval_id")
            same_identity = all(new[key] == old[key] for key in identity)
            retained_endpoints = all(old[key] is None or new[key] == old[key] for key in endpoints)
            pending = new["status"] == "planned" and new["reconciliation_status"] == "pending" and new["completed_at"] is None
            completed = new["status"] == "completed" and all(new[key] is not None for key in endpoints) and new["reconciliation_status"] == "completed" and new["completed_at"] is not None
            if same_identity and retained_endpoints and (pending or completed):
                continue
        if (
            old["status"] == "planned"
            and old["approval_id"] is None
            and old["completed_at"] is None
            and old["reconciliation_status"] == "pending"
            and new == {**old, "status": "retired"}
        ):
            continue
        raise ValueError("relation history must retain identities and published or approved operations")


def validate_review(previous, current, scope=False, draft=False):
    if previous["schema_version"] not in ({1, 2} if scope else {2, 3}) or current["schema_version"] != (3 if scope else 4):
        raise ValueError("unsupported explicit legacy review")
    if draft and not scope:
        raise ValueError("draft review is only supported for scopes")
    revision = scope and "legacy_review" in current
    if revision:
        validate_scope_revision(previous, current, draft=draft)
    exceptions = {"schema_version", "approvals"}
    if scope:
        exceptions |= {"catalog", "phase", "completed_phases", "first_item"}
    for key, value in previous.items():
        if key not in exceptions and not revision:
            preserved(value, current.get(key), key)
    old_approvals = {a["id"]: a for a in previous["approvals"]}
    current_approvals = {a["id"]: a for a in current["approvals"]}
    for approval_id, old in old_approvals.items():
        new = current_approvals.get(approval_id, {})
        if new.get("status") != "invalidated" or any(new.get(key) != value for key, value in old.items() if key != "status"):
            raise ValueError("legacy review must retain and invalidate incompatible approvals")
        if old.get("status") == "valid" and (not new.get("invalidated_reason") or not new.get("invalidated_at")):
            raise ValueError("legacy review must explain and date approval invalidation")
    if scope:
        items = {i["id"]: i for i in current["catalog"]}
        for old in previous["catalog"]:
            new = items.get(old["id"], {})
            for key, value in old.items():
                if key != "status" and not revision:
                    preserved(value, new.get(key), f"catalog.{old['id']}.{key}")
        expected = previous["completed_phases"]
        if previous["schema_version"] == 1:
            expected = [p for p in expected if p not in {"first-item-started", "first-item-completed"}]
        if current["completed_phases"] != expected:
            raise ValueError("legacy review changed completed facts")
        first = previous.get("first_item")
        if first:
            match = next((p for p in current["item_progress"] if p["catalog_item_id"] == first["catalog_item_id"]), {})
            for key in ("issue_id", "artifact_path", "state_path", "requirement_phase", "completed_at"):
                if key in first and match.get(key) != first[key]:
                    raise ValueError("legacy review lost first item issue, artifacts or progress")
        if draft and any(a["status"] == "valid" for a in current["approvals"]):
            raise ValueError("draft review must not contain valid approvals")
        if not draft and not any(a["kind"] == "complete-catalog-and-order" and a["status"] == "valid" and a["id"] not in old_approvals for a in current["approvals"]):
            raise ValueError("legacy review requires a new complete catalog approval")
    elif not any(a["status"] == "valid" and a["id"] not in old_approvals for a in current["approvals"]):
        raise ValueError("legacy review requires new approval")
