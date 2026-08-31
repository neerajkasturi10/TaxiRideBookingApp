"""Sample pickup/drop-off locations (San Francisco landmarks) with coordinates."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Location:
    name: str
    latitude: float
    longitude: float


LOCATIONS: list[Location] = [
    Location("Downtown SF - Union Square", 37.7880, -122.4074),
    Location("SFO Airport (SFO)", 37.6213, -122.3790),
    Location("Golden Gate Park", 37.7694, -122.4862),
    Location("Fisherman's Wharf", 37.8080, -122.4177),
    Location("Oracle Park", 37.7786, -122.3893),
    Location("Mission District", 37.7599, -122.4148),
    Location("Golden Gate Bridge", 37.8199, -122.4783),
    Location("Twin Peaks", 37.7544, -122.4477),
    Location("Palo Alto - Downtown", 37.4419, -122.1430),
    Location("Oakland - Jack London Square", 37.7955, -122.2793),
]


def location_by_name(name: str) -> Location:
    for location in LOCATIONS:
        if location.name == name:
            return location
    raise ValueError(f"Unknown location: {name}")
