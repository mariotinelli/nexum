#!/usr/bin/env bash
set -euo pipefail

if [[ "${1:-}" != "execute" || $# -lt 2 ]]; then
  echo "usage: ralph.sh execute <planning.md> [--max-attempts N] [--dev-timeout-minutes N] [--validation-timeout-minutes N] [--tests-timeout-minutes N] [--verbose]" >&2
  exit 64
fi

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
if [[ -n "${PYTHON:-}" ]]; then
  python_bin="$PYTHON"
elif command -v python3 >/dev/null 2>&1; then
  python_bin="python3"
elif command -v python >/dev/null 2>&1; then
  python_bin="python"
else
  echo "Ralph requires Python 3.10+; neither python3 nor python was found in PATH." >&2
  exit 127
fi
shift
exec "$python_bin" "$script_dir/scripts/execute_phase.py" "$@"
