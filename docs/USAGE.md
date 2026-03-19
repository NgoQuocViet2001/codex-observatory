# Usage Guide

This repo exists because Codex does not expose a native stats command yet. `codex-observatory` gives you that missing view from local logs.

## Default dashboard

```bash
codex-observatory
```

Fallback if the script directory is not on `PATH`:

```bash
python -m codex_observatory
```

## View modes

```bash
codex-observatory compact
codex-observatory full
```

## Useful flags

```bash
codex-observatory --no-color
codex-observatory --heatmap-weeks 24
codex-observatory --daily-days 14
codex-observatory --monthly-months 12
codex-observatory --top-models 8
codex-observatory --json
codex-observatory --width 140
codex-observatory --codex-home ~/.codex
codex-observatory --now 2026-03-19T10:00:00
```

## Alias command

```bash
codex-stats
```

## Optional native-feeling Codex command

After running the integration installer with patch mode:

```bash
codex-observatory install-codex --patch-codex
codex stats
codex stats compact
codex stats full --daily-days 14
```
