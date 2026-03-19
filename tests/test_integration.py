from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from codex_observatory.codex_integration import (
    default_runner_command,
    install_integration,
    patch_cmd_shim,
    patch_powershell_shim,
    patch_shell_shim,
)


class CodexIntegrationTests(unittest.TestCase):
    def test_patch_powershell_shim_is_idempotent(self) -> None:
        source = "#!/usr/bin/env pwsh\n$basedir=Split-Path $MyInvocation.MyCommand.Definition -Parent\n"
        patched = patch_powershell_shim(source)
        self.assertIn("codex-observatory stats hook", patched)
        self.assertIn("$env:CODEX_HOME", patched)
        self.assertIn("$basedir=Split-Path", patched)
        self.assertEqual(patched, patch_powershell_shim(patched))

    def test_patch_cmd_shim_inserts_dispatch_and_target(self) -> None:
        source = "@ECHO off\r\nCALL :find_dp0\r\nendLocal & goto #_undefined_#\r\n"
        patched = patch_cmd_shim(source)
        self.assertIn("codex_observatory_stats", patched)
        self.assertIn('SET "STATS_ROOT=%CODEX_HOME%"', patched)
        self.assertIn("codex-observatory stats dispatch", patched)
        self.assertEqual(patched, patch_cmd_shim(patched))

    def test_patch_shell_shim_inserts_stats_hook(self) -> None:
        source = '#!/bin/sh\nif [ -x "$basedir/node" ]; then\n  exec "$basedir/node"\nfi\n'
        patched = patch_shell_shim(source)
        self.assertIn('codex_home="${CODEX_HOME:-$HOME/.codex}"', patched)
        self.assertIn('stats_script="$codex_home/tools/codex-stats.sh"', patched)
        self.assertEqual(patched, patch_shell_shim(patched))

    def test_install_integration_writes_tools_and_patches_local_shims(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo_root = root / "repo"
            codex_home = root / ".codex"
            shim_dir = root / "npm"
            skill_dir = repo_root / "integrations" / "codex-skill"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text("skill", encoding="utf-8")
            shim_dir.mkdir(parents=True)
            (shim_dir / "codex.ps1").write_text("#!/usr/bin/env pwsh\n$basedir='x'\n", encoding="utf-8")
            (shim_dir / "codex.cmd").write_text("@ECHO off\r\nCALL :find_dp0\r\n", encoding="utf-8")
            (shim_dir / "codex").write_text('#!/bin/sh\nif [ -x "$basedir/node" ]; then\nfi\n', encoding="utf-8")

            messages = install_integration(
                codex_home=codex_home,
                repo_root=repo_root,
                runner_command=default_runner_command(python_bin="python"),
                patch_codex=True,
                shim_dir=shim_dir,
                codex_bin=(shim_dir / "codex") if sys.platform != "win32" else None,
            )

            self.assertTrue((codex_home / "skills" / "codex-observatory" / "SKILL.md").exists())
            self.assertTrue((codex_home / "tools" / "codex-stats.ps1").exists())
            self.assertTrue((codex_home / "tools" / "codex-stats.sh").exists())
            backup_dir = codex_home / "integrations" / "codex-observatory" / "backups"
            if sys.platform == "win32":
                self.assertTrue((backup_dir / "codex.ps1.orig").exists())
            else:
                self.assertTrue((backup_dir / "codex.orig").exists())
            self.assertIn("Patched Codex shim", "\n".join(messages))
