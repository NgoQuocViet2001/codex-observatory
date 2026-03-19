from __future__ import annotations

import argparse
import os
import shutil
import stat
import subprocess
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
UNIX_WRAPPER_MARKER = "# >>> codex-observatory launcher wrapper >>>"

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


def path_exists(path: Path) -> bool:
    return path.exists() or path.is_symlink()


def ensure_backup(path: Path, backup_dir: Path) -> None:
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_path = backup_dir / f"{path.name}.orig"
    if path_exists(backup_path):
        return
    if path.is_symlink():
        backup_path.symlink_to(os.readlink(path))
        return
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


def render_unix_launcher_wrapper(backup_path: Path) -> str:
    original_launcher = shell_quote(str(backup_path).replace("\\", "/"))
    return (
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        f"{UNIX_WRAPPER_MARKER}\n"
        'if [ "${1-}" = "stats" ] || [ "${1-}" = "stat" ]; then\n'
        "  shift\n"
        '  codex_home="${CODEX_HOME:-$HOME/.codex}"\n'
        '  stats_script="$codex_home/tools/codex-stats.sh"\n'
        '  if [ ! -f "$stats_script" ]; then\n'
        '    echo "Missing stats script: $stats_script" >&2\n'
        "    exit 1\n"
        "  fi\n"
        '  exec "$stats_script" "$@"\n'
        "fi\n"
        f"exec {original_launcher} \"$@\"\n"
    )


def patch_unix_launcher(path: Path, backup_dir: Path) -> bool:
    if not path_exists(path) or path.is_dir():
        return False

    original = path.read_text(encoding="utf-8", errors="ignore")
    if UNIX_WRAPPER_MARKER in original and not path.is_symlink():
        return False

    ensure_backup(path, backup_dir)
    backup_path = backup_dir / f"{path.name}.orig"

    if path.is_symlink():
        path.unlink()

    write_text(path, render_unix_launcher_wrapper(backup_path), executable=True)
    return True


def find_upstream_unix_codex_target(unix_launcher: Path) -> Path | None:
    candidates: list[Path] = []

    npm_bin = shutil.which("npm")
    if npm_bin:
        try:
            result = subprocess.run(
                [npm_bin, "root", "-g"],
                check=False,
                capture_output=True,
                text=True,
            )
        except OSError:
            result = None
        if result and result.returncode == 0:
            npm_root = result.stdout.strip()
            if npm_root:
                candidates.append(Path(npm_root) / "@openai" / "codex" / "bin" / "codex.js")

    candidates.append(unix_launcher.parent.parent / "lib" / "node_modules" / "@openai" / "codex" / "bin" / "codex.js")

    seen: set[Path] = set()
    for candidate in candidates:
        resolved = candidate.expanduser()
        if resolved in seen:
            continue
        seen.add(resolved)
        if resolved.exists() and resolved.is_file():
            return resolved.resolve()
    return None


def rebuild_unix_launcher_backup(unix_launcher: Path, backup_dir: Path) -> Path | None:
    backup_path = backup_dir / f"{unix_launcher.name}.orig"
    if path_exists(backup_path):
        return None

    upstream_target = find_upstream_unix_codex_target(unix_launcher)
    if upstream_target is None:
        return None

    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_path.symlink_to(upstream_target)
    return backup_path


def resolve_symlink_target(path: Path) -> Path | None:
    if not path_exists(path) or not path.is_symlink():
        return None
    try:
        target = (path.parent / Path(os.readlink(path))).resolve()
    except OSError:
        return None
    return target if target != path else None


def restore_legacy_unix_target(unix_launcher: Path, backup_dir: Path) -> Path | None:
    candidate_paths: list[Path] = []

    direct_target = resolve_symlink_target(unix_launcher)
    if direct_target is not None:
        candidate_paths.append(direct_target)

    launcher_backup = backup_dir / f"{unix_launcher.name}.orig"
    backup_target = resolve_symlink_target(launcher_backup)
    if backup_target is not None and backup_target not in candidate_paths:
        candidate_paths.append(backup_target)

    for target_path in candidate_paths:
        backup_path = backup_dir / f"{target_path.name}.orig"
        if not path_exists(backup_path):
            continue
        if path_exists(target_path) and target_path.is_dir():
            continue
        if path_exists(target_path):
            current = target_path.read_text(encoding="utf-8", errors="ignore")
            if SH_MARKER not in current:
                continue
        if restore_backup(target_path, backup_path):
            return target_path
    return None


def restore_backup(target_path: Path, backup_path: Path) -> bool:
    if not path_exists(backup_path):
        return False

    target_path.parent.mkdir(parents=True, exist_ok=True)
    if path_exists(target_path):
        if target_path.is_dir():
            return False
        target_path.unlink()

    if backup_path.is_symlink():
        target_path.symlink_to(os.readlink(backup_path))
    else:
        shutil.copy2(backup_path, target_path)
    return True


