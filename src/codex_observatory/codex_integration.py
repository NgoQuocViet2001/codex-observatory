from __future__ import annotations

import argparse
import os
import shutil
import stat
import sys
from pathlib import Path


PS_MARKER = "# >>> codex-observatory stats hook >>>"
CMD_MARKER = "REM >>> codex-observatory stats dispatch >>>"
SH_MARKER = "# >>> codex-observatory stats hook >>>"

PS_HOOK = """# >>> codex-observatory stats hook >>>
if ($args.Length -gt 0 -and ($args[0] -eq 'stats' -or $args[0] -eq 'stat')) {
  $codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME '.codex' }
  $statsScript = Join-Path $codexHome 'tools\\codex-stats.ps1'
  if (-not (Test-Path $statsScript)) {
    Write-Error "Missing stats script: $statsScript"
    exit 1
  }
  $statsArgs = @()
  if ($args.Length -gt 1) {
    $statsArgs = $args[1..($args.Length - 1)]
  }
  & $statsScript @statsArgs
  exit $LASTEXITCODE
}
# <<< codex-observatory stats hook <<<
"""

CMD_DISPATCH = """REM >>> codex-observatory stats dispatch >>>
IF /I "%~1"=="stats" GOTO codex_observatory_stats
IF /I "%~1"=="stat" GOTO codex_observatory_stats
REM <<< codex-observatory stats dispatch <<<
"""

CMD_TARGET = """REM >>> codex-observatory stats target >>>
:codex_observatory_stats
SHIFT
IF DEFINED CODEX_HOME (
  SET "STATS_ROOT=%CODEX_HOME%"
) ELSE (
  SET "STATS_ROOT=%USERPROFILE%\\.codex"
)
SET "STATS_SCRIPT=%STATS_ROOT%\\tools\\codex-stats.ps1"
IF NOT EXIST "%STATS_SCRIPT%" (
  ECHO Missing stats script: %STATS_SCRIPT%
  EXIT /b 1
)
WHERE pwsh >NUL 2>NUL
IF %ERRORLEVEL% EQU 0 (
  pwsh -NoProfile -File "%STATS_SCRIPT%" %*
) ELSE (
  powershell -NoProfile -ExecutionPolicy Bypass -File "%STATS_SCRIPT%" %*
)
EXIT /b %ERRORLEVEL%
REM <<< codex-observatory stats target <<<
"""

SH_HOOK = """# >>> codex-observatory stats hook >>>
if [ "${1-}" = "stats" ] || [ "${1-}" = "stat" ]; then
  shift
  codex_home="${CODEX_HOME:-$HOME/.codex}"
  stats_script="$codex_home/tools/codex-stats.sh"
  if [ ! -f "$stats_script" ]; then
    echo "Missing stats script: $stats_script" >&2
    exit 1
  fi
  exec "$stats_script" "$@"
fi
# <<< codex-observatory stats hook <<<
"""


def detect_newline(text: str) -> str:
    return "\r\n" if "\r\n" in text else "\n"


