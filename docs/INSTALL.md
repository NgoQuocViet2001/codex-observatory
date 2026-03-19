# Install Guide

## Supported Platforms

- Windows x64 and arm64
- macOS Intel and Apple Silicon
- Linux x64 and arm64

## Requirements

- Node.js 18+
- Codex already installed on the machine

## Install

The same install flow works across Windows, macOS, and Linux:

```bash
npm install -g codex-observatory
```

After install, the package auto-patches the local `codex` launcher so these commands should work immediately:

```bash
codex stats
codex stats compact
codex stats full
codex stats --json
```

## Repair

If the npm install ran with scripts disabled, or if Codex was installed after Codex Observatory, repair the integration with:

```bash
codex-observatory install-codex --patch-codex
```

## Direct Aliases

These are still valid direct entrypoints:

```bash
codex-observatory
codex-stats
```

## Clean Uninstall

First remove the Codex integration:

```bash
codex-observatory uninstall-codex
```

Then remove the npm package:

```bash
npm uninstall -g codex-observatory
```

## Why Two Uninstall Steps

`npm uninstall -g codex-observatory` removes the npm package itself, but npm does not run uninstall lifecycle hooks for packages anymore. Because `codex stats` works by patching the local `codex` launcher, the clean rollback step has to happen before the npm package is removed.
