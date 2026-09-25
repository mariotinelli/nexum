#!/usr/bin/env python3
"""Open one fresh Codex execution with a structured result contract."""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("develop", "validate", "validate-integral"), required=True)
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--schema", required=True)
    parser.add_argument("--result", required=True)
    parser.add_argument("--repo", required=True)
    arguments = parser.parse_args()

    sandbox = "workspace-write" if arguments.mode == "develop" else "read-only"
    command = [
        os.environ.get("CODEX_BIN", "codex"),
        "exec",
        "--sandbox",
        sandbox,
        "--output-schema",
        str(Path(arguments.schema).resolve()),
        "--output-last-message",
        str(Path(arguments.result).resolve()),
        "-",
    ]
    prompt = Path(arguments.prompt).read_text(encoding="utf-8")
    completed = subprocess.run(
        command,
        cwd=arguments.repo,
        input=prompt,
        text=True,
        encoding="utf-8",
        errors="strict",
        check=False,
    )
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
