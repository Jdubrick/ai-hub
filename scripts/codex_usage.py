#!/usr/bin/env python3
"""Summarize token usage from locally retained Codex session logs."""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterable


MILLION = 1_000_000
TOKEN_FIELDS = (
    "input_tokens",
    "cached_input_tokens",
    "cache_write_input_tokens",
    "output_tokens",
    "reasoning_output_tokens",
    "total_tokens",
)

# Standard short-context prices per 1M tokens, as documented on September 2,
# 2026. The cache-write field is present in Codex's local token snapshots.
PRICES = {
    "gpt-5.6-sol": {
        "input": 4.00,
        "cached_input": 0.40,
        "cache_write": 5.00,
        "output": 20.00,
    },
    "gpt-5.6-terra": {
        "input": 2.00,
        "cached_input": 0.20,
        "cache_write": 2.50,
        "output": 12.00,
    },
    "gpt-5.6-luna": {
        "input": 0.20,
        "cached_input": 0.02,
        "cache_write": 0.25,
        "output": 1.20,
    },
}


def parse_iso_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def parse_date_arg(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"invalid date: {value!r}; use YYYY-MM-DD") from exc


def format_tokens(value: int) -> str:
    if value >= MILLION:
        return f"{value / MILLION:.2f}M"
    if value >= 1_000:
        return f"{value / 1_000:.1f}K"
    return str(value)


def format_cost(value: float) -> str:
    return f"${value:,.4f}"


def format_percent(value: float, total: int) -> str:
    if total == 0:
        return "0.0%"
    return f"{value / total * 100:.1f}%"


def local_date(value: datetime | None) -> date | None:
    if value is None:
        return None
    return value.astimezone().date() if value.tzinfo else value.date()


def classify_source(source: Any) -> str:
    if source == "vscode":
        return "direct"
    if isinstance(source, dict) and source.get("subagent", {}).get("other") == "guardian":
        return "guardian"
    return "task-subagent"


def numeric_value(value: Any, fallback: int = 0) -> int:
    if isinstance(value, bool):
        return fallback
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return fallback


@dataclass
class Usage:
    input_tokens: int = 0
    cached_input_tokens: int = 0
    cache_write_input_tokens: int = 0
    output_tokens: int = 0
    reasoning_output_tokens: int = 0
    total_tokens: int = 0
    cost_usd: float = 0.0
    thread_ids: set[str] = field(default_factory=set)

    @property
    def cache_reuse_percent(self) -> float:
        if self.input_tokens == 0:
            return 0.0
        return self.cached_input_tokens / self.input_tokens * 100

    def add_delta(self, model: str, thread_id: str, delta: dict[str, int]) -> None:
        self.input_tokens += delta["input_tokens"]
        self.cached_input_tokens += delta["cached_input_tokens"]
        self.cache_write_input_tokens += delta["cache_write_input_tokens"]
        self.output_tokens += delta["output_tokens"]
        self.reasoning_output_tokens += delta["reasoning_output_tokens"]
        self.total_tokens += delta["total_tokens"]
        self.thread_ids.add(thread_id)

        prices = PRICES.get(model)
        if prices is None:
            return
        self.cost_usd += (
            delta["input_tokens"] - delta["cached_input_tokens"] - delta["cache_write_input_tokens"]
        ) * prices["input"] / MILLION
        self.cost_usd += delta["cached_input_tokens"] * prices["cached_input"] / MILLION
        self.cost_usd += delta["cache_write_input_tokens"] * prices["cache_write"] / MILLION
        self.cost_usd += delta["output_tokens"] * prices["output"] / MILLION

    def merge(self, other: "Usage") -> None:
        self.input_tokens += other.input_tokens
        self.cached_input_tokens += other.cached_input_tokens
        self.cache_write_input_tokens += other.cache_write_input_tokens
        self.output_tokens += other.output_tokens
        self.reasoning_output_tokens += other.reasoning_output_tokens
        self.total_tokens += other.total_tokens
        self.cost_usd += other.cost_usd
        self.thread_ids.update(other.thread_ids)


