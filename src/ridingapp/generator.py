"""Synthetic booking generator, for demoing a continuous stream into Event Hub."""

from __future__ import annotations

import random

from faker import Faker

from ridingapp.locations import LOCATIONS
from ridingapp.models import build_booking_event
from ridingapp.pricing import CAR_TYPES

fake = Faker()

PAYMENT_METHODS = ["Card", "Cash", "Wallet"]
CARD_BRANDS = ["Visa", "Mastercard", "Amex", "Discover"]
PROMO_CODES = [None, None, None, "WELCOME10", "SAVE20"]


def generate_random_booking(event_timestamp: str | None = None, source: str = "synthetic_generator") -> dict:
    pickup, dropoff = random.sample(LOCATIONS, 2)
    car_type = random.choice(list(CAR_TYPES.keys()))
    payment_method = random.choice(PAYMENT_METHODS)

    card_details = None
    if payment_method == "Card":
        card_details = {
            "brand": random.choice(CARD_BRANDS),
            "last4": f"{random.randint(0, 9999):04d}",
            "holder_name": fake.name(),
        }

    return build_booking_event(
        customer_name=fake.name(),
        customer_email=fake.email(),
        customer_phone=fake.phone_number(),
        customer_rating=round(random.uniform(3.8, 5.0), 2),
        pickup=pickup,
        dropoff=dropoff,
        car_type=car_type,
        payment_method=payment_method,
        card_details=card_details,
        promo_code=random.choice(PROMO_CODES),
        surge_multiplier=round(random.uniform(1.0, 1.8), 2) if random.random() < 0.2 else 1.0,
        source=source,
        event_timestamp=event_timestamp,
    )
