#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
SKILL_DIR="$CODEX_HOME/skills/codex-observatory"

echo "Installing codex-observatory package..."
python3 -m pip install -e "$REPO_ROOT"

echo "Installing Codex skill into $SKILL_DIR ..."
mkdir -p "$SKILL_DIR"
cp "$REPO_ROOT/integrations/codex-skill/SKILL.md" "$SKILL_DIR/SKILL.md"

echo
echo "Done."
echo "Try:"
echo "  codex-stats"
echo "  codex-stats compact"
