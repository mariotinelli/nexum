#!/usr/bin/env python3
"""Prepare Project Flow folders or print a read-only legacy organization review."""

import argparse
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True

from artifact_paths import checked_path, contained_path, relocated_path


IGNORE_RULES = (
    "/.runs/",
    "/.locks/",
    "/features/*/.work/",
    "/bugs/*/.work/",
    "/scopes/*/.work/",
)


def artifact_directory(repository, relative):
    parts = Path(relative).parts
    if len(parts) != 4 or parts[:2] != ("docs", "harness") or parts[2] not in {"features", "bugs", "scopes", ".runs"}:
        raise ValueError("artifact must be docs/harness/<features|bugs|scopes|.runs>/<identity>")
    if parts[3] in {".flow", ".work", ".", ".."}:
        raise ValueError("invalid artifact identity")
    return contained_path(repository, relative)


def prepare(repository, relative):
    repository = checked_path(repository)
    if not repository.is_dir():
        raise ValueError("repository must be an existing directory")
    root = artifact_directory(repository, relative)
    ignore = contained_path(repository, "docs/harness/.gitignore")
    original = ignore.read_bytes() if ignore.exists() else b""
    existing = original.decode("utf-8").splitlines()
    missing = [rule for rule in IGNORE_RULES if rule not in existing]
    content = original
    if missing:
        content += (b"\n" if original and not original.endswith(b"\n") else b"")
        content += ("\n# Project Flow temporary execution files\n" + "\n".join(missing) + "\n").encode("utf-8")
    created = []
    temporary = None
    try:
        for directory in (root, root / ".flow", root / ".work"):
            checked_path(directory)
            absent = []
            current = directory
            while not current.exists():
                absent.append(current)
                current = current.parent
            for candidate in reversed(absent):
                candidate.mkdir()
                created.append(candidate)
            if not directory.is_dir():
                raise ValueError("artifact location conflicts with a file")
        if missing:
            descriptor, name = tempfile.mkstemp(prefix=".gitignore-", suffix=".tmp", dir=ignore.parent)
            temporary = Path(name)
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
            checked_path(ignore)
            if (ignore.read_bytes() if ignore.exists() else b"") != original:
                raise ValueError("Git ignore rules changed during preparation; retry")
            os.replace(temporary, ignore)
        return {"artifact": relative, "state_directory": ".flow", "temporary_directory": ".work", "gitignore": "docs/harness/.gitignore"}
    except BaseException:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
        for directory in reversed(created):
            directory.rmdir()
        raise


def review(repository, relative):
    root = artifact_directory(checked_path(repository), relative)
    if not root.is_dir():
        raise ValueError("artifact directory does not exist")
    entries = []
    # Only classify known documentation. Operational files need dependency and
    # immutable-history review, never a deletion heuristic based on their names.
    for path in sorted(root.rglob("*")):
        checked_path(path)
        if not path.is_file():
            continue
        source = path.relative_to(root).as_posix()
        destination = None
        action = "retain"
        if path.parent == root and path.name in {"interview.md", "pending-questions.md"}:
            destination = "history/" + path.name
            action = "review-move"
        elif path.parent == root and path.name not in {"feature.md", "bug.md", "scope.md"}:
            action = "review-dependencies"
        elif source.startswith(".work/"):
            action = "review-discardability"
        entries.append({
            "path": source,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "action": action,
            "proposed_destination": destination,
            "conflict": destination is not None and (root / destination).exists(),
        })
    return {"artifact": relative, "read_only": True, "files": entries}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "review", "locate"))
    parser.add_argument("repository", type=Path)
    parser.add_argument("artifact", help="Repository-relative item or scope directory")
    args = parser.parse_args()
    try:
        if args.action == "locate":
            result = {"path": str(relocated_path(contained_path(args.repository, args.artifact)))}
        else:
            result = (prepare if args.action == "prepare" else review)(args.repository, args.artifact)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (OSError, ValueError, UnicodeDecodeError) as error:
        print(f"invalid: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
