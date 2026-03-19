# Codex Observatory

Production-style local observability for Codex. Track prompts, sessions, token flow, cache share, model mix, streaks, heatmaps, and recent activity directly from local Codex logs.

[![CI](https://github.com/NgoQuocViet2001/codex-observatory/actions/workflows/ci.yml/badge.svg)](https://github.com/NgoQuocViet2001/codex-observatory/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/NgoQuocViet2001/codex-observatory)](https://github.com/NgoQuocViet2001/codex-observatory/releases)
[![Python](https://img.shields.io/badge/python-3.10%2B-3776AB)](https://www.python.org/)

## Why this exists

Codex already writes rich local usage logs, but it does not ship a built-in `codex stats` command, dashboard, or token analytics view. `codex-observatory` exists to close that gap and turn raw JSONL telemetry into a production-style local dashboard.

It reads:

- `~/.codex/history.jsonl`
- `~/.codex/sessions/**/*.jsonl`

## Highlights

- Live local metrics without calling any remote API.
- Smart terminal dashboard with `compact`, `normal`, and `full` views.
- Model breakdowns for both 30-day and all-time windows.
- Bordered tables, heatmap, sparkline, load bars, and cache-share summaries.
- JSON output for automation or scripting.
- Works on Windows, macOS, and Linux with Python 3.10+.
- Optional shim patch so `codex stats` works as a native-feeling subcommand.

## Install

### Option 1: install from GitHub with `pipx`

```bash
pipx install git+https://github.com/NgoQuocViet2001/codex-observatory.git
```

### Option 2: install from a local clone

```bash
git clone git@git-personal:NgoQuocViet2001/codex-observatory.git
cd codex-observatory
python -m pip install -e .
```

If your Python scripts directory is not on `PATH`, use:

```bash
python -m codex_observatory
```

## Core commands

```bash
codex-observatory
codex-observatory compact
codex-observatory full --daily-days 14 --monthly-months 12
codex-stats compact --no-color
codex-observatory --json
python -m codex_observatory full --no-color
```

## Optional Codex integration

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

The default install adds the local package, helper scripts, and a Codex skill into `~/.codex/skills/codex-observatory`.

The optional patch mode also injects a small dispatch hook into the local `codex` launcher so these work directly:

```bash
codex stats
codex stats compact
```

Why patch the launcher? Because Codex does not have built-in stats today, and most people will naturally try `codex stats` before they remember a separate binary name.

## Docs

- [Install guide](./docs/INSTALL.md)
- [Usage guide](./docs/USAGE.md)
- [Codex integration](./docs/CODEX_INTEGRATION.md)
- [Changelog](./CHANGELOG.md)

## Release flow

```bash
python -m unittest discover -s tests -v
python -m pip install build
python -m build
git tag v1.0.0
git push origin main --tags
```

Pushing a `v*` tag triggers GitHub Actions to build `sdist` and `wheel`, then publish them as GitHub release assets.