def patch_file(path: Path, patcher, backup_dir: Path) -> bool:
    if not path_exists(path) or path.is_dir():
        return False
    original = path.read_text(encoding="utf-8", errors="ignore")
    updated = patcher(original)
    if updated == original:
        return False
    ensure_backup(path, backup_dir)
    write_text(path, updated, executable=bool(path.stat().st_mode & stat.S_IXUSR))
    return True


def integration_targets(*, codex_home: Path) -> tuple[Path, Path, Path]:
    skill_dir = codex_home / "skills" / "codex-observatory"
    tool_dir = codex_home / "tools"
    integration_dir = codex_home / "integrations" / "codex-observatory"
    return skill_dir, tool_dir, integration_dir


def launcher_targets(*, shim_dir: Path | None = None, codex_bin: Path | None = None):
    if os.name == "nt":
        shim_root = shim_dir or Path(os.environ.get("APPDATA", str(Path.home() / "AppData" / "Roaming"))) / "npm"
        return [
            (shim_root / "codex.ps1", patch_powershell_shim),
            (shim_root / "codex.cmd", patch_cmd_shim),
            (shim_root / "codex", patch_shell_shim),
        ]
    return []


def resolve_unix_launcher(*, codex_bin: Path | None = None) -> Path | None:
    found_codex = str(codex_bin) if codex_bin else shutil.which("codex")
    return Path(found_codex).expanduser() if found_codex else None


def unlink_if_exists(path: Path) -> bool:
    if not path_exists(path) or path.is_dir():
        return False
    path.unlink()
    return True


def rmtree_if_exists(path: Path) -> bool:
    if not path_exists(path):
        return False
    if path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink()
    return True


def prune_empty_dirs(path: Path, *, stop_at: Path) -> None:
    current = path
    while current.exists() and current.is_dir():
        try:
            current.rmdir()
        except OSError:
            break
        if current == stop_at:
            break
        current = current.parent


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

    skill_dir, tool_dir, integration_dir = integration_targets(codex_home=codex_home)
    skill_target = skill_dir / "SKILL.md"
    write_text(skill_target, resolve_skill_content(repo_root, skill_source))
    messages.append(f"Installed Codex skill: {skill_target}")

    ps1_tool = tool_dir / "codex-stats.ps1"
    sh_tool = tool_dir / "codex-stats.sh"
    write_text(ps1_tool, render_stats_ps1(runner_command))
    write_text(sh_tool, render_stats_sh(runner_command), executable=True)
    messages.append(f"Installed helper tools: {ps1_tool} and {sh_tool}")

    if not patch_codex:
        messages.append("Skipped Codex shim patch. Re-run with --patch-codex if you want `codex stats`.")
        return messages

    backup_dir = integration_dir / "backups"
    patched_any = False

    if os.name == "nt":
        targets = launcher_targets(shim_dir=shim_dir, codex_bin=codex_bin)
        for path, patcher in targets:
            if patch_file(path, patcher, backup_dir):
                messages.append(f"Patched Codex shim: {path}")
                patched_any = True
            elif path_exists(path):
                messages.append(f"Codex shim already patched: {path}")

        if not patched_any and not any(path_exists(path) for path, _ in targets):
            raise FileNotFoundError("Could not find a Codex launcher to patch. Install Codex first, or pass an explicit launcher path.")
    else:
        unix_launcher = resolve_unix_launcher(codex_bin=codex_bin)
        restored_target = restore_legacy_unix_target(unix_launcher, backup_dir) if unix_launcher else None
        if restored_target is not None:
            messages.append(f"Restored legacy Codex launcher target: {restored_target}")
        rebuilt_backup = rebuild_unix_launcher_backup(unix_launcher, backup_dir) if unix_launcher else None
        if rebuilt_backup is not None and restored_target is None:
            messages.append(f"Rebuilt missing Codex launcher backup: {rebuilt_backup}")
        if unix_launcher and patch_unix_launcher(unix_launcher, backup_dir):
            messages.append(f"Patched Codex shim: {unix_launcher}")
            patched_any = True
        elif unix_launcher and path_exists(unix_launcher):
            messages.append(f"Codex shim already patched: {unix_launcher}")
        else:
            raise FileNotFoundError("Could not find a Codex launcher to patch. Install Codex first, or pass an explicit launcher path.")

    messages.append(f"Backups are stored in: {backup_dir}")
    return messages


