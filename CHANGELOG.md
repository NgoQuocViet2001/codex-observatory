# Changelog

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
