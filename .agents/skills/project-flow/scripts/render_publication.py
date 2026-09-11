#!/usr/bin/env python3
"""Render and check the functional Redmine projection of an approved requirement."""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

from validate_state import validate
from artifact_paths import artifact_root, contained_path
from artifact_layout import approved_document


START = "<!-- project-flow:start -->"
END = "<!-- project-flow:end -->"
FOOTER = "Requisito canônico"


def sections(document):
    """Recognize headings outside fenced examples, preserving section bodies."""
    lines = document.replace("\r\n", "\n").splitlines(keepends=True)
    result = []
    current = None
    fence = None
    for line in lines:
        marker = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if marker:
            token = marker.group(1)
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
        heading = re.match(r"^## (.+?)\s*$", line) if fence is None else None
        if heading:
            current = [heading.group(1), ""]
            result.append(current)
        elif current is not None:
            current[1] += line
    if fence is not None:
        raise ValueError("unclosed fenced example")
    names = [name for name, _ in result]
    if len(names) != len(set(names)):
        raise ValueError("duplicate section heading")
    return [(name, body.strip()) for name, body in result]


def functional_sections(document, item_type):
    if item_type not in {"Feature", "Bug"}:
        raise ValueError("unsupported requirement type")
    template = Path(__file__).parent.parent / "templates" / f"{item_type.lower()}.md"
    required = [name for name, _ in sections(template.read_text(encoding="utf-8"))]
    parsed = sections(document)
    bodies = dict(parsed)
    if any(not bodies.get(name) for name in required):
        raise ValueError("canonical requirement has a missing or empty required section")
    if FOOTER in bodies or START in document or END in document:
        raise ValueError("canonical requirement contains publication metadata")
    preamble = document.split("\n## ", 1)[0].splitlines()
    if not preamble or not preamble[0].startswith("# "):
        raise ValueError("canonical title missing")
    if any(line.strip() and not line.startswith("Issue: #") for line in preamble[1:]):
        raise ValueError("functional content outside canonical sections")
    # Feature evidence provenance stays local; Bug evidence defines the deviation.
    return [(name, body) for name, body in parsed if item_type != "Feature" or name != "Designs e evidências"]


def split_managed(description):
    if description.count(START) != 1 or description.count(END) != 1:
        raise ValueError("description requires exactly one managed delimiter pair")
    start = description.index(START)
    end = description.index(END)
    if end <= start:
        raise ValueError("managed delimiters are reversed")
    return description[:start], description[start + len(START):end], description[end + len(END):]


def projection(document, item_type, canonical_path, approved_by):
    content = "\n\n".join(f"## {name}\n\n{body}" for name, body in functional_sections(document, item_type))
    return f"\n{content}\n\n## {FOOTER}\n\nDocumento aprovado por {approved_by}: {canonical_path}\n"


def issue_snapshot(value, subject_fallback=None):
    if not isinstance(value, dict):
        raise ValueError("issue snapshot must be an object")
    nested = value.get("issue")
    if nested is not None and not isinstance(nested, dict):
        raise ValueError("issue must be an object")
    records = [value, nested] if nested is not None else [value]
    identifiers = [record[key] for record in records for key in ("id", "issue_id") if key in record]
    if not identifiers:
        raise ValueError("issue snapshot requires id or issue_id")
    if len({str(identifier) for identifier in identifiers}) != 1:
        raise ValueError("issue snapshot contains conflicting IDs")
    result = {"id": identifiers[0]}
    for field in ("subject", "description", "status", "status_id", "relations"):
        values = [record[field] for record in records if field in record]
        if values:
            if any(candidate != values[0] for candidate in values[1:]):
                raise ValueError(f"issue snapshot contains conflicting {field}")
            result[field] = values[0]
    if "subject" not in result and subject_fallback is not None:
        result["subject"] = subject_fallback
    if not isinstance(result.get("subject"), str) or not isinstance(result.get("description"), str):
        raise ValueError("issue snapshot requires subject and description")
    return result


