"""Streamlit app: book a ride manually, or stream synthetic bookings, into Azure Event Hub."""

from __future__ import annotations

import time

import streamlit as st

from ridingapp.config import load_eventhub_settings
from ridingapp.eventhub_client import RideEventPublisher
from ridingapp.generator import generate_random_booking
from ridingapp.locations import LOCATIONS, location_by_name
from ridingapp.models import build_booking_event, build_card_details
from ridingapp.pricing import CAR_TYPES

st.set_page_config(page_title="RideApp Booking", layout="centered")


@st.cache_resource
def get_publisher() -> RideEventPublisher | None:
    try:
        settings = load_eventhub_settings()
    except RuntimeError:
        return None
    return RideEventPublisher(settings)


def render_sidebar() -> None:
    st.sidebar.header("Event Hub")
    try:
        settings = load_eventhub_settings()
        st.sidebar.success(f"Instance: {settings.eventhub_name}")
    except RuntimeError as exc:
        st.sidebar.error(str(exc))


def booking_tab() -> None:
    st.subheader("Book a ride")

    location_names = [loc.name for loc in LOCATIONS]

    with st.form("booking_form"):
        col1, col2 = st.columns(2)
        with col1:
            customer_name = st.text_input("Full name")
            customer_email = st.text_input("Email")
            customer_phone = st.text_input("Contact number")
        with col2:
            pickup_name = st.selectbox("From", location_names, index=0)
            dropoff_name = st.selectbox("To", location_names, index=1)
            car_type = st.selectbox("Car type", list(CAR_TYPES.keys()))

        customer_rating = st.slider("Your rating (as a passenger)", 1.0, 5.0, 4.8, 0.1)

        payment_method = st.radio("Payment method", ["Card", "Cash", "Wallet"], horizontal=True)

        card_holder = card_brand = card_number = None
        if payment_method == "Card":
            c1, c2 = st.columns(2)
            with c1:
                card_holder = st.text_input("Cardholder name")
                card_brand = st.selectbox("Card brand", ["Visa", "Mastercard", "Amex", "Discover"])
            with c2:
                card_number = st.text_input("Card number", type="password")

        promo_code = st.text_input("Promo code (optional)")

        submitted = st.form_submit_button("Book ride")

    if not submitted:
        return

    errors = []
    if not customer_name:
        errors.append("Full name is required.")
    if not customer_email:
        errors.append("Email is required.")
    if not customer_phone:
        errors.append("Contact number is required.")
    if pickup_name == dropoff_name:
        errors.append("Pickup and drop-off locations must be different.")
    if payment_method == "Card" and (not card_holder or not card_number):
        errors.append("Cardholder name and card number are required for card payments.")

    if errors:
        for error in errors:
            st.error(error)
        return

    card_details = None
    if payment_method == "Card":
        card_details = build_card_details(card_number, card_holder, card_brand)

    event = build_booking_event(
        customer_name=customer_name,
        customer_email=customer_email,
        customer_phone=customer_phone,
        customer_rating=customer_rating,
        pickup=location_by_name(pickup_name),
        dropoff=location_by_name(dropoff_name),
        car_type=car_type,
        payment_method=payment_method,
        card_details=card_details,
        promo_code=promo_code or None,
        source="streamlit_app",
    )

    st.json(event)

    publisher = get_publisher()
    if publisher is None:
        st.warning("Event Hub is not configured — event was built but not sent. See .env.example.")
        return

    try:
        publisher.send(event)
        st.success(f"Ride booked and sent to Event Hub. Booking ID: {event['booking_id']}")
    except Exception as exc:
        st.error(f"Failed to send event to Event Hub: {exc}")


def generator_tab() -> None:
    st.subheader("Synthetic booking generator")
    st.write("Stream randomly generated bookings into Event Hub — useful for demoing volume.")

    count = st.number_input("Number of bookings to generate", min_value=1, max_value=500, value=10)
    delay = st.slider("Delay between events (seconds)", 0.0, 5.0, 0.5, 0.1)

    if st.button("Start streaming"):
        publisher = get_publisher()
        if publisher is None:
            st.error("Event Hub is not configured. See .env.example.")
            return

        progress = st.progress(0)
        log = st.empty()
        sent = 0

        for i in range(int(count)):
            event = generate_random_booking()
            try:
                publisher.send(event)
                sent += 1
            except Exception as exc:
                st.error(f"Failed to send event {i + 1}: {exc}")
                break
            progress.progress((i + 1) / int(count))
            log.text(f"Sent {sent}/{int(count)} — last booking_id: {event['booking_id']}")
            if delay:
                time.sleep(delay)

        st.success(f"Done. Sent {sent} events to Event Hub.")


def main() -> None:
    st.title("RideApp — Book a Ride")
    render_sidebar()

    tab1, tab2 = st.tabs(["Book a Ride", "Synthetic Generator"])
    with tab1:
        booking_tab()
    with tab2:
        generator_tab()


main()
