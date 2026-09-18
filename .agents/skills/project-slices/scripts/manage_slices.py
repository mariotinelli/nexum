#!/usr/bin/env python3
"""Validate and persist Project Slices artifacts without remote access."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any


class ContractError(ValueError):
    pass


SECRET_KEY_PATTERN = re.compile(
    r"^(?:api[_-]?key|authorization|x-redmine-api-key|password|secret|access[_-]?token)$",
    re.IGNORECASE,
)
SECRET_VALUE_PATTERN = re.compile(
    r"(?:authorization\s*:\s*(?:bearer|basic)|x-redmine-api-key\s*:|api[_-]?key\s*[:=])",
    re.IGNORECASE,
)
SHA256_PATTERN = re.compile(r"^[a-f0-9]{64}$")
PREFIX_PATTERN = re.compile(r"^(?:\[[A-ZÀ-Ý0-9_-]+\]\s*)+")


def fail(message: str) -> None:
    raise ContractError(message)


def load_json(path: Path) -> dict[str, Any]:
    assert_safe_read(path)
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


def file_digest(path: Path) -> str:
    assert_safe_read(path)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def assert_safe_read(path: Path) -> None:
    if not path.is_file() or is_link_like(path):
        fail(f"regular non-symlink file required: {path}")
    for current in path.absolute().parents:
        if is_link_like(current):
            fail(f"symlink path component is not allowed: {current}")


def is_link_like(path: Path) -> bool:
    if path.is_symlink():
        return True
    try:
        attributes = os.lstat(path).st_file_attributes
    except (AttributeError, FileNotFoundError, OSError):
        return False
    return bool(attributes & 0x400)


def assert_safe_write(path: Path) -> None:
    absolute = path.absolute()
    for current in (absolute, *absolute.parents):
        if current.exists() and is_link_like(current):
            fail(f"symlink path component is not allowed: {current}")
        if current.exists() and current != absolute and not current.is_dir():
            fail(f"unsafe output path: {path}")
    if path.exists() and (is_link_like(path) or not path.is_file()):
        fail(f"regular output file required: {path}")


def atomic_write(path: Path, content: bytes) -> None:
    assert_safe_write(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.parent.is_symlink():
        fail(f"symlink output directory is not allowed: {path.parent}")
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
        except FileNotFoundError:
            pass
        raise


def require_exact_path(path: Path, expected: Path, label: str) -> None:
    if path.absolute() != expected.absolute():
        fail(f"{label} must be {expected}")


def require_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        fail(f"{label} must be a non-empty string")
    return value


def require_timestamp(value: Any, label: str) -> str:
    text = require_text(value, label)
    try:
        datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        fail(f"{label} must be an ISO-8601 timestamp")
    return text


def reject_secrets(value: Any, label: str = "document") -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if SECRET_KEY_PATTERN.fullmatch(str(key)):
                fail(f"{label} contains credential material")
            reject_secrets(item, label)
    elif isinstance(value, list):
        for item in value:
            reject_secrets(item, label)
    elif isinstance(value, str) and SECRET_VALUE_PATTERN.search(value):
        fail(f"{label} contains credential material")


def project_flow_contract() -> tuple[Any, Any, Any, Any]:
    project_flow_scripts = Path(__file__).resolve().parents[2] / "project-flow" / "scripts"
    if not project_flow_scripts.is_dir():
        fail("the packaged project-flow dependency is required")
    sys.path.insert(0, str(project_flow_scripts))
    try:
        from artifact_layout import approved_document, resolve_path
        from render_publication import canonical_reference_path, check_projection, issue_snapshot
    except ImportError as error:
        fail(f"cannot load the project-flow verification contract: {error}")
    return approved_document, resolve_path, canonical_reference_path, (check_projection, issue_snapshot)


def validate_feature_approval(feature_dir: Path, *, permit_divergence: bool = False) -> tuple[Path, Path, dict[str, Any], dict[str, Any], bytes]:
    if not feature_dir.is_dir() or is_link_like(feature_dir):
        fail("feature directory must be a regular directory")
    approved_document, resolve_path, _, _ = project_flow_contract()
    candidates = [
        feature_dir / ".flow" / "feature-state.json", feature_dir / "feature-state.json",
        feature_dir / ".flow" / "bug-state.json", feature_dir / "bug-state.json",
    ]
    states = []
    for candidate in candidates:
        resolved = resolve_path(candidate)
        if resolved.is_file() and resolved not in states:
            states.append(resolved)
    if len(states) != 1:
        fail("exactly one project-flow Feature or Bug state is required")
    state = load_json(states[0])
    if state.get("schema_version") not in (2, 3, 4):
        fail("unsupported project-flow requirement state")
    if state.get("item_type") not in {"Feature", "Bug"}:
        fail("project-slices accepts only a Feature or Bug")
    canonical = resolve_path(feature_dir / f"{state['item_type'].lower()}.md")
    if state.get("phase") != "completed":
        fail("project-flow parent item must be completed")
    redmine = state.get("redmine")
    if not isinstance(redmine, dict) or not isinstance(redmine.get("issue_id"), int) or redmine["issue_id"] < 1:
        fail("completed parent item must have a Redmine issue_id")
    approvals = [
        item for item in state.get("approvals", [])
        if isinstance(item, dict) and item.get("kind") == "requirement" and item.get("status") == "valid"
    ]
    if len(approvals) != 1:
        fail("parent item requires exactly one valid local requirement approval")
    approval = approvals[0]
    try:
        canonical_content = approved_document(canonical, approval.get("subject_sha256"))
    except (OSError, ValueError, TypeError) as error:
        fail(f"canonical parent requirement does not match its valid local approval: {error}")
    divergences = state.get("requirement_divergences", [])
    if not isinstance(divergences, list) or any(
        isinstance(item, dict) and item.get("status") == "pending" for item in divergences
    ):
        fail("pending requirement divergence blocks slicing approval")
    correction_path = feature_dir / ".flow" / "slices-divergence.json"
    if correction_path.exists() and not permit_divergence:
        try:
            from manage_divergence import local_is_current, validate_state as validate_divergence_state
            correction = load_json(correction_path)
            validate_divergence_state(correction, check_files=False)
            if correction.get("status") != "completed":
                fail("material parent/slice divergence blocks child publication until correction alignment completes")
            local_is_current(correction)
        except ImportError as error:
            fail(f"cannot load the divergence verification contract: {error}")
    return canonical, states[0], state, approval, canonical_content


def contained_feature_path(feature_dir: Path, value: Any, label: str) -> Path:
    relative = Path(require_text(value, label))
    if relative.is_absolute() or relative.anchor or ".." in relative.parts:
        fail(f"{label} must be a contained Feature-relative path")
    candidate = (feature_dir / relative).absolute()
    try:
        candidate.relative_to(feature_dir.absolute())
    except ValueError:
        fail(f"{label} must be a contained Feature-relative path")
    return candidate


def validate_input_linkage(feature_dir: Path, proposal: dict[str, Any], input_check_path: Path) -> None:
    input_check = load_json(input_check_path)
    if input_check.get("status") != "ready" or set(input_check) != {
        "status", "feature_path", "state_path", "issue_id", "requirement_sha256",
        "remote_snapshot_sha256", "checked_at",
    }:
        fail("input check artifact is invalid")
    feature = proposal["feature"]
    if feature["input_check_sha256"] != file_digest(input_check_path):
        fail("proposal does not reference the exact input check artifact")
    canonical, feature_state_path, feature_state, approval, canonical_content = validate_feature_approval(feature_dir)
    _, resolve_path, _, _ = project_flow_contract()
    artifact_path = contained_feature_path(feature_dir, feature["artifact_path"], "feature.artifact_path")
    proposal_state_path = contained_feature_path(feature_dir, feature["state_path"], "feature.state_path")
    proposal_input_check = contained_feature_path(feature_dir, feature["input_check_path"], "feature.input_check_path")
    if resolve_path(artifact_path).absolute() != canonical.absolute():
        fail("proposal Feature artifact path differs from the checked input")
    if resolve_path(proposal_state_path).absolute() != feature_state_path.absolute():
        fail("proposal Feature state path differs from the checked input")
    if proposal_input_check != input_check_path.absolute():
        fail("proposal input check path differs from the checked input")
    checked_feature_path = Path(require_text(input_check["feature_path"], "input check feature_path"))
    checked_state_path = Path(require_text(input_check["state_path"], "input check state_path"))
    if checked_feature_path.absolute() != canonical.absolute() or checked_state_path.absolute() != feature_state_path.absolute():
        fail("input check paths differ from the current Feature")
    if feature["issue_id"] != input_check["issue_id"] or feature["issue_id"] != feature_state["redmine"]["issue_id"]:
        fail("proposal Feature identity differs from the checked input")
    if feature["requirement_sha256"] != input_check["requirement_sha256"] or feature["requirement_sha256"] != approval["subject_sha256"]:
        fail("proposal Feature requirement differs from the checked input")
    try:
        approved_title = canonical_content.decode("utf-8").splitlines()[0].removeprefix("# ").strip()
    except (UnicodeDecodeError, IndexError) as error:
        fail(f"cannot read the approved parent title: {error}")
    if feature["title"] != approved_title:
        fail("proposal parent title differs from the approved parent")
    if any(item.get("api_delivery") is True for item in proposal.get("slices", []) if isinstance(item, dict)):
        approved_text = canonical_content.decode("utf-8")
        if "[API]" not in approved_title and re.search(r"\bAPI\b", approved_text, re.IGNORECASE) is None:
            fail("material divergence: API delivery is absent from the approved requirement; resolve and align the parent before proposing affected children")


def command_check_input(arguments: argparse.Namespace) -> None:
    feature_dir = Path(arguments.feature_dir)
    canonical, feature_state_path, state, approval, canonical_content = validate_feature_approval(feature_dir)
    _, _, canonical_reference_path, publication_contract = project_flow_contract()
    check_projection, issue_snapshot = publication_contract
    redmine = state["redmine"]
    canonical_sha = approval["subject_sha256"]
    remote = load_json(Path(arguments.remote))
    reject_secrets(remote, "remote snapshot")
    try:
        issue = issue_snapshot(remote)
        if str(issue["id"]) != str(redmine["issue_id"]):
            fail("remote issue identity differs from the local parent")
        document = canonical_content.decode("utf-8")
        if document.splitlines()[0].removeprefix("# ").strip() != issue["subject"]:
            fail("remote issue title differs from the approved parent")
        check_projection(
            document,
            state["item_type"],
            canonical_reference_path(canonical),
            require_text(approval.get("approved_by"), "requirement approval approved_by"),
            issue,
            issue,
        )
    except (OSError, ValueError, TypeError, KeyError, UnicodeDecodeError) as error:
        fail(f"local and Redmine requirements diverge: {error}")
    result = {
        "status": "ready",
        "feature_path": str(canonical.absolute()),
        "state_path": str(feature_state_path.absolute()),
        "issue_id": redmine["issue_id"],
        "requirement_sha256": canonical_sha,
        "remote_snapshot_sha256": file_digest(Path(arguments.remote)),
        "checked_at": require_timestamp(arguments.at, "at"),
    }
    output_path = Path(arguments.output)
    require_exact_path(output_path, feature_dir / ".flow" / "slices-input-check.json", "input check output")
    encoded = json.dumps(result, ensure_ascii=False, indent=2).encode("utf-8") + b"\n"
    atomic_write(output_path, encoded)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


def expected_title(parent_title: str, suffix: str, api_delivery: bool) -> str:
    base = parent_title.strip()
    if api_delivery:
        match = PREFIX_PATTERN.match(base)
        if match is None or "[WEB]" not in match.group(0):
            fail("an API delivery title requires the parent [WEB] prefix")
        prefix = match.group(0).strip().split()
        prefix.insert(prefix.index("[WEB]") + 1, "[API]")
        base = " ".join(prefix) + " " + base[match.end():]
    return f"[DEV] {base} - {suffix.strip()}"


def validate_proposal(proposal: dict[str, Any]) -> None:
    required_fields = {"feature", "inspection", "requirements", "slices", "coverage", "decisions"}
    if not required_fields.issubset(proposal) or not set(proposal).issubset(required_fields | {"study_evidence"}):
        fail("proposal has unknown or missing top-level fields")
    reject_secrets(proposal, "proposal")
    feature = proposal["feature"]
    if not isinstance(feature, dict) or set(feature) != {
        "title", "artifact_path", "state_path", "issue_id", "requirement_sha256",
        "input_check_path", "input_check_sha256",
    }:
        fail("proposal.feature fields are invalid")
    parent_title = require_text(feature["title"], "feature.title")
    require_text(feature["artifact_path"], "feature.artifact_path")
    require_text(feature["state_path"], "feature.state_path")
    if not isinstance(feature["issue_id"], int) or feature["issue_id"] < 1:
        fail("feature.issue_id must be a positive integer")
    if not isinstance(feature["requirement_sha256"], str) or not SHA256_PATTERN.fullmatch(feature["requirement_sha256"]):
        fail("feature.requirement_sha256 is invalid")
    require_text(feature["input_check_path"], "feature.input_check_path")
    if not isinstance(feature["input_check_sha256"], str) or not SHA256_PATTERN.fullmatch(feature["input_check_sha256"]):
        fail("feature.input_check_sha256 is invalid")

    inspection = proposal["inspection"]
    if not isinstance(inspection, list) or not inspection:
        fail("proposal requires code inspection evidence")
    for index, finding in enumerate(inspection):
        if not isinstance(finding, dict) or set(finding) != {"path", "finding", "classification"}:
            fail(f"inspection[{index}] fields are invalid")
        require_text(finding["path"], f"inspection[{index}].path")
        require_text(finding["finding"], f"inspection[{index}].finding")
        if finding["classification"] not in ("create", "adapt", "existing"):
            fail(f"inspection[{index}].classification is invalid")

    requirements = proposal["requirements"]
    if not isinstance(requirements, list) or not requirements:
        fail("proposal requires at least one requirement")
    requirement_ids: list[str] = []
    for index, requirement in enumerate(requirements):
        if not isinstance(requirement, dict) or set(requirement) != {"id", "summary"}:
            fail(f"requirements[{index}] fields are invalid")
        requirement_id = require_text(requirement["id"], f"requirements[{index}].id")
        require_text(requirement["summary"], f"requirements[{index}].summary")
        requirement_ids.append(requirement_id)
    if len(requirement_ids) != len(set(requirement_ids)):
        fail("requirement ids must be unique")

    slices = proposal["slices"]
    if not isinstance(slices, list):
        fail("proposal.slices must be an array")
    numbers: list[int] = []
    traceability: dict[int, list[str]] = {}
    for index, slice_value in enumerate(slices):
        if not isinstance(slice_value, dict) or set(slice_value) != {
            "number", "title", "title_suffix", "api_delivery", "estimate_hours",
            "estimate_exception", "blocked_by", "description",
        } | ({"external_blockers"} if "external_blockers" in slice_value else set()):
            fail(f"slices[{index}] fields are invalid")
        number = slice_value["number"]
        if not isinstance(number, int):
            fail(f"slices[{index}].number must be an integer")
        numbers.append(number)
        suffix = require_text(slice_value["title_suffix"], f"slices[{index}].title_suffix")
        if not isinstance(slice_value["api_delivery"], bool):
            fail(f"slices[{index}].api_delivery must be boolean")
        if slice_value["title"] != expected_title(parent_title, suffix, slice_value["api_delivery"]):
            fail(f"slices[{index}].title does not preserve the approved parent title")
        estimate = slice_value["estimate_hours"]
        if not isinstance(estimate, (int, float)) or isinstance(estimate, bool) or estimate <= 0:
            fail(f"slices[{index}].estimate_hours must be positive")
        exception = slice_value["estimate_exception"]
        if exception is not None and not isinstance(exception, str):
            fail(f"slices[{index}].estimate_exception must be text or null")
        if estimate > 6 and (not isinstance(exception, str) or not exception.strip()):
            fail(f"slices[{index}] exceeds the six-hour reference without justification")
        blockers = slice_value["blocked_by"]
        if not isinstance(blockers, list) or any(not isinstance(item, int) for item in blockers):
            fail(f"slices[{index}].blocked_by must contain slice numbers")
        if any(blocker >= number or blocker < 1 for blocker in blockers) or len(blockers) != len(set(blockers)):
            fail(f"slices[{index}].blocked_by must reference unique earlier slices")
        external = slice_value.get("external_blockers", [])
        if not isinstance(external, list):
            fail(f"slices[{index}].external_blockers must be an array")
        external_keys: list[str] = []
        for blocker_index, blocker in enumerate(external):
            fields = {
                "key", "feature_issue_id", "feature_title", "capability", "blocking_reason",
                "source_slice_issue_id", "source_slice_title",
            }
            if not isinstance(blocker, dict) or set(blocker) != fields:
                fail(f"slices[{index}].external_blockers[{blocker_index}] fields are invalid")
            external_keys.append(require_text(blocker["key"], f"slices[{index}].external_blockers[{blocker_index}].key"))
            if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", blocker["key"]):
                fail(f"slices[{index}].external_blockers[{blocker_index}].key must be stable kebab-case")
            if not isinstance(blocker["feature_issue_id"], int) or blocker["feature_issue_id"] < 1 or blocker["feature_issue_id"] == feature["issue_id"]:
                fail(f"slices[{index}].external_blockers[{blocker_index}].feature_issue_id is invalid")
            for field in ("feature_title", "capability", "blocking_reason"):
                require_text(blocker[field], f"slices[{index}].external_blockers[{blocker_index}].{field}")
            source_id = blocker["source_slice_issue_id"]
            source_title = blocker["source_slice_title"]
            if source_id is None:
                if source_title is not None:
                    fail(f"slices[{index}].external_blockers[{blocker_index}] provisional blocker cannot name a slice title")
            elif not isinstance(source_id, int) or source_id < 1 or not isinstance(source_title, str) or not source_title.strip():
                fail(f"slices[{index}].external_blockers[{blocker_index}] specific blocker requires a slice id and title")
        if len(external_keys) != len(set(external_keys)):
            fail(f"slices[{index}].external_blockers keys must be unique")
        description = slice_value["description"]
        required_fields = {"delivery", "limits", "criteria", "dependencies", "traceability"}
        allowed_fields = required_fields | {"technical_context"}
        if not isinstance(description, dict) or not required_fields.issubset(description) or not set(description).issubset(allowed_fields):
            fail(f"slices[{index}].description fields are invalid")
        for field in required_fields - {"criteria", "traceability"}:
            require_text(description[field], f"slices[{index}].description.{field}")
        technical_context = description.get("technical_context")
        if technical_context is not None:
            require_text(technical_context, f"slices[{index}].description.technical_context")
        criteria = description["criteria"]
        if not isinstance(criteria, list) or not criteria:
            fail(f"slices[{index}] requires acceptance criteria")
        kinds: set[str] = set()
        for criterion_index, criterion in enumerate(criteria):
            if not isinstance(criterion, dict) or set(criterion) != {"kind", "text"}:
                fail(f"slices[{index}].criteria[{criterion_index}] fields are invalid")
            if criterion["kind"] not in ("success", "error", "permission"):
                fail(f"slices[{index}].criteria[{criterion_index}].kind is invalid")
            require_text(criterion["text"], f"slices[{index}].criteria[{criterion_index}].text")
            kinds.add(criterion["kind"])
        if "success" not in kinds:
            fail(f"slices[{index}] requires a success criterion")
        traces = description["traceability"]
        if not isinstance(traces, list) or not traces or any(item not in requirement_ids for item in traces):
            fail(f"slices[{index}].description.traceability is invalid")
        traceability[number] = traces
    if numbers != list(range(1, len(numbers) + 1)):
        fail("slice numbers must be contiguous from 1")

    coverage = proposal["coverage"]
    if not isinstance(coverage, list) or len(coverage) != len(requirement_ids):
        fail("coverage must contain exactly one row per requirement")
    covered: list[str] = []
    for index, row in enumerate(coverage):
        if not isinstance(row, dict) or set(row) != {"requirement_id", "disposition", "slice_numbers", "evidence"}:
            fail(f"coverage[{index}] fields are invalid")
        requirement_id = row["requirement_id"]
        if requirement_id not in requirement_ids:
            fail(f"coverage[{index}].requirement_id is unknown")
        covered.append(requirement_id)
        disposition = row["disposition"]
        if disposition not in ("slice", "existing", "other-feature"):
            fail(f"coverage[{index}].disposition is invalid")
        slice_numbers = row["slice_numbers"]
        if not isinstance(slice_numbers, list) or any(item not in numbers for item in slice_numbers):
            fail(f"coverage[{index}].slice_numbers is invalid")
        if disposition == "slice" and len(slice_numbers) != 1:
            fail(f"coverage[{index}] must have exactly one owning slice")
        if disposition != "slice" and slice_numbers:
            fail(f"coverage[{index}] outside this Feature cannot name a slice")
        require_text(row["evidence"], f"coverage[{index}].evidence")
        if disposition == "slice" and requirement_id not in traceability[slice_numbers[0]]:
            fail(f"coverage[{index}] is absent from its slice traceability")
    if sorted(covered) != sorted(requirement_ids) or len(covered) != len(set(covered)):
        fail("coverage must be exhaustive and non-duplicated")
    if not slices and any(row["disposition"] == "slice" for row in coverage):
        fail("coverage cannot reference DEV work when no slice exists")
    decisions = proposal["decisions"]
    if not isinstance(decisions, list) or any(not isinstance(item, str) or not item.strip() for item in decisions):
        fail("proposal.decisions must contain readable decision strings")
    study_evidence = proposal.get("study_evidence", [])
    if not isinstance(study_evidence, list):
        fail("proposal.study_evidence must be an array")
    study_ids: list[int] = []
    evidence_fields = {
        "study_state_path", "study_revision", "study_publication_sha256", "study_remote_id",
        "question", "expected_result", "effort_limit", "result", "source", "authored_by",
        "authored_at", "recorded_by", "recorded_at", "result_sha256",
    }
    for index, evidence in enumerate(study_evidence):
        if not isinstance(evidence, dict) or set(evidence) != evidence_fields:
            fail(f"proposal.study_evidence[{index}] fields are invalid")
        require_text(evidence["study_state_path"], f"proposal.study_evidence[{index}].study_state_path")
        if not isinstance(evidence["study_revision"], int) or evidence["study_revision"] < 1:
            fail(f"proposal.study_evidence[{index}].study_revision is invalid")
        if not isinstance(evidence["study_remote_id"], int) or evidence["study_remote_id"] < 1:
            fail(f"proposal.study_evidence[{index}].study_remote_id is invalid")
        study_ids.append(evidence["study_remote_id"])
        for field in ("study_publication_sha256", "result_sha256"):
            if not isinstance(evidence[field], str) or not SHA256_PATTERN.fullmatch(evidence[field]):
                fail(f"proposal.study_evidence[{index}].{field} is invalid")
        for field in ("question", "expected_result", "effort_limit", "result", "authored_by", "recorded_by"):
            require_text(evidence[field], f"proposal.study_evidence[{index}].{field}")
        require_timestamp(evidence["authored_at"], f"proposal.study_evidence[{index}].authored_at")
        require_timestamp(evidence["recorded_at"], f"proposal.study_evidence[{index}].recorded_at")
        source = evidence["source"]
        if not isinstance(source, dict) or set(source) != {"kind", "reference"}:
            fail(f"proposal.study_evidence[{index}].source is invalid")
        require_text(source["kind"], f"proposal.study_evidence[{index}].source.kind")
        require_text(source["reference"], f"proposal.study_evidence[{index}].source.reference")
    if len(study_ids) != len(set(study_ids)):
        fail("proposal.study_evidence must not duplicate a Study remote ID")


def validate_state(state: dict[str, Any], previous: dict[str, Any] | None = None) -> None:
    if set(state) != {"schema_version", "status", "current_revision", "revisions", "approvals"}:
        fail("state has unknown or missing fields")
    reject_secrets(state, "state")
    if state["schema_version"] != 1 or state["status"] not in ("proposed", "approved"):
        fail("unsupported state version or status")
    revisions = state["revisions"]
    approvals = state["approvals"]
    if not isinstance(revisions, list) or not revisions or not isinstance(approvals, list):
        fail("state revisions and approvals are invalid")
    if state["current_revision"] != len(revisions):
        fail("current_revision must select the last revision")
    for index, revision in enumerate(revisions, start=1):
        fields = {
            "number", "recorded_by", "recorded_at", "reason", "proposal_sha256", "proposal",
        }
        if "semantic_baseline" in revision:
            fields.add("semantic_baseline")
        if not isinstance(revision, dict) or set(revision) != fields:
            fail(f"revision {index} fields are invalid")
        if revision["number"] != index:
            fail("revision numbers must be contiguous")
        require_text(revision["recorded_by"], f"revision {index}.recorded_by")
        require_timestamp(revision["recorded_at"], f"revision {index}.recorded_at")
        require_text(revision["reason"], f"revision {index}.reason")
        validate_proposal(revision["proposal"])
        if revision["proposal_sha256"] != digest(revision["proposal"]):
            fail(f"revision {index} proposal hash differs")
        if "semantic_baseline" in revision:
            baseline = revision["semantic_baseline"]
            if not isinstance(baseline, dict) or set(baseline) != {
                "requirement_sha256", "semantic_model_sha256", "semantic_model",
            }:
                fail(f"revision {index} semantic baseline fields are invalid")
            if baseline["requirement_sha256"] != revision["proposal"]["feature"]["requirement_sha256"]:
                fail(f"revision {index} semantic baseline references another requirement version")
            if baseline["semantic_model_sha256"] != digest(baseline["semantic_model"]):
                fail(f"revision {index} semantic baseline hash differs")
    for index, approval in enumerate(approvals):
        if not isinstance(approval, dict) or set(approval) != {
            "revision", "proposal_sha256", "approved_by", "approved_at", "status",
        }:
            fail(f"approvals[{index}] fields are invalid")
        if approval["status"] not in ("valid", "invalidated"):
            fail(f"approvals[{index}].status is invalid")
        revision_number = approval["revision"]
        if not isinstance(revision_number, int) or revision_number < 1 or revision_number > len(revisions):
            fail(f"approvals[{index}].revision is invalid")
        if approval["proposal_sha256"] != revisions[revision_number - 1]["proposal_sha256"]:
            fail(f"approvals[{index}] does not match its revision")
        require_text(approval["approved_by"], f"approvals[{index}].approved_by")
        require_timestamp(approval["approved_at"], f"approvals[{index}].approved_at")
    current_valid = [item for item in approvals if item["revision"] == len(revisions) and item["status"] == "valid"]
    if state["status"] == "approved":
        if len(current_valid) != 1:
            fail("approved state requires exactly one valid approval for the current revision")
    elif current_valid:
        fail("proposed state cannot retain a valid current approval")
    if previous is not None:
        validate_state(previous)
        if state["schema_version"] != previous["schema_version"]:
            fail("schema version cannot change")
        if state["revisions"][:len(previous["revisions"])] != previous["revisions"]:
            fail("revisions are append-only")
        if len(state["revisions"]) < len(previous["revisions"]):
            fail("revisions cannot be removed")
        old_approvals = previous["approvals"]
        if len(state["approvals"]) < len(old_approvals):
            fail("approvals cannot be removed")
        for index, old in enumerate(old_approvals):
            current = state["approvals"][index]
            if current != old and not (
                old["status"] == "valid"
                and current == {**old, "status": "invalidated"}
            ):
                fail("approval history is append-only except valid-to-invalidated status")


def semantic_baseline(proposal: dict[str, Any]) -> dict[str, Any]:
    model = {key: copy.deepcopy(proposal.get(key, [])) for key in ("requirements", "slices", "coverage", "decisions", "study_evidence")}
    return {"requirement_sha256": proposal["feature"]["requirement_sha256"], "semantic_model_sha256": digest(model), "semantic_model": model}


def command_record_proposal(arguments: argparse.Namespace) -> None:
    proposal = load_json(Path(arguments.proposal))
    validate_proposal(proposal)
    input_check_path = Path(arguments.input_check)
    state_path = Path(arguments.state)
    if state_path.name != "slices-state.json" or state_path.parent.name != ".flow":
        fail("state must be stored at <feature>/.flow/slices-state.json")
    feature_root = state_path.parent.parent
    require_exact_path(Path(arguments.proposal), feature_root / ".work" / "slices-proposal.json", "proposal")
    require_exact_path(input_check_path, feature_root / ".flow" / "slices-input-check.json", "input check")
    validate_input_linkage(feature_root, proposal, input_check_path)
    if state_path.exists():
        state = load_json(state_path)
        validate_state(state)
        state = copy.deepcopy(state)
        for approval in state["approvals"]:
            if approval["status"] == "valid":
                approval["status"] = "invalidated"
    else:
        state = {"schema_version": 1, "status": "proposed", "current_revision": 0, "revisions": [], "approvals": []}
    revision_number = len(state["revisions"]) + 1
    state["revisions"].append({
        "number": revision_number,
        "recorded_by": require_text(arguments.actor, "actor"),
        "recorded_at": require_timestamp(arguments.at, "at"),
        "reason": require_text(arguments.reason, "reason"),
        "proposal_sha256": digest(proposal),
        "proposal": proposal,
        "semantic_baseline": semantic_baseline(proposal),
    })
    state["current_revision"] = revision_number
    state["status"] = "proposed"
    validate_state(state)
    atomic_write(state_path, json.dumps(state, ensure_ascii=False, indent=2).encode("utf-8") + b"\n")
    print(json.dumps({"status": "proposed", "revision": revision_number, "proposal_sha256": digest(proposal)}, sort_keys=True))


def command_approve(arguments: argparse.Namespace) -> None:
    state_path = Path(arguments.state)
    if state_path.name != "slices-state.json" or state_path.parent.name != ".flow":
        fail("state must be stored at <feature>/.flow/slices-state.json")
    state = load_json(state_path)
    validate_state(state)
    revision = state["revisions"][-1]
    validate_input_linkage(state_path.parent.parent, revision["proposal"], state_path.parent / "slices-input-check.json")
    state = copy.deepcopy(state)
    revision = state["revisions"][-1]
    if any(item["status"] == "valid" and item["revision"] == revision["number"] for item in state["approvals"]):
        fail("current revision is already approved")
    state["approvals"].append({
        "revision": revision["number"],
        "proposal_sha256": revision["proposal_sha256"],
        "approved_by": require_text(arguments.actor, "actor"),
        "approved_at": require_timestamp(arguments.at, "at"),
        "status": "valid",
    })
    state["status"] = "approved"
    validate_state(state)
    atomic_write(state_path, json.dumps(state, ensure_ascii=False, indent=2).encode("utf-8") + b"\n")
    print(json.dumps({"status": "approved", "revision": revision["number"], "proposal_sha256": revision["proposal_sha256"]}, sort_keys=True))


def render_markdown(proposal: dict[str, Any], revision: int, proposal_sha: str) -> str:
    lines = [f"# Fatiamento de {proposal['feature']['title']}", "", f"Revisão: {revision}  ", f"Hash: `{proposal_sha}`", "", "## Prévia numerada", ""]
    for slice_value in proposal["slices"]:
        blockers = ", ".join(str(item) for item in slice_value["blocked_by"]) or "Nenhum"
        external = []
        for blocker in slice_value.get("external_blockers", []):
            source = f"slice Redmine {blocker['source_slice_issue_id']} ({blocker['source_slice_title']})" if blocker["source_slice_issue_id"] else f"Feature Redmine {blocker['feature_issue_id']} (provisorio)"
            external.append(f"{source}: {blocker['capability']} - {blocker['blocking_reason']}")
        lines.extend([
            f"{slice_value['number']}. **{slice_value['title']}** — {slice_value['estimate_hours']}h",
            f"   - Entrega: {slice_value['description']['delivery']}",
            f"   - Bloqueado por: {blockers}",
            f"   - Bloqueios externos: {'; '.join(external) or 'Nenhum'}",
        ])
        if slice_value["estimate_exception"]:
            lines.append(f"   - Exceção de estimativa: {slice_value['estimate_exception']}")
    if not proposal["slices"]:
        lines.append("Sem trabalho DEV necessário; a inspeção e a cobertura registram a evidência.")
    lines.extend(["", "## Cobertura", "", "| Regra ou critério | Destino | Evidência |", "| --- | --- | --- |"])
    summaries = {item["id"]: item["summary"] for item in proposal["requirements"]}
    for row in proposal["coverage"]:
        destination = f"Slice {row['slice_numbers'][0]}" if row["disposition"] == "slice" else ("Existente" if row["disposition"] == "existing" else "Outra Feature")
        lines.append(f"| {row['requirement_id']}: {summaries[row['requirement_id']]} | {destination} | {row['evidence']} |")
    if proposal.get("study_evidence"):
        lines.extend(["", "## Evidencias de estudos", ""])
        for evidence in proposal["study_evidence"]:
            lines.extend([
                f"### Estudo Redmine {evidence['study_remote_id']}", "",
                f"- Pergunta: {evidence['question']}",
                f"- Resultado esperado: {evidence['expected_result']}",
                f"- Limite: {evidence['effort_limit']}",
                f"- Fonte: {evidence['source']['kind']} - {evidence['source']['reference']}",
                f"- Autoria: {evidence['authored_by']} em {evidence['authored_at']}",
                f"- Resultado: {evidence['result']}", "",
            ])
    lines.extend(["", "## Descrições completas", ""])
    for slice_value in proposal["slices"]:
        description = slice_value["description"]
        lines.extend([
            f"### {slice_value['number']}. {slice_value['title']}", "", "#### Entrega", "", description["delivery"], "",
            "#### Escopo e limites", "", description["limits"], "", "#### Critérios de aceite", "",
        ])
        lines.extend(f"- {item['text']}" for item in description["criteria"])
        lines.extend(["", "#### Dependências", "", description["dependencies"]])
        if description.get("technical_context"):
            lines.extend(["", "#### Contexto técnico", "", description["technical_context"]])
        lines.extend(["", "#### Referências", "", f"Item pai Redmine `#{proposal['feature']['issue_id']}`; regras/critérios {', '.join(description['traceability'])}.", ""])
    return "\n".join(lines).rstrip() + "\n"


def command_render(arguments: argparse.Namespace) -> None:
    state_path = Path(arguments.state)
    if state_path.name != "slices-state.json" or state_path.parent.name != ".flow":
        fail("state must be stored at <feature>/.flow/slices-state.json")
    output_path = Path(arguments.output)
    require_exact_path(output_path, state_path.parent.parent / "slices" / "slices.md", "render output")
    state = load_json(state_path)
    validate_state(state)
    revision = state["revisions"][-1]
    content = render_markdown(revision["proposal"], revision["number"], revision["proposal_sha256"])
    atomic_write(output_path, content.encode("utf-8"))
    print(json.dumps({"status": "rendered", "revision": revision["number"], "output": arguments.output}, ensure_ascii=False, sort_keys=True))


def command_validate(arguments: argparse.Namespace) -> None:
    state_path = Path(arguments.state)
    if state_path.name != "slices-state.json" or state_path.parent.name != ".flow":
        fail("state must be stored at <feature>/.flow/slices-state.json")
    state = load_json(state_path)
    previous = load_json(Path(arguments.previous)) if arguments.previous else None
    validate_state(state, previous)
    print(json.dumps({"status": "valid", "workflow_status": state["status"], "revision": state["current_revision"]}, sort_keys=True))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    check_input = commands.add_parser("check-input")
    check_input.add_argument("feature_dir")
    check_input.add_argument("--remote", required=True)
    check_input.add_argument("--output", required=True)
    check_input.add_argument("--at", required=True)
    check_input.set_defaults(run=command_check_input)
    record = commands.add_parser("record-proposal")
    record.add_argument("state")
    record.add_argument("proposal")
    record.add_argument("--input-check", required=True)
    record.add_argument("--actor", required=True)
    record.add_argument("--at", required=True)
    record.add_argument("--reason", required=True)
    record.set_defaults(run=command_record_proposal)
    approve = commands.add_parser("approve")
    approve.add_argument("state")
    approve.add_argument("--actor", required=True)
    approve.add_argument("--at", required=True)
    approve.set_defaults(run=command_approve)
    render = commands.add_parser("render")
    render.add_argument("state")
    render.add_argument("output")
    render.set_defaults(run=command_render)
    validate = commands.add_parser("validate")
    validate.add_argument("state")
    validate.add_argument("--previous")
    validate.set_defaults(run=command_validate)
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
