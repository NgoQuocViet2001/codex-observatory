from __future__ import annotations

import argparse
import os
import shutil
import stat
import sys
from pathlib import Path


DEFAULT_SKILL_MD = """---
name: codex-observatory
description: Use this skill when the user asks for Codex usage stats, token trends, model breakdowns, streaks, or a local dashboard. Prefer `codex stats` when the launcher patch is installed, otherwise run `codex-observatory`.
---

# Codex Observatory

Use this skill when the user wants live local Codex usage information from machine logs.

## Workflow

1. Prefer `codex stats` for the default dashboard when the launcher patch is installed.
2. Otherwise run `codex-observatory`.
3. Use `compact` for a shorter view.
4. Use `full` for a detailed view.
5. Add `--no-color` when ANSI output is hard to read in the current surface.
6. Use `--json` if the user wants a machine-readable export.
"""

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


def escape_ps_single(value: str) -> str:
    return value.replace("'", "''")


def shell_quote(value: str) -> str:
    return "'" + value.replace("'", "'\"'\"'") + "'"


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
        insert_at = len(content) if insert_at < 0 else insert_at + len(newline)
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
    if not path.exists() or path.is_dir():
        return False
    original = path.read_text(encoding="utf-8", errors="ignore")
    updated = patcher(original)
    if updated == original:
        return False
    ensure_backup(path, backup_dir)
    write_text(path, updated, executable=bool(path.stat().st_mode & stat.S_IXUSR))
    return True


def render_stats_ps1(runner_command: list[str]) -> str:
    runner_items = ", ".join(f"'{escape_ps_single(item)}'" for item in runner_command)
    return (
        "param(\n"
        "    [Parameter(ValueFromRemainingArguments = $true)]\n"
        "    [string[]]$CliArgs\n"
        ")\n\n"
        f"$runner = @({runner_items})\n"
        "$cmd = $runner[0]\n"
        "$cmdArgs = @()\n"
        "if ($runner.Count -gt 1) {\n"
        "  $cmdArgs = $runner[1..($runner.Count - 1)]\n"
        "}\n"
        "& $cmd @cmdArgs @CliArgs\n"
        "exit $LASTEXITCODE\n"
    )


def render_stats_sh(runner_command: list[str]) -> str:
    runner_items = " ".join(shell_quote(item.replace("\\", "/")) for item in runner_command)
    return (
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        f"RUNNER=({runner_items})\n"
        'exec "${RUNNER[@]}" "$@"\n'
    )


def resolve_skill_content(repo_root: Path | None, skill_source: Path | None) -> str:
    candidates = []
    if skill_source is not None:
        candidates.append(skill_source)
    if repo_root is not None:
        candidates.append(repo_root / "integrations" / "codex-skill" / "SKILL.md")
    for candidate in candidates:
        if candidate.exists():
            return candidate.read_text(encoding="utf-8")
    return DEFAULT_SKILL_MD


def default_runner_command(*, runner_bin: str | None = None, python_bin: str | None = None) -> list[str]:
    if runner_bin:
        return [runner_bin]
    return [python_bin or sys.executable, "-m", "codex_observatory"]


def install_integration(
    *,
    codex_home: Path,
    runner_command: list[str],
    patch_codex: bool,
    repo_root: Path | None = None,
    skill_source: Path | None = None,
    shim_dir: Path | None = None,
    codex_bin: Path | None = None,
) -> list[str]:
    messages: list[str] = []

    skill_target = codex_home / "skills" / "codex-observatory" / "SKILL.md"
    write_text(skill_target, resolve_skill_content(repo_root, skill_source))
    messages.append(f"Installed Codex skill: {skill_target}")

    tool_dir = codex_home / "tools"
    ps1_tool = tool_dir / "codex-stats.ps1"
    sh_tool = tool_dir / "codex-stats.sh"
    write_text(ps1_tool, render_stats_ps1(runner_command))
    write_text(sh_tool, render_stats_sh(runner_command), executable=True)
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
        found_codex = str(codex_bin) if codex_bin else shutil.which("codex")
        targets = [(Path(found_codex).resolve(), patch_shell_shim)] if found_codex else []

    for path, patcher in targets:
        if patch_file(path, patcher, backup_dir):
            messages.append(f"Patched Codex shim: {path}")
            patched_any = True
        elif path.exists():
            messages.append(f"Codex shim already patched: {path}")

    if not patched_any and not any(path.exists() for path, _ in targets):
        raise FileNotFoundError("Could not find a Codex launcher to patch. Install Codex first, or pass an explicit launcher path.")

    messages.append(f"Backups are stored in: {backup_dir}")
    return messages


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Install Codex Observatory skill, helper tools, and optional `codex stats` launcher patch.")
    parser.add_argument("--repo-root", help="Path to the codex-observatory repository root.")
    parser.add_argument("--skill-source", help="Optional path to a SKILL.md file to install instead of the built-in template.")
    parser.add_argument("--python-bin", help="Python interpreter to embed in generated helper scripts.")
    parser.add_argument("--runner-bin", help="Executable to embed in generated helper scripts instead of Python.")
    parser.add_argument("--codex-home", default=os.environ.get("CODEX_HOME", "~/.codex"), help="Path to the .codex directory.")
    parser.add_argument("--patch-codex", action="store_true", help="Patch the local `codex` launcher so `codex stats` works directly.")
    parser.add_argument("--shim-dir", help="Windows-only override for the npm shim directory.")
    parser.add_argument("--codex-bin", help="Unix-only override for the `codex` launcher path.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).expanduser().resolve() if args.repo_root else None
    skill_source = Path(args.skill_source).expanduser().resolve() if args.skill_source else None
    codex_home = Path(args.codex_home).expanduser().resolve()
    shim_dir = Path(args.shim_dir).expanduser().resolve() if args.shim_dir else None
    codex_bin = Path(args.codex_bin).expanduser().resolve() if args.codex_bin else None
    runner_command = default_runner_command(runner_bin=args.runner_bin, python_bin=args.python_bin)

    for message in install_integration(
        codex_home=codex_home,
        runner_command=runner_command,
        patch_codex=args.patch_codex,
        repo_root=repo_root,
        skill_source=skill_source,
        shim_dir=shim_dir,
        codex_bin=codex_bin,
    ):
        print(message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
