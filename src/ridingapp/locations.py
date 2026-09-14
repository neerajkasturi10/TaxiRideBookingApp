"""Sample pickup/drop-off locations (San Francisco landmarks) with coordinates."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Location:
    name: str
    latitude: float
    longitude: float
    city: str
    state: str
    region: str
    zip_code: str


LOCATIONS: list[Location] = [
    Location("Downtown SF - Union Square", 37.7880, -122.4074, "San Francisco", "CA", "West", "94108"),
    Location("SFO Airport (SFO)", 37.6213, -122.3790, "San Francisco", "CA", "West", "94128"),
    Location("Golden Gate Park", 37.7694, -122.4862, "San Francisco", "CA", "West", "94122"),
    Location("Fisherman's Wharf", 37.8080, -122.4177, "San Francisco", "CA", "West", "94133"),
    Location("Oracle Park", 37.7786, -122.3893, "San Francisco", "CA", "West", "94107"),
    Location("Mission District", 37.7599, -122.4148, "San Francisco", "CA", "West", "94110"),
    Location("Golden Gate Bridge", 37.8199, -122.4783, "San Francisco", "CA", "West", "94129"),
    Location("Twin Peaks", 37.7544, -122.4477, "San Francisco", "CA", "West", "94131"),
    Location("Palo Alto - Downtown", 37.4419, -122.1430, "Palo Alto", "CA", "West", "94301"),
    Location("Oakland - Jack London Square", 37.7955, -122.2793, "Oakland", "CA", "West", "94607"),
]


def location_by_name(name: str) -> Location:
    for location in LOCATIONS:
        if location.name == name:
            return location
    raise ValueError(f"Unknown location: {name}")
