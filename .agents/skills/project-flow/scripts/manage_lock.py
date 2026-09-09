#!/usr/bin/env python3
"""Manage recoverable Project Flow item locks without network access."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path


def fail(message: str) -> None:
    raise ValueError(message)


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def require_uuid(value: str, label: str) -> None:
    try:
        uuid.UUID(value)
    except ValueError:
        fail(f"{label} must be a UUID")


def prepare_directory(path: Path) -> Path:
    absolute = Path(os.path.abspath(path))
    absolute.mkdir(parents=True, exist_ok=True)
    if Path(os.path.realpath(absolute)) != absolute or absolute.is_symlink():
        fail("locks directory cannot be a symlink or junction")
    return absolute


def paths(directory: Path, item_key: str) -> tuple[Path, Path]:
    if not item_key.strip():
        fail("item_key must be non-empty")
    digest = hashlib.sha256(item_key.encode("utf-8")).hexdigest()
    return directory / f"{digest}.lock.json", directory / f"{digest}.guard"


def read_lock(path: Path) -> dict[str, object]:
    if path.is_symlink():
        fail("lock file cannot be a symlink")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail("lock does not exist")
    if not isinstance(value, dict):
        fail("lock content must be an object")
    required = {"schema_version", "item_key", "run_id", "lock_id", "acquired_at"}
    if required - value.keys() or value.keys() - (required | {"recovered_from", "recovery_reason"}):
        fail("lock content has invalid fields")
    if value["schema_version"] != 1:
        fail("unsupported lock schema_version")
    require_uuid(str(value["run_id"]), "lock run_id")
    require_uuid(str(value["lock_id"]), "lock_id")
    return value


def write_exclusive(path: Path, payload: dict[str, object]) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
    except Exception:
        path.unlink(missing_ok=True)
        raise


def acquire(directory: Path, item_key: str, run_id: str) -> dict[str, object]:
    require_uuid(run_id, "run_id")
    lock_path, _ = paths(directory, item_key)
    payload: dict[str, object] = {
        "schema_version": 1,
        "item_key": item_key,
        "run_id": run_id,
        "lock_id": str(uuid.uuid4()),
        "acquired_at": now(),
    }
    try:
        write_exclusive(lock_path, payload)
    except FileExistsError:
        owner = read_lock(lock_path)
        fail(f"item is locked by run {owner['run_id']} lock {owner['lock_id']} acquired {owner['acquired_at']}")
    return payload


def verify(directory: Path, item_key: str, run_id: str, lock_id: str) -> dict[str, object]:
    require_uuid(run_id, "run_id")
    require_uuid(lock_id, "lock_id")
    lock_path, _ = paths(directory, item_key)
    owner = read_lock(lock_path)
    if owner["item_key"] != item_key or owner["run_id"] != run_id or owner["lock_id"] != lock_id:
        fail("lock ownership changed; this execution is fenced")
    return owner


def guard(path: Path) -> int:
    try:
        return os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        fail("lock recovery or release is already in progress")


def recover(directory: Path, item_key: str, run_id: str, expected_lock_id: str, reason: str) -> dict[str, object]:
    require_uuid(run_id, "run_id")
    require_uuid(expected_lock_id, "expected_lock_id")
    if not reason.strip():
        fail("recovery reason must be non-empty")
    lock_path, guard_path = paths(directory, item_key)
    guard_descriptor = guard(guard_path)
    replacement_path = directory / f".{lock_path.name}.{uuid.uuid4()}.tmp"
    try:
        owner = read_lock(lock_path)
        if owner["item_key"] != item_key or owner["lock_id"] != expected_lock_id:
            fail("lock owner changed; recovery refused")
        payload: dict[str, object] = {
            "schema_version": 1,
            "item_key": item_key,
            "run_id": run_id,
            "lock_id": str(uuid.uuid4()),
            "acquired_at": now(),
            "recovered_from": expected_lock_id,
            "recovery_reason": reason,
        }
        write_exclusive(replacement_path, payload)
        os.replace(replacement_path, lock_path)
        return payload
    finally:
        os.close(guard_descriptor)
        replacement_path.unlink(missing_ok=True)
        guard_path.unlink(missing_ok=True)


def release(directory: Path, item_key: str, run_id: str, lock_id: str) -> dict[str, object]:
    lock_path, guard_path = paths(directory, item_key)
    guard_descriptor = guard(guard_path)
    try:
        owner = verify(directory, item_key, run_id, lock_id)
        lock_path.unlink()
        return owner
    finally:
        os.close(guard_descriptor)
        guard_path.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    acquire_parser = subparsers.add_parser("acquire")
    acquire_parser.add_argument("directory", type=Path)
    acquire_parser.add_argument("item_key")
    acquire_parser.add_argument("run_id")
    verify_parser = subparsers.add_parser("verify")
    verify_parser.add_argument("directory", type=Path)
    verify_parser.add_argument("item_key")
    verify_parser.add_argument("run_id")
    verify_parser.add_argument("lock_id")
    recover_parser = subparsers.add_parser("recover")
    recover_parser.add_argument("directory", type=Path)
    recover_parser.add_argument("item_key")
    recover_parser.add_argument("run_id")
    recover_parser.add_argument("expected_lock_id")
    recover_parser.add_argument("reason")
    release_parser = subparsers.add_parser("release")
    release_parser.add_argument("directory", type=Path)
    release_parser.add_argument("item_key")
    release_parser.add_argument("run_id")
    release_parser.add_argument("lock_id")
    args = parser.parse_args()
    try:
        directory = prepare_directory(args.directory)
        if args.command == "acquire":
            result = acquire(directory, args.item_key, args.run_id)
        elif args.command == "verify":
            result = verify(directory, args.item_key, args.run_id, args.lock_id)
        elif args.command == "recover":
            result = recover(directory, args.item_key, args.run_id, args.expected_lock_id, args.reason)
        else:
            result = release(directory, args.item_key, args.run_id, args.lock_id)
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
