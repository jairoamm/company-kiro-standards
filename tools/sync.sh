#!/bin/sh
set -eu

SCRIPT_DIRECTORY=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

if [ -n "${PYTHON:-}" ]; then
  PYTHON_COMMAND=$PYTHON
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_COMMAND=$(command -v python3)
elif command -v python >/dev/null 2>&1; then
  PYTHON_COMMAND=$(command -v python)
else
  echo "ERROR: Python 3 is required to run the synchronizer." >&2
  exit 127
fi

exec "$PYTHON_COMMAND" "$SCRIPT_DIRECTORY/sync.py" "$@"
