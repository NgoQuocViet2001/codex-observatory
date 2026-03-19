from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def unix_seconds(value: str) -> int:
    return int(datetime.fromisoformat(value).replace(tzinfo=timezone.utc).timestamp())


class CodexObservatoryTests(unittest.TestCase):
    def make_fixture(self, *, include_history: bool = True) -> Path:
        temp_dir = Path(tempfile.mkdtemp())
        codex_home = temp_dir / ".codex"
        sessions_dir = codex_home / "sessions" / "2026" / "03" / "19"
        sessions_dir.mkdir(parents=True)

        history_rows = [
            {"session_id": "session-a", "ts": unix_seconds("2026-03-18T01:00:00")},
            {"session_id": "session-a", "ts": unix_seconds("2026-03-18T01:05:00")},
            {"session_id": "session-b", "ts": unix_seconds("2026-03-19T01:00:00")},
        ]
        if include_history:
            (codex_home / "history.jsonl").write_text(
                "\n".join(json.dumps(row) for row in history_rows) + "\n",
                encoding="utf-8",
            )

        session_a = [
            {"timestamp": "2026-03-18T01:00:00Z", "type": "session_meta", "payload": {"id": "session-a"}},
            {
                "timestamp": "2026-03-18T00:59:30Z",
                "type": "response_item",
                "payload": {
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": "<environment_context>\n  <cwd>D:\\fixture</cwd>\n</environment_context>"}],
                },
            },
            {
                "timestamp": "2026-03-18T01:00:00Z",
                "type": "response_item",
                "payload": {
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": "prompt one"}],
                },
            },
            {"timestamp": "2026-03-18T01:00:00Z", "type": "event_msg", "payload": {"type": "user_message", "message": "prompt one"}},
            {
                "timestamp": "2026-03-18T01:05:00Z",
                "type": "response_item",
                "payload": {
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": "prompt two"}],
                },
            },
            {"timestamp": "2026-03-18T01:05:00Z", "type": "event_msg", "payload": {"type": "user_message", "message": "prompt two"}},
            {"timestamp": "2026-03-18T01:01:00Z", "type": "turn_context", "payload": {"model": "gpt-5.4"}},
            {
                "timestamp": "2026-03-18T01:02:00Z",
                "type": "event_msg",
                "payload": {
                    "type": "token_count",
                    "info": {
                        "total_token_usage": {
                            "input_tokens": 1000,
                            "cached_input_tokens": 300,
                            "output_tokens": 120,
                            "reasoning_output_tokens": 80,
                            "total_tokens": 1120,
                        }
                    },
                },
            },
            {
                "timestamp": "2026-03-18T01:03:00Z",
                "type": "event_msg",
                "payload": {
                    "type": "token_count",
                    "info": {
                        "total_token_usage": {
                            "input_tokens": 1600,
                            "cached_input_tokens": 500,
                            "output_tokens": 210,
                            "reasoning_output_tokens": 110,
                            "total_tokens": 1810,
                        }
                    },
                },
            },
        ]

        session_b = [
            {"timestamp": "2026-03-19T01:00:00Z", "type": "session_meta", "payload": {"id": "session-b"}},
            {
                "timestamp": "2026-03-19T00:59:45Z",
                "type": "response_item",
                "payload": {
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": "<environment_context>\n  <cwd>D:\\fixture</cwd>\n</environment_context>"}],
                },
            },
            {
                "timestamp": "2026-03-19T01:00:00Z",
                "type": "response_item",
                "payload": {
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": "prompt three"}],
                },
            },
            {"timestamp": "2026-03-19T01:00:00Z", "type": "event_msg", "payload": {"type": "user_message", "message": "prompt three"}},
            {"timestamp": "2026-03-19T01:01:00Z", "type": "turn_context", "payload": {"model": "gpt-5.3-codex"}},
            {
                "timestamp": "2026-03-19T01:02:00Z",
                "type": "event_msg",
                "payload": {
                    "type": "token_count",
                    "info": {
                        "total_token_usage": {
                            "input_tokens": 2000,
                            "cached_input_tokens": 1000,
                            "output_tokens": 220,
                            "reasoning_output_tokens": 100,
                            "total_tokens": 2220,
                        }
                    },
                },
            },
        ]

        (sessions_dir / "session-a.jsonl").write_text("\n".join(json.dumps(row) for row in session_a) + "\n", encoding="utf-8")
        (sessions_dir / "session-b.jsonl").write_text("\n".join(json.dumps(row) for row in session_b) + "\n", encoding="utf-8")
        return codex_home

    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(ROOT / "src")
        return subprocess.run(
            [sys.executable, "-m", "codex_observatory", *args],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
            env=env,
        )

    def test_json_summary_has_expected_totals(self) -> None:
        codex_home = self.make_fixture()
        result = self.run_cli("--json", "--codex-home", str(codex_home), "--now", "2026-03-19T10:00:00")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["summary"]["today"]["prompts"], 1)
        self.assertEqual(payload["summary"]["all_time"]["prompts"], 3)
        self.assertEqual(payload["summary"]["all_time"]["sessions"], 2)
        self.assertEqual(payload["summary"]["latest_model"], "gpt-5.3-codex")
        self.assertEqual(len(payload["models_30d"]), 2)

    def test_json_summary_works_without_history_file_by_parsing_session_logs(self) -> None:
        codex_home = self.make_fixture(include_history=False)
        result = self.run_cli("--json", "--codex-home", str(codex_home), "--now", "2026-03-19T10:00:00")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["summary"]["today"]["prompts"], 1)
        self.assertEqual(payload["summary"]["all_time"]["prompts"], 3)
        self.assertEqual(payload["summary"]["all_time"]["sessions"], 2)
        self.assertEqual(payload["summary"]["latest_model"], "gpt-5.3-codex")

    def test_parent_path_resolves_nested_session_only_codex_home(self) -> None:
        codex_home = self.make_fixture(include_history=False)
        result = self.run_cli("--json", "--codex-home", str(codex_home.parent), "--now", "2026-03-19T10:00:00")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["summary"]["all_time"]["prompts"], 3)
        self.assertTrue(payload["codex_home"].endswith(".codex"))

    def test_text_dashboard_renders_core_sections(self) -> None:
        codex_home = self.make_fixture()
        result = self.run_cli(
            "full",
            "--codex-home",
            str(codex_home),
            "--now",
            "2026-03-19T10:00:00",
            "--no-color",
            "--width",
            "140",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("CODEX STATS", result.stdout)
        self.assertIn("MODEL BREAKDOWN (30d)", result.stdout)
        self.assertIn("MODEL BREAKDOWN (all-time)", result.stdout)
        self.assertIn("RECENT ACTIVITY", result.stdout)
        self.assertIn("DAY-OF-WEEK PATTERN", result.stdout)
