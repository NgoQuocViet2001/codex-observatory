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
    def make_fixture(self, *, include_history: bool = True, include_sessions: bool = True) -> Path:
        temp_dir = Path(tempfile.mkdtemp())
        codex_home = temp_dir / ".codex"
        codex_home.mkdir(parents=True, exist_ok=True)
        sessions_dir = codex_home / "sessions" / "2026" / "03" / "19"
        if include_sessions:
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

        if include_sessions:
            (sessions_dir / "session-a.jsonl").write_text(
                "\n".join(json.dumps(row) for row in session_a) + "\n",
                encoding="utf-8",
            )
            (sessions_dir / "session-b.jsonl").write_text(
                "\n".join(json.dumps(row) for row in session_b) + "\n",
                encoding="utf-8",
            )
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
        self.assertAlmostEqual(payload["costs"]["today"]["total_cost_usd"], 0.005005, places=9)
        self.assertAlmostEqual(payload["costs"]["all_time"]["total_cost_usd"], 0.01103, places=9)
        self.assertAlmostEqual(payload["costs"]["thirty_days"]["cache_savings_usd"], 0.0027, places=9)
        self.assertEqual(payload["costs"]["coverage_pct"]["all_time"], 100.0)
        self.assertEqual(payload["pricing"]["verified_at"], "2026-04-29")
        self.assertEqual(payload["pricing"]["long_context_input_threshold"], 272000)
        self.assertEqual(
            payload["pricing"]["scope_note"],
            "Estimated API-equivalent spend only; Codex app or subscription billing may differ.",
        )
        self.assertEqual(payload["pricing"]["unpriced_models"], [])
        self.assertEqual(payload["summary"]["all_time"]["turns"], 2)
        self.assertEqual(payload["summary"]["all_time"]["input_tokens"], 3600)
        self.assertEqual(payload["summary"]["all_time"]["cached_input_tokens"], 1500)
        self.assertEqual(payload["summary"]["all_time"]["output_tokens"], 430)
        self.assertEqual(payload["summary"]["all_time"]["reasoning_output_tokens"], 210)
        recent_activity = {row["date"]: row["cost_usd"] for row in payload["recent_activity"]}
        monthly_trend = {row["month"]: row["cost_usd"] for row in payload["monthly_trend"]}
        day_of_week = {row["day"]: row["cost_usd"] for row in payload["day_of_week"]}
        self.assertAlmostEqual(recent_activity["03-18"], 0.006025, places=9)
        self.assertAlmostEqual(recent_activity["03-19"], 0.005005, places=9)
        self.assertAlmostEqual(monthly_trend["2026-03"], 0.01103, places=9)
        self.assertAlmostEqual(day_of_week["Wed"], 0.006025, places=9)
        self.assertAlmostEqual(day_of_week["Thu"], 0.005005, places=9)
        self.assertEqual(next(row for row in payload["recent_activity"] if row["date"] == "03-18")["input_tokens"], 1600)
        self.assertEqual(next(row for row in payload["monthly_trend"] if row["month"] == "2026-03")["turns"], 2)
        self.assertEqual(next(row for row in payload["day_of_week"] if row["day"] == "Wed")["cached_input_tokens"], 500)

    def test_gpt_5_5_pricing_includes_cached_and_long_context_rates(self) -> None:
        temp_dir = Path(tempfile.mkdtemp())
        codex_home = temp_dir / ".codex"
        sessions_dir = codex_home / "sessions" / "2026" / "04" / "29"
        sessions_dir.mkdir(parents=True)
        (codex_home / "history.jsonl").write_text(
            json.dumps({"session_id": "session-gpt-55", "ts": unix_seconds("2026-04-29T01:00:00")}) + "\n",
            encoding="utf-8",
        )
        rows = [
            {"timestamp": "2026-04-29T01:00:00Z", "type": "session_meta", "payload": {"id": "session-gpt-55"}},
            {"timestamp": "2026-04-29T01:01:00Z", "type": "turn_context", "payload": {"model": "gpt-5.5"}},
            {
                "timestamp": "2026-04-29T01:02:00Z",
                "type": "event_msg",
                "payload": {
                    "type": "token_count",
                    "info": {
                        "total_token_usage": {
                            "input_tokens": 100000,
                            "cached_input_tokens": 50000,
                            "output_tokens": 10000,
                            "reasoning_output_tokens": 2000,
                            "total_tokens": 110000,
                        }
                    },
                },
            },
            {"timestamp": "2026-04-29T01:03:00Z", "type": "turn_context", "payload": {"model": "gpt-5.5-2026-04-23"}},
            {
                "timestamp": "2026-04-29T01:04:00Z",
                "type": "event_msg",
                "payload": {
                    "type": "token_count",
                    "info": {
                        "total_token_usage": {
                            "input_tokens": 400000,
                            "cached_input_tokens": 150000,
                            "output_tokens": 20000,
                            "reasoning_output_tokens": 4000,
                            "total_tokens": 420000,
                        }
                    },
                },
            },
        ]
        (sessions_dir / "session-gpt-55.jsonl").write_text(
            "\n".join(json.dumps(row) for row in rows) + "\n",
            encoding="utf-8",
        )

        result = self.run_cli("--json", "--codex-home", str(codex_home), "--now", "2026-04-29T10:00:00")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        models = {row["model"]: row for row in payload["models_30d"]}

        self.assertAlmostEqual(models["gpt-5.5"]["total_cost_usd"], 0.575, places=9)
        self.assertAlmostEqual(models["gpt-5.5-2026-04-23"]["total_cost_usd"], 2.55, places=9)
        self.assertAlmostEqual(payload["costs"]["today"]["total_cost_usd"], 3.125, places=9)
        self.assertEqual(payload["pricing"]["unpriced_models"], [])

    def test_json_month_selector_expands_daily_rows_for_that_month(self) -> None:
        codex_home = self.make_fixture()
        result = self.run_cli("--json", "--codex-home", str(codex_home), "--now", "2026-03-19T10:00:00", "--month", "2026-03")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)

        self.assertEqual(payload["selected_range"]["label"], "2026-03")
        self.assertEqual(payload["selected_range"]["start_date"], "2026-03-01")
        self.assertEqual(payload["selected_range"]["end_date"], "2026-03-31")
        self.assertEqual(payload["selected_range"]["stats"]["prompts"], 3)
        self.assertEqual(payload["selected_range"]["stats"]["tokens"], 4030)
        self.assertEqual(len(payload["recent_activity"]), 31)
        self.assertEqual(payload["recent_activity"][17]["date"], "03-18")
        self.assertEqual(payload["recent_activity"][17]["input_tokens"], 1600)
        self.assertEqual(len(payload["monthly_trend"]), 1)
        self.assertEqual(payload["monthly_trend"][0]["month"], "2026-03")
        self.assertEqual(payload["monthly_trend"][0]["prompts"], 3)
        self.assertEqual(payload["monthly_trend"][0]["turns"], 2)
        self.assertEqual(payload["monthly_trend"][0]["input_tokens"], 3600)
        self.assertEqual(payload["monthly_trend"][0]["cached_input_tokens"], 1500)
        self.assertEqual(payload["monthly_trend"][0]["output_tokens"], 430)
        self.assertEqual(payload["monthly_trend"][0]["reasoning_output_tokens"], 210)
        self.assertEqual(payload["monthly_trend"][0]["tokens"], 4030)
        self.assertAlmostEqual(payload["monthly_trend"][0]["cost_usd"], 0.01103, places=9)

    def test_json_custom_date_range_selector_is_inclusive(self) -> None:
        codex_home = self.make_fixture()
        result = self.run_cli(
            "--json",
            "--codex-home",
            str(codex_home),
            "--now",
            "2026-03-19T10:00:00",
            "--from",
            "2026-03-18",
            "--to",
            "2026-03-18",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)

        self.assertEqual(payload["selected_range"]["label"], "2026-03-18..2026-03-18")
        self.assertEqual(payload["selected_range"]["stats"]["prompts"], 2)
        self.assertEqual(payload["selected_range"]["stats"]["turns"], 1)
        self.assertEqual(payload["selected_range"]["stats"]["tokens"], 1810)
        self.assertEqual(len(payload["recent_activity"]), 1)
        self.assertEqual(payload["recent_activity"][0]["date"], "03-18")

        day_result = self.run_cli("--json", "--codex-home", str(codex_home), "--now", "2026-03-19T10:00:00", "--day", "2026-03-18")
        self.assertEqual(day_result.returncode, 0, day_result.stderr)
        day_payload = json.loads(day_result.stdout)
        self.assertEqual(day_payload["selected_range"]["label"], "2026-03-18")
        self.assertEqual(day_payload["selected_range"]["stats"], payload["selected_range"]["stats"])

    def test_json_year_selector_expands_monthly_rows_for_the_year(self) -> None:
        codex_home = self.make_fixture()
        result = self.run_cli("--json", "--codex-home", str(codex_home), "--now", "2026-03-19T10:00:00", "--year", "2026")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)

        self.assertEqual(payload["selected_range"]["label"], "2026")
        self.assertEqual(payload["selected_range"]["start_date"], "2026-01-01")
        self.assertEqual(payload["selected_range"]["end_date"], "2026-12-31")
        self.assertEqual(payload["selected_range"]["stats"]["prompts"], 3)
        self.assertEqual(len(payload["monthly_trend"]), 12)
        self.assertEqual(payload["monthly_trend"][0]["month"], "2026-01")
        self.assertEqual(payload["monthly_trend"][2]["month"], "2026-03")
        self.assertEqual(payload["monthly_trend"][2]["tokens"], 4030)
        self.assertEqual(payload["monthly_trend"][-1]["month"], "2026-12")

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

    def test_json_summary_works_with_history_only_codex_home(self) -> None:
        codex_home = self.make_fixture(include_sessions=False)
        result = self.run_cli("--json", "--codex-home", str(codex_home), "--now", "2026-03-19T10:00:00")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["summary"]["today"]["prompts"], 1)
        self.assertEqual(payload["summary"]["all_time"]["prompts"], 3)
        self.assertEqual(payload["summary"]["all_time"]["sessions"], 2)
        self.assertEqual(payload["summary"]["all_time"]["tokens"], 0)
        self.assertEqual(payload["summary"]["latest_model"], "unknown")

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
        self.assertIn("API COST SNAPSHOT", result.stdout)
        self.assertIn("API $", result.stdout)
        self.assertIn("Estimated API-equivalent spend only", result.stdout)
        self.assertIn("MODEL BREAKDOWN (30d)", result.stdout)
        self.assertIn("MODEL BREAKDOWN (all-time)", result.stdout)
        self.assertIn("RECENT ACTIVITY", result.stdout)
        self.assertIn("DAY-OF-WEEK PATTERN", result.stdout)
