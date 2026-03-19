# Usage Guide

## Main Commands

```bash
codex stats
codex stats compact
codex stats full
codex stats --json
```

## Common Flags

| Flag | Description |
| --- | --- |
| `compact` | Smaller dashboard |
| `full` | Expanded dashboard |
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
codex stats
codex stats compact --no-color
codex stats full --daily-days 14 --monthly-months 12
codex stats full --top-models 8
codex stats --json
```

## Direct Aliases

If you prefer direct commands instead of the patched `codex` subcommand, these are equivalent:

```bash
codex-observatory compact
codex-stats --json
```

## Data Sources

Codex Observatory works with both Codex log layouts:

- older installs with `~/.codex/history.jsonl`
- newer installs with `~/.codex/sessions/**/*.jsonl`
- mixed homes where one of those sources is missing
