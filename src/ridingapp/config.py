"""Environment-based configuration for the Event Hub connection."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class EventHubSettings:
    connection_str: str
    eventhub_name: str


def load_eventhub_settings() -> EventHubSettings:
    connection_str = os.environ.get("EVENTHUB_CONNECTION_STR", "")
    eventhub_name = os.environ.get("EVENTHUB_NAME", "riding_topic")

    if not connection_str:
        raise RuntimeError(
            "EVENTHUB_CONNECTION_STR is not set. Copy .env.example to .env and fill it in."
        )

    return EventHubSettings(
        connection_str=connection_str,
        eventhub_name=eventhub_name,
    )
