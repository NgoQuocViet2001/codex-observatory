from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable, Sequence

from . import __version__

ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
DOW_NAMES = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
THEME = {
    "border": "38;5;240",
    "title": "1;38;5;51",
    "header": "1;38;5;117",
    "muted": "38;5;246",
    "accent": "38;5;81",
    "good": "38;5;121",
    "warn": "38;5;221",
    "hot": "38;5;214",
    "bar": "38;5;45",
    "dim": "38;5;244",
}
PRICING_VERIFIED_AT = "2026-03-29"
API_EQUIVALENT_NOTE = "Estimated API-equivalent spend only; Codex app or subscription billing may differ."
PRICING_SOURCES = [
    "https://openai.com/api/pricing/",
    "https://developers.openai.com/api/docs/models/gpt-5.4",
    "https://developers.openai.com/api/docs/models/gpt-5.3-codex",
    "https://developers.openai.com/api/docs/models/gpt-5.2-codex",
    "https://developers.openai.com/api/docs/models/gpt-5.1",
    "https://developers.openai.com/api/docs/models/gpt-5.1-codex",
    "https://developers.openai.com/api/docs/models/gpt-5.1-codex-max",
    "https://developers.openai.com/api/docs/models/gpt-5.1-codex-mini",
    "https://developers.openai.com/api/docs/models/gpt-5",
    "https://developers.openai.com/api/docs/models/gpt-5-mini",
    "https://developers.openai.com/api/docs/models/gpt-5-nano",
    "https://developers.openai.com/api/docs/models/gpt-5-codex",
    "https://developers.openai.com/api/docs/models/codex-mini-latest",
]


@dataclass(frozen=True)
class ModelPricing:
    input_usd_per_million: float
    cached_input_usd_per_million: float
    output_usd_per_million: float


MODEL_PRICING = {
    "codex-mini-latest": ModelPricing(1.50, 0.375, 6.00),
    "gpt-5": ModelPricing(1.25, 0.125, 10.00),
    "gpt-5-codex": ModelPricing(1.25, 0.125, 10.00),
    "gpt-5-mini": ModelPricing(0.25, 0.025, 2.00),
    "gpt-5-nano": ModelPricing(0.05, 0.005, 0.40),
    "gpt-5.1": ModelPricing(1.25, 0.125, 10.00),
    "gpt-5.1-codex": ModelPricing(1.25, 0.125, 10.00),
    "gpt-5.1-codex-max": ModelPricing(1.25, 0.125, 10.00),
    "gpt-5.1-codex-mini": ModelPricing(0.25, 0.025, 2.00),
    "gpt-5.2": ModelPricing(1.75, 0.175, 14.00),
    "gpt-5.2-codex": ModelPricing(1.75, 0.175, 14.00),
    "gpt-5.3-codex": ModelPricing(1.75, 0.175, 14.00),
    "gpt-5.4": ModelPricing(2.50, 0.25, 15.00),
    "gpt-5.4-mini": ModelPricing(0.75, 0.075, 4.50),
    "gpt-5.4-nano": ModelPricing(0.20, 0.02, 1.25),
}
MODEL_ALIASES = {
    "gpt-5 mini": "gpt-5-mini",
    "gpt-5 nano": "gpt-5-nano",
    "gpt-5.1 codex": "gpt-5.1-codex",
    "gpt-5.1 codex max": "gpt-5.1-codex-max",
    "gpt-5.1 codex mini": "gpt-5.1-codex-mini",
    "gpt-5.4 mini": "gpt-5.4-mini",
    "gpt-5.4 nano": "gpt-5.4-nano",
}


@dataclass(frozen=True)
class PromptEvent:
    timestamp: datetime
    session_id: str
    date_key: str
    month_key: str


@dataclass(frozen=True)
class TurnEvent:
    timestamp: datetime
    model: str


@dataclass(frozen=True)
class TokenEvent:
    timestamp: datetime
    date_key: str
    month_key: str
    hour: int
    dow: int
    model: str
    input_tokens: int
    cached_input_tokens: int
    output_tokens: int
    reasoning_output_tokens: int
    total_tokens: int


@dataclass
class PeriodStats:
    prompts: int
    sessions: int
    tokens: int


@dataclass
class DailyRow:
    date: str
    prompts: int
    sessions: int
    tokens: int
    cost_usd: float


@dataclass
class MonthlyRow:
    month: str
    prompts: int
    tokens: int
    cost_usd: float


@dataclass
class DOWRow:
    day: str
    prompts: int
    tokens: int
    cost_usd: float


@dataclass
class ModelStats:
    turns: int = 0
    input_tokens: int = 0
    cached_input_tokens: int = 0
    output_tokens: int = 0
    reasoning_output_tokens: int = 0
    total_tokens: int = 0
    input_cost_usd: float = 0.0
    cached_input_cost_usd: float = 0.0
    output_cost_usd: float = 0.0
    total_cost_usd: float = 0.0
    cache_savings_usd: float = 0.0
    pricing_model: str | None = None


@dataclass
class CostStats:
    input_cost_usd: float = 0.0
    cached_input_cost_usd: float = 0.0
    output_cost_usd: float = 0.0
    total_cost_usd: float = 0.0
    cache_savings_usd: float = 0.0
    priced_tokens: int = 0
    unpriced_tokens: int = 0


@dataclass
class Report:
    generated_at: datetime
    latest_prompt_time: datetime | None
    latest_token_time: datetime | None
    latest_model: str
    today: PeriodStats
    seven_days: PeriodStats
    thirty_days: PeriodStats
    all_time: PeriodStats
    active_days: int
    current_streak: int
    longest_streak: int
    avg_prompts_per_day: float
    avg_tokens_per_prompt: float
    cache_share_30d: float
    today_cost: CostStats
    seven_days_cost: CostStats
    thirty_days_cost: CostStats
    all_time_cost: CostStats
    pricing_verified_at: str
    pricing_scope_note: str
    unpriced_models: list[str]
    busiest_hour: int
    busiest_day: str
    top_prompt_day: str
    top_prompt_count: int
    top_token_day: str
    top_token_count: int
    top_model_30d: str
    heatmap_weeks: int
    heatmap_header: str
    heatmap_lines: list[str]
    model_30d: list[tuple[str, ModelStats]]
    model_all_time: list[tuple[str, ModelStats]]
    daily_rows: list[DailyRow]
    monthly_rows: list[MonthlyRow]
    dow_rows: list[DOWRow]


