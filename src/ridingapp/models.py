"""Booking event schema — the payload sent to Azure Event Hub."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from ridingapp.drivers import random_driver
from ridingapp.locations import Location
from ridingapp.pricing import estimate_fare


def build_card_details(card_number: str, holder_name: str, brand: str) -> dict:
    """Mask the card number down to its last 4 digits before it ever reaches the event."""
    digits = "".join(ch for ch in card_number if ch.isdigit())
    last4 = digits[-4:] if len(digits) >= 4 else digits
    return {"brand": brand, "last4": last4, "holder_name": holder_name}


def build_booking_event(
    *,
    customer_name: str,
    customer_email: str,
    customer_phone: str,
    customer_rating: float,
    pickup: Location,
    dropoff: Location,
    car_type: str,
    payment_method: str,
    card_details: dict | None = None,
    promo_code: str | None = None,
    surge_multiplier: float = 1.0,
    source: str = "streamlit_app",
    event_timestamp: str | None = None,
) -> dict:
    fare = estimate_fare(pickup, dropoff, car_type, surge_multiplier=surge_multiplier)

    return {
        "booking_id": str(uuid.uuid4()),
        "event_type": "ride_booked",
        "event_timestamp": event_timestamp or datetime.now(timezone.utc).isoformat(),
        "source": source,
        "ride_status": "REQUESTED",
        "customer": {
            "name": customer_name,
            "email": customer_email,
            "phone": customer_phone,
            "avg_rating": customer_rating,
        },
        "pickup_location": {
            "name": pickup.name,
            "latitude": pickup.latitude,
            "longitude": pickup.longitude,
        },
        "dropoff_location": {
            "name": dropoff.name,
            "latitude": dropoff.latitude,
            "longitude": dropoff.longitude,
        },
        "car_type": car_type,
        "distance_km": fare["distance_km"],
        "estimated_duration_min": fare["estimated_duration_min"],
        "price": {"amount": fare["price"], "currency": "USD"},
        "payment": {
            "method": payment_method,
            **({"card": card_details} if card_details else {}),
        },
        "driver": random_driver(),
        "promo_code": promo_code,
    }
