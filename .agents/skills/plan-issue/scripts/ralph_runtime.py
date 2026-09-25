#!/usr/bin/env python3
"""Durable runtime primitives for Ralph execution."""
from __future__ import annotations

import errno
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path
from typing import Any


class RuntimeFailure(RuntimeError):
    pass


SECRET_VALUES = re.compile(
    r"bearer\s+\S+|https?://[^/\s:@]+:[^@\s/]+@|(?:authorization|proxy-authorization)\s*[:=]\s*\S+(?:\s+\S+)?|(?:[A-Za-z0-9_-]*(?:password|secret|token|cookie)|api[_-]?key)\s*[:=]\s*\S+",
    re.I,
)
SECRET_KEYS = re.compile(r"authorization|password|secret|token|cookie|api[_-]?key", re.I)
QUOTED_SECRET_VALUES = re.compile(
    r'''(["'][^"'\n]*(?:authorization|password|secret|token|cookie|api[_-]?key)["']\s*:\s*)(?:"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|[^\s,}]+)''',
    re.I,
)


def sanitize(value: str, limit: int = 500) -> str:
    return sanitize_text(value.strip())[:limit]


def sanitize_text(value: str) -> str:
    """Keep complete multiline evidence, redacting credentials without truncation."""
    value = QUOTED_SECRET_VALUES.sub(r'\1"[REDACTED]"', value)
    return "\n".join(SECRET_VALUES.sub("[REDACTED]", line) for line in value.split("\n"))


def normalized_failures(lines: list[str], returncode: int) -> list[str]:
    return [] if returncode == 0 else [sanitize_text(line.strip()) for line in lines if line.strip()]


