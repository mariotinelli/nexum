"""Verify navigation-only artifact migrations without inventing approvals."""

import hashlib
import json
import posixpath
import re
from pathlib import Path, PurePosixPath

from artifact_paths import checked_path, contained_path


RECORD = "docs/harness/.flow/artifact-layout.json"
INLINE_LINK = re.compile(r'(?<=\]\()(<[^>\n]+>|[^\s()]+)(?=(?:\s+"[^"\n]*")?\))')
REFERENCE_LINK = re.compile(r'^(\s{0,3}\[[^]\n]+\]:\s*)(<[^>\n]+>|[^\s]+)', re.MULTILINE)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def repository_for(path):
    parts = path.absolute().parts
    anchors = [index for index in range(len(parts) - 1) if parts[index:index + 2] == ("docs", "harness")]
    return Path(*parts[:anchors[-1]]) if anchors else None


def validate_reference(value):
    if not isinstance(value, str) or not value.startswith("docs/harness/") or ".work" in PurePosixPath(value).parts or ".runs" in PurePosixPath(value).parts:
        raise ValueError("layout references must stay in durable docs/harness files")
    if ".." in PurePosixPath(value).parts or "\\" in value or ":" in value:
        raise ValueError("layout references must be contained relative paths")


def checked_reference(repository, value):
    validate_reference(value)
    return contained_path(repository, value)


def load_layout(repository):
    path = contained_path(repository, RECORD)
    if not path.exists():
        return None
    record = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(record, dict) or set(record) != {"schema_version", "kind", "moves", "documents"} or record["schema_version"] != 1 or record["kind"] != "artifact-layout":
        raise ValueError("unsupported artifact layout record")
    if not isinstance(record["moves"], dict) or not isinstance(record["documents"], list):
        raise ValueError("invalid artifact layout collections")
    for source, target in record["moves"].items():
        validate_reference(source)
        validate_reference(target)
        if source == target or target in record["moves"]:
            raise ValueError("layout moves must resolve directly without cycles")
    seen = set()
    for document in record["documents"]:
        if not isinstance(document, dict) or set(document) != {"path", "original_path", "original_snapshot", "original_sha256", "relocated_sha256"}:
            raise ValueError("invalid layout document")
        for key in ("path", "original_path", "original_snapshot"):
            validate_reference(document[key])
        if document["path"] in seen or record["moves"].get(document["original_path"], document["original_path"]) != document["path"]:
            raise ValueError("layout document has an ambiguous identity")
        seen.add(document["path"])
        for key in ("original_sha256", "relocated_sha256"):
            if not isinstance(document[key], str) or not re.fullmatch(r"[a-f0-9]{64}", document[key]):
                raise ValueError("invalid layout document hash")
    return record


def resolve_path(path):
    repository = repository_for(path)
    if repository is None:
        return checked_path(path)
    original = checked_path(path, root=repository)
    record = load_layout(repository)
    if record is None:
        return original
    relative = original.relative_to(repository.resolve()).as_posix()
    target = record["moves"].get(relative)
    if target is None:
        return original
    destination = checked_reference(repository, target)
    if original.exists():
        raise ValueError("both historical and relocated artifact paths exist")
    if not destination.is_file():
        raise ValueError("relocated artifact is missing")
    return destination


def rewrite_links(data, original_path, new_path, moves):
    """Only link destinations change; prose, labels, examples and line endings remain."""
    def rewrite(value):
        bracketed = value.startswith("<") and value.endswith(">")
        url = value[1:-1] if bracketed else value
        if url.startswith(("#", "/")) or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", url):
            return value
        target, separator, fragment = url.partition("#")
        if not target:
            return value
        old_target = posixpath.normpath(posixpath.join(posixpath.dirname(original_path), target))
        # A repository-root reference is sometimes used in historical Markdown.
        if target.startswith("docs/harness/"):
            old_target = target
        new_target = moves.get(old_target, old_target)
        rewritten = posixpath.relpath(new_target, posixpath.dirname(new_path))
        if new_target == old_target and original_path == new_path:
            return value
        rewritten += separator + fragment
        return "<" + rewritten + ">" if bracketed else rewritten

    text = data.decode("utf-8")
    text = INLINE_LINK.sub(lambda match: rewrite(match.group(0)), text)
    text = REFERENCE_LINK.sub(lambda match: match.group(1) + rewrite(match.group(2)), text)
    return text.encode("utf-8")


def approved_document(path, expected_sha256):
    """Return the exact approved bytes after checking the current reading copy."""
    path = resolve_path(path)
    current = path.read_bytes()
    if sha256(current) == expected_sha256:
        return current
    repository = repository_for(path)
    record = load_layout(repository) if repository is not None else None
    relative = path.relative_to(repository.resolve()).as_posix() if repository is not None else None
    document = next((entry for entry in record["documents"] if entry["path"] == relative and entry["original_sha256"] == expected_sha256), None) if record else None
    if document is None:
        raise ValueError("canonical bytes differ from the approved requirement")
    original = checked_reference(repository, document["original_snapshot"]).read_bytes()
    if sha256(original) != expected_sha256 or sha256(current) != document["relocated_sha256"]:
        raise ValueError("artifact layout snapshot or reading copy hash differs")
    if rewrite_links(original, document["original_path"], document["path"], record["moves"]) != current:
        raise ValueError("artifact layout changed content beyond link destinations")
    return original
