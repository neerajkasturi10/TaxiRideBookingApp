"""Generate a batch of historical bookings, for batch/historical-load demos."""

from __future__ import annotations

import argparse
import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

from ridingapp.generator import generate_random_booking

DEFAULT_COUNT = 5000
DEFAULT_DAYS_BACK = 90
DEFAULT_OUTPUT = Path("data/historical_bookings.jsonl")


def random_historical_timestamp(days_back: int) -> str:
    now = datetime.now(timezone.utc)
    seconds_back = random.uniform(0, days_back * 24 * 3600)
    return (now - timedelta(seconds=seconds_back)).isoformat()


def generate_historical_bookings(count: int, days_back: int) -> list[dict]:
    events = [
        generate_random_booking(
            event_timestamp=random_historical_timestamp(days_back),
            source="historical_batch",
        )
        for _ in range(count)
    ]
    events.sort(key=lambda event: event["event_timestamp"])
    return events


def write_jsonl(events: list[dict], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w") as f:
        for event in events:
            f.write(json.dumps(event) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate historical ride bookings for batch load demos.")
    parser.add_argument("--count", type=int, default=DEFAULT_COUNT)
    parser.add_argument("--days-back", type=int, default=DEFAULT_DAYS_BACK)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    events = generate_historical_bookings(args.count, args.days_back)
    write_jsonl(events, args.output)
    print(f"Wrote {len(events)} historical bookings to {args.output}")


if __name__ == "__main__":
    main()
