#!/usr/bin/env bash
set -euo pipefail

if [[ "${1:-}" != "execute" || $# -lt 4 || "${3:-}" != "--state" ]]; then
  echo "usage: ralph.sh execute <planning.md> --state <plan-issue.json> [--max-gate-rejections N] [--dev-timeout-minutes N] [--validation-timeout-minutes N] [--tests-timeout-minutes N] [--authorize-discard SHA256 --authorized-by ACTOR] [--verbose]" >&2
  exit 64
fi

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
python_bin="${PYTHON:-python3}"
planning="$2"
state="$4"
shift 4
exec "$python_bin" "$script_dir/scripts/execute_phase.py" "$planning" --state "$state" "$@"
