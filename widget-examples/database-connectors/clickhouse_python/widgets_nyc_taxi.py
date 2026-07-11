from fastapi import APIRouter, Query

from core import register_widget, async_cached_query

router = APIRouter()

ZONE_PARAM = {
    "paramName": "zone",
    "label": "Pickup Zone",
    "description": "Filter by pickup location",
    "type": "endpoint",
    "optionsEndpoint": "nyc_zones_list",
    "multiSelect": True,
    "value": "",
}

LIMIT_PARAM = {
    "paramName": "limit",
    "label": "Results",
    "description": "Number of zones to show",
    "type": "text",
    "value": "20",
    "options": [
        {"label": "10", "value": "10"},
        {"label": "20", "value": "20"},
        {"label": "50", "value": "50"},
        {"label": "100", "value": "100"},
    ],
}


@router.get("/nyc_zones_list")
async def nyc_zones_list():
    data = await async_cached_query("""
        SELECT pickup_ntaname AS zone
        FROM nyc_taxi.trips_small
        WHERE pickup_ntaname != ''
        GROUP BY zone ORDER BY zone
    """)
    options = [{"label": "All", "value": ""}]
    options.extend({"label": r["zone"], "value": r["zone"]} for r in data)
    return options


def zone_filter(zone: str) -> tuple[str, dict[str, str]]:
    if not zone:
        return "", {}
    zones = [z.strip() for z in zone.split(",") if z.strip()]
    if not zones:
        return "", {}
    parameters = {f"zone_{index}": value for index, value in enumerate(zones)}
    placeholders = ", ".join(f"{{{name}:String}}" for name in parameters)
    return f"AND pickup_ntaname IN ({placeholders})", parameters


@register_widget({
    "name": "NYC Taxi Metrics",
    "description": "Key NYC taxi trip metrics",
    "type": "metric",
    "endpoint": "nyc_trip_metrics",
    "gridData": {"w": 40, "h": 5},
    "source": ["NYC TLC"],
    "params": [ZONE_PARAM],
})
@router.get("/nyc_trip_metrics")
async def nyc_trip_metrics(zone: str = Query("")):
    flt, parameters = zone_filter(zone)
    data = await async_cached_query(f"""
        SELECT
            round(avg(fare_amount), 2) AS avg_fare,
            round(avg(trip_distance), 2) AS avg_distance,
            count() AS total_trips
        FROM nyc_taxi.trips_small
        WHERE 1=1 {flt}
    """, parameters)
    row = data[0]
    return [
        {"label": "Avg Fare", "value": row["avg_fare"], "unit": "USD"},
        {"label": "Avg Distance", "value": row["avg_distance"], "unit": "mi"},
        {"label": "Total Trips", "value": row["total_trips"]},
    ]


@register_widget({
    "name": "Trips by Hour",
    "description": "NYC taxi trip volume and averages by hour of day",
    "type": "table",
    "endpoint": "nyc_trips_by_hour",
    "gridData": {"w": 20, "h": 14},
    "source": ["NYC TLC"],
    "params": [ZONE_PARAM],
    "data": {
        "table": {
            "columnsDefs": [
                {"field": "hour", "headerName": "Hour", "width": 80, "cellDataType": "number"},
                {"field": "trips", "headerName": "Trips", "width": 120, "cellDataType": "number", "formatterFn": "int"},
                {"field": "avg_fare", "headerName": "Avg Fare (USD)", "width": 140, "cellDataType": "number", "formatterFn": "none"},
                {"field": "avg_distance", "headerName": "Avg Distance (mi)", "width": 160, "cellDataType": "number", "formatterFn": "none"},
                {"field": "avg_passengers", "headerName": "Avg Passengers", "width": 140, "cellDataType": "number", "formatterFn": "none"},
            ]
        }
    },
})
@router.get("/nyc_trips_by_hour")
async def nyc_trips_by_hour(zone: str = Query("")):
    flt, parameters = zone_filter(zone)
    return await async_cached_query(f"""
        SELECT
            toHour(pickup_datetime) AS hour,
            count() AS trips,
            round(avg(fare_amount), 2) AS avg_fare,
            round(avg(trip_distance), 2) AS avg_distance,
            round(avg(passenger_count), 1) AS avg_passengers
        FROM nyc_taxi.trips_small
        WHERE 1=1 {flt}
        GROUP BY hour ORDER BY hour
    """, parameters)


