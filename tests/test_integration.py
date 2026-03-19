from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import sys
import os


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from codex_observatory.codex_integration import (
    default_runner_command,
    install_integration,
    patch_cmd_shim,
    patch_powershell_shim,
    patch_shell_shim,
    uninstall_integration,
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

    def test_uninstall_integration_restores_shims_and_removes_managed_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo_root = root / "repo"
            codex_home = root / ".codex"
            shim_dir = root / "npm"
            skill_dir = repo_root / "integrations" / "codex-skill"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text("skill", encoding="utf-8")
            shim_dir.mkdir(parents=True)

            original_ps1 = "#!/usr/bin/env pwsh\n$basedir='x'\n"
            original_cmd = "@ECHO off\r\nCALL :find_dp0\r\n"
            original_sh = '#!/bin/sh\nif [ -x "$basedir/node" ]; then\nfi\n'
            (shim_dir / "codex.ps1").write_text(original_ps1, encoding="utf-8")
            (shim_dir / "codex.cmd").write_text(original_cmd, encoding="utf-8")
            (shim_dir / "codex").write_text(original_sh, encoding="utf-8")
            expected_ps1 = (shim_dir / "codex.ps1").read_text(encoding="utf-8")
            expected_cmd = (shim_dir / "codex.cmd").read_text(encoding="utf-8")
            expected_sh = (shim_dir / "codex").read_text(encoding="utf-8")

            install_integration(
                codex_home=codex_home,
                repo_root=repo_root,
                runner_command=default_runner_command(python_bin="python"),
                patch_codex=True,
                shim_dir=shim_dir,
                codex_bin=(shim_dir / "codex") if sys.platform != "win32" else None,
            )

            messages = uninstall_integration(
                codex_home=codex_home,
                shim_dir=shim_dir,
                codex_bin=(shim_dir / "codex") if sys.platform != "win32" else None,
            )

            self.assertFalse((codex_home / "skills" / "codex-observatory").exists())
            self.assertFalse((codex_home / "tools" / "codex-stats.ps1").exists())
            self.assertFalse((codex_home / "tools" / "codex-stats.sh").exists())
            self.assertFalse((codex_home / "integrations" / "codex-observatory").exists())
            if sys.platform == "win32":
                self.assertEqual((shim_dir / "codex.ps1").read_text(encoding="utf-8"), expected_ps1)
                self.assertEqual((shim_dir / "codex.cmd").read_text(encoding="utf-8"), expected_cmd)
                self.assertEqual((shim_dir / "codex").read_text(encoding="utf-8"), expected_sh)
            else:
                self.assertEqual((shim_dir / "codex").read_text(encoding="utf-8"), expected_sh)
            self.assertIn("Removed helper tool", "\n".join(messages))

    @unittest.skipIf(sys.platform == "win32", "Unix launcher symlink behavior is only relevant on Unix")
    def test_install_integration_wraps_unix_symlink_launcher_without_touching_js_target(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo_root = root / "repo"
            codex_home = root / ".codex"
            bin_dir = root / "bin"
            lib_dir = root / "lib"
            skill_dir = repo_root / "integrations" / "codex-skill"
            skill_dir.mkdir(parents=True)
            skill_dir.joinpath("SKILL.md").write_text("skill", encoding="utf-8")
            bin_dir.mkdir(parents=True)
            lib_dir.mkdir(parents=True)

            real_launcher = lib_dir / "codex.js"
            original_js = "#!/usr/bin/env node\nconsole.log('codex');\n"
            real_launcher.write_text(original_js, encoding="utf-8")

            launcher_link = bin_dir / "codex"
            launcher_link.symlink_to(real_launcher)

            messages = install_integration(
                codex_home=codex_home,
                repo_root=repo_root,
                runner_command=default_runner_command(python_bin="python"),
                patch_codex=True,
                codex_bin=launcher_link,
            )

            backup_path = codex_home / "integrations" / "codex-observatory" / "backups" / "codex.orig"
            self.assertTrue(backup_path.is_symlink())
            self.assertFalse(launcher_link.is_symlink())
            self.assertIn("codex-observatory launcher wrapper", launcher_link.read_text(encoding="utf-8"))
            self.assertEqual(real_launcher.read_text(encoding="utf-8"), original_js)
            self.assertIn("Patched Codex shim", "\n".join(messages))

            uninstall_messages = uninstall_integration(
                codex_home=codex_home,
                codex_bin=launcher_link,
            )

            self.assertTrue(launcher_link.is_symlink())
            restored_target = (launcher_link.parent / Path(os.readlink(launcher_link))).resolve()
            self.assertEqual(restored_target, real_launcher.resolve())
            self.assertEqual(real_launcher.read_text(encoding="utf-8"), original_js)
            self.assertIn("Restored Codex shim", "\n".join(uninstall_messages))

    @unittest.skipIf(sys.platform == "win32", "Legacy Unix launcher recovery is only relevant on Unix")
    def test_install_integration_recovers_legacy_patched_js_target_before_wrapping(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo_root = root / "repo"
            codex_home = root / ".codex"
            bin_dir = root / "bin"
            lib_dir = root / "lib"
            skill_dir = repo_root / "integrations" / "codex-skill"
            backup_dir = codex_home / "integrations" / "codex-observatory" / "backups"
            skill_dir.mkdir(parents=True)
            skill_dir.joinpath("SKILL.md").write_text("skill", encoding="utf-8")
            bin_dir.mkdir(parents=True)
            lib_dir.mkdir(parents=True)
            backup_dir.mkdir(parents=True)

            real_launcher = lib_dir / "codex.js"
            original_js = "#!/usr/bin/env node\nconsole.log('codex');\n"
            real_launcher.write_text("# >>> codex-observatory stats hook >>>\nconsole.log('broken');\n", encoding="utf-8")
            (backup_dir / "codex.js.orig").write_text(original_js, encoding="utf-8")

            launcher_link = bin_dir / "codex"
            launcher_link.symlink_to(real_launcher)

            messages = install_integration(
                codex_home=codex_home,
                repo_root=repo_root,
                runner_command=default_runner_command(python_bin="python"),
                patch_codex=True,
                codex_bin=launcher_link,
            )

            self.assertEqual(real_launcher.read_text(encoding="utf-8"), original_js)
            self.assertFalse(launcher_link.is_symlink())
            self.assertIn("Restored legacy Codex launcher target", "\n".join(messages))

    @unittest.skipIf(sys.platform == "win32", "Legacy Unix launcher recovery is only relevant on Unix")
    def test_uninstall_integration_restores_legacy_patched_js_target_without_wrapper_backup(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            codex_home = root / ".codex"
            bin_dir = root / "bin"
            lib_dir = root / "lib"
            backup_dir = codex_home / "integrations" / "codex-observatory" / "backups"
            bin_dir.mkdir(parents=True)
            lib_dir.mkdir(parents=True)
            backup_dir.mkdir(parents=True)

            real_launcher = lib_dir / "codex.js"
            original_js = "#!/usr/bin/env node\nconsole.log('codex');\n"
            real_launcher.write_text("# >>> codex-observatory stats hook >>>\nconsole.log('broken');\n", encoding="utf-8")
            (backup_dir / "codex.js.orig").write_text(original_js, encoding="utf-8")

            launcher_link = bin_dir / "codex"
            launcher_link.symlink_to(real_launcher)

            messages = uninstall_integration(
                codex_home=codex_home,
                codex_bin=launcher_link,
            )

            self.assertEqual(real_launcher.read_text(encoding="utf-8"), original_js)
            self.assertTrue(launcher_link.is_symlink())
            self.assertFalse((codex_home / "integrations" / "codex-observatory").exists())
            self.assertIn("Restored legacy Codex launcher target", "\n".join(messages))
