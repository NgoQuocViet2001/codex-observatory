# Changelog

## 1.2.10 - 2026-03-19

- Repaired upgrades from older macOS and Unix installs that had patched the resolved `codex.js` target instead of the launcher symlink.
- Added automatic recovery for legacy `codex.js.orig` backups during install and uninstall so broken Homebrew-style launchers can heal on the next update.
- Added Unix regression tests that cover legacy launcher recovery paths in addition to the wrapper-based patch flow.

## 1.2.9 - 2026-03-19

- Fixed macOS and Unix Codex launcher patching when `codex` resolves to a symlink into `codex.js` instead of a shell shim.
- Switched Unix launcher integration to a wrapper-based patch so `codex stats` no longer injects shell code into the upstream JavaScript entrypoint.
- Added a regression test that covers symlink-based Unix launchers and restore-on-uninstall behavior.

## 1.2.8 - 2026-03-19

- Added npm-first setup so global npm installs can automatically wire `codex stats` into the local Codex launcher.
- Simplified the user-facing docs to one main flow: `npm install -g codex-observatory` and then `codex stats`.
- Added npm publish support in the release workflow and documented the clean two-step uninstall flow required by modern npm.

## 1.2.7 - 2026-03-19

- Simplified the docs around one recommended user-facing flow: install, patch, then use `codex stats`.
- Added `uninstall-codex` so users can remove Codex Observatory integration files and restore patched Codex launchers from backups with one command.
- Added uninstall guidance for npm, pip, pipx, and standalone binary installs, while keeping `codex-observatory` and `codex-stats` documented as direct aliases.

## 1.2.6 - 2026-03-19

- Added a true `history.jsonl` fallback for older Codex installs that do not have a `sessions/` directory, so the dashboard still opens with prompt/session counts instead of failing.
- Added native npm/release support for `linux-arm64` and `windows-arm64`, plus ARM smoke coverage in CI.
- Updated install and usage docs to call out both history-only Codex homes and the new ARM64 binary assets.

## 1.2.5 - 2026-03-19

- Fixed the missing `history.jsonl` crash on newer Codex installs by reconstructing prompt history from `sessions/**/*.jsonl` when needed.
- Taught the npm wrapper to backfill a synthetic `~/.codex/history.jsonl` for current native releases and to refresh `codex stats` helper scripts so npm installs keep going through the compatibility wrapper.
- Updated tests and install docs for Codex homes that only contain session logs.

## 1.2.4 - 2026-03-19

- Synced the Python package version with the npm/native release version so wheel, sdist, npm, and binary assets all publish the same release number.
- Kept the `v1.2.3` fixes: Windows GitHub-based npm installs no longer depend on `postinstall`, and the Windows native binary entrypoint now starts correctly.

## 1.2.3 - 2026-03-19

- Fixed `npm install -g github:NgoQuocViet2001/codex-observatory` on Windows by removing the npm `postinstall` dependency and downloading the native binary on first run instead.
- Fixed the Windows native binary entrypoint so `codex-observatory.exe` and the npm-downloaded Windows binary start correctly.
- Kept the quickstart docs short and command-first for Windows, macOS, and Ubuntu.

## 1.2.2 - 2026-03-19

- Switched the macOS release build to the current GitHub Actions macOS runner labels so the native release matrix does not get canceled mid-run.
- Kept the `v1.2.1` fixes: green CI across Windows, macOS, and Ubuntu plus clear no-Python install paths.

## 1.2.1 - 2026-03-19

- Fixed the cross-platform Codex integration test so CI passes on macOS and Ubuntu as well as Windows.
- Kept the Python-free install paths documented for Windows, macOS, and Ubuntu with npm, npx, and standalone binaries.

## 1.2.0 - 2026-03-19

- Fixed the Unix integration path bug that broke CI on macOS and Ubuntu when no launcher path was passed explicitly.
- Added a standalone `install-codex` command so Python installs, native binaries, and npm installs can all wire `codex stats` into Codex the same way.
- Added npm/npx distribution support and prepared release assets for platform-specific standalone binaries.
- Rewrote install guidance to be clearer for Windows, macOS, and Ubuntu users.

## 1.1.0 - 2026-03-19

- Added an optional Codex launcher patch so `codex stats` and `codex stat` work directly.
- Added packaged helper tools under `~/.codex/tools` for both PowerShell and Bash-based Codex launchers.
- Added backup-aware launcher patching so existing Codex shims are preserved before modification.
- Updated the install and integration guides to explain that this repo exists because Codex does not currently ship built-in stats.

## 1.0.0 - 2026-03-19

- First public release of `codex-observatory`.
- Added live local analytics for Codex prompts, sessions, tokens, cache share, streaks, and model usage.
- Added compact, normal, and full terminal dashboards with ANSI color, bordered tables, heatmap, sparkline, and load bars.
- Added JSON export for automation and downstream scripting.
- Added cross-platform install scripts for Windows, macOS, and Linux.
- Added Codex skill bootstrap script to let Codex call the local stats command directly.
- Added CI and tag-based release workflows for GitHub Actions.
