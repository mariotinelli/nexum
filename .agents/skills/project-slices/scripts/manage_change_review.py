#!/usr/bin/env python3
"""Record semantic requirement-change reviews without mutating tracker tasks."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

from manage_slices import (
    ContractError,
    atomic_write,
    canonical_bytes,
    digest,
    fail,
    file_digest,
    load_json,
    reject_secrets,
    require_text,
    require_timestamp,
    validate_feature_approval,
    validate_state as validate_slices_state,
)


IMPACT_KINDS = ("tasks", "acceptance_criteria", "coverage", "dependencies")


def exact(value: Any, fields: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != fields:
        fail(f"{label} fields are invalid")
    return value


def approved_sources(slices_path: Path, publication_path: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    slices = load_json(slices_path)
    validate_slices_state(slices)
    slicing = slices["revisions"][-1]
    approvals = [item for item in slices["approvals"] if item["status"] == "valid" and item["revision"] == slicing["number"]]
    if slices["status"] != "approved" or len(approvals) != 1:
        fail("change review requires the approved slicing revision")
    baseline = slicing.get("semantic_baseline")
    if not isinstance(baseline, dict) or baseline.get("semantic_model_sha256") != digest(baseline.get("semantic_model")):
        fail("approved slicing has no provable semantic baseline")

    publication = load_json(publication_path)
    try:
        from manage_publication import validate_publication_state
    except ImportError as error:
        fail(f"cannot load publication contract: {error}")
    # Publication artifact hashes describe the immutable initial materialization.
    # A completed revision application may have advanced the canonical files.
    validate_publication_state(publication, check_files=False)
    published = publication["revisions"][-1]
    publication_approvals = [
        item for item in publication["approvals"]
        if item["status"] == "valid" and item["revision"] == published["number"]
    ]
    if publication["status"] != "completed" or len(publication_approvals) != 1:
        fail("change review requires a completed approved publication")
    if published.get("semantic_baseline") != baseline:
        fail("publication is not bound to the approved slicing semantic baseline")
    if published["slicing_revision"] != slicing["number"] or published["slicing_approval_sha256"] != digest(approvals[0]):
        fail("publication references another slicing approval")
    return slices, slicing, publication, published


def baseline_inventory(slicing: dict[str, Any], published: dict[str, Any]) -> dict[str, set[str]]:
    model = slicing["semantic_baseline"]["semantic_model"]
    tasks = {item["key"] for item in published["children"]}
    criteria = {
        f"dev-{item['number']}:criterion-{index}"
        for item in model["slices"]
        for index, _criterion in enumerate(item["description"]["criteria"], start=1)
    }
    coverage = {item["requirement_id"] for item in model["coverage"]}
    dependencies = {item["key"] for item in published["relations"]}
    for item in model["slices"]:
        dependencies.update(f"dev-{item['number']}:external:{blocker['key']}" for blocker in item.get("external_blockers", []))
    return {"tasks": tasks, "acceptance_criteria": criteria, "coverage": coverage, "dependencies": dependencies}


def applied_inventory(feature_dir: Path, published: dict[str, Any], publication: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any] | None]:
    """Carry identities created by completed applications into the next review."""
    path = feature_dir / ".flow" / "slices-revision-application.json"
    if not path.exists():
        return published, None
    application = load_json(path)
    if application["status"] != "completed":
        review_path = feature_dir / ".flow" / "slices-change-review.json"
        prior = load_json(review_path)["revisions"][-1]["baseline"].get("application") if review_path.exists() else None
        if prior is None:
            return published, None
        path = Path(prior["path"])
        application = load_json(path)
    from manage_revision_application import validate_state as validate_application
    validate_application(application, check_authority=False)
    if file_digest(Path(application["readback"]["path"])) != application["readback"]["sha256"]:
        fail("completed application readback is stale or tampered")
    effective = copy.deepcopy(published)
    children = {item["key"]: item for item in effective["children"]}
    edges = {item["key"]: item for item in effective["relations"]}
    remote_edges = {key.removeprefix("relation:"): item.get("remote_id") for key, item in publication["operations"].items() if key.startswith("relation:")}
    for revision in application["revisions"]:
        for operation in revision["operations"]:
            record = application["operations"].get(operation["key"])
            if record is None or record["status"] != "completed":
                continue
            if operation["action"] == "create":
                children[operation["task_key"]] = {"key": operation["task_key"], "source": "adopted", "remote_id": record["remote_id"]}
            elif operation["action"] == "relation-add":
                edges[operation["key"]] = {"key": operation["key"]}
                remote_edges[operation["key"]] = record["remote_id"]
            elif operation["action"] == "relation-remove":
                for key in list(edges):
                    if remote_edges.get(key) == operation["relation_id"]:
                        del edges[key]
    effective["children"] = list(children.values())
    effective["relations"] = list(edges.values())
    frozen = freeze_evidence(path, feature_dir / ".flow" / "review-evidence")
    return effective, {"path": str(frozen), "sha256": file_digest(frozen)}


def validate_impact(impact: Any, inventory: dict[str, set[str]], classification: str) -> dict[str, Any]:
    fields = {f"{side}_{kind}" for side in ("affected", "unaffected") for kind in IMPACT_KINDS}
    exact(impact, fields, "impact")
    for kind in IMPACT_KINDS:
        seen: dict[str, set[str]] = {}
        for side in ("affected", "unaffected"):
            rows = impact[f"{side}_{kind}"]
            if not isinstance(rows, list):
                fail(f"impact.{side}_{kind} must be an array")
            ids: list[str] = []
            for index, row in enumerate(rows):
                exact(row, {"id", "reason"}, f"impact.{side}_{kind}[{index}]")
                ids.append(require_text(row["id"], f"impact.{side}_{kind}[{index}].id"))
                require_text(row["reason"], f"impact.{side}_{kind}[{index}].reason")
            if len(ids) != len(set(ids)):
                fail(f"impact.{side}_{kind} contains duplicate identifiers")
            seen[side] = set(ids)
        if seen["affected"] & seen["unaffected"] or seen["affected"] | seen["unaffected"] != inventory[kind]:
            fail(f"impact must classify every baseline {kind} exactly once")
        if classification == "editorial" and seen["affected"]:
            fail("editorial review cannot mark functional artifacts as affected")
    if classification == "functional" and not impact["affected_tasks"]:
        fail("functional review requires at least one affected task")
    return impact


def review_digest(revision: dict[str, Any]) -> str:
    return digest({
        "review_id": revision["review_id"],
        "baseline": revision["baseline"],
        "current_requirement": revision["current_requirement"],
        "classification": revision["classification"],
        "summary": revision["summary"],
        "changes": revision["changes"],
        "impact": revision["impact"],
        "preservation": revision["preservation"],
    })


def freeze_evidence(path: Path, directory: Path) -> Path:
    """Keep content-addressed evidence independent of mutable working files."""
    target = directory / (file_digest(path) + path.suffix)
    if target.exists():
        if target.is_symlink() or target.read_bytes() != path.read_bytes():
            fail("immutable evidence differs")
    else:
        atomic_write(target, path.read_bytes())
    return target.absolute()


def validate_state(state: dict[str, Any], *, check_files: bool = True, check_current: bool = True) -> None:
    exact(state, {"schema_version", "status", "review_id", "revisions", "decisions", "authorizations"}, "change review state")
    reject_secrets(state, "change review state")
    if state["schema_version"] != 1 or state["status"] not in {"pending", "approved", "rejected", "authorized"}:
        fail("unsupported change review state")
    if not isinstance(state["revisions"], list) or not state["revisions"]:
        fail("change review requires revision history")
    for number, revision in enumerate(state["revisions"], start=1):
        exact(revision, {
            "number", "review_id", "recorded_by", "recorded_at", "reason", "baseline",
            "current_requirement", "classification", "summary", "changes", "impact",
            "preservation", "review_sha256",
        }, f"change review revision {number}")
        if revision["number"] != number or (number == len(state["revisions"]) and revision["review_id"] != state["review_id"]):
            fail("change review revision identity is invalid")
        require_text(revision["recorded_by"], "revision.recorded_by")
        require_timestamp(revision["recorded_at"], "revision.recorded_at")
        require_text(revision["reason"], "revision.reason")
        if revision["classification"] not in {"editorial", "functional"}:
            fail("semantic classification must be editorial or functional")
        require_text(revision["summary"], "revision.summary")
        if not isinstance(revision["changes"], list) or not revision["changes"]:
            fail("semantic review requires explicit changes")
        for change in revision["changes"]:
            exact(change, {"id", "classification", "before", "after", "rationale"}, "semantic change")
            if change["classification"] not in {"editorial", "functional"}:
                fail("semantic change classification is invalid")
            for field in ("id", "before", "after", "rationale"):
                require_text(change[field], f"semantic change.{field}")
        if revision["classification"] == "editorial" and any(item["classification"] != "editorial" for item in revision["changes"]):
            fail("editorial review contains a functional change")
        if revision["classification"] == "functional" and not any(item["classification"] == "functional" for item in revision["changes"]):
            fail("functional review contains no functional change")
        baseline_fields = {
            "slices_state_path", "slices_state_sha256", "slicing_revision", "slicing_approval_sha256",
            "publication_state_path", "publication_state_sha256", "publication_revision", "publication_approval_sha256",
            "requirement_sha256", "semantic_model_sha256",
        }
        if "application" in revision["baseline"]:
            baseline_fields.add("application")
        baseline = exact(revision["baseline"], baseline_fields, "review baseline")
        current_fields = {
            "path", "sha256", "state_path", "state_sha256", "approval_sha256",
        }
        if "source_path" in revision["current_requirement"]:
            current_fields |= {"source_path", "source_state_path"}
        current = exact(revision["current_requirement"], current_fields, "current requirement")
        for evidence in (baseline, current):
            for key, value in evidence.items():
                if key.endswith("_path") or key == "path":
                    continue
                if key.endswith("_sha256") and (not isinstance(value, str) or len(value) != 64):
                    fail("review evidence hash is invalid")
        preservation = exact(revision["preservation"], {
            "published_children", "existing_children_review_sha256", "study_evidence_sha256",
            "divergence_state", "dependency_state",
        }, "preservation evidence")
        if not isinstance(preservation["published_children"], list):
            fail("preservation published children must be an array")
        if revision["review_sha256"] != review_digest(revision):
            fail("change review hash differs")
        if check_files:
            application = baseline.get("application")
            if application is not None and file_digest(Path(application["path"])) != application["sha256"]:
                fail("prior application evidence is stale or tampered")
            if check_current and number == len(state["revisions"]):
                if file_digest(Path(current.get("source_path", current["path"]))) != current["sha256"]:
                    fail("current requirement evidence is stale or tampered")
                if file_digest(Path(current.get("source_state_path", current["state_path"]))) != current["state_sha256"]:
                    fail("current requirement approval state is stale or tampered")
            for path_key, sha_key in (("slices_state_path", "slices_state_sha256"), ("publication_state_path", "publication_state_sha256")):
                path = Path(baseline[path_key])
                if file_digest(path) != baseline[sha_key]:
                    fail("semantic baseline evidence is stale or tampered")
            if file_digest(Path(current["path"])) != current["sha256"]:
                fail("current requirement evidence is stale or tampered")
            state_path = Path(current["state_path"])
            if file_digest(state_path) != current["state_sha256"]:
                fail("current requirement approval state is stale or tampered")
            feature_state = load_json(state_path)
            approvals = [
                item for item in feature_state.get("approvals", [])
                if item.get("kind") == "requirement" and item.get("status") == "valid"
                and item.get("subject_sha256") == current["sha256"]
            ]
            if len(approvals) != 1 or digest(approvals[0]) != current["approval_sha256"]:
                fail("current requirement approval is stale or tampered")
            for key in ("divergence_state", "dependency_state"):
                evidence = preservation[key]
                if evidence is not None and file_digest(Path(evidence["path"])) != evidence["sha256"]:
                    fail("preserved workflow evidence is stale or tampered")
    decided_revisions: set[int] = set()
    for decision in state["decisions"]:
        exact(decision, {"revision", "review_sha256", "decision", "decided_by", "decided_at", "reason"}, "change review decision")
        revision_number = decision["revision"]
        if not isinstance(revision_number, int) or revision_number < 1 or revision_number > len(state["revisions"]):
            fail("change review decision references an unknown revision")
        if revision_number in decided_revisions or decision["review_sha256"] != state["revisions"][revision_number - 1]["review_sha256"]:
            fail("change review decision is duplicated or bound to another revision")
        decided_revisions.add(revision_number)
        if decision["decision"] not in {"approved", "rejected"}:
            fail("change review decision is invalid")
        require_text(decision["decided_by"], "decision.decided_by")
        require_timestamp(decision["decided_at"], "decision.decided_at")
        require_text(decision["reason"], "decision.reason")
    authorized_revisions: set[int] = set()
    for authorization in state["authorizations"]:
        exact(authorization, {"revision", "review_sha256", "affected_task_keys", "authorized_at"}, "change authorization")
        revision_number = authorization["revision"]
        if not isinstance(revision_number, int) or revision_number in authorized_revisions or revision_number < 1 or revision_number > len(state["revisions"]):
            fail("change authorization is duplicated or references an unknown revision")
        authorized_revisions.add(revision_number)
        revision = state["revisions"][revision_number - 1]
        approved = any(item["revision"] == revision_number and item["decision"] == "approved" for item in state["decisions"])
        affected = {item["id"] for item in revision["impact"]["affected_tasks"]}
        keys = authorization["affected_task_keys"]
        if revision["classification"] != "functional" or not approved or authorization["review_sha256"] != revision["review_sha256"]:
            fail("change authorization lacks its bound functional approval")
        if not isinstance(keys, list) or not keys or len(keys) != len(set(keys)) or set(keys) - affected:
            fail("change authorization contains invalid affected task keys")
        require_timestamp(authorization["authorized_at"], "authorization.authorized_at")
    current_number = len(state["revisions"])
    current_decisions = [item for item in state["decisions"] if item["revision"] == current_number]
    if state["status"] == "pending" and current_decisions:
        fail("pending review cannot have a decision")
    if state["status"] != "pending" and len(current_decisions) != 1:
        fail("decided review requires exactly one current decision")
    if state["status"] == "authorized" and len([item for item in state["authorizations"] if item["revision"] == current_number]) != 1:
        fail("authorized review requires one current authorization")


def preservation(feature_dir: Path, slicing: dict[str, Any], publication: dict[str, Any], published: dict[str, Any]) -> dict[str, Any]:
    children = []
    for child in published["children"]:
        operation = publication["operations"].get(f"create:{child['key']}")
        remote_id = child.get("remote_id") if child.get("source") == "adopted" else (operation or {}).get("remote_id")
        children.append({"key": child["key"], "source": child.get("source", "create"), "remote_id": remote_id})
    review = published.get("existing_children_review")
    study = slicing["proposal"].get("study_evidence", [])
    result: dict[str, Any] = {
        "published_children": children,
        "existing_children_review_sha256": digest(review) if review is not None else None,
        "study_evidence_sha256": digest(study),
        "divergence_state": None,
        "dependency_state": None,
    }
    for filename, key in (("slices-divergence.json", "divergence_state"), ("slices-dependencies.json", "dependency_state")):
        path = feature_dir / ".flow" / filename
        if path.is_file():
            result[key] = {"path": str(path.absolute()), "sha256": file_digest(path)}
    return result


def render_preview(revision: dict[str, Any]) -> str:
    labels = {
        "tasks": "Tarefas",
        "acceptance_criteria": "Critérios de aceite",
        "coverage": "Itens de cobertura",
        "dependencies": "Dependências",
    }
    lines = [
        "# Revisão de mudança do requisito", "",
        f"Classificação semântica: **{revision['classification']}**  ",
        f"Revisão: {revision['number']}  ",
        f"Hash da revisão: `{revision['review_sha256']}`", "",
        "## Resumo", "", revision["summary"], "", "## Mudanças observadas", "",
    ]
    for change in revision["changes"]:
        lines.extend([
            f"### {change['id']} — {change['classification']}", "",
            f"- Antes: {change['before']}", f"- Agora: {change['after']}",
            f"- Justificativa: {change['rationale']}", "",
        ])
    for side, title in (("affected", "Impactos localizados"), ("unaffected", "Itens que permanecem válidos")):
        lines.extend([f"## {title}", ""])
        for kind in IMPACT_KINDS:
            lines.extend([f"### {labels[kind]}", ""])
            rows = revision["impact"][f"{side}_{kind}"]
            lines.extend(f"- `{item['id']}` — {item['reason']}" for item in rows)
            if not rows:
                lines.append("- Nenhum.")
            lines.append("")
    lines.extend([
        "## Preservação", "",
        "Filhas publicadas, decisões sobre filhas existentes/externas, estudos, divergências e evidências de dependência permanecem intactos enquanto esta revisão estiver pendente ou rejeitada.", "",
    ])
    return "\n".join(lines)


def command_prepare(arguments: argparse.Namespace) -> None:
    state_path = Path(arguments.state)
    feature_dir = state_path.parent.parent
    if state_path != feature_dir / ".flow" / "slices-change-review.json":
        fail("change review state must use .flow/slices-change-review.json")
    slices_path = Path(arguments.slices_state).absolute()
    publication_path = Path(arguments.publication_state).absolute()
    current_path = Path(arguments.current_requirement).absolute()
    preview_path = Path(arguments.preview).absolute()
    if preview_path != (feature_dir / "slices" / "change-review.md").absolute():
        fail("change review preview must use slices/change-review.md")
    plan = load_json(Path(arguments.plan))
    exact(plan, {"classification", "summary", "changes", "impact"}, "change review plan")
    slices, slicing, publication, published = approved_sources(slices_path, publication_path)
    canonical, feature_state_path, _feature_state, approval, _content = validate_feature_approval(feature_dir, permit_divergence=True)
    if canonical.absolute() != current_path:
        fail("current requirement path differs from the approved Feature")
    current_sha = file_digest(current_path)
    if approval.get("subject_sha256") != current_sha:
        fail("current requirement version lacks matching approval")
    baseline = slicing["semantic_baseline"]
    if current_sha == baseline["requirement_sha256"]:
        fail("current requirement is identical to the semantic baseline version")
    classification = plan.get("classification")
    if classification not in {"editorial", "functional"}:
        fail("classification must be editorial or functional")
    effective, application_evidence = applied_inventory(feature_dir, published, publication)
    inventory = baseline_inventory(slicing, effective)
    impact = validate_impact(plan.get("impact"), inventory, classification)
    review_id = digest({
        "issue_id": slicing["proposal"]["feature"]["issue_id"],
        "baseline_requirement_sha256": baseline["requirement_sha256"],
        "current_requirement_sha256": current_sha,
    })
    slicing_approval = next(item for item in slices["approvals"] if item["status"] == "valid")
    publication_approval = next(item for item in publication["approvals"] if item["status"] == "valid")
    revision = {
        "number": 1,
        "review_id": review_id,
        "recorded_by": require_text(arguments.actor, "recorded_by"),
        "recorded_at": require_timestamp(arguments.at, "recorded_at"),
        "reason": require_text(arguments.reason, "reason"),
        "baseline": {
            "slices_state_path": str(slices_path), "slices_state_sha256": file_digest(slices_path),
            "slicing_revision": slicing["number"], "slicing_approval_sha256": digest(slicing_approval),
            "publication_state_path": str(publication_path), "publication_state_sha256": file_digest(publication_path),
            "publication_revision": published["number"], "publication_approval_sha256": digest(publication_approval),
            "requirement_sha256": baseline["requirement_sha256"],
            "semantic_model_sha256": baseline["semantic_model_sha256"],
        },
        "current_requirement": {
            "path": str(freeze_evidence(current_path, feature_dir / ".flow" / "review-evidence")), "sha256": current_sha,
            "state_path": str(freeze_evidence(feature_state_path, feature_dir / ".flow" / "review-evidence")), "state_sha256": file_digest(feature_state_path),
            "source_path": str(current_path), "source_state_path": str(feature_state_path.absolute()),
            "approval_sha256": digest(approval),
        },
        "classification": classification,
        "summary": require_text(plan.get("summary"), "summary"),
        "changes": copy.deepcopy(plan.get("changes")),
        "impact": copy.deepcopy(impact),
        "preservation": preservation(feature_dir, slicing, publication, effective),
    }
    if application_evidence is not None:
        revision["baseline"]["application"] = application_evidence
    revision["review_sha256"] = review_digest(revision)
    if state_path.exists():
        state = load_json(state_path)
        validate_state(state, check_current=False)
        current = state["revisions"][-1]
        if current["review_sha256"] == revision["review_sha256"]:
            print(json.dumps({"status": state["status"], "review_id": review_id, "revision": current["number"], "review_sha256": current["review_sha256"]}))
            return
        revision["number"] = len(state["revisions"]) + 1
        state["revisions"].append(revision)
        state["review_id"] = review_id
        state["status"] = "pending"
    else:
        state = {"schema_version": 1, "status": "pending", "review_id": review_id, "revisions": [revision], "decisions": [], "authorizations": []}
    validate_state(state)
    atomic_write(state_path, json.dumps(state, ensure_ascii=False, indent=2).encode("utf-8") + b"\n")
    atomic_write(preview_path, render_preview(revision).encode("utf-8"))
    print(json.dumps({"status": "pending", "review_id": review_id, "revision": revision["number"], "review_sha256": revision["review_sha256"]}))


def command_decide(arguments: argparse.Namespace) -> None:
    state_path = Path(arguments.state)
    state = load_json(state_path)
    validate_state(state)
    if state["status"] != "pending":
        fail("only a pending review can be decided")
    current = state["revisions"][-1]
    slices = load_json(Path(current["baseline"]["slices_state_path"]))
    slicing_approval = next(item for item in slices["approvals"] if item["status"] == "valid")
    actor = require_text(arguments.actor, "decided_by")
    if actor != slicing_approval["approved_by"]:
        fail("only the tech lead who owns the approved slicing may decide this review")
    decision = arguments.decision
    state["decisions"].append({
        "revision": current["number"], "review_sha256": current["review_sha256"],
        "decision": decision, "decided_by": actor,
        "decided_at": require_timestamp(arguments.at, "decided_at"),
        "reason": require_text(arguments.reason, "decision reason"),
    })
    state["status"] = decision
    validate_state(state)
    atomic_write(state_path, json.dumps(state, ensure_ascii=False, indent=2).encode("utf-8") + b"\n")
    print(json.dumps({"status": decision, "review_id": state["review_id"], "review_sha256": current["review_sha256"]}))


def command_authorize(arguments: argparse.Namespace) -> None:
    state_path = Path(arguments.state)
    state = load_json(state_path)
    validate_state(state)
    current = state["revisions"][-1]
    if state["status"] not in {"approved", "authorized"}:
        fail("affected mutation requires a specific approved semantic review")
    if current["classification"] != "functional":
        fail("editorial change does not authorize or require task mutation")
    requested = sorted(item for item in arguments.keys.split(",") if item)
    affected = [item["id"] for item in current["impact"]["affected_tasks"]]
    if not requested or len(requested) != len(set(requested)) or set(requested) - set(affected):
        fail("authorization may contain only affected task keys")
    existing = next((item for item in state["authorizations"] if item["revision"] == current["number"] and item["affected_task_keys"] == requested), None)
    if existing is None:
        state["authorizations"].append({
            "revision": current["number"], "review_sha256": current["review_sha256"],
            "affected_task_keys": requested, "authorized_at": require_timestamp(arguments.at, "authorized_at"),
        })
        state["status"] = "authorized"
        validate_state(state)
        atomic_write(state_path, json.dumps(state, ensure_ascii=False, indent=2).encode("utf-8") + b"\n")
        existing = state["authorizations"][-1]
    print(json.dumps({
        "status": "authorized", "review_id": state["review_id"], "review_sha256": current["review_sha256"],
        "affected_task_keys": existing["affected_task_keys"],
        "instruction": "Prepare fresh slicing/publication revisions and bound tech-lead approvals for these keys; this helper does not update or remove tasks.",
    }))


def command_validate(arguments: argparse.Namespace) -> None:
    state = load_json(Path(arguments.state))
    validate_state(state)
    print(json.dumps({"status": "valid", "workflow_status": state["status"], "review_id": state["review_id"], "revision": len(state["revisions"])}))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    prepare = commands.add_parser("prepare")
    prepare.add_argument("state"); prepare.add_argument("plan"); prepare.add_argument("--slices-state", required=True); prepare.add_argument("--publication-state", required=True)
    prepare.add_argument("--current-requirement", required=True); prepare.add_argument("--preview", required=True); prepare.add_argument("--actor", required=True); prepare.add_argument("--at", required=True); prepare.add_argument("--reason", required=True); prepare.set_defaults(run=command_prepare)
    decide = commands.add_parser("decide")
    decide.add_argument("state"); decide.add_argument("--decision", choices=("approved", "rejected"), required=True); decide.add_argument("--actor", required=True); decide.add_argument("--at", required=True); decide.add_argument("--reason", required=True); decide.set_defaults(run=command_decide)
    authorize = commands.add_parser("authorize")
    authorize.add_argument("state"); authorize.add_argument("--keys", required=True); authorize.add_argument("--at", required=True); authorize.set_defaults(run=command_authorize)
    validate = commands.add_parser("validate")
    validate.add_argument("state"); validate.set_defaults(run=command_validate)
    return parser


def main() -> int:
    try:
        arguments = build_parser().parse_args()
        arguments.run(arguments)
        return 0
    except ContractError as error:
        print(f"invalid: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