class Style:
    def __init__(self, use_color: bool) -> None:
        self.use_color = use_color

    def paint(self, text: str, theme_key: str | None) -> str:
        if not text or not theme_key or not self.use_color:
            return text
        code = THEME.get(theme_key)
        if not code:
            return text
        return f"\x1b[{code}m{text}\x1b[0m"


def configure_stdio() -> None:
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if stream is not None and hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass


def strip_ansi(text: str) -> str:
    return ANSI_RE.sub("", text or "")


def visible_length(text: str) -> int:
    return len(strip_ansi(text))


def format_cell(text: str, width: int, align: str = "left") -> str:
    text = text or ""
    if width <= 0:
        return ""
    visible = visible_length(text)
    if visible > width:
        plain = strip_ansi(text)
        text = plain if len(plain) <= width else plain[: width - 1] + "…"
        visible = visible_length(text)
    padding = " " * (width - visible)
    return f"{padding}{text}" if align == "right" else f"{text}{padding}"


def format_int(value: int | float) -> str:
    return f"{round(value):,}"


def format_short(value: int | float) -> str:
    value = float(value)
    abs_value = abs(value)
    if abs_value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f}B"
    if abs_value >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    if abs_value >= 1_000:
        return f"{value / 1_000:.1f}K"
    return f"{value:.0f}"


def format_usd(value: float) -> str:
    abs_value = abs(value)
    if abs_value == 0:
        return "$0.00"
    if abs_value >= 100:
        return f"${value:,.2f}"
    if abs_value >= 1:
        return f"${value:,.2f}"
    if abs_value >= 0.1:
        return f"${value:,.3f}"
    if abs_value >= 0.01:
        return f"${value:,.4f}"
    return f"${value:,.5f}"


def make_sparkline(values: Sequence[int]) -> str:
    chars = "▁▂▃▄▅▆▇█"
    if not values:
        return ""
    peak = max(values)
    if peak <= 0:
        return chars[0] * len(values)
    rendered: list[str] = []
    for value in values:
        index = round((value / peak) * (len(chars) - 1))
        index = max(0, min(len(chars) - 1, index))
        rendered.append(chars[index])
    return "".join(rendered)


def make_bar(value: int, peak: int, width: int = 20, style: Style | None = None) -> str:
    style = style or Style(False)
    if peak <= 0:
        return style.paint("░" * width, "dim")
    ratio = max(0.0, min(1.0, value / peak))
    filled = max(0, min(width, round(ratio * width)))
    theme = "bar"
    if ratio >= 0.85:
        theme = "hot"
    elif ratio >= 0.55:
        theme = "warn"
    elif ratio >= 0.25:
        theme = "accent"
    full = style.paint("█" * filled, theme) if filled else ""
    empty = style.paint("░" * (width - filled), "dim") if filled < width else ""
    return full + empty


def heat_cell(count: int, peak: int, style: Style) -> str:
    if count <= 0 or peak <= 0:
        return style.paint("·", "dim")
    level = max(1, min(4, int((count / peak) * 4 + 0.9999)))
    if level == 1:
        return style.paint("░", "bar")
    if level == 2:
        return style.paint("▒", "accent")
    if level == 3:
        return style.paint("▓", "warn")
    return style.paint("█", "hot")


def relative_age(timestamp: datetime | None, now: datetime) -> str:
    if timestamp is None:
        return "n/a"
    delta = now - timestamp
    if delta.total_seconds() < 60:
        return "just now"
    if delta.total_seconds() < 3600:
        return f"{int(delta.total_seconds() // 60)}m ago"
    if delta.total_seconds() < 86400:
        return f"{int(delta.total_seconds() // 3600)}h ago"
    return f"{delta.days}d ago"


def parse_local_time(value: str) -> datetime:
    raw = value.strip()
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    dt = datetime.fromisoformat(raw)
    if dt.tzinfo is not None:
        return dt.astimezone().replace(tzinfo=None)
    return dt


def from_unix_seconds(value: int | str) -> datetime:
    return datetime.fromtimestamp(int(value), tz=timezone.utc).astimezone().replace(tzinfo=None)


def has_supported_codex_data(path: Path) -> bool:
    return (path / "history.jsonl").exists() or (path / "session_index.jsonl").exists() or (path / "sessions").exists()


def resolve_codex_home(path_value: str | None) -> Path:
    candidate = Path(path_value or "~/.codex").expanduser()
    if has_supported_codex_data(candidate):
        return candidate
    nested = candidate / ".codex"
    if has_supported_codex_data(nested):
        return nested
    return candidate


def read_jsonl_lines(path: Path) -> list[str]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", errors="ignore") as handle:
        return [line.rstrip("\n") for line in handle]


def load_history(codex_home: Path) -> tuple[list[PromptEvent], datetime | None]:
    history_path = codex_home / "history.jsonl"
    if not history_path.exists():
        raise FileNotFoundError(f"Missing history file: {history_path}")
    events: list[PromptEvent] = []
    latest_prompt_time: datetime | None = None
    for line in read_jsonl_lines(history_path):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
            timestamp = from_unix_seconds(item["ts"])
            session_id = str(item["session_id"])
        except Exception:
            continue
        events.append(
            PromptEvent(
                timestamp=timestamp,
                session_id=session_id,
                date_key=timestamp.strftime("%Y-%m-%d"),
                month_key=timestamp.strftime("%Y-%m"),
            )
        )
        if latest_prompt_time is None or timestamp > latest_prompt_time:
            latest_prompt_time = timestamp
    return events, latest_prompt_time


def parse_timestamp_or_fallback(raw_value: object, fallback: datetime) -> datetime:
    if raw_value:
        try:
            return parse_local_time(str(raw_value))
        except Exception:
            pass
    return fallback


def response_item_user_text(payload: dict) -> str:
    parts: list[str] = []
    for part in payload.get("content") or []:
        if not isinstance(part, dict):
            continue
        text = part.get("text")
        if isinstance(text, str) and text.strip():
            parts.append(text)
    return "\n".join(parts).strip()


def is_environment_context_prompt(text: str) -> bool:
    return text.lstrip().startswith("<environment_context>")


