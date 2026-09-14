# RideApp

A ride-booking app that streams booking events to Azure Event Hub — built as the producer side of an Azure real-time streaming portfolio project.

- Event Hub Namespace: `RideApp-Events`
- Event Hub instance: `riding_topic`

## Setup

```bash
uv sync
cp .env.example .env
# then edit .env with your Event Hub connection string
```

The connection string comes from the Event Hub namespace's Shared Access Policy (e.g. `RootManageSharedAccessKey`) in the Azure Portal. It should **not** include an `EntityPath` — the Event Hub instance name is supplied separately via `EVENTHUB_NAME`, which is passed explicitly as `eventhub_name` to `EventHubProducerClient.from_connection_string(...)`. That's what pins every send to `riding_topic` specifically — creating other Event Hub instances in the same namespace later has no effect on where this app sends events.

## Run

```bash
uv run streamlit run src/ridingapp/app.py
```

This opens a browser UI with two tabs:

- **Book a Ride** — a booking form (customer info, pickup/drop-off, car type, payment method, promo code). On submit, it builds a booking event and sends it to Event Hub.
- **Synthetic Generator** — generates and streams N randomly generated bookings (via Faker), useful for demoing continuous event volume through the pipeline.

## Event schema

Each booking produces a JSON event like:

```json
{
  "booking_id": "uuid",
  "event_type": "ride_booked",
  "event_timestamp": "2026-08-31T12:00:00+00:00",
  "source": "streamlit_app",
  "ride_status": "REQUESTED",
  "customer": {"name": "...", "email": "...", "phone": "...", "avg_rating": 4.8},
  "pickup_location": {"name": "...", "latitude": 0.0, "longitude": 0.0},
  "dropoff_location": {"name": "...", "latitude": 0.0, "longitude": 0.0},
  "car_type": "Economy",
  "distance_km": 5.2,
  "estimated_duration_min": 8.9,
  "price": {"amount": 12.5, "currency": "USD"},
  "payment": {"method": "Card", "card": {"brand": "Visa", "last4": "1234", "holder_name": "..."}},
  "driver": {"driver_id": "uuid", "name": "...", "vehicle_make": "...", "vehicle_model": "...", "vehicle_plate": "...", "rating": 4.9},
  "promo_code": null
}
```

Card details are masked to brand + last 4 digits before the event is built — the full card number is never stored or transmitted.

## Historical batch data

`data/historical_bookings.jsonl` contains 5000 pre-generated bookings (same event schema as above, `source: "historical_batch"`), with `event_timestamp` spread randomly across the last 90 days and sorted chronologically. Use it for batch/historical-load demos (e.g. bulk loading into a data lake or warehouse) without needing a live Event Hub connection.

Regenerate it with:

```bash
uv run ridingapp-generate-historical --count 5000 --days-back 90
```

## Mapper files

`data/mappers/` has dimension-style lookup files for the categorical fields in the event data, derived from the same source lists the app uses to generate bookings. Each maps a natural value to a surrogate id plus a few descriptive attributes, so they can be used directly as small dimension tables in analytics:

- `car_type_mapper.json` — `{id, category, capacity, base_fare, per_km_rate, multiplier}`
- `payment_method_mapper.json` — `{id, description, is_cashless, requires_card_details}`
- `vehicle_model_mapper.json` — `{id, make, model, vehicle_category, fuel_type}`
- `location_mapper.json` — `{id, city, state, region, zip, latitude, longitude}`
- `card_brand_mapper.json` — `{id, country_of_origin, network_type}`

Join these against `data/historical_bookings.jsonl` on the field's natural value (e.g. `car_type`, `payment.method`, `driver.vehicle_make` + `driver.vehicle_model`, `pickup_location.name`) to bring in the surrogate id and attributes.

Regenerate them with:

```bash
uv run ridingapp-generate-mappers
```

## Customer transactions

`data/customer_transactions.csv` has 2000 standalone synthetic transactions (`transaction_id`, `customer_id`, `customer_name`, `customer_email`, `transaction_type`, `transaction_amount`, `currency`, `payment_method`, `card_brand`, `transaction_status`, `transaction_timestamp`), not tied to any specific booking — useful as its own batch-load source. `transaction_type` includes `ride_payment`, `tip`, `refund`, and `cancellation_fee` (refunds/fees are negative amounts); `transaction_status` is weighted mostly `SUCCESS` with some `FAILED`/`PENDING`/`REFUNDED`.

Regenerate it with:

```bash
uv run ridingapp-generate-transactions --count 2000 --days-back 90
```

## Project layout

- `src/ridingapp/app.py` — Streamlit UI
- `src/ridingapp/models.py` — booking event schema
- `src/ridingapp/eventhub_client.py` — Event Hub producer wrapper
- `src/ridingapp/generator.py` — synthetic booking generator
- `src/ridingapp/historical.py` — generates the historical batch JSONL file
- `src/ridingapp/mappers.py` — generates the value → id lookup files
- `src/ridingapp/transactions.py` — generates the standalone customer transactions CSV
- `src/ridingapp/pricing.py` — fare/distance estimation
- `src/ridingapp/locations.py` — sample pickup/drop-off locations
- `src/ridingapp/drivers.py` — random driver/vehicle assignment
- `src/ridingapp/config.py` — loads Event Hub settings from `.env`
