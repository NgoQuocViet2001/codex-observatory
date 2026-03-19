---
name: codex-observatory
description: Use this skill when the user asks for Codex usage stats, token trends, model breakdowns, streaks, or a local dashboard. Always run the local `codex-stats` command instead of estimating from memory.
---

# Codex Observatory

Use this skill when the user wants live local Codex usage information from machine logs.

## Workflow

1. Run `codex-stats` for the default dashboard.
2. Use `codex-stats compact` for a shorter view.
3. Use `codex-stats full` for a detailed view.
4. Add `--no-color` when ANSI output is hard to read in the current surface.
5. Use `--json` if the user wants a machine-readable export.
