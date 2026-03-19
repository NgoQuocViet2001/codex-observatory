# Codex Observatory

Local stats dashboard for Codex. Read usage directly from machine logs and inspect prompts, tokens, sessions, streaks, model mix, and trends.

[![CI](https://github.com/NgoQuocViet2001/codex-observatory/actions/workflows/ci.yml/badge.svg)](https://github.com/NgoQuocViet2001/codex-observatory/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/NgoQuocViet2001/codex-observatory)](https://github.com/NgoQuocViet2001/codex-observatory/releases)
[![Node](https://img.shields.io/badge/node-18%2B-5FA04E)](https://nodejs.org/)
[![Python](https://img.shields.io/badge/python-3.10%2B-3776AB)](https://www.python.org/)

## Why

Codex writes rich local logs, but it does not ship a built-in `codex stats` command.

Codex Observatory fills that gap with a local-first dashboard built from Codex prompt/session logs, including:

- `~/.codex/history.jsonl` when the Codex install still writes it
- `~/.codex/sessions/**/*.jsonl` on newer Codex installs that only keep session logs

This is especially useful when:

- one Codex account is shared by multiple people
- one machine uses multiple Codex accounts
- you want machine-level usage, not account-level usage

## Recommended Flow

Use this setup everywhere:

```bash
npm install -g github:NgoQuocViet2001/codex-observatory
codex-observatory install-codex --patch-codex
codex stats
```

From that point on, use `codex stats` as the main command in this repo and in the docs.

One-shot without global install:

```bash
npx github:NgoQuocViet2001/codex-observatory compact
```

## Quickstart

### Windows

If you already have Node.js:

```powershell
npm install -g github:NgoQuocViet2001/codex-observatory
codex-observatory install-codex --patch-codex
codex stats
```

No Node, use the binary:

```powershell
Invoke-WebRequest "https://github.com/NgoQuocViet2001/codex-observatory/releases/latest/download/codex-observatory-windows-x64.exe" -OutFile "$HOME\\codex-observatory.exe"
& "$HOME\\codex-observatory.exe" install-codex --patch-codex
codex stats
```

Windows ARM64:

```powershell
Invoke-WebRequest "https://github.com/NgoQuocViet2001/codex-observatory/releases/latest/download/codex-observatory-windows-arm64.exe" -OutFile "$HOME\\codex-observatory.exe"
& "$HOME\\codex-observatory.exe" install-codex --patch-codex
codex stats
```

### macOS

If you already have Node.js:

```bash
npm install -g github:NgoQuocViet2001/codex-observatory
codex-observatory install-codex --patch-codex
codex stats
```

No Node, use the binary:

Apple Silicon:

```bash
curl -L https://github.com/NgoQuocViet2001/codex-observatory/releases/latest/download/codex-observatory-macos-arm64 -o ./codex-observatory
chmod +x ./codex-observatory
./codex-observatory install-codex --patch-codex
codex stats
```

Intel:

```bash
curl -L https://github.com/NgoQuocViet2001/codex-observatory/releases/latest/download/codex-observatory-macos-x64 -o ./codex-observatory
chmod +x ./codex-observatory
./codex-observatory install-codex --patch-codex
codex stats
```

### Ubuntu / Linux

If you already have Node.js:

```bash
npm install -g github:NgoQuocViet2001/codex-observatory
codex-observatory install-codex --patch-codex
codex stats
```

No Node, use the binary:

```bash
curl -L https://github.com/NgoQuocViet2001/codex-observatory/releases/latest/download/codex-observatory-linux-x64 -o ./codex-observatory
chmod +x ./codex-observatory
./codex-observatory install-codex --patch-codex
codex stats
```

Linux ARM64:

```bash
curl -L https://github.com/NgoQuocViet2001/codex-observatory/releases/latest/download/codex-observatory-linux-arm64 -o ./codex-observatory
chmod +x ./codex-observatory
./codex-observatory install-codex --patch-codex
codex stats
```

## Common Cases

| Case | Command |
| --- | --- |
| First-time setup | `codex-observatory install-codex --patch-codex` |
| Open the default dashboard | `codex stats` |
| Open a short dashboard | `codex stats compact` |
| Open the full dashboard | `codex stats full` |
| Emit JSON | `codex stats --json` |

## Commands

| Command | Description |
| --- | --- |
| `codex-observatory install-codex --patch-codex` | Install helper assets and enable `codex stats` |
| `codex stats` | Recommended dashboard command after patch |
| `codex stats compact` | Short dashboard |
| `codex stats full` | Detailed dashboard |
| `codex stats --json` | JSON output |
| `codex-observatory uninstall-codex` | Remove helper assets and restore patched `codex` launcher from backups |
| `npx github:NgoQuocViet2001/codex-observatory compact` | One-shot run without global install |

## Flags

| Flag | Description |
| --- | --- |
| `compact` | Smaller dashboard |
| `full` | Expanded dashboard |
| `--no-color` | Disable ANSI colors |
| `--json` | Emit JSON |
| `--daily-days N` | Daily table window |
| `--monthly-months N` | Monthly table window |
| `--heatmap-weeks N` | Heatmap width |
| `--top-models N` | Limit model rows |
| `--width N` | Override terminal width |
| `--codex-home PATH` | Read logs from another Codex home |

## Direct Aliases

If you do not want to patch Codex, or you just prefer direct commands, these still work and accept the same view and flag arguments:

- `codex-observatory`
- `codex-stats`

Examples:

```bash
codex-observatory compact
codex-stats --json
```

They are equivalent direct entrypoints to the same dashboard. The docs recommend `codex stats` so the experience feels like a built-in Codex extension.

## Uninstall

First remove the Codex integration:

```bash
codex-observatory uninstall-codex
```

Then remove the package or binary you installed:

- `npm`: `npm uninstall -g codex-observatory`
- `pipx`: `pipx uninstall codex-observatory`
- `pip`: `python -m pip uninstall codex-observatory`
- local repo clone on Windows: `.\scripts\uninstall-codex.ps1`
- local repo clone on macOS/Linux: `./scripts/uninstall-codex.sh`
- local binary on macOS/Linux: `rm ./codex-observatory`
- local binary on Windows: `Remove-Item "$HOME\\codex-observatory.exe"`

## Notes

- `codex stats` requires Codex to already be installed on the machine.
- `codex stats` only exists after `install-codex --patch-codex`.
- `codex-observatory` and `codex-stats` work without patching.
- `npm` installs download the matching native binary on first run.
- If `history.jsonl` is missing, `codex-observatory` rebuilds prompt history from session logs instead of failing.
- If `sessions/` is missing but `history.jsonl` exists, `codex-observatory` still renders prompt/session counts and falls back to zero token totals plus `unknown` model metadata.

## Docs

- [Install Guide](./docs/INSTALL.md)
- [Usage Guide](./docs/USAGE.md)
- [Codex Integration](./docs/CODEX_INTEGRATION.md)
- [Changelog](./CHANGELOG.md)
