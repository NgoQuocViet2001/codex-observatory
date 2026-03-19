# Install Guide

`codex-observatory` exists because Codex does not currently ship a built-in stats/dashboard command. The package gives you a local dashboard now, and the optional shim patch lets that experience live behind `codex stats`.

## Requirements

- Python 3.10 or newer
- Access to your local Codex logs
- A terminal that supports UTF-8 for the best dashboard output

## Windows

```powershell
git clone git@git-personal:NgoQuocViet2001/codex-observatory.git
cd D:\Personal\Projects\codex-observatory
python -m pip install -e .
codex-observatory
codex-observatory compact
codex-observatory full --daily-days 14
python -m codex_observatory --no-color
```

Optional built-in style integration:

```powershell
.\scripts\install-codex.ps1 -PatchCodex
codex stats
codex stats full
```

## macOS / Linux

```bash
git clone git@git-personal:NgoQuocViet2001/codex-observatory.git
cd codex-observatory
python3 -m pip install -e .
codex-observatory
codex-observatory compact
codex-observatory full --daily-days 14
python3 -m codex_observatory --no-color
```

Optional built-in style integration:

```bash
./scripts/install-codex.sh --patch-codex
codex stats
codex stats full
```

## Install with pipx

```bash
pipx install git+https://github.com/NgoQuocViet2001/codex-observatory.git
codex-observatory
```
