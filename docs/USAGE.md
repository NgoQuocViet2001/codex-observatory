# Usage Guide

## Common cases

### 1. Check your local Codex usage

```bash
codex stats
```

This works on both Codex layouts:

- older installs with `~/.codex/history.jsonl`, with or without `~/.codex/sessions/`
- newer installs that only keep `~/.codex/sessions/**/*.jsonl`

### 2. Open a shorter dashboard

```bash
codex stats compact
```

### 3. Use a native-feeling Codex command

```bash
codex-observatory install-codex --patch-codex
codex stats
```

## Commands

| Command | Description |
| --- | --- |
| `codex stats` | Recommended dashboard command |
| `codex stats compact` | Compact dashboard |
| `codex stats full` | Full dashboard |
| `codex stats --json` | JSON export |
| `codex-observatory` | Direct alias to the same dashboard |
| `codex-stats` | Direct alias to the same dashboard |
| `npx github:NgoQuocViet2001/codex-observatory compact` | One-shot run |
| `codex-observatory uninstall-codex` | Remove integration and restore patched launcher backups |

## Flags

| Flag | Description |
| --- | --- |
| `--no-color` | Disable ANSI color |
| `--json` | Output JSON instead of terminal UI |
| `--daily-days N` | Show N daily rows |
| `--monthly-months N` | Show N monthly rows |
| `--heatmap-weeks N` | Show N heatmap weeks |
| `--top-models N` | Show top N models |
| `--width N` | Force render width |
| `--codex-home PATH` | Read another Codex home |

## Examples

```bash
codex stats full --daily-days 14 --monthly-months 12
codex stats compact --no-color
codex stats full --top-models 8
codex stats --json
```

## Direct aliases

If you skip patching Codex, or just prefer direct commands, these are equivalent:

```bash
codex-observatory compact
codex-stats --json
```