def load_history_from_sessions(codex_home: Path) -> tuple[list[PromptEvent], datetime | None]:
    sessions_root = codex_home / "sessions"
    if not sessions_root.exists():
        return [], None

    events: list[PromptEvent] = []
    latest_prompt_time: datetime | None = None

    for session_file in sorted(sessions_root.rglob("*.jsonl")):
        session_id = session_file.stem
        fallback_time = datetime.fromtimestamp(session_file.stat().st_mtime).replace(microsecond=0)
        explicit_prompt_events: list[PromptEvent] = []
        fallback_prompt_events: list[PromptEvent] = []

        for line in read_jsonl_lines(session_file):
            if not line.strip():
                continue
            try:
                item = json.loads(line)
            except Exception:
                continue

            payload = item.get("payload") or {}
            if item.get("type") == "session_meta":
                session_id = str(payload.get("id") or session_id)
                continue

            timestamp = parse_timestamp_or_fallback(item.get("timestamp"), fallback_time)

            if item.get("type") == "event_msg" and payload.get("type") == "user_message":
                message = str(payload.get("message") or "").strip()
                if not message:
                    continue
                explicit_prompt_events.append(
                    PromptEvent(
                        timestamp=timestamp,
                        session_id=session_id,
                        date_key=timestamp.strftime("%Y-%m-%d"),
                        month_key=timestamp.strftime("%Y-%m"),
                    )
                )
                continue

            if item.get("type") == "response_item" and payload.get("type") == "message" and payload.get("role") == "user":
                prompt_text = response_item_user_text(payload)
                if not prompt_text or is_environment_context_prompt(prompt_text):
                    continue
                fallback_prompt_events.append(
                    PromptEvent(
                        timestamp=timestamp,
                        session_id=session_id,
                        date_key=timestamp.strftime("%Y-%m-%d"),
                        month_key=timestamp.strftime("%Y-%m"),
                    )
                )

        session_events = explicit_prompt_events or fallback_prompt_events
        events.extend(session_events)
        if session_events:
            session_latest = max(event.timestamp for event in session_events)
            if latest_prompt_time is None or session_latest > latest_prompt_time:
                latest_prompt_time = session_latest

    events.sort(key=lambda event: (event.timestamp, event.session_id))
    return events, latest_prompt_time


def load_prompt_history(
    codex_home: Path,
    *,
    status: Callable[[str], None] | None = None,
) -> tuple[list[PromptEvent], datetime | None]:
    history_path = codex_home / "history.jsonl"
    if history_path.exists():
        if status:
            status("Reading prompt history...")
        return load_history(codex_home)
    if status:
        status("Reconstructing prompt history from session logs...")
    return load_history_from_sessions(codex_home)


def load_sessions(codex_home: Path) -> tuple[list[TurnEvent], list[TokenEvent], datetime | None, str]:
    sessions_root = codex_home / "sessions"
    if not sessions_root.exists():
        raise FileNotFoundError(f"Missing sessions directory: {sessions_root}")

    turn_events: list[TurnEvent] = []
    token_events: list[TokenEvent] = []
    latest_token_time: datetime | None = None
    latest_turn_time: datetime | None = None
    latest_model = "unknown"

    for session_file in sorted(sessions_root.rglob("*.jsonl")):
        current_model = "unknown"
        prev_input = prev_cached = prev_output = prev_reasoning = prev_total = 0
        fallback_time = datetime.fromtimestamp(session_file.stat().st_mtime).replace(microsecond=0)

        for line in read_jsonl_lines(session_file):
            if not line.strip():
                continue
            try:
                item = json.loads(line)
            except Exception:
                continue

            timestamp = fallback_time
            raw_timestamp = item.get("timestamp")
            if raw_timestamp:
                try:
                    timestamp = parse_local_time(str(raw_timestamp))
                except Exception:
                    timestamp = fallback_time

            payload = item.get("payload") or {}
            if item.get("type") == "turn_context":
                current_model = str(payload.get("model") or current_model)
                turn_events.append(TurnEvent(timestamp=timestamp, model=current_model))
                if latest_turn_time is None or timestamp > latest_turn_time:
                    latest_turn_time = timestamp
                    latest_model = current_model
                continue

            if item.get("type") != "event_msg" or payload.get("type") != "token_count":
                continue

            info = payload.get("info") or {}
            usage = info.get("total_token_usage") or {}
            current_input = int(usage.get("input_tokens") or 0)
            current_cached = int(usage.get("cached_input_tokens") or 0)
            current_output = int(usage.get("output_tokens") or 0)
            current_reasoning = int(usage.get("reasoning_output_tokens") or 0)
            current_total = int(usage.get("total_tokens") or 0)

            delta_input = current_input - prev_input
            delta_cached = current_cached - prev_cached
            delta_output = current_output - prev_output
            delta_reasoning = current_reasoning - prev_reasoning
            delta_total = current_total - prev_total

            if delta_input < 0:
                delta_input = current_input
            if delta_cached < 0:
                delta_cached = current_cached
            if delta_output < 0:
                delta_output = current_output
            if delta_reasoning < 0:
                delta_reasoning = current_reasoning
            if delta_total < 0:
                delta_total = current_total

            prev_input = current_input
            prev_cached = current_cached
            prev_output = current_output
            prev_reasoning = current_reasoning
            prev_total = current_total

            if not any((delta_input, delta_cached, delta_output, delta_reasoning, delta_total)):
                continue

            token_events.append(
                TokenEvent(
                    timestamp=timestamp,
                    date_key=timestamp.strftime("%Y-%m-%d"),
                    month_key=timestamp.strftime("%Y-%m"),
                    hour=timestamp.hour,
                    dow=(timestamp.weekday() + 1) if timestamp.weekday() < 6 else 0,
                    model=current_model,
                    input_tokens=delta_input,
                    cached_input_tokens=delta_cached,
                    output_tokens=delta_output,
                    reasoning_output_tokens=delta_reasoning,
                    total_tokens=delta_total,
                )
            )
            if latest_token_time is None or timestamp > latest_token_time:
                latest_token_time = timestamp

    return turn_events, token_events, latest_token_time, latest_model


def get_period_stats(prompts: Sequence[PromptEvent], tokens: Sequence[TokenEvent], start: datetime) -> PeriodStats:
    prompt_slice = [event for event in prompts if event.timestamp >= start]
    return PeriodStats(
        prompts=len(prompt_slice),
        sessions=len({event.session_id for event in prompt_slice}),
        tokens=sum(event.total_tokens for event in tokens if event.timestamp >= start),
    )


def resolve_view(requested_view: str, width: int) -> str:
    if requested_view != "smart":
        return requested_view
    if width >= 145:
        return "full"
    if width >= 110:
        return "normal"
    return "compact"


def add_months(year: int, month: int, delta: int) -> tuple[int, int]:
    zero_based = year * 12 + (month - 1) + delta
    new_year, month_index = divmod(zero_based, 12)
    return new_year, month_index + 1


def normalize_model_name(model: str) -> str:
    normalized = str(model or "unknown").strip().lower()
    return MODEL_ALIASES.get(normalized, normalized)


