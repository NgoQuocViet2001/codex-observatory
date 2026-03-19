# Codex Integration

## What it does

`install-codex --patch-codex` adds a small hook to the local `codex` launcher so this works:

```bash
codex stats
codex stats compact
codex stats full
```

Without that patch, use:

```bash
codex-observatory
codex-stats
```

## Install

### Installed from `npm`, `pip`, or `pipx`

```bash
codex-observatory install-codex --patch-codex
codex stats
```

### Installed from a standalone binary

```bash
./codex-observatory install-codex --patch-codex
codex stats
```

Windows:

```powershell
& "$HOME\\codex-observatory.exe" install-codex --patch-codex
codex stats
```

### Installed from a local repo clone

```powershell
.\scripts\install-codex.ps1 -PatchCodex
codex stats
```

```bash
./scripts/install-codex.sh --patch-codex
codex stats
```

## What gets installed

- `~/.codex/skills/codex-observatory/SKILL.md`
- `~/.codex/tools/codex-stats.ps1`
- `~/.codex/tools/codex-stats.sh`
- a small `stats` dispatch hook inside the local `codex` launcher

## Uninstall

```bash
codex-observatory uninstall-codex
```

This removes the Codex Observatory skill, helper tools, and restores the patched `codex` launcher from the backups created during install when those backups exist.

For local repo clones, you can also use:

```powershell
.\scripts\uninstall-codex.ps1
```

```bash
./scripts/uninstall-codex.sh
```

## Notes

- only `stats` and `stat` are intercepted
- other Codex commands still run normally
- Codex must already be installed before patching
- `codex stats` is the recommended user-facing command in the docs
- `codex-observatory` and `codex-stats` remain available as direct aliases
