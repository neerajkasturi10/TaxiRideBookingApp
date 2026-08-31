"""Random driver + vehicle assignment for a booked ride."""

from __future__ import annotations

import random
import uuid

from faker import Faker

fake = Faker()

VEHICLES: list[tuple[str, str]] = [
    ("Toyota", "Camry"),
    ("Honda", "Accord"),
    ("Tesla", "Model 3"),
    ("Ford", "Explorer"),
    ("Chevrolet", "Suburban"),
    ("BMW", "5 Series"),
    ("Hyundai", "Elantra"),
]


def random_driver() -> dict:
    make, model = random.choice(VEHICLES)
    return {
        "driver_id": str(uuid.uuid4()),
        "name": fake.name(),
        "vehicle_make": make,
        "vehicle_model": model,
        "vehicle_plate": fake.license_plate(),
        "rating": round(random.uniform(4.2, 5.0), 2),
    }