@register_widget({
    "name": "Trips per Zone",
    "description": "Pickup zones ranked by number of trips",
    "type": "table",
    "endpoint": "nyc_trips_per_zone",
    "gridData": {"w": 20, "h": 14},
    "source": ["NYC TLC"],
    "params": [LIMIT_PARAM, ZONE_PARAM],
    "data": {
        "table": {
            "index": "zone",
            "showAll": True,
            "columnsDefs": [
                {
                    "field": "zone",
                    "headerName": "Pickup Zone",
                    "width": 280,
                    "cellDataType": "text",
                    "pinned": "left",
                    "renderFn": "cellOnClick",
                    "renderFnParams": {
                        "actionType": "groupBy",
                        "groupBy": {"paramName": "zone"},
                    },
                },
                {"field": "trips", "headerName": "Trips", "width": 120, "cellDataType": "number", "formatterFn": "int"},
            ],
        }
    },
})
@router.get("/nyc_trips_per_zone")
async def nyc_trips_per_zone(
    limit: int = Query(20, ge=1, le=100),
    zone: str = Query(""),
):
    flt, parameters = zone_filter(zone)
    return await async_cached_query(f"""
        SELECT
            pickup_ntaname AS zone,
            count() AS trips
        FROM nyc_taxi.trips_small
        WHERE pickup_ntaname != '' {flt}
        GROUP BY zone
        ORDER BY trips DESC
        LIMIT {int(limit)}
    """, parameters)


@register_widget({
    "name": "Avg Fare per Zone",
    "description": "Pickup zones ranked by average fare",
    "type": "table",
    "endpoint": "nyc_avg_fare_per_zone",
    "gridData": {"w": 20, "h": 14},
    "source": ["NYC TLC"],
    "params": [LIMIT_PARAM, ZONE_PARAM],
    "data": {
        "table": {
            "index": "zone",
            "showAll": True,
            "columnsDefs": [
                {
                    "field": "zone",
                    "headerName": "Pickup Zone",
                    "width": 280,
                    "cellDataType": "text",
                    "pinned": "left",
                    "renderFn": "cellOnClick",
                    "renderFnParams": {
                        "actionType": "groupBy",
                        "groupBy": {"paramName": "zone"},
                    },
                },
                {"field": "avg_fare", "headerName": "Avg Fare (USD)", "width": 140, "cellDataType": "number", "formatterFn": "none"},
            ],
        }
    },
})
@router.get("/nyc_avg_fare_per_zone")
async def nyc_avg_fare_per_zone(
    limit: int = Query(20, ge=1, le=100),
    zone: str = Query(""),
):
    flt, parameters = zone_filter(zone)
    return await async_cached_query(f"""
        SELECT
            pickup_ntaname AS zone,
            round(avg(fare_amount), 2) AS avg_fare
        FROM nyc_taxi.trips_small
        WHERE pickup_ntaname != '' {flt}
        GROUP BY zone
        ORDER BY avg_fare DESC
        LIMIT {int(limit)}
    """, parameters)


@register_widget({
    "name": "Fare Distribution",
    "description": "Distribution of NYC taxi fares in $5 buckets",
    "type": "table",
    "endpoint": "nyc_fare_distribution",
    "gridData": {"w": 40, "h": 14},
    "source": ["NYC TLC"],
    "params": [ZONE_PARAM],
    "data": {
        "table": {
            "columnsDefs": [
                {"field": "fare_range", "headerName": "Fare Range", "width": 140, "cellDataType": "text"},
                {"field": "trips", "headerName": "Trips", "width": 120, "cellDataType": "number", "formatterFn": "int"},
                {"field": "pct", "headerName": "% of Total", "width": 120, "cellDataType": "number", "formatterFn": "none"},
                {"field": "avg_tip", "headerName": "Avg Tip (USD)", "width": 130, "cellDataType": "number", "formatterFn": "none"},
                {"field": "avg_distance", "headerName": "Avg Distance (mi)", "width": 160, "cellDataType": "number", "formatterFn": "none"},
            ]
        }
    },
})
@router.get("/nyc_fare_distribution")
async def nyc_fare_distribution(zone: str = Query("")):
    flt, parameters = zone_filter(zone)
    return await async_cached_query(f"""
        SELECT
            concat('$', toString(toUInt32(floor(fare_amount / 5) * 5)), '-$', toString(toUInt32(floor(fare_amount / 5) * 5 + 5))) AS fare_range,
            count() AS trips,
            round(count() * 100.0 / (SELECT count() FROM nyc_taxi.trips_small WHERE fare_amount > 0 AND fare_amount < 100 {flt}), 1) AS pct,
            round(avg(tip_amount), 2) AS avg_tip,
            round(avg(trip_distance), 2) AS avg_distance
        FROM nyc_taxi.trips_small
        WHERE fare_amount > 0 AND fare_amount < 100 {flt}
        GROUP BY fare_range, floor(fare_amount / 5)
        ORDER BY floor(fare_amount / 5)
    """, parameters)
