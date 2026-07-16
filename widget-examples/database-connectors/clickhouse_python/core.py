import asyncio
import os
import time
from functools import wraps
from queue import Empty, Full, Queue
from typing import Any

import clickhouse_connect
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI(
    title="ClickHouse Explorer",
    description="Explore ClickHouse sample datasets in OpenBB Workspace",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://pro.openbb.co",
        "https://pro.openbb.dev",
        "https://excel.openbb.co",
        "https://excel.openbb.dev",
        "http://localhost",
        "http://localhost:1420",
        "http://localhost:5050",
        "tauri://localhost",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def allow_private_network(request, call_next):
    """Allow Workspace's public origin to reach a backend running locally."""
    response = await call_next(request)
    if request.headers.get("access-control-request-private-network"):
        response.headers["Access-Control-Allow-Private-Network"] = "true"
    return response


POOL_SIZE = 10
_client_pool = Queue(maxsize=POOL_SIZE)


def _create_client():
    return clickhouse_connect.get_client(
        host=os.environ["CLICKHOUSE_HOST"],
        port=int(os.environ.get("CLICKHOUSE_PORT", "8443")),
        username=os.environ.get("CLICKHOUSE_USER", "default"),
        password=os.environ["CLICKHOUSE_PASSWORD"],
        secure=True,
    )


def _get_client():
    try:
        return _client_pool.get_nowait()
    except Empty:
        return _create_client()


def _return_client(client):
    try:
        _client_pool.put_nowait(client)
    except Full:
        client.close()


WIDGETS = {}

_cache: dict[tuple[str, tuple[tuple[str, str], ...]], tuple[float, list[dict]]] = {}
CACHE_TTL = 120


def register_widget(widget_config):
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await func(*args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        endpoint = widget_config.get("endpoint")
        if endpoint:
            if "widgetId" not in widget_config:
                widget_config["widgetId"] = endpoint
            WIDGETS[widget_config["widgetId"]] = widget_config

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


def _cache_key(sql: str, parameters: dict[str, Any] | None = None):
    normalized = tuple(sorted((key, repr(value)) for key, value in (parameters or {}).items()))
    return sql, normalized


def _run_query(sql: str, parameters: dict[str, Any] | None = None):
    client = _get_client()
    try:
        result = client.query(sql, parameters=parameters)
        data = [dict(zip(result.column_names, row)) for row in result.result_rows]
    except Exception:
        client.close()
        raise
    _return_client(client)
    return data


def cached_query(
    sql: str,
    parameters: dict[str, Any] | None = None,
    ttl: int = CACHE_TTL,
):
    now = time.time()
    key = _cache_key(sql, parameters)
    if key in _cache:
        cached_time, cached_data = _cache[key]
        if now - cached_time < ttl:
            return cached_data
    data = _run_query(sql, parameters)
    _cache[key] = (now, data)
    return data


async def async_cached_query(
    sql: str,
    parameters: dict[str, Any] | None = None,
    ttl: int = CACHE_TTL,
):
    now = time.time()
    key = _cache_key(sql, parameters)
    if key in _cache:
        cached_time, cached_data = _cache[key]
        if now - cached_time < ttl:
            return cached_data
    data = await asyncio.to_thread(_run_query, sql, parameters)
    _cache[key] = (now, data)
    return data


async def warm_cache():
    """Pre-warm cache with unfiltered queries in the background."""
    queries = [
        # UK Housing
        "SELECT round(avg(price)) AS avg_price, count() AS total_transactions FROM uk.uk_price_paid",
        "SELECT toYear(date) AS year, round(avg(price)) AS avg_price FROM uk.uk_price_paid GROUP BY year ORDER BY year DESC LIMIT 2",
        """SELECT toYear(date) AS year, round(avg(price)) AS avg_price, min(price) AS min_price,
            max(price) AS max_price, count() AS transactions FROM uk.uk_price_paid GROUP BY year ORDER BY year""",
        """SELECT town, round(avg(price)) AS avg_price, count() AS transactions FROM uk.uk_price_paid
            WHERE town != '' GROUP BY town HAVING transactions > 1000 ORDER BY avg_price DESC LIMIT 20""",
        """SELECT toYear(date) AS year, round(avgIf(price, type = 'detached')) AS detached,
            round(avgIf(price, type = 'semi-detached')) AS semi_detached,
            round(avgIf(price, type = 'terraced')) AS terraced,
            round(avgIf(price, type = 'flat')) AS flat,
            round(avgIf(price, type = 'other')) AS other FROM uk.uk_price_paid GROUP BY year ORDER BY year""",
        # NYC Taxi
        "SELECT round(avg(fare_amount), 2) AS avg_fare, round(avg(trip_distance), 2) AS avg_distance, count() AS total_trips FROM nyc_taxi.trips_small WHERE 1=1 ",
        """SELECT toHour(pickup_datetime) AS hour, count() AS trips, round(avg(fare_amount), 2) AS avg_fare,
            round(avg(trip_distance), 2) AS avg_distance, round(avg(passenger_count), 1) AS avg_passengers
            FROM nyc_taxi.trips_small WHERE 1=1  GROUP BY hour ORDER BY hour""",
        """SELECT pickup_ntaname AS pickup_zone, count() AS trips, round(avg(fare_amount), 2) AS avg_fare
            FROM nyc_taxi.trips_small WHERE pickup_ntaname != '' GROUP BY pickup_zone ORDER BY trips DESC LIMIT 20""",
        "SELECT pickup_ntaname AS zone FROM nyc_taxi.trips_small WHERE pickup_ntaname != '' GROUP BY zone ORDER BY zone",
    ]
    for sql in queries:
        try:
            await async_cached_query(sql, ttl=CACHE_TTL)
        except Exception:
            pass