def resolve_model_pricing(model: str) -> tuple[str | None, ModelPricing | None]:
    normalized = normalize_model_name(model)
    pricing = MODEL_PRICING.get(normalized)
    if pricing is not None:
        return normalized, pricing
    for canonical in sorted(MODEL_PRICING, key=len, reverse=True):
        if normalized.startswith(f"{canonical}-"):
            return canonical, MODEL_PRICING[canonical]
    return None, None


def estimate_token_costs(input_tokens: int, cached_input_tokens: int, output_tokens: int, pricing: ModelPricing) -> tuple[float, float, float, float, float]:
    billed_cached_input = max(0, min(cached_input_tokens, input_tokens))
    billed_uncached_input = max(0, input_tokens - billed_cached_input)
    input_cost = billed_uncached_input / 1_000_000 * pricing.input_usd_per_million
    cached_input_cost = billed_cached_input / 1_000_000 * pricing.cached_input_usd_per_million
    output_cost = output_tokens / 1_000_000 * pricing.output_usd_per_million
    total_cost = input_cost + cached_input_cost + output_cost
    cache_savings = billed_cached_input / 1_000_000 * (pricing.input_usd_per_million - pricing.cached_input_usd_per_million)
    return input_cost, cached_input_cost, output_cost, total_cost, cache_savings


def apply_model_pricing(model_name: str, stats: ModelStats) -> bool:
    pricing_model, pricing = resolve_model_pricing(model_name)
    stats.pricing_model = pricing_model
    if pricing is None:
        return False
    (
        stats.input_cost_usd,
        stats.cached_input_cost_usd,
        stats.output_cost_usd,
        stats.total_cost_usd,
        stats.cache_savings_usd,
    ) = estimate_token_costs(stats.input_tokens, stats.cached_input_tokens, stats.output_tokens, pricing)
    return True


def summarize_costs(tokens: Sequence[TokenEvent], *, start: datetime | None = None) -> CostStats:
    out = CostStats()
    for event in tokens:
        if start is not None and event.timestamp < start:
            continue
        _pricing_model, pricing = resolve_model_pricing(event.model)
        if pricing is None:
            out.unpriced_tokens += event.total_tokens
            continue
        input_cost, cached_input_cost, output_cost, total_cost, cache_savings = estimate_token_costs(
            event.input_tokens,
            event.cached_input_tokens,
            event.output_tokens,
            pricing,
        )
        out.input_cost_usd += input_cost
        out.cached_input_cost_usd += cached_input_cost
        out.output_cost_usd += output_cost
        out.total_cost_usd += total_cost
        out.cache_savings_usd += cache_savings
        out.priced_tokens += event.total_tokens
    return out


def cost_coverage(cost: CostStats) -> float:
    total_tokens = cost.priced_tokens + cost.unpriced_tokens
    return (cost.priced_tokens / total_tokens * 100.0) if total_tokens else 100.0


def estimate_event_cost_total(event: TokenEvent) -> float:
    _pricing_model, pricing = resolve_model_pricing(event.model)
    if pricing is None:
        return 0.0
    _input_cost, _cached_input_cost, _output_cost, total_cost, _cache_savings = estimate_token_costs(
        event.input_tokens,
        event.cached_input_tokens,
        event.output_tokens,
        pricing,
    )
    return total_cost


