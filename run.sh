#!/usr/bin/env sh
# Wrapper for the wiki tooling (contract C6). Run from the repository root.
#
#   ./run.sh index [--check] [--root PATH]
#   ./run.sh lint [--root PATH]
#   ./run.sh serve
#   ./run.sh test
#
# Extra arguments pass through unchanged. Requires uv; there is no fallback
# to a system Python.

set -u

if ! command -v uv >/dev/null 2>&1; then
    echo "uv not found"
    exit 2
fi

cd "$(dirname "$0")" || exit 2

cmd="${1:-}"
if [ "$#" -gt 0 ]; then
    shift
fi

case "$cmd" in
    index) exec uv run python scripts/wiki/build_index.py "$@" ;;
    lint)  exec uv run python scripts/wiki/lint.py "$@" ;;
    serve) exec uv run mkdocs serve "$@" ;;
    test)  exec uv run pytest "$@" ;;
    *)
        echo "usage: ./run.sh <index|lint|serve|test> [args...]"
        exit 2
        ;;
esac
