"""Generate dimension-style lookup files for the categorical fields in the booking event,
for use as analytics tables joined against the historical batch data."""

from __future__ import annotations

import json
from pathlib import Path

from ridingapp.drivers import VEHICLES
from ridingapp.generator import CARD_BRANDS, PAYMENT_METHODS
from ridingapp.locations import LOCATIONS
from ridingapp.pricing import CAR_TYPES

DEFAULT_OUTPUT_DIR = Path("data/mappers")

CAR_TYPE_ATTRIBUTES = {
    "Economy": {"category": "Standard", "capacity": 4},
    "Comfort": {"category": "Standard", "capacity": 4},
    "XL": {"category": "Extra Large", "capacity": 6},
    "Premium": {"category": "Luxury", "capacity": 4},
    "Pool": {"category": "Shared", "capacity": 4},
}

PAYMENT_METHOD_ATTRIBUTES = {
    "Card": {"description": "Credit or debit card", "is_cashless": True, "requires_card_details": True},
    "Cash": {"description": "Physical cash payment", "is_cashless": False, "requires_card_details": False},
    "Wallet": {"description": "Digital wallet balance", "is_cashless": True, "requires_card_details": False},
}

CARD_BRAND_ATTRIBUTES = {
    "Visa": {"country_of_origin": "USA", "network_type": "Global"},
    "Mastercard": {"country_of_origin": "USA", "network_type": "Global"},
    "Amex": {"country_of_origin": "USA", "network_type": "Global"},
    "Discover": {"country_of_origin": "USA", "network_type": "Domestic"},
}

VEHICLE_ATTRIBUTES = {
    ("Toyota", "Camry"): {"vehicle_category": "Sedan", "fuel_type": "Gasoline"},
    ("Honda", "Accord"): {"vehicle_category": "Sedan", "fuel_type": "Gasoline"},
    ("Tesla", "Model 3"): {"vehicle_category": "Sedan", "fuel_type": "Electric"},
    ("Ford", "Explorer"): {"vehicle_category": "SUV", "fuel_type": "Gasoline"},
    ("Chevrolet", "Suburban"): {"vehicle_category": "SUV", "fuel_type": "Gasoline"},
    ("BMW", "5 Series"): {"vehicle_category": "Sedan", "fuel_type": "Gasoline"},
    ("Hyundai", "Elantra"): {"vehicle_category": "Sedan", "fuel_type": "Gasoline"},
}


def build_mappers() -> dict[str, dict]:
    return {
        "car_type": {
            name: {
                "id": i + 1,
                "category": CAR_TYPE_ATTRIBUTES[name]["category"],
                "capacity": CAR_TYPE_ATTRIBUTES[name]["capacity"],
                "base_fare": rates["base_fare"],
                "per_km_rate": rates["per_km"],
                "multiplier": rates["multiplier"],
            }
            for i, (name, rates) in enumerate(CAR_TYPES.items())
        },
        "payment_method": {
            name: {"id": i + 1, **PAYMENT_METHOD_ATTRIBUTES[name]}
            for i, name in enumerate(PAYMENT_METHODS)
        },
        "vehicle_model": {
            f"{make} {model}": {
                "id": i + 1,
                "make": make,
                "model": model,
                **VEHICLE_ATTRIBUTES[(make, model)],
            }
            for i, (make, model) in enumerate(VEHICLES)
        },
        "location": {
            location.name: {
                "id": i + 1,
                "city": location.city,
                "state": location.state,
                "region": location.region,
                "zip": location.zip_code,
                "latitude": location.latitude,
                "longitude": location.longitude,
            }
            for i, location in enumerate(LOCATIONS)
        },
        "card_brand": {
            name: {"id": i + 1, **CARD_BRAND_ATTRIBUTES[name]}
            for i, name in enumerate(CARD_BRANDS)
        },
    }


def write_mappers(mappers: dict[str, dict], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for field_name, mapping in mappers.items():
        path = output_dir / f"{field_name}_mapper.json"
        with path.open("w") as f:
            json.dump(mapping, f, indent=2)


def main() -> None:
    mappers = build_mappers()
    write_mappers(mappers, DEFAULT_OUTPUT_DIR)
    for field_name, mapping in mappers.items():
        print(f"{field_name}: {len(mapping)} entries -> {DEFAULT_OUTPUT_DIR / f'{field_name}_mapper.json'}")


if __name__ == "__main__":
    main()
