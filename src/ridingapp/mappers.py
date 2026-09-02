"""Generate value -> id lookup files for the categorical fields in the booking event,
for joining against the historical batch data as dimension lookups."""

from __future__ import annotations

import json
from pathlib import Path

from ridingapp.drivers import VEHICLES
from ridingapp.generator import CARD_BRANDS, PAYMENT_METHODS
from ridingapp.locations import LOCATIONS
from ridingapp.pricing import CAR_TYPES

DEFAULT_OUTPUT_DIR = Path("data/mappers")


def build_mappers() -> dict[str, dict[str, int]]:
    return {
        "car_type": {name: i + 1 for i, name in enumerate(CAR_TYPES)},
        "payment_method": {name: i + 1 for i, name in enumerate(PAYMENT_METHODS)},
        "vehicle_model": {f"{make} {model}": i + 1 for i, (make, model) in enumerate(VEHICLES)},
        "location": {location.name: i + 1 for i, location in enumerate(LOCATIONS)},
        "card_brand": {name: i + 1 for i, name in enumerate(CARD_BRANDS)},
    }


def write_mappers(mappers: dict[str, dict[str, int]], output_dir: Path) -> None:
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