@dataclass
class SessionReport:
    thread_id: str
    run_type: str
    role: str
    nickname: str
    started_at: datetime | None
    model_usage: dict[str, Usage]
    reset_count: int = 0

    @property
    def usage(self) -> Usage:
        combined = Usage()
        for usage in self.model_usage.values():
            combined.merge(usage)
        return combined

    @property
    def models(self) -> list[str]:
        return list(self.model_usage)


def read_jsonl(path: Path, warnings: list[str]) -> Iterable[dict[str, Any]]:
    try:
        with path.open("r", encoding="utf-8") as stream:
            for line_number, line in enumerate(stream, start=1):
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    warnings.append(f"{path.name}:{line_number} is not valid JSON")
                    continue
                if isinstance(record, dict):
                    yield record
    except OSError as exc:
        warnings.append(f"could not read {path}: {exc}")


def load_session(path: Path, warnings: list[str]) -> SessionReport | None:
    metadata: dict[str, Any] = {}
    first_timestamp: datetime | None = None
    active_model = "unknown"
    previous = {field_name: 0 for field_name in TOKEN_FIELDS}
    seen_token_count = False
    model_usage: dict[str, Usage] = {}
    reset_count = 0

    for record in read_jsonl(path, warnings):
        timestamp = parse_iso_timestamp(record.get("timestamp"))
        if first_timestamp is None and timestamp is not None:
            first_timestamp = timestamp

        record_type = record.get("type")
        payload = record.get("payload")
        if not isinstance(payload, dict):
            continue

        if record_type == "session_meta" and not metadata:
            metadata = payload
            continue

        if record_type == "turn_context":
            model = payload.get("model")
            if isinstance(model, str) and model:
                active_model = model
            continue

        if record_type != "event_msg" or payload.get("type") != "token_count":
            continue

        info = payload.get("info")
        cumulative = info.get("total_token_usage") if isinstance(info, dict) else None
        if not isinstance(cumulative, dict) or "total_tokens" not in cumulative:
            continue

        current = {
            field_name: numeric_value(cumulative.get(field_name), previous[field_name])
            for field_name in TOKEN_FIELDS
        }
        delta: dict[str, int] = {}
        for field_name in TOKEN_FIELDS:
            if current[field_name] < previous[field_name]:
                reset_count += 1
                delta[field_name] = current[field_name]
            else:
                delta[field_name] = current[field_name] - previous[field_name]
        previous = current
        seen_token_count = True

        if delta["total_tokens"] <= 0:
            continue

        usage = model_usage.setdefault(active_model, Usage())
        thread_id = str(metadata.get("id") or path.stem)
        usage.add_delta(active_model, thread_id, delta)

    if not seen_token_count or not model_usage:
        return None

    source = metadata.get("source")
    run_type = classify_source(source)
    role = metadata.get("agent_role")
    if not isinstance(role, str) or not role:
        role = "guardian" if run_type == "guardian" else run_type
    nickname = metadata.get("agent_nickname")
    if not isinstance(nickname, str):
        nickname = ""

    return SessionReport(
        thread_id=str(metadata.get("id") or path.stem),
        run_type=run_type,
        role=role,
        nickname=nickname,
        started_at=first_timestamp,
        model_usage=model_usage,
        reset_count=reset_count,
    )


def session_paths(codex_home: Path) -> list[Path]:
    paths: list[Path] = []
    for directory_name in ("sessions", "archived_sessions"):
        directory = codex_home / directory_name
        if directory.is_dir():
            paths.extend(directory.rglob("rollout-*.jsonl"))
    return sorted(set(paths))


