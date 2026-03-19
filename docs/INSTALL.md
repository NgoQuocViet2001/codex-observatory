# Install Guide

`codex-observatory` exists because Codex does not ship a built-in stats/dashboard command today. Pick the install path that matches what you already have on your machine.

## Short answer

If you stop after installing the app itself, you get a standalone dashboard:

```bash
codex-observatory
```

If you install through `npm` or `pip`, you also get:

```bash
codex-stats
```

If you specifically want this:

```bash
codex stats
```

you must run one extra step after install:

```bash
codex-observatory install-codex --patch-codex
```

The repo scripts:

```bash
./scripts/install-codex.sh
./scripts/install-codex.sh --patch-codex
```

and:

```powershell
.\scripts\install-codex.ps1
.\scripts\install-codex.ps1 -PatchCodex
```

are mainly for people who cloned this repository locally.

## Command matrix

| Install method | Works immediately | Gives `codex-stats` | Gives `codex stats` |
| --- | --- | --- | --- |
| Standalone binary | `codex-observatory` | No | No |
| `npm install -g ...` | `codex-observatory` | Yes | No |
| `pip install ...` / `pipx install ...` | `codex-observatory` | Yes | No |
| Any of the above, then `install-codex --patch-codex` | `codex-observatory` | Depends on install method | Yes |

## Windows

### Easiest: one binary, no Python

```powershell
Invoke-WebRequest "https://github.com/NgoQuocViet2001/codex-observatory/releases/download/v1.2.2/codex-observatory-windows-x64.exe" -OutFile "$HOME\\codex-observatory.exe"
& "$HOME\\codex-observatory.exe"
```

To make `codex stats` work:

```powershell
& "$HOME\\codex-observatory.exe" install-codex --patch-codex
codex stats
```

### If you already have Node.js

```powershell
npm install -g github:NgoQuocViet2001/codex-observatory#v1.2.2
codex-observatory
codex-stats
```

To make `codex stats` work:

```powershell
codex-observatory install-codex --patch-codex
codex stats
```

One-shot without global install:

```powershell
npx github:NgoQuocViet2001/codex-observatory#v1.2.2 compact
```

### If you already have Python

```powershell
python -m pip install git+https://github.com/NgoQuocViet2001/codex-observatory.git
codex-observatory
codex-stats
codex-observatory install-codex --patch-codex
codex stats
```

## macOS

### Easiest: one binary, no Python

Apple Silicon:

```bash
curl -L https://github.com/NgoQuocViet2001/codex-observatory/releases/download/v1.2.2/codex-observatory-macos-arm64 -o ./codex-observatory
chmod +x ./codex-observatory
./codex-observatory
```

Intel:

```bash
curl -L https://github.com/NgoQuocViet2001/codex-observatory/releases/download/v1.2.2/codex-observatory-macos-x64 -o ./codex-observatory
chmod +x ./codex-observatory
./codex-observatory
```

If macOS blocks the binary the first time:

```bash
xattr -d com.apple.quarantine ./codex-observatory
```

To make `codex stats` work:

```bash
./codex-observatory install-codex --patch-codex
codex stats
```

### If you already have Node.js

```bash
npm install -g github:NgoQuocViet2001/codex-observatory#v1.2.2
codex-observatory
codex-stats
```

To make `codex stats` work:

```bash
codex-observatory install-codex --patch-codex
codex stats
```

One-shot without global install:

```bash
npx github:NgoQuocViet2001/codex-observatory#v1.2.2 full
```

### If you already have Python

```bash
python3 -m pip install git+https://github.com/NgoQuocViet2001/codex-observatory.git
codex-observatory
codex-stats
codex-observatory install-codex --patch-codex
codex stats
```

## Ubuntu / Linux

### Easiest: one binary, no Python

```bash
curl -L https://github.com/NgoQuocViet2001/codex-observatory/releases/download/v1.2.2/codex-observatory-linux-x64 -o ./codex-observatory
chmod +x ./codex-observatory
./codex-observatory
```

To make `codex stats` work:

```bash
./codex-observatory install-codex --patch-codex
codex stats
```

### If you already have Node.js

```bash
npm install -g github:NgoQuocViet2001/codex-observatory#v1.2.2
codex-observatory
codex-stats
```

To make `codex stats` work:

```bash
codex-observatory install-codex --patch-codex
codex stats
```

One-shot without global install:

```bash
npx github:NgoQuocViet2001/codex-observatory#v1.2.2 compact
```

### If you already have Python

```bash
python3 -m pip install git+https://github.com/NgoQuocViet2001/codex-observatory.git
codex-observatory
codex-stats
codex-observatory install-codex --patch-codex
codex stats
```

## Make `codex stats` work directly

If you installed from a binary, `npm`, or `pip`, run:

```bash
codex-observatory install-codex --patch-codex
codex stats
```

If you cloned this repo locally and want a one-step script:

```powershell
.\scripts\install-codex.ps1 -PatchCodex
```

```bash
./scripts/install-codex.sh --patch-codex
```

If you are using a downloaded standalone binary that is not on `PATH`, replace `codex-observatory` with that binary path:

```powershell
& "$HOME\codex-observatory.exe" install-codex --patch-codex
```

```bash
./codex-observatory install-codex --patch-codex
```
