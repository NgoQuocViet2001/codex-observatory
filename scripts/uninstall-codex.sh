#!/usr/bin/env bash
set -euo pipefail

REMOVE_PACKAGE=0
PYTHON_BIN="${PYTHON_BIN:-python3}"

while (($#)); do
  case "$1" in
    --remove-package)
      REMOVE_PACKAGE=1
      shift
      ;;
    --python)
      if [ $# -lt 2 ]; then
        echo "Missing value for --python" >&2
        exit 1
      fi
      PYTHON_BIN="$2"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

PYTHON_PATH="$(command -v "$PYTHON_BIN")"

echo "Removing Codex integration assets..."
"$PYTHON_PATH" -m codex_observatory uninstall-codex

if [ "$REMOVE_PACKAGE" -eq 1 ]; then
  echo "Removing codex-observatory package..."
  "$PYTHON_PATH" -m pip uninstall -y codex-observatory
fi

echo
echo "Done."
