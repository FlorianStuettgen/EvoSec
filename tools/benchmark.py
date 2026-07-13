from __future__ import annotations

import argparse
from datetime import UTC, datetime, timedelta
from time import perf_counter

from soc_replay.engine import evaluate_rule
from soc_replay.models import Aggregate, Condition, Event, Response, Rule


def build_events(count: int) -> list[Event]:
    start = datetime(2026, 1, 1, tzinfo=UTC)
    return [
        Event(
            event_id=f"event-{index:08d}",
            timestamp=start + timedelta(milliseconds=index),
            source="benchmark",
            category="network_connection",
            action="connection_attempt",
            source_ip="10.0.0.10",
            destination_ip="10.0.0.20",
            destination_port=1000 + (index % 100),
            outcome="blocked",
            tags=("synthetic",),
        )
        for index in range(count)
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a local, synthetic SOC_Replay throughput benchmark.")
    parser.add_argument("--events", type=int, default=100_000)
    args = parser.parse_args()
    if args.events < 1:
        parser.error("--events must be positive")
    rule = Rule(
        rule_id="BENCH-001",
        name="Benchmark rule",
        severity="medium",
        description="Synthetic benchmark only.",
        conditions=(Condition("category", "eq", "network_connection"), Condition("outcome", "eq", "blocked")),
        aggregate=Aggregate(
            group_by=("source_ip", "destination_ip"),
            count_gte=50,
            within_seconds=5,
            distinct_field="destination_port",
            distinct_gte=50,
        ),
        response=Response("recommend_review", "Synthetic benchmark response."),
    )
    events = build_events(args.events)
    started = perf_counter()
    detections = evaluate_rule(rule, events)
    elapsed = perf_counter() - started
    rate = args.events / elapsed
    print(
        f"events={args.events} detections={len(detections)} elapsed_seconds={elapsed:.6f} events_per_second={rate:.0f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