def aggregate(
    sessions: list[SessionReport],
) -> tuple[Usage, dict[str, Usage], dict[str, Usage], dict[str, Usage], dict[date, Usage]]:
    total = Usage()
    by_model: dict[str, Usage] = defaultdict(Usage)
    by_run_type: dict[str, Usage] = defaultdict(Usage)
    by_role: dict[str, Usage] = defaultdict(Usage)
    by_day: dict[date, Usage] = defaultdict(Usage)

    for session in sessions:
        session_day = local_date(session.started_at)
        for model, usage in session.model_usage.items():
            by_model[model].merge(usage)
            by_run_type[session.run_type].merge(usage)
            by_role[session.role].merge(usage)
            if session_day is not None:
                by_day[session_day].merge(usage)
            total.merge(usage)

    return total, by_model, by_run_type, by_role, by_day


def print_usage(label: str, usage: Usage, total_tokens: int | None = None, indent: str = "  ") -> None:
    total_for_percent = total_tokens if total_tokens is not None else usage.total_tokens
    share = f" ({format_percent(usage.total_tokens, total_for_percent)})" if total_tokens is not None else ""
    print(f"{indent}{label}: {format_tokens(usage.total_tokens)}{share}")
    print(f"{indent}  Input: {format_tokens(usage.input_tokens)}")
    print(f"{indent}  Cached input: {format_tokens(usage.cached_input_tokens)} ({usage.cache_reuse_percent:.1f}% of input)")
    print(f"{indent}  Cache writes: {format_tokens(usage.cache_write_input_tokens)}")
    print(f"{indent}  Output: {format_tokens(usage.output_tokens)}")
    print(f"{indent}  Reasoning output: {format_tokens(usage.reasoning_output_tokens)}")
    print(f"{indent}  Estimated cost: {format_cost(usage.cost_usd)}")


