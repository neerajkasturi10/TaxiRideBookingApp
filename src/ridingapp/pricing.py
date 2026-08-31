"""Fare estimation for a ride, based on straight-line distance between two points."""

from __future__ import annotations

from math import asin, cos, radians, sin, sqrt

from ridingapp.locations import Location

EARTH_RADIUS_KM = 6371.0

CAR_TYPES: dict[str, dict[str, float]] = {
    "Economy": {"base_fare": 2.50, "per_km": 1.10, "multiplier": 1.0},
    "Comfort": {"base_fare": 3.50, "per_km": 1.40, "multiplier": 1.2},
    "XL": {"base_fare": 5.00, "per_km": 1.80, "multiplier": 1.5},
    "Premium": {"base_fare": 8.00, "per_km": 2.50, "multiplier": 2.0},
    "Pool": {"base_fare": 1.50, "per_km": 0.80, "multiplier": 0.7},
}


def haversine_km(origin: Location, destination: Location) -> float:
    lat1, lon1, lat2, lon2 = map(
        radians, (origin.latitude, origin.longitude, destination.latitude, destination.longitude)
    )
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_KM * asin(sqrt(a))


def estimate_fare(origin: Location, destination: Location, car_type: str, surge_multiplier: float = 1.0) -> dict:
    distance_km = haversine_km(origin, destination)
    rates = CAR_TYPES[car_type]
    duration_min = round((distance_km / 35.0) * 60, 1)  # assume ~35 km/h average city speed

    price = (rates["base_fare"] + rates["per_km"] * distance_km) * rates["multiplier"] * surge_multiplier

    return {
        "distance_km": round(distance_km, 2),
        "estimated_duration_min": duration_min,
        "price": round(price, 2),
    }
