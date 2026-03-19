# Install Guide

`codex-observatory` exists because Codex does not ship a built-in stats/dashboard command today. Pick the install path that matches what you already have on your machine.

## Windows

### Easiest: one binary, no Python

```powershell
Invoke-WebRequest "https://github.com/NgoQuocViet2001/codex-observatory/releases/download/v1.2.0/codex-observatory-windows-x64.exe" -OutFile "$HOME\\codex-observatory.exe"
& "$HOME\\codex-observatory.exe"
```

### If you already have Node.js

```powershell
npm install -g github:NgoQuocViet2001/codex-observatory#v1.2.0
codex-observatory
```

One-shot without global install:

```powershell
npx github:NgoQuocViet2001/codex-observatory#v1.2.0 compact
```

### If you already have Python

```powershell
python -m pip install git+https://github.com/NgoQuocViet2001/codex-observatory.git
codex-observatory
```

## macOS

### Easiest: one binary, no Python

Apple Silicon:

```bash
curl -L https://github.com/NgoQuocViet2001/codex-observatory/releases/download/v1.2.0/codex-observatory-macos-arm64 -o ./codex-observatory
chmod +x ./codex-observatory
./codex-observatory
```

Intel:

```bash
curl -L https://github.com/NgoQuocViet2001/codex-observatory/releases/download/v1.2.0/codex-observatory-macos-x64 -o ./codex-observatory
chmod +x ./codex-observatory
./codex-observatory
```

If macOS blocks the binary the first time:

```bash
xattr -d com.apple.quarantine ./codex-observatory
```

### If you already have Node.js

```bash
npm install -g github:NgoQuocViet2001/codex-observatory#v1.2.0
codex-observatory
```

One-shot without global install:

```bash
npx github:NgoQuocViet2001/codex-observatory#v1.2.0 full
```

### If you already have Python

```bash
python3 -m pip install git+https://github.com/NgoQuocViet2001/codex-observatory.git
codex-observatory
```

## Ubuntu / Linux

### Easiest: one binary, no Python

```bash
curl -L https://github.com/NgoQuocViet2001/codex-observatory/releases/download/v1.2.0/codex-observatory-linux-x64 -o ./codex-observatory
chmod +x ./codex-observatory
./codex-observatory
```

### If you already have Node.js

```bash
npm install -g github:NgoQuocViet2001/codex-observatory#v1.2.0
codex-observatory
```

One-shot without global install:

```bash
npx github:NgoQuocViet2001/codex-observatory#v1.2.0 compact
```

### If you already have Python

```bash
python3 -m pip install git+https://github.com/NgoQuocViet2001/codex-observatory.git
codex-observatory
```

## Make `codex stats` work directly

After any install method above, run:

```bash
codex-observatory install-codex --patch-codex
codex stats
```

If you are using a downloaded standalone binary that is not on `PATH`, replace `codex-observatory` with that binary path:

```powershell
& "$HOME\codex-observatory.exe" install-codex --patch-codex
```

```bash
./codex-observatory install-codex --patch-codex
```
