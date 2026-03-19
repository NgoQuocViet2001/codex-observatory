# Codex Observatory

Production-style local observability for Codex. Track prompts, sessions, token flow, cache share, model mix, streaks, heatmaps, and recent activity directly from local Codex logs.

[![CI](https://github.com/NgoQuocViet2001/codex-observatory/actions/workflows/ci.yml/badge.svg)](https://github.com/NgoQuocViet2001/codex-observatory/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/NgoQuocViet2001/codex-observatory)](https://github.com/NgoQuocViet2001/codex-observatory/releases)
[![Python](https://img.shields.io/badge/python-3.10%2B-3776AB)](https://www.python.org/)
[![Node](https://img.shields.io/badge/node-18%2B-5FA04E)](https://nodejs.org/)

## Why this exists

Codex already writes rich local usage logs, but it does not ship a built-in `codex stats` command, dashboard, or token analytics view. `codex-observatory` exists to close that gap and turn raw JSONL telemetry into a production-style local dashboard.

It reads:

- `~/.codex/history.jsonl`
- `~/.codex/sessions/**/*.jsonl`

## What you get after install

`codex-observatory` is a standalone CLI first.

It does **not** automatically turn into `codex stats` unless you run the optional Codex integration patch.

| What you want | What you install | Command that works right away | Extra step for `codex stats` |
| --- | --- | --- | --- |
| Standalone dashboard with no patching | Binary, `npm`, or `pip` | `codex-observatory` | Yes |
| Short standalone alias | `npm` or `pip` | `codex-stats` | Yes |
| Native-feeling Codex subcommand | Any install method | `codex-observatory` first | Run `install-codex --patch-codex` |

If you only do this:

```bash
codex-observatory
```

then you have the standalone dashboard only.

If you want this:

```bash
codex stats
```

you must run the extra integration step:

```bash
codex-observatory install-codex --patch-codex
```

## Highlights

- Live local metrics without calling any remote API.
- Smart terminal dashboard with `compact`, `normal`, and `full` views.
- Model breakdowns for both 30-day and all-time windows.
- Bordered tables, heatmap, sparkline, load bars, and cache-share summaries.
- JSON output for automation or scripting.
- Works on Windows, macOS, and Linux with Python 3.10+.
- Ships prebuilt binaries for Windows x64, macOS Intel, macOS Apple Silicon, and Linux x64.
- Can be installed with `npm` / `npx` if you do not want to install Python first.
- Optional shim patch so `codex stats` works as a native-feeling subcommand.

## Install

Choose the outcome you want:

- `codex-observatory`: standalone dashboard command
- `codex-stats`: short standalone alias, available for `npm` and `pip` installs
- `codex stats`: built-in style Codex subcommand, available only after the patch step

### Windows

No Python, direct binary:

```powershell
Invoke-WebRequest "https://github.com/NgoQuocViet2001/codex-observatory/releases/download/v1.2.2/codex-observatory-windows-x64.exe" -OutFile "$HOME\\codex-observatory.exe"
& "$HOME\\codex-observatory.exe"
```

Enable `codex stats` after the binary install:

```powershell
& "$HOME\\codex-observatory.exe" install-codex --patch-codex
codex stats
```

Node / npm:

```powershell
npm install -g github:NgoQuocViet2001/codex-observatory#v1.2.2
codex-observatory
codex-stats
```

Enable `codex stats` after the npm install:

```powershell
codex-observatory install-codex --patch-codex
codex stats
```

### macOS

No Python, direct binary:

```bash
curl -L https://github.com/NgoQuocViet2001/codex-observatory/releases/download/v1.2.2/codex-observatory-macos-arm64 -o ./codex-observatory
chmod +x ./codex-observatory
./codex-observatory
```

If you are on Intel Mac, download `codex-observatory-macos-x64` instead.

Enable `codex stats` after the binary install:

```bash
./codex-observatory install-codex --patch-codex
codex stats
```

Node / npm:

```bash
npm install -g github:NgoQuocViet2001/codex-observatory#v1.2.2
codex-observatory
codex-stats
```

Enable `codex stats` after the npm install:

```bash
codex-observatory install-codex --patch-codex
codex stats
```

### Ubuntu / Linux

No Python, direct binary:

```bash
curl -L https://github.com/NgoQuocViet2001/codex-observatory/releases/download/v1.2.2/codex-observatory-linux-x64 -o ./codex-observatory
chmod +x ./codex-observatory
./codex-observatory
```

Enable `codex stats` after the binary install:

```bash
./codex-observatory install-codex --patch-codex
codex stats
```

Node / npm:

```bash
npm install -g github:NgoQuocViet2001/codex-observatory#v1.2.2
codex-observatory
codex-stats
```

Enable `codex stats` after the npm install:

```bash
codex-observatory install-codex --patch-codex
codex stats
```

### Python / pipx

```bash
pipx install git+https://github.com/NgoQuocViet2001/codex-observatory.git
codex-observatory
codex-stats
codex-observatory install-codex --patch-codex
codex stats
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
codex-observatory install-codex --patch-codex
codex-observatory --json
python -m codex_observatory full --no-color
```

## Optional Codex integration

Important:

- `codex-observatory` and `codex-stats` are standalone commands
- `codex stats` is a separate, optional integration step
- `./scripts/install-codex.ps1` and `./scripts/install-codex.sh` are mainly for people who cloned this repo locally
- if you installed from a binary, `npm`, or `pip`, prefer `codex-observatory install-codex --patch-codex`

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

The default script install adds the local package, helper scripts, and a Codex skill into `~/.codex/skills/codex-observatory`.

It does **not** enable `codex stats` yet.

The optional patch mode also injects a small dispatch hook into the local `codex` launcher so these work directly:

```bash
codex stats
codex stats compact
```

Why patch the launcher? Because Codex does not have built-in stats today, and most people will naturally try `codex stats` before they remember a separate binary name.

If you installed the standalone binary instead of a global command, run the same step with that binary path:

```bash
./codex-observatory install-codex --patch-codex
```

## Docs

- [Install guide](./docs/INSTALL.md)
- [Usage guide](./docs/USAGE.md)
- [Codex integration](./docs/CODEX_INTEGRATION.md)
- [Changelog](./CHANGELOG.md)

## Release flow

```bash
python -m unittest discover -s tests -v
npm test
python -m pip install build
git tag v1.2.2
git push origin main --tags
```

Pushing a `v*` tag triggers GitHub Actions to build the Python package plus standalone binaries for Windows, macOS, and Linux, then publish them as GitHub release assets.
