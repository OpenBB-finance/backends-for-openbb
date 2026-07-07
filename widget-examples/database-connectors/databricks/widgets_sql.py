import json

from fastapi import APIRouter, Body

from core import CATALOG, DataFormat, OmniWidgetResponse, register_widget, query

router = APIRouter()

READ_ONLY_STATEMENTS = {"select", "with", "show", "describe", "desc", "explain"}

DEFAULT_SQL = """SELECT product, SUM(totalPrice) AS revenue
FROM samples.bakehouse.sales_transactions
GROUP BY product
ORDER BY revenue DESC"""

SQL_HELP = f"""### Databricks SQL Explorer

Run read-only SQL against the `{CATALOG}` catalog.

**Example queries:**
- `SHOW SCHEMAS IN samples`
- `SHOW TABLES IN samples.wanderbricks`
- `DESCRIBE samples.nyctaxi.trips`
- `SELECT * FROM samples.tpch.orders LIMIT 10`
- `SELECT product, SUM(totalPrice) AS revenue FROM samples.bakehouse.sales_transactions GROUP BY product ORDER BY revenue DESC`
"""


def is_read_only(sql_text: str) -> bool:
    stripped = sql_text.strip().rstrip(";")
    if ";" in stripped:
        return False
    first_word = stripped.split(None, 1)[0].lower() if stripped.split() else ""
    return first_word in READ_ONLY_STATEMENTS


@router.get("/schemas")
def get_schemas():
    rows = query(f"SHOW SCHEMAS IN {CATALOG}")
    return [r["databaseName"] for r in rows if r["databaseName"] != "information_schema"]


@register_widget({
    "name": "Databricks Tables",
    "description": "Browse available tables in Databricks schemas",
    "category": "database",
    "endpoint": "tables",
    "widgetId": "databricks_tables",
    "gridData": {"w": 13, "h": 9},
    "params": [
        {
            "paramName": "schema",
            "label": "Schema",
            "description": "Select a Databricks schema",
            "type": "endpoint",
            "optionsEndpoint": "schemas",
            "value": "nyctaxi",
        }
    ],
    "data": {
        "table": {
            "showAll": True,
            "columnsDefs": [{"headerName": "Table", "field": "table"}],
        }
    },
})
@router.get("/tables")
def get_tables(schema: str = "nyctaxi"):
    escaped = schema.replace("`", "")
    rows = query(f"SHOW TABLES IN {CATALOG}.`{escaped}`")
    return [{"table": r["tableName"]} for r in rows]


def _omni_sql_widget(widget_id: str, name: str, description: str, default_sql: str, param_description: str):
    """Widget config for an omni SQL widget bound to the shared /omni-sql endpoint."""
    return {
        "name": name,
        "description": description,
        "category": "database",
        "type": "omni",
        "endpoint": "omni-sql",
        "widgetId": widget_id,
        "gridData": {"w": 20, "h": 10},
        "params": [
            {
                "paramName": "prompt",
                "type": "text",
                "description": param_description,
                "label": "SQL Query",
                "value": default_sql,
                "show": False,
                "language": "sql",
            }
        ],
    }


