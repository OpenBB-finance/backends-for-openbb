from fastapi import APIRouter, Query

from core import register_widget, query

router = APIRouter()


@register_widget({
    "name": "NYC Taxi Metrics",
    "description": "Key metrics for the NYC taxi sample dataset",
    "category": "database",
    "type": "metric",
    "endpoint": "taxi/metrics",
    "widgetId": "taxi_metrics",
    "gridData": {"w": 40, "h": 4},
})
@router.get("/taxi/metrics")
def taxi_metrics():
    row = query("""
        SELECT
            COUNT(*) AS trips,
            ROUND(AVG(fare_amount), 2) AS avg_fare,
            ROUND(AVG(trip_distance), 2) AS avg_distance,
            ROUND(AVG(TIMESTAMPDIFF(MINUTE, tpep_pickup_datetime, tpep_dropoff_datetime)), 1) AS avg_minutes
        FROM samples.nyctaxi.trips
    """)[0]
    return [
        {"label": "Total Trips", "value": row["trips"]},
        {"label": "Avg Fare", "value": row["avg_fare"], "unit": "USD"},
        {"label": "Avg Distance", "value": row["avg_distance"], "unit": "mi"},
        {"label": "Avg Duration", "value": row["avg_minutes"], "unit": "min"},
    ]


@register_widget({
    "name": "NYC Taxi Daily Stats",
    "description": "Daily trip counts and average fares from the Databricks NYC taxi sample dataset",
    "category": "database",
    "endpoint": "taxi/daily",
    "widgetId": "taxi_daily",
    "defaultViz": "table",
    "gridData": {"w": 20, "h": 9},
    "data": {
        "table": {
            "showAll": True,
            "chartView": {"enabled": True, "chartType": "line"},
            "columnsDefs": [
                {"headerName": "Date", "field": "date"},
                {"headerName": "Trips", "field": "trips", "cellDataType": "number", "formatterFn": "int"},
                {"headerName": "Avg Fare ($)", "field": "avg_fare", "cellDataType": "number"},
                {"headerName": "Avg Distance (mi)", "field": "avg_distance", "cellDataType": "number"},
            ],
        }
    },
})
@router.get("/taxi/daily")
def taxi_daily():
    rows = query("""
        SELECT
            DATE(tpep_pickup_datetime) AS date,
            COUNT(*) AS trips,
            ROUND(AVG(fare_amount), 2) AS avg_fare,
            ROUND(AVG(trip_distance), 2) AS avg_distance
        FROM samples.nyctaxi.trips
        GROUP BY DATE(tpep_pickup_datetime)
        ORDER BY date
    """)
    return [{**r, "date": r["date"].isoformat()} for r in rows]


@register_widget({
    "name": "NYC Taxi Trips by Hour",
    "description": "Trip volume and averages by hour of day",
    "category": "database",
    "endpoint": "taxi/by-hour",
    "widgetId": "taxi_by_hour",
    "gridData": {"w": 20, "h": 9},
    "data": {
        "table": {
            "showAll": True,
            "chartView": {"enabled": True, "chartType": "column"},
            "columnsDefs": [
                {"headerName": "Hour", "field": "hour", "cellDataType": "number"},
                {"headerName": "Trips", "field": "trips", "cellDataType": "number", "formatterFn": "int"},
                {"headerName": "Avg Fare ($)", "field": "avg_fare", "cellDataType": "number"},
                {"headerName": "Avg Distance (mi)", "field": "avg_distance", "cellDataType": "number"},
            ],
        }
    },
})
@router.get("/taxi/by-hour")
def taxi_by_hour():
    return query("""
        SELECT
            HOUR(tpep_pickup_datetime) AS hour,
            COUNT(*) AS trips,
            ROUND(AVG(fare_amount), 2) AS avg_fare,
            ROUND(AVG(trip_distance), 2) AS avg_distance
        FROM samples.nyctaxi.trips
        GROUP BY HOUR(tpep_pickup_datetime)
        ORDER BY hour
    """)


@register_widget({
    "name": "NYC Taxi Trips",
    "description": "Most recent trips from the Databricks NYC taxi sample dataset",
    "category": "database",
    "endpoint": "taxi/trips",
    "widgetId": "taxi_trips",
    "gridData": {"w": 40, "h": 9},
    "params": [
        {
            "paramName": "limit",
            "value": "100",
            "label": "Limit",
            "description": "Number of trips to fetch",
            "type": "number",
        }
    ],
    "data": {
        "table": {
            "showAll": True,
            "columnsDefs": [
                {"headerName": "Pickup", "field": "pickup"},
                {"headerName": "Dropoff", "field": "dropoff"},
                {"headerName": "Distance (mi)", "field": "distance", "cellDataType": "number"},
                {"headerName": "Fare ($)", "field": "fare", "cellDataType": "number"},
                {"headerName": "Pickup Zip", "field": "pickup_zip"},
                {"headerName": "Dropoff Zip", "field": "dropoff_zip"},
            ],
        }
    },
})
@router.get("/taxi/trips")
def taxi_trips(limit: int = Query(100, ge=1, le=10000)):
    rows = query(f"""
        SELECT
            tpep_pickup_datetime AS pickup,
            tpep_dropoff_datetime AS dropoff,
            trip_distance AS distance,
            fare_amount AS fare,
            pickup_zip,
            dropoff_zip
        FROM samples.nyctaxi.trips
        ORDER BY tpep_pickup_datetime DESC
        LIMIT {int(limit)}
    """)
    return [
        {**r, "pickup": r["pickup"].isoformat(), "dropoff": r["dropoff"].isoformat()}
        for r in rows
    ]
