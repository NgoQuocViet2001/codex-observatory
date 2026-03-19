# Codex Observatory

Local stats dashboard for Codex. Read usage directly from machine logs and inspect prompts, tokens, sessions, streaks, model mix, and trends.

[![CI](https://github.com/NgoQuocViet2001/codex-observatory/actions/workflows/ci.yml/badge.svg)](https://github.com/NgoQuocViet2001/codex-observatory/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/NgoQuocViet2001/codex-observatory)](https://github.com/NgoQuocViet2001/codex-observatory/releases)
[![Node](https://img.shields.io/badge/node-18%2B-5FA04E)](https://nodejs.org/)
[![Python](https://img.shields.io/badge/python-3.10%2B-3776AB)](https://www.python.org/)

## Why

Codex writes rich local logs, but it does not ship a built-in `codex stats` command.

Codex Observatory fills that gap with a local-first dashboard built from:

- `~/.codex/history.jsonl`
- `~/.codex/sessions/**/*.jsonl`

This is especially useful when:

- one Codex account is shared by multiple people
- one machine uses multiple Codex accounts
- you want machine-level usage, not account-level usage

## Quick Answer

There are 3 command styles:

| Command | What it is |
| --- | --- |
| `codex-observatory` | Main standalone CLI |
| `codex-stats` | Short alias from `npm` and `pip` installs |
| `codex stats` | Optional native-feeling Codex subcommand after patching |

Yes, this flow works:

```bash
npm install -g github:NgoQuocViet2001/codex-observatory
codex-stats
codex-observatory install-codex --patch-codex
codex stats
```

`codex stats` only exists after the patch step.

One-shot without global install:

```bash
npx github:NgoQuocViet2001/codex-observatory compact
```

## Quickstart

### Windows

If you already have Node.js:

```powershell
npm install -g github:NgoQuocViet2001/codex-observatory
codex-stats
codex-observatory install-codex --patch-codex
codex stats
```

No Node, use the binary:

```powershell
Invoke-WebRequest "https://github.com/NgoQuocViet2001/codex-observatory/releases/latest/download/codex-observatory-windows-x64.exe" -OutFile "$HOME\\codex-observatory.exe"
& "$HOME\\codex-observatory.exe"
& "$HOME\\codex-observatory.exe" install-codex --patch-codex
codex stats
```

### macOS

If you already have Node.js:

```bash
npm install -g github:NgoQuocViet2001/codex-observatory
codex-stats
codex-observatory install-codex --patch-codex
codex stats
```

No Node, use the binary:

Apple Silicon:

```bash
curl -L https://github.com/NgoQuocViet2001/codex-observatory/releases/latest/download/codex-observatory-macos-arm64 -o ./codex-observatory
chmod +x ./codex-observatory
./codex-observatory
./codex-observatory install-codex --patch-codex
codex stats
```

Intel:

```bash
curl -L https://github.com/NgoQuocViet2001/codex-observatory/releases/latest/download/codex-observatory-macos-x64 -o ./codex-observatory
chmod +x ./codex-observatory
./codex-observatory
./codex-observatory install-codex --patch-codex
codex stats
```

### Ubuntu / Linux

If you already have Node.js:

```bash
npm install -g github:NgoQuocViet2001/codex-observatory
codex-stats
codex-observatory install-codex --patch-codex
codex stats
```

No Node, use the binary:

```bash
curl -L https://github.com/NgoQuocViet2001/codex-observatory/releases/latest/download/codex-observatory-linux-x64 -o ./codex-observatory
chmod +x ./codex-observatory
./codex-observatory
./codex-observatory install-codex --patch-codex
codex stats
```

## Common Cases

| Case | Command |
| --- | --- |
| Open the default dashboard | `codex-observatory` |
| Open a short dashboard | `codex-stats compact` |
| Add a native Codex command | `codex-observatory install-codex --patch-codex` |

## Commands

| Command | Description |
| --- | --- |
| `codex-observatory` | Default dashboard |
| `codex-observatory compact` | Short view |
| `codex-observatory full` | Detailed view |
| `codex-stats` | Alias to the same dashboard |
| `codex stats` | Codex-native style command after patch |
| `npx github:NgoQuocViet2001/codex-observatory compact` | One-shot run without global install |
| `codex-observatory --json` | JSON output for scripts |
| `codex-observatory install-codex --patch-codex` | Install Codex helper assets and patch `codex` launcher |

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

## Notes

- `codex stats` requires Codex to already be installed on the machine.
- `codex-observatory` works without patching.
- `codex-stats` is available for `npm` and `pip` installs.

## Docs

- [Install Guide](./docs/INSTALL.md)
- [Usage Guide](./docs/USAGE.md)
- [Codex Integration](./docs/CODEX_INTEGRATION.md)
- [Changelog](./CHANGELOG.md)
