"""
Setup script to create ClickHouse sample databases and load data.

Usage:
    CLICKHOUSE_HOST=... CLICKHOUSE_PASSWORD=... python setup.py
"""

import os
import sys

import clickhouse_connect
from dotenv import load_dotenv

load_dotenv()


def main():
    host = os.environ.get("CLICKHOUSE_HOST")
    password = os.environ.get("CLICKHOUSE_PASSWORD")

    if not host or not password:
        print("Set CLICKHOUSE_HOST and CLICKHOUSE_PASSWORD environment variables")
        sys.exit(1)

    client = clickhouse_connect.get_client(
        host=host,
        port=int(os.environ.get("CLICKHOUSE_PORT", "8443")),
        username=os.environ.get("CLICKHOUSE_USER", "default"),
        password=password,
        secure=True,
        send_receive_timeout=1800,
    )

    print("Connected to ClickHouse")

    # --- UK Price Paid ---
    print("\n=== Setting up UK Price Paid dataset ===")

    print("Creating database 'uk'...")
    client.command("CREATE DATABASE IF NOT EXISTS uk")

    print("Creating table 'uk.uk_price_paid'...")
    client.command("""
        CREATE TABLE IF NOT EXISTS uk.uk_price_paid (
            price UInt32,
            date Date,
            postcode1 LowCardinality(String),
            postcode2 LowCardinality(String),
            type Enum8('terraced' = 1, 'semi-detached' = 2, 'detached' = 3, 'flat' = 4, 'other' = 0),
            is_new UInt8,
            duration Enum8('freehold' = 1, 'leasehold' = 2, 'unknown' = 0),
            addr1 String,
            addr2 String,
            street LowCardinality(String),
            locality LowCardinality(String),
            town LowCardinality(String),
            district LowCardinality(String),
            county LowCardinality(String)
        )
        ENGINE = MergeTree
        ORDER BY (postcode1, postcode2, addr1, addr2)
    """)

    count = client.command("SELECT count() FROM uk.uk_price_paid")
    if count and count > 0:
        print(f"  UK data already loaded ({count:,} rows). Skipping.")
    else:
        print("Loading UK property data from Land Registry (~27M rows, this may take several minutes)...")
        client.command("""
            INSERT INTO uk.uk_price_paid
            SELECT
                toUInt32(price_string) AS price,
                parseDateTimeBestEffortUS(time) AS date,
                splitByChar(' ', postcode)[1] AS postcode1,
                splitByChar(' ', postcode)[2] AS postcode2,
                transform(a, ['T', 'S', 'D', 'F', 'O'], ['terraced', 'semi-detached', 'detached', 'flat', 'other']) AS type,
                b = 'Y' AS is_new,
                transform(c, ['F', 'L', 'U'], ['freehold', 'leasehold', 'unknown']) AS duration,
                addr1, addr2, street, locality, town, district, county
            FROM url(
                'http://prod1.publicdata.landregistry.gov.uk.s3-website-eu-west-1.amazonaws.com/pp-complete.csv',
                'CSV',
                'uuid_string String, price_string String, time String, postcode String,
                 a String, b String, c String, addr1 String, addr2 String,
                 street String, locality String, town String, district String,
                 county String, d String, e String'
            )
            SETTINGS max_http_get_redirects=10
        """)
        count = client.command("SELECT count() FROM uk.uk_price_paid")
        print(f"  Loaded {count:,} rows")

    # --- NYC Taxi ---
    print("\n=== Setting up NYC Taxi dataset ===")

    print("Creating database 'nyc_taxi'...")
    client.command("CREATE DATABASE IF NOT EXISTS nyc_taxi")

    print("Creating table 'nyc_taxi.trips_small'...")
    client.command("""
        CREATE TABLE IF NOT EXISTS nyc_taxi.trips_small (
            trip_id UInt32,
            pickup_datetime DateTime,
            dropoff_datetime DateTime,
            pickup_longitude Nullable(Float64),
            pickup_latitude Nullable(Float64),
            dropoff_longitude Nullable(Float64),
            dropoff_latitude Nullable(Float64),
            passenger_count UInt8,
            trip_distance Float32,
            fare_amount Float32,
            extra Float32,
            tip_amount Float32,
            tolls_amount Float32,
            total_amount Float32,
            payment_type Enum('CSH' = 1, 'CRE' = 2, 'NOC' = 3, 'DIS' = 4, 'UNK' = 5),
            pickup_ntaname LowCardinality(String),
            dropoff_ntaname LowCardinality(String)
        )
        ENGINE = MergeTree
        PRIMARY KEY (pickup_datetime, dropoff_datetime)
    """)

    count = client.command("SELECT count() FROM nyc_taxi.trips_small")
    if count and count > 0:
        print(f"  NYC Taxi data already loaded ({count:,} rows). Skipping.")
    else:
        print("Loading NYC Taxi data (~3M rows)...")
        client.command("""
            INSERT INTO nyc_taxi.trips_small
            SELECT
                trip_id, pickup_datetime, dropoff_datetime,
                pickup_longitude, pickup_latitude,
                dropoff_longitude, dropoff_latitude,
                passenger_count, trip_distance, fare_amount,
                extra, tip_amount, tolls_amount, total_amount,
                payment_type, pickup_ntaname, dropoff_ntaname
            FROM s3(
                'https://datasets-documentation.s3.eu-west-3.amazonaws.com/nyc-taxi/trips_{0..2}.gz',
                'TabSeparatedWithNames'
            )
        """)
        count = client.command("SELECT count() FROM nyc_taxi.trips_small")
        print(f"  Loaded {count:,} rows")

    print("\n=== Setup complete! ===")
    print("Start the app with: python main.py")


if __name__ == "__main__":
    main()