def build_report(
    codex_home: Path,
    *,
    now: datetime,
    daily_days: int,
    monthly_months: int,
    heatmap_weeks: int,
    top_models: int,
    status: Callable[[str], None] | None = None,
) -> Report:
    prompt_events, latest_prompt_time = load_prompt_history(codex_home, status=status)
    history_path = codex_home / "history.jsonl"
    sessions_root = codex_home / "sessions"
    if status:
        status("Scanning session logs...")
    if sessions_root.exists():
        turn_events, token_events, latest_token_time, latest_model = load_sessions(codex_home)
    elif history_path.exists():
        turn_events, token_events, latest_token_time, latest_model = [], [], None, "unknown"
        if status:
            status("Session logs not found; using history.jsonl only for prompt/session counts...")
    else:
        raise FileNotFoundError(f"Missing sessions directory: {sessions_root}")
    if status:
        status("Aggregating trends and model usage...")

    prompt_by_date = Counter(event.date_key for event in prompt_events)
    prompt_by_month = Counter(event.month_key for event in prompt_events)
    prompt_by_hour = [0] * 24
    prompt_by_dow = [0] * 7
    sessions_by_date: dict[str, set[str]] = {}
    for event in prompt_events:
        prompt_by_hour[event.timestamp.hour] += 1
        prompt_by_dow[(event.timestamp.weekday() + 1) if event.timestamp.weekday() < 6 else 0] += 1
        sessions_by_date.setdefault(event.date_key, set()).add(event.session_id)

    token_by_date = Counter()
    token_by_month = Counter()
    token_by_dow = [0] * 7
    cost_by_date: dict[str, float] = {}
    cost_by_month: dict[str, float] = {}
    cost_by_dow = [0.0] * 7
    for event in token_events:
        token_by_date[event.date_key] += event.total_tokens
        token_by_month[event.month_key] += event.total_tokens
        token_by_dow[event.dow] += event.total_tokens
        event_cost = estimate_event_cost_total(event)
        cost_by_date[event.date_key] = cost_by_date.get(event.date_key, 0.0) + event_cost
        cost_by_month[event.month_key] = cost_by_month.get(event.month_key, 0.0) + event_cost
        cost_by_dow[event.dow] += event_cost

    today_start = datetime(now.year, now.month, now.day)
    stats_today = get_period_stats(prompt_events, token_events, today_start)
    stats_7d = get_period_stats(prompt_events, token_events, today_start - timedelta(days=6))
    stats_30d = get_period_stats(prompt_events, token_events, today_start - timedelta(days=29))
    all_time = PeriodStats(
        prompts=len(prompt_events),
        sessions=len({event.session_id for event in prompt_events}),
        tokens=sum(event.total_tokens for event in token_events),
    )

    first_prompt_date = min((event.timestamp.date() for event in prompt_events), default=today_start.date())
    usage_span_days = max(1, (today_start.date() - first_prompt_date).days + 1)
    active_days = len(prompt_by_date)
    avg_prompts_per_day = all_time.prompts / usage_span_days if usage_span_days else 0.0
    avg_tokens_per_prompt = all_time.tokens / all_time.prompts if all_time.prompts else 0.0

    current_streak = 0
    for offset in range(usage_span_days):
        key = (today_start.date() - timedelta(days=offset)).strftime("%Y-%m-%d")
        if key in prompt_by_date:
            current_streak += 1
        else:
            break

    longest_streak = 0
    previous_day = None
    running = 0
    for date_key in sorted(prompt_by_date):
        current_day = datetime.strptime(date_key, "%Y-%m-%d").date()
        if previous_day is not None and (current_day - previous_day).days == 1:
            running += 1
        else:
            running = 1
        longest_streak = max(longest_streak, running)
        previous_day = current_day

    top_prompt_day = "n/a"
    top_prompt_count = 0
    if prompt_by_date:
        top_prompt_day, top_prompt_count = sorted(prompt_by_date.items(), key=lambda item: (-item[1], item[0]))[0]

    top_token_day = "n/a"
    top_token_count = 0
    if token_by_date:
        top_token_day, top_token_count = sorted(token_by_date.items(), key=lambda item: (-item[1], item[0]))[0]

    busiest_hour = max(range(24), key=lambda hour: (prompt_by_hour[hour], -hour))
    busiest_dow_index = max(range(7), key=lambda index: (prompt_by_dow[index], -index))
    busiest_day = DOW_NAMES[busiest_dow_index]

    model_all_time: dict[str, ModelStats] = {}
    for event in turn_events:
        model_all_time.setdefault(event.model, ModelStats()).turns += 1
    for event in token_events:
        stats = model_all_time.setdefault(event.model, ModelStats())
        stats.input_tokens += event.input_tokens
        stats.cached_input_tokens += event.cached_input_tokens
        stats.output_tokens += event.output_tokens
        stats.reasoning_output_tokens += event.reasoning_output_tokens
        stats.total_tokens += event.total_tokens

    model_30d: dict[str, ModelStats] = {name: ModelStats() for name in model_all_time}
    window_start = today_start - timedelta(days=29)
    for event in turn_events:
        if event.timestamp >= window_start:
            model_30d.setdefault(event.model, ModelStats()).turns += 1
    for event in token_events:
        if event.timestamp >= window_start:
            stats = model_30d.setdefault(event.model, ModelStats())
            stats.input_tokens += event.input_tokens
            stats.cached_input_tokens += event.cached_input_tokens
            stats.output_tokens += event.output_tokens
            stats.reasoning_output_tokens += event.reasoning_output_tokens
            stats.total_tokens += event.total_tokens

    for name, stats in model_all_time.items():
        apply_model_pricing(name, stats)
    for name, stats in model_30d.items():
        apply_model_pricing(name, stats)

    today_cost = summarize_costs(token_events, start=today_start)
    seven_days_cost = summarize_costs(token_events, start=today_start - timedelta(days=6))
    thirty_days_cost = summarize_costs(token_events, start=window_start)
    all_time_cost = summarize_costs(token_events)

    total_30_input = sum(stats.input_tokens for stats in model_30d.values())
    total_30_cached = sum(stats.cached_input_tokens for stats in model_30d.values())
    cache_share_30d = (total_30_cached / total_30_input * 100.0) if total_30_input else 0.0
    sorted_model_30d = sorted(
        ((name, stats) for name, stats in model_30d.items() if stats.turns or stats.total_tokens),
        key=lambda item: (-item[1].total_tokens, item[0]),
    )[:top_models]
    sorted_model_all = sorted(
        ((name, stats) for name, stats in model_all_time.items() if stats.turns or stats.total_tokens),
        key=lambda item: (-item[1].total_tokens, item[0]),
    )[:top_models]
    top_model_30d = sorted_model_30d[0][0] if sorted_model_30d else "n/a"
    unpriced_models = sorted(
        name for name, stats in model_all_time.items() if stats.total_tokens and stats.pricing_model is None
    )

    daily_rows: list[DailyRow] = []
    for offset in range(daily_days - 1, -1, -1):
        day = today_start.date() - timedelta(days=offset)
        key = day.strftime("%Y-%m-%d")
        daily_rows.append(
            DailyRow(
                date=day.strftime("%m-%d"),
                prompts=prompt_by_date.get(key, 0),
                sessions=len(sessions_by_date.get(key, set())),
                tokens=token_by_date.get(key, 0),
                cost_usd=cost_by_date.get(key, 0.0),
            )
        )

    monthly_rows: list[MonthlyRow] = []
    for offset in range(monthly_months - 1, -1, -1):
        year, month = add_months(today_start.year, today_start.month, -offset)
        key = f"{year:04d}-{month:02d}"
        monthly_rows.append(
            MonthlyRow(
                month=key,
                prompts=prompt_by_month.get(key, 0),
                tokens=token_by_month.get(key, 0),
                cost_usd=cost_by_month.get(key, 0.0),
            )
        )

    heat_start = today_start.date() - timedelta(days=heatmap_weeks * 7 - 1)
    while heat_start.weekday() != 0:
        heat_start -= timedelta(days=1)
    peak = 0
    for column in range(heatmap_weeks):
        for row in range(7):
            day = heat_start + timedelta(days=column * 7 + row)
            if day > today_start.date():
                continue
            peak = max(peak, prompt_by_date.get(day.strftime("%Y-%m-%d"), 0))
    heat_header = "     "
    for column in range(heatmap_weeks):
        week_start = heat_start + timedelta(days=column * 7)
        heat_header += week_start.strftime("%m") if week_start.day <= 7 else "  "
    heat_lines: list[str] = []
    raw_style = Style(False)
    for row_index, label in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
        cells = []
        for column in range(heatmap_weeks):
            day = heat_start + timedelta(days=column * 7 + row_index)
            if day > today_start.date():
                cells.append(" ")
                continue
            count = prompt_by_date.get(day.strftime("%Y-%m-%d"), 0)
            cells.append(heat_cell(count, peak, raw_style))
        heat_lines.append(f"{label:<3}  {''.join(cells)}")

    dow_rows = [
        DOWRow(
            day=DOW_NAMES[index],
            prompts=prompt_by_dow[index],
            tokens=token_by_dow[index],
            cost_usd=cost_by_dow[index],
        )
        for index in range(7)
    ]

    return Report(
        generated_at=now,
        latest_prompt_time=latest_prompt_time,
        latest_token_time=latest_token_time,
        latest_model=latest_model,
        today=stats_today,
        seven_days=stats_7d,
        thirty_days=stats_30d,
        all_time=all_time,
        active_days=active_days,
        current_streak=current_streak,
        longest_streak=longest_streak,
        avg_prompts_per_day=avg_prompts_per_day,
        avg_tokens_per_prompt=avg_tokens_per_prompt,
        cache_share_30d=cache_share_30d,
        today_cost=today_cost,
        seven_days_cost=seven_days_cost,
        thirty_days_cost=thirty_days_cost,
        all_time_cost=all_time_cost,
        pricing_verified_at=PRICING_VERIFIED_AT,
        pricing_scope_note=API_EQUIVALENT_NOTE,
        unpriced_models=unpriced_models,
        busiest_hour=busiest_hour,
        busiest_day=busiest_day,
        top_prompt_day=top_prompt_day,
        top_prompt_count=top_prompt_count,
        top_token_day=top_token_day,
        top_token_count=top_token_count,
        top_model_30d=top_model_30d,
        heatmap_weeks=heatmap_weeks,
        heatmap_header=heat_header,
        heatmap_lines=heat_lines,
        model_30d=sorted_model_30d,
        model_all_time=sorted_model_all,
        daily_rows=daily_rows,
        monthly_rows=monthly_rows,
        dow_rows=dow_rows,
    )