class EventSink:
    """Write a safe console projection and private, structured execution records."""

    def __init__(self, git_directory: Path, state_path: Path, *, verbose: bool = False) -> None:
        task = hashlib.sha256(str(state_path.resolve()).encode()).hexdigest()[:16]
        self.root = git_directory / "ralph-runtime" / task / f"run-{uuid.uuid4()}"
        self.root.mkdir(parents=True, mode=0o700)
        try:
            self.root.chmod(0o700)
        except OSError:
            pass
        self.events_path = self.root / "events.jsonl"
        self.verbose = verbose
        self.color = bool(getattr(sys.stdout, "isatty", lambda: False)()) and "NO_COLOR" not in os.environ

    def private_file(self, name: str) -> Path:
        path = self.root / re.sub(r"[^A-Za-z0-9_.-]+", "-", name)
        path.touch(mode=0o600, exist_ok=True)
        try:
            path.chmod(0o600)
        except OSError:
            pass
        return path

    def emit(
        self,
        event: str,
        *,
        phase: int | str = "-",
        gate: str = "-",
        attempt: int | str = "-",
        duration_ms: int | str = "-",
        result: str,
        report_path: str | Path = "-",
        details: dict[str, Any] | None = None,
    ) -> None:
        record: dict[str, Any] = {
            "time": datetime_now(),
            "event": sanitize(event, 80),
            "phase": phase,
            "gate": sanitize(str(gate), 80),
            "attempt": attempt,
            "duration_ms": duration_ms,
            "result": sanitize(result, 160),
            "report_path": sanitize(str(report_path), 500),
        }
        if details:
            record["details"] = sanitize_value(details)
        with self.events_path.open("a", encoding="utf-8", newline="\n") as stream:
            json.dump(record, stream, ensure_ascii=False, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        line = " ".join(f"{key}={record[key]}" for key in ("time", "phase", "gate", "attempt", "duration_ms", "result", "report_path"))
        if self.verbose:
            line += f" event={record['event']}"
            if "details" in record:
                line += f" details={json.dumps(record['details'], ensure_ascii=False, sort_keys=True)}"
        if self.color:
            color = "\033[32m" if result in {"approved", "completed", "success", "resumed"} else "\033[31m" if result in {"failed", "rejected", "interrupted"} else "\033[36m"
            line = f"{color}{line}\033[0m"
        print(line, flush=True)


def sanitize_value(value: Any) -> Any:
    if isinstance(value, str):
        return sanitize(value)
    if isinstance(value, list):
        return [sanitize_value(item) for item in value]
    if isinstance(value, dict):
        return {sanitize(str(key), 80): "[REDACTED]" if SECRET_KEYS.search(str(key)) else sanitize_value(item) for key, item in value.items()}
    return value


def datetime_now() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat()


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        if os.environ.get("RALPH_TEST_ATOMIC_FAILURE") == "before-replace":
            raise OSError("simulated atomic write failure")
        os.replace(temporary, path)
        if os.name != "nt":
            descriptor = os.open(path.parent, os.O_RDONLY)
            try:
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass


def process_identity(pid: int) -> str | None:
    """Return a process birth identity, not merely a reusable PID."""
    if sys_platform_linux():
        try:
            stat = Path(f"/proc/{pid}/stat").read_text(encoding="utf-8")
            boot = Path("/proc/sys/kernel/random/boot_id").read_text(encoding="utf-8").strip()
            return f"linux:{boot}:{stat.rsplit(')', 1)[1].split()[19]}"
        except (OSError, IndexError):
            return None
    if os.name == "posix":
        result = subprocess.run(
            ["ps", "-o", "lstart=", "-p", str(pid)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        started = " ".join(result.stdout.split())
        return f"posix:{started}" if result.returncode == 0 and started else None
    if os.name == "nt":
        script = f"(Get-CimInstance Win32_Process -Filter \"ProcessId={pid}\").CreationDate.ToUniversalTime().ToString('o')"
        result = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", script],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        started = result.stdout.strip()
        return f"windows:{started}" if result.returncode == 0 and started else None
    return None


def sys_platform_linux() -> bool:
    return os.name == "posix" and Path("/proc/self/stat").is_file()


def process_verdict(pid: int, identity: str | None) -> str:
    """Return active, exited, or unverifiable for the exact prior process."""
    if os.name == "nt":
        current = process_identity(pid)
        if current is None:
            return "exited"
        if identity is None:
            return "unverifiable"
        return "active" if current == identity else "exited"
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return "exited"
    except PermissionError:
        return "unverifiable"
    except OSError as exception:
        return "exited" if exception.errno == errno.ESRCH else "unverifiable"
    current = process_identity(pid)
    if identity is None or current is None:
        return "unverifiable"
    return "active" if current == identity else "exited"


class TaskLock:
    def __init__(self, state_path: Path, lock_root: Path | None = None) -> None:
        if lock_root is None:
            lock_root = state_path.parent
            name = "ralph.lock"
        else:
            lock_root.mkdir(parents=True, exist_ok=True)
            name = hashlib.sha256(str(state_path.resolve()).encode()).hexdigest()
        self.path = lock_root / name
        self.owner_path = self.path / "owner.json"
        self.token = str(uuid.uuid4())
        self.owner = {
            "pid": os.getpid(),
            "process_identity": process_identity(os.getpid()),
            "token": self.token,
            "state_path": str(state_path),
            "acquired_at_ns": time.time_ns(),
        }

    def acquire(self) -> None:
        for _ in range(3):
            try:
                self.path.mkdir()
                try:
                    atomic_json(self.owner_path, self.owner)
                except Exception:
                    try:
                        self.path.rmdir()
                    except OSError:
                        pass
                    raise
                return
            except FileExistsError:
                previous = self._read_owner()
                verdict = process_verdict(previous["pid"], previous.get("process_identity"))
                if verdict == "active":
                    raise RuntimeFailure(f"a execução da tarefa já está ativa no PID {previous['pid']}")
                if verdict != "exited":
                    raise RuntimeFailure("o lock existente não pode ser recuperado porque a morte do proprietário não foi comprovada")
                if self._read_owner() != previous:
                    continue
                abandoned = self.path.with_name(f"{self.path.name}.abandoned-{self.token}")
                try:
                    os.replace(self.path, abandoned)
                except (FileNotFoundError, FileExistsError):
                    continue
                shutil.rmtree(abandoned)
        raise RuntimeFailure("o lock da tarefa mudou durante a recuperação; tente novamente")

    def _read_owner(self) -> dict[str, Any]:
        try:
            owner = json.loads(self.owner_path.read_text(encoding="utf-8"))
            if not isinstance(owner, dict) or not isinstance(owner.get("pid"), int) or not isinstance(owner.get("token"), str):
                raise ValueError
            return owner
        except (OSError, ValueError, json.JSONDecodeError):
            raise RuntimeFailure("o lock existente não pode ser recuperado porque sua identidade não é verificável")

    def release(self) -> None:
        try:
            current = self._read_owner()
        except RuntimeFailure:
            return
        if current.get("token") != self.token:
            return
        try:
            self.owner_path.unlink()
            self.path.rmdir()
        except FileNotFoundError:
            pass


def terminate_process_tree(process: subprocess.Popen[Any]) -> None:
    if process.poll() is not None:
        return
    if os.name == "posix":
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            return
    else:
        subprocess.run(
            ["taskkill", "/PID", str(process.pid), "/T", "/F"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    try:
        process.wait(timeout=5)
        return
    except subprocess.TimeoutExpired:
        pass
    if os.name == "posix":
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    else:
        process.kill()
    process.wait()


def popen_group(command: list[str] | str, **kwargs: Any) -> subprocess.Popen[Any]:
    if os.name == "posix":
        kwargs["start_new_session"] = True
    elif os.name == "nt":
        kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    return subprocess.Popen(command, **kwargs)


def evidence_digest(value: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
