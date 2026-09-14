"""Generate a standalone CSV of customer transaction data, for batch load demos."""

from __future__ import annotations

import argparse
import csv
import random
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from faker import Faker

fake = Faker()

DEFAULT_COUNT = 2000
DEFAULT_DAYS_BACK = 90
DEFAULT_OUTPUT = Path("data/customer_transactions.csv")

PAYMENT_METHODS = ["Card", "Cash", "Wallet"]
CARD_BRANDS = ["Visa", "Mastercard", "Amex", "Discover"]
TRANSACTION_TYPES = ["ride_payment", "tip", "refund", "cancellation_fee"]
STATUS_WEIGHTS = [("SUCCESS", 0.90), ("FAILED", 0.05), ("PENDING", 0.03), ("REFUNDED", 0.02)]

FIELDNAMES = [
    "transaction_id",
    "customer_id",
    "customer_name",
    "customer_email",
    "transaction_type",
    "transaction_amount",
    "currency",
    "payment_method",
    "card_brand",
    "transaction_status",
    "transaction_timestamp",
]


def random_timestamp(days_back: int) -> str:
    now = datetime.now(timezone.utc)
    seconds_back = random.uniform(0, days_back * 24 * 3600)
    return (now - timedelta(seconds=seconds_back)).isoformat()


def generate_transaction(days_back: int) -> dict:
    payment_method = random.choice(PAYMENT_METHODS)
    transaction_type = random.choice(TRANSACTION_TYPES)
    amount = round(random.uniform(4.0, 180.0), 2)
    if transaction_type in ("refund", "cancellation_fee"):
        amount = -amount

    return {
        "transaction_id": str(uuid.uuid4()),
        "customer_id": str(uuid.uuid4()),
        "customer_name": fake.name(),
        "customer_email": fake.email(),
        "transaction_type": transaction_type,
        "transaction_amount": amount,
        "currency": "USD",
        "payment_method": payment_method,
        "card_brand": random.choice(CARD_BRANDS) if payment_method == "Card" else "",
        "transaction_status": random.choices(
            [status for status, _ in STATUS_WEIGHTS],
            weights=[weight for _, weight in STATUS_WEIGHTS],
        )[0],
        "transaction_timestamp": random_timestamp(days_back),
    }


def generate_transactions(count: int, days_back: int) -> list[dict]:
    transactions = [generate_transaction(days_back) for _ in range(count)]
    transactions.sort(key=lambda transaction: transaction["transaction_timestamp"])
    return transactions


def write_csv(transactions: list[dict], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(transactions)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a CSV of customer transaction data.")
    parser.add_argument("--count", type=int, default=DEFAULT_COUNT)
    parser.add_argument("--days-back", type=int, default=DEFAULT_DAYS_BACK)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    transactions = generate_transactions(args.count, args.days_back)
    write_csv(transactions, args.output)
    print(f"Wrote {len(transactions)} transactions to {args.output}")


if __name__ == "__main__":
    main()