def uninstall_integration(
    *,
    codex_home: Path,
    shim_dir: Path | None = None,
    codex_bin: Path | None = None,
) -> list[str]:
    messages: list[str] = []
    skill_dir, tool_dir, integration_dir = integration_targets(codex_home=codex_home)
    backup_dir = integration_dir / "backups"
    keep_integration_state = False

    restored_any = False
    if os.name == "nt":
        for target_path, _patcher in launcher_targets(shim_dir=shim_dir, codex_bin=codex_bin):
            backup_path = backup_dir / f"{target_path.name}.orig"
            if not restore_backup(target_path, backup_path):
                continue
            messages.append(f"Restored Codex shim: {target_path}")
            restored_any = True
    else:
        unix_launcher = resolve_unix_launcher(codex_bin=codex_bin)
        if unix_launcher:
            rebuilt_backup = rebuild_unix_launcher_backup(unix_launcher, backup_dir)
            if rebuilt_backup is not None:
                messages.append(f"Rebuilt missing Codex launcher backup: {rebuilt_backup}")
            backup_path = backup_dir / f"{unix_launcher.name}.orig"
            if restore_backup(unix_launcher, backup_path):
                messages.append(f"Restored Codex shim: {unix_launcher}")
                restored_any = True
            restored_target = restore_legacy_unix_target(unix_launcher, backup_dir)
            if restored_target is not None:
                messages.append(f"Restored legacy Codex launcher target: {restored_target}")
                restored_any = True
            if path_exists(unix_launcher) and not unix_launcher.is_symlink():
                current = unix_launcher.read_text(encoding="utf-8", errors="ignore")
                if UNIX_WRAPPER_MARKER in current:
                    keep_integration_state = True
                    messages.append(f"Kept integration state because the Codex launcher is still wrapped: {unix_launcher}")
    if not restored_any:
        messages.append(f"No Codex launcher backups found under: {backup_dir}")

    ps1_tool = tool_dir / "codex-stats.ps1"
    sh_tool = tool_dir / "codex-stats.sh"
    if unlink_if_exists(ps1_tool):
        messages.append(f"Removed helper tool: {ps1_tool}")
    if unlink_if_exists(sh_tool):
        messages.append(f"Removed helper tool: {sh_tool}")
    prune_empty_dirs(tool_dir, stop_at=codex_home)

    if rmtree_if_exists(skill_dir):
        messages.append(f"Removed Codex skill: {skill_dir}")
    prune_empty_dirs(skill_dir.parent, stop_at=codex_home)

    if not keep_integration_state and rmtree_if_exists(integration_dir):
        messages.append(f"Removed integration state: {integration_dir}")
    if not keep_integration_state:
        prune_empty_dirs(integration_dir.parent, stop_at=codex_home)

    if len(messages) == 1 and messages[0].startswith("No Codex launcher backups found"):
        messages.append("No Codex Observatory integration files were removed.")
    return messages


def build_parser(*, action: str) -> argparse.ArgumentParser:
    description = (
        "Install Codex Observatory skill, helper tools, and optional `codex stats` launcher patch."
        if action == "install"
        else "Remove Codex Observatory integration files and restore the local `codex` launcher from backups when available."
    )
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--codex-home", default=os.environ.get("CODEX_HOME", "~/.codex"), help="Path to the .codex directory.")
    parser.add_argument("--shim-dir", help="Windows-only override for the npm shim directory.")
    parser.add_argument("--codex-bin", help="Unix-only override for the `codex` launcher path.")
    if action == "install":
        parser.add_argument("--repo-root", help="Path to the codex-observatory repository root.")
        parser.add_argument("--skill-source", help="Optional path to a SKILL.md file to install instead of the built-in template.")
        parser.add_argument("--python-bin", help="Python interpreter to embed in generated helper scripts.")
        parser.add_argument("--runner-bin", help="Executable to embed in generated helper scripts instead of Python.")
        parser.add_argument("--patch-codex", action="store_true", help="Patch the local `codex` launcher so `codex stats` works directly.")
    return parser


def main(argv: list[str] | None = None, *, action: str = "install") -> int:
    parser = build_parser(action=action)
    args = parser.parse_args(argv)

    codex_home = Path(args.codex_home).expanduser().resolve()
    shim_dir = Path(args.shim_dir).expanduser().resolve() if args.shim_dir else None
    codex_bin = Path(args.codex_bin).expanduser().resolve() if args.codex_bin else None
    if action == "install":
        repo_root = Path(args.repo_root).expanduser().resolve() if args.repo_root else None
        skill_source = Path(args.skill_source).expanduser().resolve() if args.skill_source else None
        runner_command = default_runner_command(runner_bin=args.runner_bin, python_bin=args.python_bin)
        messages = install_integration(
            codex_home=codex_home,
            runner_command=runner_command,
            patch_codex=args.patch_codex,
            repo_root=repo_root,
            skill_source=skill_source,
            shim_dir=shim_dir,
            codex_bin=codex_bin,
        )
    else:
        messages = uninstall_integration(
            codex_home=codex_home,
            shim_dir=shim_dir,
            codex_bin=codex_bin,
        )

    for message in messages:
        print(message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