def table_border(widths: Sequence[int], left: str, middle: str, right: str) -> str:
    return left + middle.join("─" * (width + 2) for width in widths) + right


def render_table_row(
    cells: Sequence[str],
    widths: Sequence[int],
    aligns: Sequence[str],
    style: Style,
    cell_theme: str | None = None,
) -> str:
    separator = style.paint("│", "border")
    rendered: list[str] = []
    for index, width in enumerate(widths):
        cell = cells[index] if index < len(cells) else ""
        align = aligns[index] if index < len(aligns) else "left"
        if cell_theme:
            cell = style.paint(cell, cell_theme)
        rendered.append(f" {format_cell(cell, width, align)} ")
    return separator + separator.join(rendered) + separator


def render_table_box(
    title: str,
    headers: Sequence[str],
    rows: Sequence[Sequence[str]],
    widths: Sequence[int],
    aligns: Sequence[str],
    style: Style,
    row_themes: Sequence[str | None] | None = None,
) -> list[str]:
    lines = [style.paint(title, "title")]
    lines.append(style.paint(table_border(widths, "┌", "┬", "┐"), "border"))
    lines.append(render_table_row(headers, widths, aligns, style, cell_theme="header"))
    lines.append(style.paint(table_border(widths, "├", "┼", "┤"), "border"))
    for index, row in enumerate(rows):
        theme = row_themes[index] if row_themes and index < len(row_themes) else None
        lines.append(render_table_row(row, widths, aligns, style, cell_theme=theme))
    lines.append(style.paint(table_border(widths, "└", "┴", "┘"), "border"))
    lines.append("")
    return lines


def render_panel(title: str, rows: Sequence[str], style: Style, max_width: int) -> list[str]:
    content_width = max((visible_length(row) for row in rows), default=24)
    panel_width = min(max_width, max(28, content_width + 4))
    lines = [style.paint(title, "title"), style.paint("┌" + "─" * (panel_width - 2) + "┐", "border")]
    for row in rows:
        content = format_cell(row, panel_width - 4)
        lines.append(f"{style.paint('│', 'border')} {content} {style.paint('│', 'border')}")
    lines.append(style.paint("└" + "─" * (panel_width - 2) + "┘", "border"))
    lines.append("")
    return lines


def ranked_themes(count: int) -> list[str | None]:
    out: list[str | None] = []
    for index in range(count):
        if index == 0:
            out.append("good")
        elif index == 1:
            out.append("accent")
        elif index == 2:
            out.append("warn")
        else:
            out.append(None)
    return out


def to_json_dict(report: Report, codex_home: Path) -> dict:
    return {
        "generated_at": report.generated_at.isoformat(),
        "codex_home": str(codex_home),
        "summary": {
            "today": asdict(report.today),
            "seven_days": asdict(report.seven_days),
            "thirty_days": asdict(report.thirty_days),
            "all_time": asdict(report.all_time),
            "active_days": report.active_days,
            "current_streak": report.current_streak,
            "longest_streak": report.longest_streak,
            "avg_prompts_per_day": report.avg_prompts_per_day,
            "avg_tokens_per_prompt": report.avg_tokens_per_prompt,
            "cache_share_30d": report.cache_share_30d,
            "latest_model": report.latest_model,
            "busiest_hour": report.busiest_hour,
            "busiest_day": report.busiest_day,
            "top_prompt_day": {"date": report.top_prompt_day, "count": report.top_prompt_count},
            "top_token_day": {"date": report.top_token_day, "tokens": report.top_token_count},
            "top_model_30d": report.top_model_30d,
        },
        "pricing": {
            "verified_at": report.pricing_verified_at,
            "scope_note": report.pricing_scope_note,
            "sources": PRICING_SOURCES,
            "unpriced_models": report.unpriced_models,
        },
        "costs": {
            "today": asdict(report.today_cost),
            "seven_days": asdict(report.seven_days_cost),
            "thirty_days": asdict(report.thirty_days_cost),
            "all_time": asdict(report.all_time_cost),
            "coverage_pct": {
                "today": cost_coverage(report.today_cost),
                "seven_days": cost_coverage(report.seven_days_cost),
                "thirty_days": cost_coverage(report.thirty_days_cost),
                "all_time": cost_coverage(report.all_time_cost),
            },
        },
        "models_30d": [{"model": name, **asdict(stats)} for name, stats in report.model_30d],
        "models_all_time": [{"model": name, **asdict(stats)} for name, stats in report.model_all_time],
        "recent_activity": [asdict(row) for row in report.daily_rows],
        "monthly_trend": [asdict(row) for row in report.monthly_rows],
        "day_of_week": [asdict(row) for row in report.dow_rows],
    }


