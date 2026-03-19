#!/usr/bin/env bash
set -euo pipefail

PATCH_CODEX=0
PYTHON_BIN="${PYTHON_BIN:-python3}"

while (($#)); do
  case "$1" in
    --patch-codex)
      PATCH_CODEX=1
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

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_PATH="$(command -v "$PYTHON_BIN")"

echo "Installing codex-observatory package..."
"$PYTHON_PATH" -m pip install -e "$REPO_ROOT"

echo "Installing Codex integration assets..."
INSTALL_ARGS=(
  -m
  codex_observatory.codex_integration
  --repo-root
  "$REPO_ROOT"
  --python-bin
  "$PYTHON_PATH"
)
if [ "$PATCH_CODEX" -eq 1 ]; then
  INSTALL_ARGS+=(--patch-codex)
fi
"$PYTHON_PATH" "${INSTALL_ARGS[@]}"

echo
echo "Done."
echo "Try:"
if [ "$PATCH_CODEX" -eq 1 ]; then
  echo "  codex stats"
  echo "  codex stats compact"
else
  echo "  codex-stats"
  echo "  codex-stats compact"
  echo
  echo "Need a built-in style Codex subcommand?"
  echo "  ./scripts/install-codex.sh --patch-codex"
fi