def build_payload(document, item_type, canonical_path, approved_by, issue):
    title = document.splitlines()[0].removeprefix("# ").strip()
    if title != issue["subject"]:
        raise ValueError("canonical title differs from issue subject")
    before, _, after = split_managed(issue["description"])
    managed = projection(document, item_type, canonical_path, approved_by)
    return {"issue_id": issue["id"], "changes": {"description": before + START + managed + END + after}}


def check_projection(document, item_type, canonical_path, approved_by, before, current):
    if str(current["id"]) != str(before["id"]) or current["subject"] != before["subject"]:
        raise ValueError("issue identity or title changed")
    for field in ("status", "status_id", "relations"):
        if field in before and current.get(field) != before[field]:
            raise ValueError(f"issue {field} changed")
    prefix, _, suffix = split_managed(before["description"])
    current_prefix, managed, current_suffix = split_managed(current["description"])
    if (prefix, suffix) != (current_prefix, current_suffix):
        raise ValueError("unmanaged human content changed")
    parsed = sections(managed)
    if not parsed or parsed[-1][0] != FOOTER:
        raise ValueError("canonical reference footer missing")
    normalized = managed.replace("\r\n", "\n").lstrip()
    if not normalized.startswith("## " + parsed[0][0] + "\n"):
        raise ValueError("unexpected content before functional sections")
    if parsed[:-1] != functional_sections(document, item_type):
        raise ValueError("functional projection differs: omitted, merged, reordered or changed content")
    footer = parsed[-1][1]
    allowed_footers = {
        f"Documento aprovado por {approved_by}: {canonical_path}",
        f"Documento aprovado: {canonical_path}\n\nRequisito aprovado por {approved_by}.",
    }
    if footer not in allowed_footers:
        raise ValueError("canonical reference or approval attribution differs")


def read_issue(path, subject_fallback=None):
    return issue_snapshot(json.loads(path.read_text(encoding="utf-8")), subject_fallback)


def canonical_reference_path(document_path):
    parts = document_path.resolve().parts
    anchors = [index for index in range(len(parts) - 1) if parts[index:index + 2] == ("docs", "harness")]
    if not anchors:
        raise ValueError("canonical document must be under docs/harness")
    return Path(*parts[anchors[-1]:]).as_posix()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("state", type=Path)
    parser.add_argument("--before", type=Path, required=True, help="Fresh issue JSON with identity, subject and description")
    parser.add_argument("--output", type=Path, help="Complete description preview")
    parser.add_argument("--payload", type=Path, help="Exact redmine_update_issue arguments")
    parser.add_argument("--check", type=Path, help="Issue JSON to compare with the approved canonical sections")
    args = parser.parse_args()
    try:
        state = validate(args.state)
        approvals = [approval for approval in state["approvals"] if approval["kind"] == "requirement" and approval["status"] == "valid"]
        if len(approvals) != 1:
            raise ValueError("requires exactly one valid canonical approval")
        approval = approvals[0]
        item_type = state["item_type"]
        document_path = contained_path(artifact_root(args.state), f"{item_type.lower()}.md")
        document_bytes = approved_document(document_path, approval["subject_sha256"])
        document = document_bytes.decode("utf-8")
        canonical_path = canonical_reference_path(document_path)
        before = read_issue(args.before)
        if str(before["id"]) != str(state["redmine"]["issue_id"]):
            raise ValueError("snapshot belongs to another issue")
        payload = build_payload(document, item_type, canonical_path, approval["approved_by"], before)
        if args.check:
            check_projection(document, item_type, canonical_path, approval["approved_by"], before, read_issue(args.check, before["subject"]))
        targets = [path.resolve() for path in (args.output, args.payload) if path]
        inputs = {path.resolve() for path in (args.state, args.before, document_path, args.check) if path}
        if len(targets) != len(set(targets)) or inputs.intersection(targets):
            raise ValueError("outputs must be distinct from inputs and each other")
        encoded = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            with args.output.open("w", encoding="utf-8", newline="") as stream:
                stream.write(payload["changes"]["description"])
        if args.payload:
            with args.payload.open("w", encoding="utf-8", newline="") as stream:
                stream.write(encoded)
        print("valid" if args.check else hashlib.sha256(encoded.encode("utf-8")).hexdigest())
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError, UnicodeDecodeError) as error:
        print(f"invalid: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
