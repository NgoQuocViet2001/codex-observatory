# Codex Integration

`codex-observatory` ships with an optional Codex skill so Codex can call the local dashboard directly instead of estimating usage from memory.

## Install the packaged skill

### PowerShell

```powershell
.\scripts\install-codex.ps1
```

### Bash / zsh

```bash
./scripts/install-codex.sh
```

## What gets installed

- the Python package itself
- `~/.codex/skills/codex-observatory/SKILL.md`

## What it does not modify

- it does not patch the global `codex` executable
- it does not overwrite your shell aliases
- it does not delete any existing Codex skills