def render_report(report: Report, *, view: str, width: int, use_color: bool) -> str:
    style = Style(use_color)
    target_width = {"compact": 100, "normal": 122, "full": 140}[view]
    layout_width = min(target_width, max(80, width))
    lines: list[str] = []

    top = style.paint("┌" + "─" * (layout_width - 2) + "┐", "border")
    mid = style.paint("├" + "─" * (layout_width - 2) + "┤", "border")
    bottom = style.paint("└" + "─" * (layout_width - 2) + "┘", "border")

    def add_summary(text: str) -> None:
        content = format_cell(text, layout_width - 4)
        lines.append(f"{style.paint('│', 'border')} {content} {style.paint('│', 'border')}")

    lines.append(top)
    add_summary(style.paint("CODEX STATS", "title"))
    lines.append(mid)
    add_summary(style.paint("Live local usage from Codex history/session logs under ~/.codex", "muted"))
    add_summary(
        style.paint(
            f"Updated: {report.generated_at:%Y-%m-%d %H:%M:%S} | "
            f"Last prompt: {relative_age(report.latest_prompt_time, report.generated_at)} | "
            f"Last token: {relative_age(report.latest_token_time, report.generated_at)}",
            "dim",
        )
    )
    add_summary(
        style.paint(
            f"Today P:{format_int(report.today.prompts)} S:{format_int(report.today.sessions)} T:{format_short(report.today.tokens)} API {format_usd(report.today_cost.total_cost_usd)}",
            "accent",
        )
        + style.paint("   |   ", "border")
        + style.paint(
            f"7d P:{format_int(report.seven_days.prompts)} S:{format_int(report.seven_days.sessions)} T:{format_short(report.seven_days.tokens)} API {format_usd(report.seven_days_cost.total_cost_usd)}",
            "good",
        )
    )
    add_summary(
        style.paint(
            f"30d P:{format_int(report.thirty_days.prompts)} S:{format_int(report.thirty_days.sessions)} T:{format_short(report.thirty_days.tokens)} API {format_usd(report.thirty_days_cost.total_cost_usd)}",
            "warn",
        )
        + style.paint("   |   ", "border")
        + style.paint(
            f"All-time P:{format_int(report.all_time.prompts)} S:{format_int(report.all_time.sessions)} T:{format_short(report.all_time.tokens)} API {format_usd(report.all_time_cost.total_cost_usd)}",
            "header",
        )
    )
    add_summary(
        style.paint(f"Active days: {report.active_days}", "good")
        + style.paint(" | ", "border")
        + style.paint(f"Streak: {report.current_streak}d / best {report.longest_streak}d", "accent")
        + style.paint(" | ", "border")
        + style.paint(f"Avg prompts/day: {report.avg_prompts_per_day:.2f}", "warn")
        + style.paint(" | ", "border")
        + style.paint(f"Avg tokens/prompt: {report.avg_tokens_per_prompt:,.1f}", "header")
    )
    add_summary(
        style.paint(f"Latest model: {report.latest_model}", "accent")
        + style.paint(" | ", "border")
        + style.paint(f"30d cache share: {report.cache_share_30d:.1f}%", "good")
        + style.paint(" | ", "border")
        + style.paint(f"30d cache savings: {format_usd(report.thirty_days_cost.cache_savings_usd)}", "good")
        + style.paint(" | ", "border")
        + style.paint(f"Cost coverage: {cost_coverage(report.all_time_cost):.1f}%", "accent")
    )
    add_summary(
        style.paint(f"Busiest hour: {report.busiest_hour:02d}:00", "warn")
        + style.paint(" | ", "border")
        + style.paint(f"Busiest day: {report.busiest_day}", "header")
    )
    add_summary(
        style.paint(f"Top prompt day: {report.top_prompt_day} ({format_int(report.top_prompt_count)})", "accent")
        + style.paint(" | ", "border")
        + style.paint(f"Top token day: {report.top_token_day} ({format_short(report.top_token_count)})", "hot")
        + style.paint(" | ", "border")
        + style.paint(f"Top 30d model: {report.top_model_30d}", "good")
    )
    lines.append(bottom)
    lines.append("")

    cost_rows = [
        style.paint(report.pricing_scope_note, "muted"),
        style.paint(f"Today estimated API spend: {format_usd(report.today_cost.total_cost_usd)}", "accent"),
        style.paint(f"7d estimated API spend: {format_usd(report.seven_days_cost.total_cost_usd)}", "good"),
        style.paint(f"30d estimated API spend: {format_usd(report.thirty_days_cost.total_cost_usd)}", "warn"),
        style.paint(f"All-time estimated API spend: {format_usd(report.all_time_cost.total_cost_usd)}", "header"),
        style.paint(
            "30d API cost mix: "
            f"in {format_usd(report.thirty_days_cost.input_cost_usd)}"
            f" | cache {format_usd(report.thirty_days_cost.cached_input_cost_usd)}"
            f" | out {format_usd(report.thirty_days_cost.output_cost_usd)}",
            "dim",
        ),
        style.paint(f"30d cache savings vs uncached input: {format_usd(report.thirty_days_cost.cache_savings_usd)}", "good"),
        style.paint(f"Pricing coverage: {cost_coverage(report.all_time_cost):.1f}% of all-time tokens", "accent"),
        style.paint(f"Pricing verified: {report.pricing_verified_at}", "dim"),
    ]
    if report.unpriced_models:
        preview = ", ".join(report.unpriced_models[:3])
        if len(report.unpriced_models) > 3:
            preview += f" (+{len(report.unpriced_models) - 3} more)"
        cost_rows.append(style.paint(f"Unpriced models: {preview}", "warn"))
    lines.extend(render_panel("API COST SNAPSHOT", cost_rows, style, layout_width))

    heat_rows = [style.paint(report.heatmap_header, "dim")]
    for raw_row in report.heatmap_lines:
        label, cells = raw_row[:3], raw_row[5:]
        rendered_cells: list[str] = []
        for cell in cells:
            theme = None
            if cell == "·":
                theme = "dim"
            elif cell == "░":
                theme = "bar"
            elif cell == "▒":
                theme = "accent"
            elif cell == "▓":
                theme = "warn"
            elif cell == "█":
                theme = "hot"
            rendered_cells.append(style.paint(cell, theme))
        heat_rows.append(style.paint(label, "header") + "  " + "".join(rendered_cells))
    heat_rows.append(
        style.paint("Legend:", "dim")
        + " "
        + style.paint("idle", "dim")
        + " "
        + style.paint("·", "dim")
        + "  "
        + style.paint("light", "bar")
        + " "
        + style.paint("░", "bar")
        + "  "
        + style.paint("medium", "accent")
        + " "
        + style.paint("▒", "accent")
        + "  "
        + style.paint("busy", "warn")
        + " "
        + style.paint("▓", "warn")
        + "  "
        + style.paint("peak", "hot")
        + " "
        + style.paint("█", "hot")
    )
    lines.extend(render_panel(f"HEATMAP (prompts, last {report.heatmap_weeks} weeks)", heat_rows, style, layout_width))

    total_30_tokens = sum(stats.total_tokens for _, stats in report.model_30d) or 1
    lines.extend(
        render_table_box(
            "MODEL BREAKDOWN (30d)",
            ["Model", "Turns", "Tokens", "API $", "Share", "Cache"],
            [
                [
                    name,
                    format_int(stats.turns),
                    format_short(stats.total_tokens),
                    format_usd(stats.total_cost_usd) if stats.pricing_model else "n/a",
                    f"{(stats.total_tokens / total_30_tokens) * 100:.1f}%",
                    f"{(stats.cached_input_tokens / stats.input_tokens * 100) if stats.input_tokens else 0.0:.1f}%",
                ]
                for name, stats in report.model_30d
            ],
            [28, 9, 10, 10, 8, 8],
            ["left", "right", "right", "right", "right", "right"],
            style,
            ranked_themes(len(report.model_30d)),
        )
    )

    if view in {"normal", "full"}:
        peak_daily_tokens = max((row.tokens for row in report.daily_rows), default=0)
        lines.extend(
            render_table_box(
                f"RECENT ACTIVITY ({len(report.daily_rows)} days)",
                ["Date", "Prompts", "Sessions", "Tokens", "API $", "Load"],
                [
                    [
                        style.paint(row.date, "good") if row is report.daily_rows[-1] else row.date,
                        format_int(row.prompts),
                        format_int(row.sessions),
                        format_short(row.tokens),
                        format_usd(row.cost_usd),
                        make_bar(row.tokens, peak_daily_tokens, 20, style),
                    ]
                    for row in report.daily_rows
                ],
                [10, 9, 10, 11, 10, 20],
                ["left", "right", "right", "right", "right", "left"],
                style,
            )
        )

    sparkline = style.paint(make_sparkline([row.tokens for row in report.monthly_rows]), "accent")
    lines.extend(render_panel(f"MONTHLY TREND ({len(report.monthly_rows)} months)", [style.paint("Token sparkline:", "dim") + " " + sparkline], style, layout_width))
    lines.extend(
        render_table_box(
            "MONTHLY TABLE",
            ["Month", "Prompts", "Tokens", "API $"],
            [
                [
                    style.paint(row.month, "good") if row is report.monthly_rows[-1] else row.month,
                    format_int(row.prompts),
                    format_short(row.tokens),
                    format_usd(row.cost_usd),
                ]
                for row in report.monthly_rows
            ],
            [10, 10, 12, 10],
            ["left", "right", "right", "right"],
            style,
        )
    )

    if view == "full":
        total_all_tokens = sum(stats.total_tokens for _, stats in report.model_all_time) or 1
        lines.extend(
            render_table_box(
                "MODEL BREAKDOWN (all-time)",
                ["Model", "Turns", "Input", "Cache", "Output", "Reason", "Total", "API $", "Share"],
                [
                    [
                        name,
                        format_int(stats.turns),
                        format_short(stats.input_tokens),
                        format_short(stats.cached_input_tokens),
                        format_short(stats.output_tokens),
                        format_short(stats.reasoning_output_tokens),
                        format_short(stats.total_tokens),
                        format_usd(stats.total_cost_usd) if stats.pricing_model else "n/a",
                        f"{(stats.total_tokens / total_all_tokens) * 100:.1f}%",
                    ]
                    for name, stats in report.model_all_time
                ],
                [24, 8, 10, 10, 10, 10, 10, 10, 8],
                ["left", "right", "right", "right", "right", "right", "right", "right", "right"],
                style,
                ranked_themes(len(report.model_all_time)),
            )
        )

        peak_dow_tokens = max((row.tokens for row in report.dow_rows), default=0)
        lines.extend(
            render_table_box(
                "DAY-OF-WEEK PATTERN (all-time)",
                ["Day", "Prompts", "Tokens", "API $", "Load"],
                [
                    [
                        style.paint(row.day, "hot") if row.day == report.busiest_day else row.day,
                        format_int(row.prompts),
                        format_short(row.tokens),
                        format_usd(row.cost_usd),
                        make_bar(row.tokens, peak_dow_tokens, 20, style),
                    ]
                    for row in report.dow_rows
                ],
                [8, 10, 12, 10, 20],
                ["left", "right", "right", "right", "left"],
                style,
            )
        )

    return "\n".join(lines).rstrip() + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="codex-observatory", description="Local observability dashboard for Codex logs.")
    parser.add_argument("view", nargs="?", choices=("smart", "compact", "full"), default="smart")
    parser.add_argument("--codex-home", default="~/.codex", help="Path to the .codex directory. Defaults to ~/.codex")
    parser.add_argument("--heatmap-weeks", type=int, default=16)
    parser.add_argument("--daily-days", type=int, default=7)
    parser.add_argument("--monthly-months", type=int, default=6)
    parser.add_argument("--top-models", type=int, default=6)
    parser.add_argument("--no-color", action="store_true", help="Disable ANSI color output")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of the terminal dashboard")
    parser.add_argument("--now", help="Override the current local time with an ISO timestamp")
    parser.add_argument("--width", type=int, help="Override terminal width for rendering")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    configure_stdio()
    argv = list(argv) if argv is not None else list(sys.argv[1:])
    if argv and argv[0] in {"install-codex", "uninstall-codex"}:
        from . import codex_integration

        integration_action = "install" if argv[0] == "install-codex" else "uninstall"
        integration_args = list(argv[1:])
        if integration_action == "install" and getattr(sys, "frozen", False):
            integration_args = ["--runner-bin", sys.executable, *integration_args]
        elif integration_action == "install":
            integration_args = ["--python-bin", sys.executable, *integration_args]
        return codex_integration.main(integration_args, action=integration_action)

    parser = build_parser()
    args = parser.parse_args(argv)

    width = args.width or shutil.get_terminal_size((120, 40)).columns
    resolved_view = resolve_view(args.view, width)
    now = parse_local_time(args.now) if args.now else datetime.now().replace(microsecond=0)
    codex_home = resolve_codex_home(args.codex_home)
    show_status = not args.json and not os.environ.get("CODEX_STATS_QUIET")

    def emit_status(message: str) -> None:
        if not show_status:
            return
        sys.stdout.write(f"[codex-observatory] {message}\n")
        sys.stdout.flush()

    try:
        report = build_report(
            codex_home,
            now=now,
            daily_days=max(5, min(30, args.daily_days)),
            monthly_months=max(3, min(18, args.monthly_months)),
            heatmap_weeks=max(4, min(52, args.heatmap_weeks)),
            top_models=max(3, min(12, args.top_models)),
            status=emit_status,
        )
    except FileNotFoundError as exc:
        parser.error(str(exc))
        return 2

    use_color = not args.no_color and sys.stdout.isatty() and not os.environ.get("NO_COLOR")
    if args.json:
        json.dump(to_json_dict(report, codex_home), sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        return 0

    sys.stdout.write(render_report(report, view=resolved_view, width=width, use_color=use_color))
    return 0
