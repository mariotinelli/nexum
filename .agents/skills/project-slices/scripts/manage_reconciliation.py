#!/usr/bin/env python3
"""Reconcile completed legacy Project Slices publications into canonical local tasks."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

from manage_publication import (
    atomic_batch_write,
    canonical_task_path,
    child_remote_id,
    compare_issue,
    exact,
    fail,
    named_id,
    positive_int,
    relation_ids,
    task_markdown,
    validate_publication_state,
)
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
)
from manage_study import compare_issue as compare_study_issue
from manage_study import validate_state as validate_study_state


def contained_path(feature_dir: Path, value: Any, directory: str, label: str) -> Path:
    path = (value if isinstance(value, Path) else Path(require_text(value, label))).absolute()
    try:
        relative = path.relative_to(feature_dir.absolute())
    except ValueError:
        fail(f"{label} must be inside the parent item directory")
    if not relative.parts or relative.parts[0] != directory or path.is_symlink():
        fail(f"{label} must be a regular path under {directory}")
    for parent in [path, *path.parents]:
        if parent == feature_dir.absolute().parent:
            break
        if parent.is_symlink():
            fail(f"{label} crosses a symbolic link")
    return path


def source_path(value: Any) -> tuple[Path, Path]:
    path = Path(require_text(value, "legacy source")).absolute()
    if path.parent.name != ".flow" or path.is_symlink() or not path.is_file():
        fail("legacy source must be a regular state file under .flow")
    feature_dir = path.parent.parent.absolute()
    contained_path(feature_dir, path, ".flow", "legacy source")
    return feature_dir, path


def parent_matches(parent: Any, baseline: dict[str, Any]) -> None:
    if not isinstance(parent, dict):
        fail("reconciliation readback parent must be structured")
    if positive_int(parent.get("id"), "parent.id") != baseline["issue_id"]:
        fail("reconciliation readback belongs to another parent")
    if "status_id" in baseline and (named_id(parent, "status") != baseline["status_id"] or require_text(parent.get("status", {}).get("name"), "parent.status.name") != baseline["status_name"]):
        fail("parent execution status changed")
    if "status_id" not in baseline and "project_id" in baseline and named_id(parent, "project") != baseline["project_id"]:
        fail("parent project changed")


def publication_artifacts(state: dict[str, Any], snapshot: dict[str, Any], feature_dir: Path) -> list[dict[str, Any]]:
    if state.get("schema_version") != 1 or state.get("status") != "completed":
        fail("ordinary reconciliation requires a completed legacy publication")
    validate_publication_state(state)
    current = state["revisions"][-1]
    exact(snapshot, {"parent", "children"}, "publication reconciliation readback")
    parent_matches(snapshot["parent"], current["parent_baseline"])
    children = snapshot["children"]
    if not isinstance(children, list) or any(not isinstance(item, dict) for item in children):
        fail("publication reconciliation children must be a complete array")
    by_id: dict[int, dict[str, Any]] = {}
    for item in children:
        issue_id = positive_int(item.get("id"), "child.id")
        if issue_id in by_id:
            fail("publication reconciliation child IDs are ambiguous")
        by_id[issue_id] = item
    expected_ids = {child_remote_id(state, child["key"]) for child in current["children"]}
    if len(expected_ids) != len(current["children"]):
        fail("legacy publication has ambiguous remote child IDs")
    if set(by_id) != expected_ids:
        fail("publication reconciliation readback must contain every managed child exactly once")
    all_relations = [relation for issue in children for relation in require_relations(issue)]
    for child in current["children"]:
        if child.get("kind") not in {"dev", "qa"}:
            fail("legacy publication child kind is invalid")
        remote_id = child_remote_id(state, child["key"])
        compare_issue(child, by_id[remote_id], current["parent_baseline"], current["native_fields"])
    for relation in current["relations"]:
        source_id, target_id = relation_ids(state, relation)
        if not any(
            item.get("issue_id") == source_id
            and item.get("issue_to_id") == target_id
            and item.get("relation_type") == "blocks"
            for item in all_relations
        ):
            fail("publication reconciliation readback is missing an approved relation")
    artifacts = []
    for child in current["children"]:
        remote_id = child_remote_id(state, child["key"])
        issue = by_id[remote_id]
        artifacts.append(artifact_record(feature_dir, child["kind"], issue, all_relations))
    return artifacts


def require_relations(issue: dict[str, Any]) -> list[dict[str, Any]]:
    relations = issue.get("relations")
    if not isinstance(relations, list):
        fail("reconciliation readback requires complete child relations")
    if any(not isinstance(item, dict) for item in relations):
        fail("reconciliation relations must be structured")
    return relations


def study_artifacts(state: dict[str, Any], snapshot: dict[str, Any], feature_dir: Path) -> list[dict[str, Any]]:
    if state.get("schema_version") != 1 or state.get("status") not in {"awaiting-result", "result-recorded", "resumed"}:
        fail("Study reconciliation requires a completed legacy Study publication")
    validate_study_state(state)
    operation = state.get("operation")
    if not isinstance(operation, dict) or operation.get("status") != "completed":
        fail("legacy Study remote identity is not proven")
    exact(snapshot, {"parent", "study"}, "Study reconciliation readback")
    current = state["revisions"][-1]
    parent_matches(snapshot["parent"], current["parent_baseline"])
    issue = snapshot["study"]
    if not isinstance(issue, dict) or positive_int(issue.get("id"), "Study id") != operation["remote_id"]:
        fail("Study reconciliation readback has the wrong remote identity")
    compare_study_issue(current["study"], issue, current["native_fields"]["default_priority_id"])
    relations = require_relations(issue)
    return [artifact_record(feature_dir, "study", issue, relations)]


def artifact_record(feature_dir: Path, kind: str, issue: dict[str, Any], relations: list[dict[str, Any]]) -> dict[str, Any]:
    remote_id = positive_int(issue.get("id"), "canonical child.id")
    path = canonical_task_path(feature_dir, kind, remote_id, require_text(issue.get("subject"), "canonical child.subject"))
    content = task_markdown(issue, kind, relations).encode("utf-8")
    if path.is_file() and path.read_bytes() != content:
        fail(f"canonical task artifact conflicts with existing content: {path}")
    return {
        "kind": kind,
        "remote_id": remote_id,
        "path": str(path.absolute()),
        "sha256": hashlib.sha256(content).hexdigest(),
        "content": content.decode("utf-8"),
    }


def inspect(legacy: Path, readback: Path) -> tuple[str, list[dict[str, Any]]]:
    state = load_json(legacy)
    snapshot = load_json(readback)
    reject_secrets(snapshot, "legacy reconciliation readback")
    feature_dir = legacy.parent.parent.absolute()
    if "operations" in state:
        return "publication", publication_artifacts(state, snapshot, feature_dir)
    if "operation" in state and "result_history" in state:
        return "study", study_artifacts(state, snapshot, feature_dir)
    fail("legacy source is not a supported publication or Study state")


def preview_text(kind: str, legacy: Path, readback: Path, artifacts: list[dict[str, Any]]) -> str:
    lines = [
        "# Reconciliação local de publicação histórica", "",
        f"- Tipo de origem: `{kind}`",
        f"- Estado histórico: `{legacy}`",
        f"- SHA-256 do estado histórico: `{file_digest(legacy)}`",
        f"- Readback sanitizado: `{readback}`",
        f"- SHA-256 do readback: `{file_digest(readback)}`", "",
        "A decisão aprova somente a materialização local abaixo. O Redmine e os arquivos históricos permanecem inalterados.", "",
    ]
    for artifact in artifacts:
        lines.extend([
            f"## {artifact['kind'].upper()} #{artifact['remote_id']}", "",
            f"Destino exato: `{artifact['path']}`", "",
            f"SHA-256: `{artifact['sha256']}`", "",
            "```markdown", artifact["content"].rstrip(), "```", "",
        ])
    return "\n".join(lines)


def state_digest(state: dict[str, Any]) -> str:
    return digest({
        "source": state["source"],
        "readback": state["readback"],
        "artifacts": state["artifacts"],
        "preview": {"path": state["preview"]["path"], "sha256": state["preview"]["sha256"]},
    })


def validate_state(state: dict[str, Any], *, check_files: bool = True) -> None:
    exact(state, {"schema_version", "status", "source", "readback", "artifacts", "preview", "decision", "completed_at"}, "legacy reconciliation state")
    if state["schema_version"] != 1 or state["status"] not in {"prepared", "approved", "completed"}:
        fail("unsupported legacy reconciliation state")
    source = exact(state["source"], {"kind", "path", "sha256"}, "legacy reconciliation source")
    if source["kind"] not in {"publication", "study"}:
        fail("legacy reconciliation source kind is invalid")
    readback = exact(state["readback"], {"path", "sha256"}, "legacy reconciliation readback")
    preview = exact(state["preview"], {"path", "sha256", "decision_sha256"}, "legacy reconciliation preview")
    if not isinstance(state["artifacts"], list) or not state["artifacts"]:
        fail("legacy reconciliation requires canonical artifacts")
    identities = set()
    for artifact in state["artifacts"]:
        exact(artifact, {"kind", "remote_id", "path", "sha256", "content"}, "legacy reconciliation artifact")
        identity = (artifact["kind"], positive_int(artifact["remote_id"], "artifact remote_id"))
        if identity in identities or artifact["sha256"] != hashlib.sha256(artifact["content"].encode("utf-8")).hexdigest():
            fail("legacy reconciliation artifact identity or content is invalid")
        identities.add(identity)
    if preview["decision_sha256"] != state_digest(state):
        fail("legacy reconciliation decision no longer matches its exact preview")
    if check_files:
        for record, label in ((source, "legacy source"), (readback, "reconciliation readback"), (preview, "reconciliation preview")):
            path = Path(record["path"])
            if not path.is_file() or file_digest(path) != record["sha256"]:
                fail(f"{label} changed after the exact preview")
    decision = state["decision"]
    if state["status"] == "prepared":
        if decision is not None or state["completed_at"] is not None:
            fail("prepared reconciliation cannot carry a decision or completion")
    else:
        decision = exact(decision, {"decision_sha256", "approved_by", "approved_at"}, "legacy reconciliation decision")
        if decision["decision_sha256"] != preview["decision_sha256"]:
            fail("tech-lead decision is stale for the exact preview")
        require_text(decision["approved_by"], "approved_by")
        require_timestamp(decision["approved_at"], "approved_at")
        if state["status"] == "completed":
            require_timestamp(state["completed_at"], "completed_at")
        elif state["completed_at"] is not None:
            fail("approved reconciliation is not yet completed")
    reject_secrets(state, "legacy reconciliation state")


def command_prepare(arguments: argparse.Namespace) -> None:
    feature_dir, legacy = source_path(arguments.legacy)
    readback = contained_path(feature_dir, arguments.readback, ".work", "reconciliation readback")
    state_path = contained_path(feature_dir, arguments.state, ".flow", "reconciliation state")
    preview_path = contained_path(feature_dir, arguments.preview, "slices", "reconciliation preview")
    kind, artifacts = inspect(legacy, readback)
    preview = preview_text(kind, legacy, readback, artifacts).encode("utf-8")
    candidate = {
        "schema_version": 1,
        "status": "prepared",
        "source": {"kind": kind, "path": str(legacy), "sha256": file_digest(legacy)},
        "readback": {"path": str(readback), "sha256": file_digest(readback)},
        "artifacts": artifacts,
        "preview": {"path": str(preview_path), "sha256": hashlib.sha256(preview).hexdigest(), "decision_sha256": ""},
        "decision": None,
        "completed_at": None,
    }
    candidate["preview"]["decision_sha256"] = state_digest(candidate)
    if state_path.exists():
        existing = load_json(state_path)
        validate_state(existing)
        same = all(existing[field] == candidate[field] for field in ("source", "readback", "artifacts", "preview"))
        if not same:
            fail("another reconciliation already exists; preserve it and resolve the conflict")
        print(json.dumps({"status": existing["status"], "decision_sha256": existing["preview"]["decision_sha256"]}))
        return
    if preview_path.is_file() and preview_path.read_bytes() != preview:
        fail("reconciliation preview conflicts with existing content")
    validate_state(candidate, check_files=False)
    atomic_batch_write({preview_path: preview, state_path: canonical_bytes(candidate) + b"\n"})
    print(json.dumps({"status": "prepared", "decision_sha256": candidate["preview"]["decision_sha256"]}))


def current_inspection(state: dict[str, Any]) -> None:
    source = Path(state["source"]["path"])
    readback = Path(state["readback"]["path"])
    kind, artifacts = inspect(source, readback)
    if kind != state["source"]["kind"] or artifacts != state["artifacts"]:
        fail("legacy source or sanitized readback diverged from the approved preview")


def validate_command_state_path(path: Path, state: dict[str, Any]) -> None:
    feature_dir = Path(state["source"]["path"]).parent.parent.absolute()
    if contained_path(feature_dir, path, ".flow", "reconciliation state") != path.absolute():
        fail("reconciliation state path changed")


def command_approve(arguments: argparse.Namespace) -> None:
    path = Path(arguments.state)
    state = load_json(path)
    validate_state(state)
    validate_command_state_path(path, state)
    if state["status"] != "prepared":
        fail("only the current prepared reconciliation preview can be approved")
    current_inspection(state)
    state["decision"] = {
        "decision_sha256": state["preview"]["decision_sha256"],
        "approved_by": require_text(arguments.actor, "approved_by"),
        "approved_at": require_timestamp(arguments.at, "approved_at"),
    }
    state["status"] = "approved"
    validate_state(state)
    atomic_write(path, canonical_bytes(state) + b"\n")
    print(json.dumps({"status": "approved", "decision_sha256": state["preview"]["decision_sha256"]}))


def command_materialize(arguments: argparse.Namespace) -> None:
    path = Path(arguments.state)
    state = load_json(path)
    validate_state(state)
    validate_command_state_path(path, state)
    if state["status"] == "completed":
        print(json.dumps({"status": "completed", "artifacts": [item["path"] for item in state["artifacts"]]}))
        return
    if state["status"] != "approved":
        fail("materialization requires the tech lead's current exact-preview decision")
    current_inspection(state)
    outputs: dict[Path, bytes] = {}
    for artifact in state["artifacts"]:
        artifact_path = Path(artifact["path"])
        content = artifact["content"].encode("utf-8")
        if artifact_path.is_file() and artifact_path.read_bytes() != content:
            fail(f"canonical task artifact conflicts with existing content: {artifact_path}")
        outputs[artifact_path] = content
    state["status"] = "completed"
    state["completed_at"] = require_timestamp(arguments.at, "completed_at")
    validate_state(state)
    outputs[path] = canonical_bytes(state) + b"\n"
    atomic_batch_write(outputs)
    print(json.dumps({"status": "completed", "artifacts": [item["path"] for item in state["artifacts"]]}))


def command_validate(arguments: argparse.Namespace) -> None:
    path = Path(arguments.state)
    state = load_json(path)
    validate_state(state)
    validate_command_state_path(path, state)
    current_inspection(state)
    if state["status"] == "completed":
        for artifact in state["artifacts"]:
            path = Path(artifact["path"])
            if not path.is_file() or path.read_text(encoding="utf-8") != artifact["content"]:
                fail("materialized canonical artifact is missing or changed")
    print("valid")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(required=True)
    prepare = commands.add_parser("prepare")
    prepare.add_argument("state"); prepare.add_argument("--legacy", required=True); prepare.add_argument("--readback", required=True); prepare.add_argument("--preview", required=True)
    prepare.set_defaults(run=command_prepare)
    approve = commands.add_parser("approve")
    approve.add_argument("state"); approve.add_argument("--actor", required=True); approve.add_argument("--at", required=True); approve.set_defaults(run=command_approve)
    materialize = commands.add_parser("materialize")
    materialize.add_argument("state"); materialize.add_argument("--at", required=True); materialize.set_defaults(run=command_materialize)
    validate = commands.add_parser("validate")
    validate.add_argument("state"); validate.set_defaults(run=command_validate)
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