# One SQL widget per sample database: name, table metadata for the editor
# tooltip, and a curated starter query. The same queries are seeded into the
# SQL Explorer app layout via state.params.prompt in apps.json.
SCHEMA_SQL_WIDGETS = {
    "omni_sql_nyctaxi": {
        "name": "SQL: NYC Taxi",
        "description": "Query samples.nyctaxi - NYC yellow cab trips",
        "metadata": "Table: samples.nyctaxi.trips (tpep_pickup_datetime, tpep_dropoff_datetime, trip_distance, fare_amount, pickup_zip, dropoff_zip)",
        "sql": (
            "SELECT pickup_zip, COUNT(*) AS trips,\n"
            "       ROUND(AVG(fare_amount), 2) AS avg_fare,\n"
            "       ROUND(AVG(trip_distance), 2) AS avg_distance\n"
            "FROM samples.nyctaxi.trips\n"
            "GROUP BY pickup_zip\n"
            "ORDER BY trips DESC\n"
            "LIMIT 15"
        ),
    },
    "omni_sql_bakehouse": {
        "name": "SQL: Bakehouse",
        "description": "Query samples.bakehouse - cookie franchise sales",
        "metadata": (
            "Tables: samples.bakehouse.sales_transactions (product, quantity, totalPrice, paymentMethod, franchiseID, dateTime), "
            "sales_franchises (franchiseID, name, city, country, size), sales_customers, sales_suppliers, media_customer_reviews (review, franchiseID, review_date)"
        ),
        "sql": (
            "SELECT f.name, f.city, f.country,\n"
            "       SUM(t.totalPrice) AS revenue, COUNT(*) AS transactions\n"
            "FROM samples.bakehouse.sales_transactions t\n"
            "JOIN samples.bakehouse.sales_franchises f ON t.franchiseID = f.franchiseID\n"
            "GROUP BY f.name, f.city, f.country\n"
            "ORDER BY revenue DESC\n"
            "LIMIT 15"
        ),
    },
    "omni_sql_wanderbricks": {
        "name": "SQL: Wanderbricks",
        "description": "Query samples.wanderbricks - vacation rental platform",
        "metadata": (
            "Tables: samples.wanderbricks.bookings (property_id, check_in, check_out, guests_count, total_amount, status), "
            "properties (property_id, destination_id, title, base_price, property_type), destinations (destination_id, destination, country), "
            "reviews (property_id, rating, comment, is_deleted), hosts, users, payments"
        ),
        "sql": (
            "SELECT d.destination, d.country,\n"
            "       ROUND(AVG(r.rating), 2) AS avg_rating, COUNT(*) AS reviews\n"
            "FROM samples.wanderbricks.reviews r\n"
            "JOIN samples.wanderbricks.properties p ON r.property_id = p.property_id\n"
            "JOIN samples.wanderbricks.destinations d ON p.destination_id = d.destination_id\n"
            "WHERE NOT r.is_deleted\n"
            "GROUP BY d.destination, d.country\n"
            "HAVING COUNT(*) > 100\n"
            "ORDER BY avg_rating DESC\n"
            "LIMIT 15"
        ),
    },
    "omni_sql_tpch": {
        "name": "SQL: TPC-H",
        "description": "Query samples.tpch - classic supply chain benchmark",
        "metadata": (
            "Tables: samples.tpch.orders (o_orderkey, o_custkey, o_totalprice, o_orderdate, o_orderpriority), "
            "customer (c_custkey, c_name, c_nationkey, c_mktsegment, c_acctbal), lineitem, part, partsupp, supplier, nation, region"
        ),
        "sql": (
            "SELECT o_orderpriority AS priority,\n"
            "       COUNT(*) AS orders,\n"
            "       ROUND(SUM(o_totalprice) / 1e6, 1) AS revenue_m\n"
            "FROM samples.tpch.orders\n"
            "GROUP BY o_orderpriority\n"
            "ORDER BY priority"
        ),
    },
    "omni_sql_accuweather": {
        "name": "SQL: AccuWeather",
        "description": "Query samples.accuweather - daily and hourly weather forecasts",
        "metadata": (
            "Tables: samples.accuweather.forecast_daily_calendar_metric / _imperial (city_name, country_code, date, "
            "minutes_of_sun_total, humidity_relative_avg, cloud_cover_perc_avg, has_rain, has_snow), forecast_hourly_*, historical_*"
        ),
        "sql": (
            "SELECT city_name, country_code,\n"
            "       ROUND(AVG(minutes_of_sun_total) / 60, 1) AS avg_sun_hours,\n"
            "       ROUND(AVG(humidity_relative_avg), 1) AS avg_humidity\n"
            "FROM samples.accuweather.forecast_daily_calendar_metric\n"
            "GROUP BY city_name, country_code\n"
            "ORDER BY avg_sun_hours DESC\n"
            "LIMIT 15"
        ),
    },
    "omni_sql_healthverity": {
        "name": "SQL: HealthVerity",
        "description": "Query samples.healthverity - synthetic medical claims",
        "metadata": (
            "Table: samples.healthverity.claims_sample_synthetic (hvid, claim_id, claim_type, date_service, "
            "diagnosis_code, procedure_code, patient_gender, patient_year_of_birth, patient_state)"
        ),
        "sql": (
            "SELECT patient_state,\n"
            "       COUNT(*) AS claims,\n"
            "       COUNT(DISTINCT hvid) AS patients\n"
            "FROM samples.healthverity.claims_sample_synthetic\n"
            "GROUP BY patient_state\n"
            "ORDER BY claims DESC\n"
            "LIMIT 15"
        ),
    },
}

for _widget_id, _cfg in SCHEMA_SQL_WIDGETS.items():
    register_widget(
        _omni_sql_widget(
            widget_id=_widget_id,
            name=_cfg["name"],
            description=_cfg["description"],
            default_sql=_cfg["sql"],
            param_description=f"Read-only SQL. {_cfg['metadata']}",
        )
    )(lambda: None)


@register_widget({
    "name": "Databricks SQL Query",
    "description": "Run read-only SQL queries against the Databricks samples catalog",
    "category": "database",
    "type": "omni",
    "endpoint": "omni-sql",
    "widgetId": "databricks_omni_sql",
    "gridData": {"w": 27, "h": 9},
    "params": [
        {
            "paramName": "prompt",
            "type": "text",
            "description": (
                "SQL to run against the Databricks samples catalog. "
                "Read-only statements only (SELECT, SHOW, DESCRIBE, EXPLAIN, WITH). "
                "Example: SELECT * FROM samples.nyctaxi.trips LIMIT 10"
            ),
            "label": "SQL Query",
            "value": DEFAULT_SQL,
            "show": False,
            "language": "sql",
        }
    ],
})
@router.post("/omni-sql")
async def omni_sql(data: str | dict = Body(...)):
    """Omni widget executing read-only SQL against Databricks"""
    if isinstance(data, str):
        data = json.loads(data)

    sql_text = (data.get("prompt") or "").strip() or DEFAULT_SQL

    if not is_read_only(sql_text):
        return OmniWidgetResponse(
            content=(
                "### Only read-only queries are allowed\n\n"
                "Single statements starting with `SELECT`, `WITH`, `SHOW`, "
                "`DESCRIBE` or `EXPLAIN`.\n\n" + SQL_HELP
            ),
            data_format=DataFormat(data_type="object", parse_as="text"),
            citable=False,
        )

    try:
        rows = query(sql_text, ttl=0)
    except Exception as exc:
        return OmniWidgetResponse(
            content=f"### SQL Error\n\n**Query:**\n```sql\n{sql_text}\n```\n\n**Error:** {exc}\n\n{SQL_HELP}",
            data_format=DataFormat(data_type="object", parse_as="text"),
            citable=False,
        )

    if not rows:
        return OmniWidgetResponse(
            content="Query returned no rows.",
            data_format=DataFormat(data_type="object", parse_as="text"),
            citable=False,
        )

    # Serialize dates/decimals for JSON transport
    content = [
        {k: (v.isoformat() if hasattr(v, "isoformat") else float(v) if type(v).__name__ == "Decimal" else v)
         for k, v in row.items()}
        for row in rows[:1000]
    ]
    return OmniWidgetResponse(
        content=content,
        data_format=DataFormat(data_type="object", parse_as="table"),
        citable=True,
    )
