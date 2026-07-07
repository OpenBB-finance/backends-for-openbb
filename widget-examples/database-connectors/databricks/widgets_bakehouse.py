from fastapi import APIRouter, Query

from core import register_widget, query

router = APIRouter()

PRODUCT_PARAM = {
    "paramName": "product",
    "label": "Product",
    "description": "Filter by cookie product",
    "type": "endpoint",
    "optionsEndpoint": "bakehouse/products",
    "value": "",
}


@router.get("/bakehouse/products")
def bakehouse_products():
    rows = query("SELECT DISTINCT product FROM samples.bakehouse.sales_transactions ORDER BY product")
    options = [{"label": "All", "value": ""}]
    options.extend({"label": r["product"], "value": r["product"]} for r in rows)
    return options


def product_filter(product: str) -> str:
    if not product:
        return ""
    escaped = product.replace("'", "''")
    return f"AND product = '{escaped}'"


@register_widget({
    "name": "Bakehouse Metrics",
    "description": "Key sales metrics for the Bakehouse cookie franchise sample dataset",
    "category": "database",
    "type": "metric",
    "endpoint": "bakehouse/metrics",
    "widgetId": "bakehouse_metrics",
    "gridData": {"w": 40, "h": 4},
    "params": [PRODUCT_PARAM],
})
@router.get("/bakehouse/metrics")
def bakehouse_metrics(product: str = Query("")):
    flt = product_filter(product)
    row = query(f"""
        SELECT
            SUM(totalPrice) AS revenue,
            COUNT(*) AS transactions,
            COUNT(DISTINCT franchiseID) AS franchises,
            COUNT(DISTINCT customerID) AS customers
        FROM samples.bakehouse.sales_transactions
        WHERE 1=1 {flt}
    """)[0]
    return [
        {"label": "Revenue", "value": row["revenue"], "unit": "USD"},
        {"label": "Transactions", "value": row["transactions"]},
        {"label": "Franchises", "value": row["franchises"]},
        {"label": "Customers", "value": row["customers"]},
    ]


@register_widget({
    "name": "Bakehouse Sales by Product",
    "description": "Cookie products ranked by revenue",
    "category": "database",
    "endpoint": "bakehouse/product-sales",
    "widgetId": "bakehouse_product_sales",
    "gridData": {"w": 20, "h": 9},
    "data": {
        "table": {
            "showAll": True,
            "chartView": {"enabled": True, "chartType": "bar"},
            "columnsDefs": [
                {"headerName": "Product", "field": "product"},
                {"headerName": "Units", "field": "units", "cellDataType": "number", "formatterFn": "int"},
                {"headerName": "Revenue ($)", "field": "revenue", "cellDataType": "number", "formatterFn": "int"},
            ],
        }
    },
})
@router.get("/bakehouse/product-sales")
def bakehouse_product_sales():
    return query("""
        SELECT
            product,
            SUM(quantity) AS units,
            SUM(totalPrice) AS revenue
        FROM samples.bakehouse.sales_transactions
        GROUP BY product
        ORDER BY revenue DESC
    """)


@register_widget({
    "name": "Bakehouse Sales by City",
    "description": "Franchise cities ranked by revenue",
    "category": "database",
    "endpoint": "bakehouse/city-sales",
    "widgetId": "bakehouse_city_sales",
    "gridData": {"w": 20, "h": 9},
    "params": [PRODUCT_PARAM],
    "data": {
        "table": {
            "showAll": True,
            "chartView": {"enabled": True, "chartType": "bar"},
            "columnsDefs": [
                {"headerName": "City", "field": "city"},
                {"headerName": "Country", "field": "country"},
                {"headerName": "Transactions", "field": "transactions", "cellDataType": "number", "formatterFn": "int"},
                {"headerName": "Revenue ($)", "field": "revenue", "cellDataType": "number", "formatterFn": "int"},
            ],
        }
    },
})
@router.get("/bakehouse/city-sales")
def bakehouse_city_sales(product: str = Query("")):
    flt = product_filter(product)
    return query(f"""
        SELECT
            f.city,
            f.country,
            COUNT(*) AS transactions,
            SUM(t.totalPrice) AS revenue
        FROM samples.bakehouse.sales_transactions t
        JOIN samples.bakehouse.sales_franchises f ON t.franchiseID = f.franchiseID
        WHERE 1=1 {flt}
        GROUP BY f.city, f.country
        ORDER BY revenue DESC
        LIMIT 20
    """)


@register_widget({
    "name": "Bakehouse Hourly Sales",
    "description": "Transactions and revenue by hour of day",
    "category": "database",
    "endpoint": "bakehouse/hourly-sales",
    "widgetId": "bakehouse_hourly_sales",
    "gridData": {"w": 20, "h": 9},
    "params": [PRODUCT_PARAM],
    "data": {
        "table": {
            "showAll": True,
            "chartView": {"enabled": True, "chartType": "column"},
            "columnsDefs": [
                {"headerName": "Hour", "field": "hour", "cellDataType": "number"},
                {"headerName": "Transactions", "field": "transactions", "cellDataType": "number", "formatterFn": "int"},
                {"headerName": "Revenue ($)", "field": "revenue", "cellDataType": "number", "formatterFn": "int"},
            ],
        }
    },
})
@router.get("/bakehouse/hourly-sales")
def bakehouse_hourly_sales(product: str = Query("")):
    flt = product_filter(product)
    return query(f"""
        SELECT
            HOUR(dateTime) AS hour,
            COUNT(*) AS transactions,
            SUM(totalPrice) AS revenue
        FROM samples.bakehouse.sales_transactions
        WHERE 1=1 {flt}
        GROUP BY HOUR(dateTime)
        ORDER BY hour
    """)


@register_widget({
    "name": "Bakehouse Customer Reviews",
    "description": "Latest customer reviews across franchises",
    "category": "database",
    "type": "markdown",
    "endpoint": "bakehouse/reviews",
    "widgetId": "bakehouse_reviews",
    "gridData": {"w": 20, "h": 9},
    "params": [
        {
            "paramName": "limit",
            "value": "5",
            "label": "Reviews",
            "description": "Number of reviews to show",
            "type": "number",
        }
    ],
})
@router.get("/bakehouse/reviews")
def bakehouse_reviews(limit: int = Query(5, ge=1, le=50)):
    rows = query(f"""
        SELECT
            r.review,
            r.review_date,
            f.city,
            f.country
        FROM samples.bakehouse.media_customer_reviews r
        LEFT JOIN samples.bakehouse.sales_franchises f ON r.franchiseID = f.franchiseID
        ORDER BY r.review_date DESC
        LIMIT {int(limit)}
    """)
    if not rows:
        return "No reviews found."
    sections = []
    for r in rows:
        location = ", ".join(x for x in [r["city"], r["country"]] if x) or "Unknown location"
        date = r["review_date"].date().isoformat() if r["review_date"] else "n/a"
        sections.append(f"**{location}** — *{date}*\n\n> {r['review']}")
    return "\n\n---\n\n".join(sections)
