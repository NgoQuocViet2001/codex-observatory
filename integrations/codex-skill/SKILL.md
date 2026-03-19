---
name: codex-observatory
description: Use this skill when the user asks for Codex usage stats, token trends, model breakdowns, streaks, or a local dashboard. Run `codex stats` when the launcher patch is installed, otherwise use `codex-stats`.
---

# Codex Observatory

Use this skill when the user wants live local Codex usage information from machine logs.

## Workflow

1. Prefer `codex stats` for the default dashboard when the launcher patch is installed.
2. Otherwise run `codex-stats`.
3. Use `compact` for a shorter view.
4. Use `full` for a detailed view.
5. Add `--no-color` when ANSI output is hard to read in the current surface.
6. Use `--json` if the user wants a machine-readable export.
