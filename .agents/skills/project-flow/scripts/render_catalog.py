#!/usr/bin/env python3
"""Render the complete local catalog preview and verify its exact approval bytes."""

import argparse
import json
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True

from catalog_contract import digest, render
from validate_scope_state import validate


START = b"<!-- project-flow:catalog:start -->"
END = b"<!-- project-flow:catalog:end -->"


def scope_block(document):
    if document.count(START) != 1 or document.count(END) != 1:
        raise ValueError("scope document requires exactly one pair of catalog markers")
    start, end = document.index(START), document.index(END) + len(END)
    if end <= start:
        raise ValueError("scope catalog markers are reversed")
    if document[end:end + 1] == b"\n":
        end += 1
    return start, end


def atomic_write(path, content):
    staged = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".catalog-", delete=False) as stream:
            staged = Path(stream.name)
            stream.write(content)
        staged.replace(path)
    finally:
        if staged is not None:
            staged.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("state", type=Path)
    parser.add_argument("--output", type=Path, help="Write the catalog block as UTF-8 with LF endings")
    parser.add_argument("--check", type=Path, help="Compare a complete preview byte-for-byte")
    parser.add_argument("--scope-document", type=Path, help="Replace the single generated block in an existing scope Markdown file")
    parser.add_argument("--check-scope", type=Path, help="Compare the generated block in a scope Markdown file")
    parser.add_argument("--hash", action="store_true")
    args = parser.parse_args()
    try:
        targets = [path.resolve() for path in (args.output, args.scope_document) if path is not None]
        if args.state.resolve() in targets or len(targets) != len(set(targets)):
            raise ValueError("output targets must be distinct from each other and the state")
        state = validate(args.state)
        if state["schema_version"] != 3 or "catalog-proposed" not in state["completed_phases"]:
            raise ValueError("rendering requires a proposed v3 catalog; explicitly enrich legacy states first")
        content = render(state).encode("utf-8")
        if args.check and args.check.read_bytes() != content:
            raise ValueError("preview differs from complete catalog projection (omitted, duplicate, reordered or changed content)")
        if args.check_scope:
            document = args.check_scope.read_bytes()
            start, end = scope_block(document)
            if document[start:end] != content:
                raise ValueError("scope document differs from complete catalog projection")
        if args.scope_document:
            if args.scope_document.resolve() == args.state.resolve():
                raise ValueError("scope document cannot replace the state")
            document = args.scope_document.read_bytes()
            start, end = scope_block(document)
            atomic_write(args.scope_document, document[:start] + content + document[end:])
        if args.output:
            if args.output.resolve() == args.state.resolve():
                raise ValueError("output cannot replace the state")
            atomic_write(args.output, content)
        if args.hash:
            print(digest(state))
        elif not any((args.output, args.check, args.scope_document, args.check_scope)):
            sys.stdout.buffer.write(content)
    except (OSError, ValueError, TypeError, KeyError, StopIteration, json.JSONDecodeError) as error:
        print(f"invalid: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
