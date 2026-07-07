from fastapi import APIRouter, Query

from core import register_widget, query

router = APIRouter()

COUNTRY_PARAM = {
    "paramName": "country",
    "label": "Country",
    "description": "Filter by destination country",
    "type": "endpoint",
    "optionsEndpoint": "wanderbricks/countries",
    "value": "",
}


@router.get("/wanderbricks/countries")
def wanderbricks_countries():
    rows = query("SELECT DISTINCT country FROM samples.wanderbricks.destinations ORDER BY country")
    options = [{"label": "All", "value": ""}]
    options.extend({"label": r["country"], "value": r["country"]} for r in rows)
    return options


def country_join_filter(country: str) -> str:
    if not country:
        return ""
    escaped = country.replace("'", "''")
    return f"AND d.country = '{escaped}'"


@register_widget({
    "name": "Wanderbricks Metrics",
    "description": "Key metrics for the Wanderbricks travel platform sample dataset",
    "category": "database",
    "type": "metric",
    "endpoint": "wanderbricks/metrics",
    "widgetId": "wanderbricks_metrics",
    "gridData": {"w": 40, "h": 4},
})
@router.get("/wanderbricks/metrics")
def wanderbricks_metrics():
    row = query("""
        SELECT
            (SELECT COUNT(*) FROM samples.wanderbricks.bookings) AS bookings,
            (SELECT ROUND(SUM(total_amount)) FROM samples.wanderbricks.bookings) AS revenue,
            (SELECT COUNT(*) FROM samples.wanderbricks.properties) AS properties,
            (SELECT ROUND(AVG(rating), 2) FROM samples.wanderbricks.reviews WHERE NOT is_deleted) AS avg_rating
    """)[0]
    return [
        {"label": "Bookings", "value": row["bookings"]},
        {"label": "Booking Revenue", "value": row["revenue"], "unit": "USD"},
        {"label": "Properties", "value": row["properties"]},
        {"label": "Avg Review Rating", "value": row["avg_rating"], "unit": "/ 5"},
    ]


@register_widget({
    "name": "Wanderbricks Monthly Bookings",
    "description": "Bookings and revenue by check-in month",
    "category": "database",
    "endpoint": "wanderbricks/monthly-bookings",
    "widgetId": "wanderbricks_monthly_bookings",
    "gridData": {"w": 40, "h": 9},
    "params": [COUNTRY_PARAM],
    "data": {
        "table": {
            "showAll": True,
            "chartView": {"enabled": True, "chartType": "line"},
            "columnsDefs": [
                {"headerName": "Month", "field": "month"},
                {"headerName": "Bookings", "field": "bookings", "cellDataType": "number", "formatterFn": "int"},
                {"headerName": "Revenue ($)", "field": "revenue", "cellDataType": "number", "formatterFn": "int"},
                {"headerName": "Avg Guests", "field": "avg_guests", "cellDataType": "number"},
            ],
        }
    },
})
@router.get("/wanderbricks/monthly-bookings")
def wanderbricks_monthly_bookings(country: str = Query("")):
    flt = country_join_filter(country)
    return query(f"""
        SELECT
            DATE_FORMAT(b.check_in, 'yyyy-MM') AS month,
            COUNT(*) AS bookings,
            ROUND(SUM(b.total_amount)) AS revenue,
            ROUND(AVG(b.guests_count), 1) AS avg_guests
        FROM samples.wanderbricks.bookings b
        JOIN samples.wanderbricks.properties p ON b.property_id = p.property_id
        JOIN samples.wanderbricks.destinations d ON p.destination_id = d.destination_id
        WHERE 1=1 {flt}
        GROUP BY DATE_FORMAT(b.check_in, 'yyyy-MM')
        ORDER BY month
    """)


@register_widget({
    "name": "Wanderbricks Top Destinations",
    "description": "Destinations ranked by booking revenue",
    "category": "database",
    "endpoint": "wanderbricks/top-destinations",
    "widgetId": "wanderbricks_top_destinations",
    "gridData": {"w": 20, "h": 9},
    "params": [COUNTRY_PARAM],
    "data": {
        "table": {
            "showAll": True,
            "chartView": {"enabled": True, "chartType": "bar"},
            "columnsDefs": [
                {"headerName": "Destination", "field": "destination"},
                {"headerName": "Country", "field": "country"},
                {"headerName": "Bookings", "field": "bookings", "cellDataType": "number", "formatterFn": "int"},
                {"headerName": "Revenue ($)", "field": "revenue", "cellDataType": "number", "formatterFn": "int"},
            ],
        }
    },
})
@router.get("/wanderbricks/top-destinations")
def wanderbricks_top_destinations(country: str = Query("")):
    flt = country_join_filter(country)
    return query(f"""
        SELECT
            d.destination,
            d.country,
            COUNT(*) AS bookings,
            ROUND(SUM(b.total_amount)) AS revenue
        FROM samples.wanderbricks.bookings b
        JOIN samples.wanderbricks.properties p ON b.property_id = p.property_id
        JOIN samples.wanderbricks.destinations d ON p.destination_id = d.destination_id
        WHERE 1=1 {flt}
        GROUP BY d.destination, d.country
        ORDER BY revenue DESC
        LIMIT 15
    """)


@register_widget({
    "name": "Wanderbricks Property Types",
    "description": "Property types by count, price and rating",
    "category": "database",
    "endpoint": "wanderbricks/property-types",
    "widgetId": "wanderbricks_property_types",
    "gridData": {"w": 20, "h": 9},
    "data": {
        "table": {
            "showAll": True,
            "chartView": {"enabled": True, "chartType": "bar"},
            "columnsDefs": [
                {"headerName": "Type", "field": "property_type"},
                {"headerName": "Properties", "field": "properties", "cellDataType": "number", "formatterFn": "int"},
                {"headerName": "Avg Price ($)", "field": "avg_price", "cellDataType": "number"},
                {"headerName": "Avg Rating", "field": "avg_rating", "cellDataType": "number"},
            ],
        }
    },
})
@router.get("/wanderbricks/property-types")
def wanderbricks_property_types():
    return query("""
        SELECT
            p.property_type,
            COUNT(DISTINCT p.property_id) AS properties,
            ROUND(AVG(p.base_price), 2) AS avg_price,
            ROUND(AVG(r.rating), 2) AS avg_rating
        FROM samples.wanderbricks.properties p
        LEFT JOIN samples.wanderbricks.reviews r
            ON p.property_id = r.property_id AND NOT r.is_deleted
        GROUP BY p.property_type
        ORDER BY properties DESC
    """)