def print_report(
    codex_home: Path,
    sessions: list[SessionReport],
    total: Usage,
    by_model: dict[str, Usage],
    by_run_type: dict[str, Usage],
    by_role: dict[str, Usage],
    by_day: dict[date, Usage],
    warnings: list[str],
    top_count: int,
) -> None:
    started = min((session.started_at for session in sessions if session.started_at), default=None)
    finished = max((session.started_at for session in sessions if session.started_at), default=None)
    local_started = local_date(started)
    local_finished = local_date(finished)
    run_counts: dict[str, int] = defaultdict(int)
    for session in sessions:
        run_counts[session.run_type] += 1

    print("Codex usage")
    print(f"Source: {codex_home / 'sessions'} and {codex_home / 'archived_sessions'}")
    if local_started and local_finished:
        print(f"Coverage: {local_started.isoformat()} through {local_finished.isoformat()} (local dates)")
    print(f"Threads: {len(sessions)} ({run_counts.get('direct', 0)} direct, {run_counts.get('task-subagent', 0)} task subagent, {run_counts.get('guardian', 0)} guardian)")
    print()

    print("Totals")
    print_usage("Recorded tokens", total)
    print(f"  Estimated cost: {format_cost(total.cost_usd)} USD")
    print(f"  Input cache reuse: {total.cache_reuse_percent:.1f}%")
    print()

    print("By model")
    for model, usage in sorted(by_model.items(), key=lambda item: item[1].total_tokens, reverse=True):
        print_usage(model, usage, total.total_tokens)
        print(f"    Threads touched: {len(usage.thread_ids)}")
    print()

    print("By run type")
    for run_type, usage in sorted(by_run_type.items(), key=lambda item: item[1].total_tokens, reverse=True):
        print(f"  {run_type}: {format_tokens(usage.total_tokens)} ({format_percent(usage.total_tokens, total.total_tokens)}), {len(usage.thread_ids)} threads, {format_cost(usage.cost_usd)}")
    print()

    print("By agent role")
    for role, usage in sorted(by_role.items(), key=lambda item: item[1].total_tokens, reverse=True):
        print(f"  {role}: {format_tokens(usage.total_tokens)} ({format_percent(usage.total_tokens, total.total_tokens)}), {len(usage.thread_ids)} threads, {format_cost(usage.cost_usd)}")
    print()

    if by_day:
        print("By local session start date")
        for day, usage in sorted(by_day.items()):
            print(f"  {day.isoformat()}: {format_tokens(usage.total_tokens)}, {format_cost(usage.cost_usd)}")
        print()

    print(f"Largest runs (top {min(top_count, len(sessions))})")
    ranked_sessions = sorted(sessions, key=lambda session: session.usage.total_tokens, reverse=True)
    for index, session in enumerate(ranked_sessions[:top_count], start=1):
        model_label = ", ".join(session.models)
        role_label = session.role if session.role != session.run_type else session.run_type
        nickname = f" / {session.nickname}" if session.nickname else ""
        print(f"  {index}. {format_tokens(session.usage.total_tokens)} | {role_label}{nickname} | {model_label} | {session.thread_id}")
    print()

    print("Cost basis")
    print("  Standard short-context prices per 1M tokens:")
    for model, prices in PRICES.items():
        print(
            f"    {model}: ${prices['input']:.2f} input, "
            f"${prices['cached_input']:.2f} cached input, "
            f"${prices['cache_write']:.2f} cache writes, "
            f"${prices['output']:.2f} output"
        )
    print("  Reasoning output is included within output tokens and is not charged twice.")
    print("  Model changes are attributed using the most recent turn_context before each token_count event.")
    print("  Estimate assumes standard short-context requests and excludes tool-specific charges.")
    print("  This is a local estimate, not an account billing export.")

    if warnings:
        print()
        print(f"Warnings: {len(warnings)} malformed or unreadable records were skipped.")
        for warning in warnings[:5]:
            print(f"  - {warning}")
        if len(warnings) > 5:
            print(f"  - ... and {len(warnings) - 5} more")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    default_codex_home = os.environ.get("CODEX_HOME") or str(Path.home() / ".codex")
    parser.add_argument(
        "--codex-home",
        type=Path,
        default=Path(default_codex_home).expanduser(),
        help="Codex data directory (default: CODEX_HOME or ~/.codex)",
    )
    parser.add_argument(
        "--exclude-thread",
        action="append",
        default=[],
        metavar="THREAD_ID",
        help="exclude a thread ID; repeat for multiple IDs",
    )
    parser.add_argument("--since", type=parse_date_arg, help="include sessions starting on or after YYYY-MM-DD")
    parser.add_argument("--until", type=parse_date_arg, help="include sessions starting on or before YYYY-MM-DD")
    parser.add_argument("--top", type=int, default=5, metavar="N", help="show N largest runs (default: 5)")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.top < 0:
        parser.error("--top must be zero or greater")
    if args.since and args.until and args.since > args.until:
        parser.error("--since must be on or before --until")

    codex_home = args.codex_home.expanduser()
    paths = session_paths(codex_home)
    if not paths:
        print(f"No rollout JSONL files found under {codex_home / 'sessions'} or {codex_home / 'archived_sessions'}.", file=sys.stderr)
        return 1

    warnings: list[str] = []
    sessions: list[SessionReport] = []
    excluded_ids = set(args.exclude_thread)
    for path in paths:
        session = load_session(path, warnings)
        if session is None or session.thread_id in excluded_ids:
            continue
        session_day = local_date(session.started_at)
        if args.since and (session_day is None or session_day < args.since):
            continue
        if args.until and (session_day is None or session_day > args.until):
            continue
        sessions.append(session)

    if not sessions:
        print("No sessions matched the selected filters.", file=sys.stderr)
        return 1

    total, by_model, by_run_type, by_role, by_day = aggregate(sessions)
    print_report(codex_home, sessions, total, by_model, by_run_type, by_role, by_day, warnings, args.top)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
