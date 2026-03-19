# Install Guide

## What you get

| Command | Available after |
| --- | --- |
| `codex stats` | run `install-codex --patch-codex` |
| `codex-observatory` | binary, `npm`, `pip`, `pipx` |
| `codex-stats` | `npm`, `pip`, `pipx` |

## Windows

### Node.js path

```powershell
npm install -g github:NgoQuocViet2001/codex-observatory
codex-observatory install-codex --patch-codex
codex stats
```

One-shot:

```powershell
npx github:NgoQuocViet2001/codex-observatory compact
```

### Binary path

```powershell
Invoke-WebRequest "https://github.com/NgoQuocViet2001/codex-observatory/releases/latest/download/codex-observatory-windows-x64.exe" -OutFile "$HOME\\codex-observatory.exe"
& "$HOME\\codex-observatory.exe" install-codex --patch-codex
codex stats
```

Windows ARM64:

```powershell
Invoke-WebRequest "https://github.com/NgoQuocViet2001/codex-observatory/releases/latest/download/codex-observatory-windows-arm64.exe" -OutFile "$HOME\\codex-observatory.exe"
& "$HOME\\codex-observatory.exe" install-codex --patch-codex
codex stats
```

## macOS

### Node.js path

```bash
npm install -g github:NgoQuocViet2001/codex-observatory
codex-observatory install-codex --patch-codex
codex stats
```

One-shot:

```bash
npx github:NgoQuocViet2001/codex-observatory compact
```

### Binary path

Apple Silicon:

```bash
curl -L https://github.com/NgoQuocViet2001/codex-observatory/releases/latest/download/codex-observatory-macos-arm64 -o ./codex-observatory
chmod +x ./codex-observatory
./codex-observatory install-codex --patch-codex
codex stats
```

Intel:

```bash
curl -L https://github.com/NgoQuocViet2001/codex-observatory/releases/latest/download/codex-observatory-macos-x64 -o ./codex-observatory
chmod +x ./codex-observatory
./codex-observatory install-codex --patch-codex
codex stats
```

## Ubuntu / Linux

### Node.js path

```bash
npm install -g github:NgoQuocViet2001/codex-observatory
codex-observatory install-codex --patch-codex
codex stats
```

One-shot:

```bash
npx github:NgoQuocViet2001/codex-observatory compact
```

### Binary path

```bash
curl -L https://github.com/NgoQuocViet2001/codex-observatory/releases/latest/download/codex-observatory-linux-x64 -o ./codex-observatory
chmod +x ./codex-observatory
./codex-observatory install-codex --patch-codex
codex stats
```

Linux ARM64:

```bash
curl -L https://github.com/NgoQuocViet2001/codex-observatory/releases/latest/download/codex-observatory-linux-arm64 -o ./codex-observatory
chmod +x ./codex-observatory
./codex-observatory install-codex --patch-codex
codex stats
```

## Python / pipx

```bash
pipx install git+https://github.com/NgoQuocViet2001/codex-observatory.git
codex-observatory install-codex --patch-codex
codex stats
```

## Local repo clone

Use this only if you cloned the repository:

```powershell
.\scripts\install-codex.ps1 -PatchCodex
codex stats
```

```bash
./scripts/install-codex.sh --patch-codex
codex stats
```

## Notes

- `codex stats` is the recommended command after setup.
- `codex stats` requires Codex to already exist on the machine.
- `codex-observatory` works even without patching Codex.
- `npm` installs download the native binary on first run.
- Newer Codex installs may not have `~/.codex/history.jsonl`; `codex-observatory` now reconstructs prompt history from `sessions/**/*.jsonl` automatically.
- Older Codex installs that only have `~/.codex/history.jsonl` still work; prompt/session counts come from history and token/model fields fall back to zero or `unknown` when session logs do not exist.

## Uninstall

Remove the Codex integration first:

```bash
codex-observatory uninstall-codex
```

Then remove the installer you used:

- `npm`: `npm uninstall -g codex-observatory`
- `pipx`: `pipx uninstall codex-observatory`
- `pip`: `python -m pip uninstall codex-observatory`
- Windows binary: `Remove-Item "$HOME\\codex-observatory.exe"`
- macOS/Linux binary: `rm ./codex-observatory`
- local repo clone on Windows: `.\scripts\uninstall-codex.ps1`
- local repo clone on macOS/Linux: `./scripts/uninstall-codex.sh`
