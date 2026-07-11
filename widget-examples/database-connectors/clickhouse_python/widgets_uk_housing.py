from fastapi import APIRouter

from core import register_widget, async_cached_query

router = APIRouter()


@register_widget({
    "name": "UK Housing Metrics",
    "description": "Key UK property market metrics",
    "type": "metric",
    "endpoint": "uk_price_metrics",
    "gridData": {"w": 40, "h": 5},
    "source": ["UK Land Registry"],
})
@router.get("/uk_price_metrics")
async def uk_price_metrics():
    overview = await async_cached_query("""
        SELECT round(avg(price)) AS avg_price, count() AS total_transactions
        FROM uk.uk_price_paid
    """)
    yoy = await async_cached_query("""
        SELECT toYear(date) AS year, round(avg(price)) AS avg_price
        FROM uk.uk_price_paid
        GROUP BY year ORDER BY year DESC LIMIT 2
    """)

    row = overview[0]
    if len(yoy) >= 2:
        change = round((yoy[0]["avg_price"] - yoy[1]["avg_price"]) / yoy[1]["avg_price"] * 100, 1)
    else:
        change = 0

    return [
        {"label": "Avg Price (All Time)", "value": row["avg_price"], "unit": "GBP"},
        {"label": "Total Transactions", "value": row["total_transactions"]},
        {"label": "YoY Change", "value": change, "unit": "%"},
    ]


@register_widget({
    "name": "Avg Price by Year",
    "description": "Average UK house price per year with transaction volume",
    "type": "table",
    "endpoint": "uk_avg_price_by_year",
    "gridData": {"w": 20, "h": 14},
    "source": ["UK Land Registry"],
    "data": {
        "table": {
            "columnsDefs": [
                {"field": "year", "headerName": "Year", "width": 90, "cellDataType": "number"},
                {"field": "avg_price", "headerName": "Avg Price (GBP)", "width": 150, "cellDataType": "number", "formatterFn": "int"},
                {"field": "min_price", "headerName": "Min Price", "width": 120, "cellDataType": "number", "formatterFn": "int"},
                {"field": "max_price", "headerName": "Max Price", "width": 130, "cellDataType": "number", "formatterFn": "int"},
                {"field": "transactions", "headerName": "Transactions", "width": 130, "cellDataType": "number", "formatterFn": "int"},
            ]
        }
    },
})
@router.get("/uk_avg_price_by_year")
async def uk_avg_price_by_year():
    return await async_cached_query("""
        SELECT
            toYear(date) AS year,
            round(avg(price)) AS avg_price,
            min(price) AS min_price,
            max(price) AS max_price,
            count() AS transactions
        FROM uk.uk_price_paid
        GROUP BY year ORDER BY year
    """)


@register_widget({
    "name": "Top 20 Most Expensive Towns",
    "description": "UK towns ranked by average property price",
    "type": "table",
    "endpoint": "uk_top_towns",
    "gridData": {"w": 20, "h": 14},
    "source": ["UK Land Registry"],
    "data": {
        "table": {
            "columnsDefs": [
                {"field": "rank", "headerName": "#", "width": 60, "cellDataType": "number"},
                {"field": "town", "headerName": "Town", "width": 180, "cellDataType": "text"},
                {"field": "avg_price", "headerName": "Avg Price (GBP)", "width": 150, "cellDataType": "number", "formatterFn": "int"},
                {"field": "transactions", "headerName": "Transactions", "width": 130, "cellDataType": "number", "formatterFn": "int"},
            ]
        }
    },
})
@router.get("/uk_top_towns")
async def uk_top_towns():
    data = await async_cached_query("""
        SELECT
            town,
            round(avg(price)) AS avg_price,
            count() AS transactions
        FROM uk.uk_price_paid
        WHERE town != ''
        GROUP BY town
        HAVING transactions > 1000
        ORDER BY avg_price DESC
        LIMIT 20
    """)
    return [{"rank": i, **r} for i, r in enumerate(data, 1)]


@register_widget({
    "name": "Price by Property Type",
    "description": "Average price per year broken down by property type",
    "type": "table",
    "endpoint": "uk_price_by_type",
    "gridData": {"w": 40, "h": 14},
    "source": ["UK Land Registry"],
    "data": {
        "table": {
            "index": "year",
            "showAll": True,
            "columnsDefs": [
                {"field": "year", "headerName": "Year", "width": 90, "cellDataType": "number"},
                {"field": "detached", "headerName": "Detached", "width": 130, "cellDataType": "number", "formatterFn": "int"},
                {"field": "semi_detached", "headerName": "Semi-Detached", "width": 140, "cellDataType": "number", "formatterFn": "int"},
                {"field": "terraced", "headerName": "Terraced", "width": 130, "cellDataType": "number", "formatterFn": "int"},
                {"field": "flat", "headerName": "Flat", "width": 130, "cellDataType": "number", "formatterFn": "int"},
                {"field": "other", "headerName": "Other", "width": 130, "cellDataType": "number", "formatterFn": "int"},
            ]
        }
    },
})
@router.get("/uk_price_by_type")
async def uk_price_by_type():
    return await async_cached_query("""
        SELECT
            toYear(date) AS year,
            round(avgIf(price, type = 'detached')) AS detached,
            round(avgIf(price, type = 'semi-detached')) AS semi_detached,
            round(avgIf(price, type = 'terraced')) AS terraced,
            round(avgIf(price, type = 'flat')) AS flat,
            round(avgIf(price, type = 'other')) AS other
        FROM uk.uk_price_paid
        GROUP BY year
        ORDER BY year
    """)
