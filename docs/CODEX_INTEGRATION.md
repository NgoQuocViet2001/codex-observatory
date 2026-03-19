# Codex Integration

`codex-observatory` ships with an optional Codex skill and an optional launcher patch so Codex can call the local dashboard directly instead of estimating usage from memory.

## Why this repo exists

Codex already stores prompt and token history locally, but it does not currently expose a built-in stats command such as `codex stats`. This repo exists to fill that product gap with a local-first dashboard and a clean way to wire that dashboard into Codex.

## Short answer

No, installing `codex-observatory` by itself does **not** automatically create `codex stats`.

There are two layers:

1. Standalone commands:

```bash
codex-observatory
codex-stats
```

2. Optional Codex launcher patch:

```bash
codex-observatory install-codex --patch-codex
codex stats
```

If you never run the patch step, `codex stats` will not exist.

## Which command should you run

| Your starting point | Recommended command |
| --- | --- |
| You installed a release binary | `./codex-observatory install-codex --patch-codex` |
| You installed with `npm` | `codex-observatory install-codex --patch-codex` |
| You installed with `pip` / `pipx` | `codex-observatory install-codex --patch-codex` |
| You cloned this repo locally | `.\scripts\install-codex.ps1 -PatchCodex` or `./scripts/install-codex.sh --patch-codex` |

The repo scripts are convenience wrappers for local contributors. End users usually do **not** need them unless they are installing from a clone.

## Install the packaged skill

### PowerShell

```powershell
.\scripts\install-codex.ps1
.\scripts\install-codex.ps1 -PatchCodex
```

### Bash / zsh

```bash
./scripts/install-codex.sh
./scripts/install-codex.sh --patch-codex
```

If you are **not** running from a local clone, use the installed command instead:

```bash
codex-observatory install-codex --patch-codex
```

If you are using a downloaded standalone binary, call the same command through that binary path:

```bash
./codex-observatory install-codex --patch-codex
```

## What gets installed

- the Python package itself
- `~/.codex/skills/codex-observatory/SKILL.md`
- `~/.codex/tools/codex-stats.ps1`
- `~/.codex/tools/codex-stats.sh`

This step installs helper assets for Codex and the skill prompt, but by itself it does **not** hook the `codex` launcher yet.

## What patch mode adds

When you pass `-PatchCodex` or `--patch-codex`, the installer adds a small dispatch hook to the existing `codex` launcher so these commands work directly:

```bash
codex stats
codex stat
codex stats compact
```

That hook only intercepts `stats` and `stat`. Every other Codex command still falls through to the original launcher.

## Full flows

### Flow A: standalone dashboard only

```bash
codex-observatory
```

or, if your install method provides it:

```bash
codex-stats
```

### Flow B: real `codex stats`

```bash
codex-observatory install-codex --patch-codex
codex stats
codex stats compact
```

### Flow C: local repo clone

```powershell
.\scripts\install-codex.ps1 -PatchCodex
codex stats
```

```bash
./scripts/install-codex.sh --patch-codex
codex stats
```

## Why patching helps

- Codex does not have a built-in stats subcommand today, so `codex stats` is the first thing many users will try.
- Teams can standardize on one memorable command instead of teaching both `codex` and `codex-stats`.
- Codex skills can use the freshest local data without asking the model to estimate usage from memory.
- The result behaves more like a native feature while still staying fully local.

## Backup and upgrade behavior

- Original launchers are backed up under `~/.codex/integrations/codex-observatory/backups`.
- If you upgrade Codex and the installer refreshes its shims, re-run the integration installer to re-apply `codex stats`.

## What it does not modify

- it does not change any Codex behavior outside `stats` / `stat`
- it does not overwrite your shell aliases
- it does not delete any existing Codex skills
