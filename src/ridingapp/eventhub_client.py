"""Thin wrapper around the Event Hub producer client."""

from __future__ import annotations

import json

from azure.eventhub import EventData, EventHubProducerClient

from ridingapp.config import EventHubSettings


class RideEventPublisher:
    def __init__(self, settings: EventHubSettings):
        self._client = EventHubProducerClient.from_connection_string(
            conn_str=settings.connection_str,
            eventhub_name=settings.eventhub_name,
        )

    def send(self, event: dict) -> None:
        batch = self._client.create_batch()
        batch.add(EventData(json.dumps(event)))
        self._client.send_batch(batch)

    def send_many(self, events: list[dict]) -> None:
        batch = self._client.create_batch()
        for event in events:
            data = EventData(json.dumps(event))
            try:
                batch.add(data)
            except ValueError:
                # batch is full — flush it and start a new one
                self._client.send_batch(batch)
                batch = self._client.create_batch()
                batch.add(data)
        if len(batch) > 0:
            self._client.send_batch(batch)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "RideEventPublisher":
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()