def write_text(path: Path, content: str, executable: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        handle.write(content)
    if executable:
        current_mode = path.stat().st_mode
        path.chmod(current_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def ensure_backup(path: Path, backup_dir: Path) -> None:
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_path = backup_dir / f"{path.name}.orig"
    if not backup_path.exists():
        shutil.copy2(path, backup_path)


def patch_powershell_shim(content: str) -> str:
    if PS_MARKER in content:
        return content
    newline = detect_newline(content)
    hook = PS_HOOK.replace("\n", newline)
    if content.startswith("#!"):
        first_break = content.find(newline)
        if first_break >= 0:
            return content[: first_break + len(newline)] + hook + newline + content[first_break + len(newline) :]
    return hook + newline + content


def patch_cmd_shim(content: str) -> str:
    if CMD_MARKER in content:
        return content
    newline = detect_newline(content)
    dispatch = CMD_DISPATCH.replace("\n", newline)
    target = CMD_TARGET.replace("\n", newline)

    needle = "CALL :find_dp0"
    index = content.find(needle)
    if index >= 0:
        insert_at = content.find(newline, index)
        if insert_at >= 0:
            insert_at += len(newline)
        else:
            insert_at = len(content)
        patched = content[:insert_at] + dispatch + newline + content[insert_at:]
    else:
        patched = dispatch + newline + content
    return patched.rstrip("\r\n") + newline + newline + target


def patch_shell_shim(content: str) -> str:
    if SH_MARKER in content:
        return content
    newline = detect_newline(content)
    hook = SH_HOOK.replace("\n", newline)
    needle = 'if [ -x "$basedir/node" ]; then'
    index = content.find(needle)
    if index >= 0:
        return content[:index] + hook + newline + content[index:]
    return content.rstrip("\r\n") + newline + newline + hook


def patch_file(path: Path, patcher, backup_dir: Path) -> bool:
    if not path.exists():
        return False
    original = path.read_text(encoding="utf-8", errors="ignore")
    updated = patcher(original)
    if updated == original:
        return False
    ensure_backup(path, backup_dir)
    write_text(path, updated, executable=bool(path.stat().st_mode & stat.S_IXUSR))
    return True


def render_stats_ps1(python_bin: str) -> str:
    return (
        "param(\n"
        "    [Parameter(ValueFromRemainingArguments = $true)]\n"
        "    [string[]]$CliArgs\n"
        ")\n\n"
        f'$python = "{python_bin}"\n'
        "& $python -m codex_observatory @CliArgs\n"
        "exit $LASTEXITCODE\n"
    )


def render_stats_sh(python_bin: str) -> str:
    normalized = python_bin.replace("\\", "/")
    return (
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        f'PYTHON_BIN="{normalized}"\n'
        'exec "$PYTHON_BIN" -m codex_observatory "$@"\n'
    )


def install_integration(repo_root: Path, codex_home: Path, python_bin: str, patch_codex: bool, shim_dir: Path | None, codex_bin: Path | None) -> list[str]:
    messages: list[str] = []
    skill_source = repo_root / "integrations" / "codex-skill" / "SKILL.md"
    skill_target = codex_home / "skills" / "codex-observatory" / "SKILL.md"
    write_text(skill_target, skill_source.read_text(encoding="utf-8"))
    messages.append(f"Installed Codex skill: {skill_target}")

    tool_dir = codex_home / "tools"
    ps1_tool = tool_dir / "codex-stats.ps1"
    sh_tool = tool_dir / "codex-stats.sh"
    write_text(ps1_tool, render_stats_ps1(python_bin))
    write_text(sh_tool, render_stats_sh(python_bin), executable=True)
    messages.append(f"Installed helper tools: {ps1_tool} and {sh_tool}")

    if not patch_codex:
        messages.append("Skipped Codex shim patch. Re-run with --patch-codex if you want `codex stats`.")
        return messages

    backup_dir = codex_home / "integrations" / "codex-observatory" / "backups"
    patched_any = False

    if os.name == "nt":
        shim_root = shim_dir or Path(os.environ.get("APPDATA", str(Path.home() / "AppData" / "Roaming"))) / "npm"
        targets = [
            (shim_root / "codex.ps1", patch_powershell_shim),
            (shim_root / "codex.cmd", patch_cmd_shim),
            (shim_root / "codex", patch_shell_shim),
        ]
    else:
        resolved_codex = codex_bin or Path(shutil.which("codex") or "")
        targets = [(resolved_codex, patch_shell_shim)] if str(resolved_codex) else []

    for path, patcher in targets:
        if path and patch_file(path, patcher, backup_dir):
            messages.append(f"Patched Codex shim: {path}")
            patched_any = True
        elif path and path.exists():
            messages.append(f"Codex shim already patched: {path}")

    if not patched_any and not any(path.exists() for path, _ in targets):
        raise FileNotFoundError("Could not find a Codex launcher to patch. Install Codex first, or pass an explicit shim path.")

    messages.append(f"Backups are stored in: {backup_dir}")
    return messages


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Install Codex Observatory skill, helper tools, and optional `codex stats` shim patch.")
    parser.add_argument("--repo-root", required=True, help="Path to the codex-observatory repository root.")
    parser.add_argument("--python-bin", default=sys.executable, help="Python interpreter to bind into the helper scripts.")
    parser.add_argument("--codex-home", default=os.environ.get("CODEX_HOME", "~/.codex"), help="Path to the .codex directory.")
    parser.add_argument("--patch-codex", action="store_true", help="Patch the local `codex` launcher so `codex stats` works directly.")
    parser.add_argument("--shim-dir", help="Windows-only override for the npm shim directory.")
    parser.add_argument("--codex-bin", help="Unix-only override for the `codex` launcher path.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).expanduser().resolve()
    codex_home = Path(args.codex_home).expanduser().resolve()
    shim_dir = Path(args.shim_dir).expanduser().resolve() if args.shim_dir else None
    codex_bin = Path(args.codex_bin).expanduser().resolve() if args.codex_bin else None

    for message in install_integration(
        repo_root=repo_root,
        codex_home=codex_home,
        python_bin=args.python_bin,
        patch_codex=args.patch_codex,
        shim_dir=shim_dir,
        codex_bin=codex_bin,
    ):
        print(message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
