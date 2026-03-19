# Usage Guide

This repo exists because Codex does not expose a native stats command yet. `codex-observatory` gives you that missing view from local logs.

## Command map

Use this table if you are not sure which command should work on your machine:

| Situation | Command |
| --- | --- |
| You installed the app and just want the dashboard | `codex-observatory` |
| You installed with `npm` or `pip` and want the short alias | `codex-stats` |
| You want a real Codex subcommand | `codex-observatory install-codex --patch-codex` then `codex stats` |

Important:

- `codex-observatory` is the primary standalone command
- `codex-stats` is an alias from `npm` and `pip` installs
- `codex stats` only exists after the optional patch step

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

`codex-stats` is available when you installed via `npm` or `pip`.

If you are using a downloaded standalone binary, the binary name stays `codex-observatory` unless you create your own shell alias.

## Optional native-feeling Codex command

After running the integration installer with patch mode:

```bash
codex-observatory install-codex --patch-codex
codex stats
codex stats compact
codex stats full --daily-days 14
```

If you installed from a release binary:

```bash
./codex-observatory install-codex --patch-codex
codex stats
```

If you installed from a local clone:

```powershell
.\scripts\install-codex.ps1 -PatchCodex
codex stats
```

```bash
./scripts/install-codex.sh --patch-codex
codex stats
```
