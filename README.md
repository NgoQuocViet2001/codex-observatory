# Codex Observatory

Local stats dashboard for Codex. Read usage directly from machine logs, estimate API spend from model pricing, and use `codex stats` like it was built into Codex.

[![CI](https://github.com/NgoQuocViet2001/codex-observatory/actions/workflows/ci.yml/badge.svg)](https://github.com/NgoQuocViet2001/codex-observatory/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/NgoQuocViet2001/codex-observatory)](https://github.com/NgoQuocViet2001/codex-observatory/releases)
[![Node](https://img.shields.io/badge/node-18%2B-5FA04E)](https://nodejs.org/)

## Quickstart

Works on:

- Windows x64 and arm64
- macOS Intel and Apple Silicon
- Linux x64 and arm64

Requirements:

- Node.js 18+
- Codex already installed on the machine

Install once:

```bash
npm install -g codex-observatory
```

Then use it like this:

```bash
codex stats
codex stats compact
codex stats full
codex stats --json
```

Global npm install auto-runs the Codex integration step and patches the local `codex` launcher so `codex stats` works immediately.

If your npm install was run with scripts disabled, or Codex was not installed yet, repair the setup with:

```bash
codex-observatory install-codex --patch-codex
```

## Commands

| Command | Description |
| --- | --- |
| `codex stats` | Recommended dashboard command |
| `codex stats compact` | Short dashboard |
| `codex stats full` | Detailed dashboard |
| `codex stats --json` | JSON output including cost and pricing metadata |
| `codex-observatory install-codex --patch-codex` | Reinstall or repair the Codex launcher patch |
| `codex-observatory uninstall-codex` | Remove the Codex integration and restore launcher backups |

## Direct Aliases

These direct commands are still available and map to the same dashboard:

- `codex-observatory`
- `codex-stats`

Examples:

```bash
codex-observatory compact
codex-stats --json
```

## Clean Uninstall

```bash
codex-observatory uninstall-codex
npm uninstall -g codex-observatory
```

The first command removes the Codex integration and restores the patched `codex` launcher. The second command removes the global npm package.

## Notes

- `npm install -g codex-observatory` is the main supported user flow.
- `npm uninstall -g codex-observatory` removes the npm package itself, but npm does not run uninstall lifecycle hooks for packages. Run `codex-observatory uninstall-codex` first for a clean rollback.
- `npm` installs download the matching native binary automatically.
- If `history.jsonl` is missing, Codex Observatory rebuilds prompt history from session logs.
- If `sessions/` is missing but `history.jsonl` exists, Codex Observatory still renders prompt and session counts and falls back to zero token totals plus `unknown` model metadata.
- Estimated spend uses built-in OpenAI API pricing by model, billing uncached input, cached input, and output separately.
- Pricing coverage is reported explicitly so unknown or unsupported models do not silently skew totals.

## Docs

- [Install Guide](./docs/INSTALL.md)
- [Usage Guide](./docs/USAGE.md)
- [Codex Integration](./docs/CODEX_INTEGRATION.md)
- [Changelog](./CHANGELOG.md)
