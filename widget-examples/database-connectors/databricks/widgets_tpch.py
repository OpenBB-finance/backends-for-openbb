from fastapi import APIRouter, Query

from core import register_widget, query

router = APIRouter()

REGION_PARAM = {
    "paramName": "region",
    "label": "Region",
    "description": "Filter by customer region",
    "type": "endpoint",
    "optionsEndpoint": "tpch/regions",
    "value": "",
}


@router.get("/tpch/regions")
def tpch_regions():
    rows = query("SELECT r_name FROM samples.tpch.region ORDER BY r_name")
    options = [{"label": "All", "value": ""}]
    options.extend({"label": r["r_name"].title(), "value": r["r_name"]} for r in rows)
    return options


def region_filter(region: str) -> str:
    if not region:
        return ""
    escaped = region.replace("'", "''")
    return f"AND r.r_name = '{escaped}'"


@register_widget({
    "name": "TPC-H Order Metrics",
    "description": "Key metrics for the TPC-H orders sample dataset",
    "category": "database",
    "type": "metric",
    "endpoint": "tpch/metrics",
    "widgetId": "tpch_metrics",
    "gridData": {"w": 40, "h": 4},
    "params": [REGION_PARAM],
})
@router.get("/tpch/metrics")
def tpch_metrics(region: str = Query("")):
    flt = region_filter(region)
    row = query(f"""
        SELECT
            COUNT(*) AS orders,
            ROUND(SUM(o.o_totalprice) / 1e9, 2) AS revenue_bn,
            COUNT(DISTINCT o.o_custkey) AS customers,
            ROUND(AVG(o.o_totalprice)) AS avg_order
        FROM samples.tpch.orders o
        JOIN samples.tpch.customer c ON o.o_custkey = c.c_custkey
        JOIN samples.tpch.nation n ON c.c_nationkey = n.n_nationkey
        JOIN samples.tpch.region r ON n.n_regionkey = r.r_regionkey
        WHERE 1=1 {flt}
    """)[0]
    return [
        {"label": "Orders", "value": row["orders"]},
        {"label": "Revenue", "value": row["revenue_bn"], "unit": "bn USD"},
        {"label": "Customers", "value": row["customers"]},
        {"label": "Avg Order Value", "value": row["avg_order"], "unit": "USD"},
    ]


@register_widget({
    "name": "TPC-H Yearly Revenue",
    "description": "Orders and revenue by order year",
    "category": "database",
    "endpoint": "tpch/yearly-revenue",
    "widgetId": "tpch_yearly_revenue",
    "gridData": {"w": 20, "h": 9},
    "params": [REGION_PARAM],
    "data": {
        "table": {
            "showAll": True,
            "chartView": {"enabled": True, "chartType": "column"},
            "columnsDefs": [
                {"headerName": "Year", "field": "year", "cellDataType": "number"},
                {"headerName": "Orders", "field": "orders", "cellDataType": "number", "formatterFn": "int"},
                {"headerName": "Revenue ($M)", "field": "revenue_m", "cellDataType": "number"},
            ],
        }
    },
})
@router.get("/tpch/yearly-revenue")
def tpch_yearly_revenue(region: str = Query("")):
    flt = region_filter(region)
    return query(f"""
        SELECT
            YEAR(o.o_orderdate) AS year,
            COUNT(*) AS orders,
            ROUND(SUM(o.o_totalprice) / 1e6, 1) AS revenue_m
        FROM samples.tpch.orders o
        JOIN samples.tpch.customer c ON o.o_custkey = c.c_custkey
        JOIN samples.tpch.nation n ON c.c_nationkey = n.n_nationkey
        JOIN samples.tpch.region r ON n.n_regionkey = r.r_regionkey
        WHERE 1=1 {flt}
        GROUP BY YEAR(o.o_orderdate)
        ORDER BY year
    """)


@register_widget({
    "name": "TPC-H Revenue by Nation",
    "description": "Customer nations ranked by order revenue",
    "category": "database",
    "endpoint": "tpch/nation-revenue",
    "widgetId": "tpch_nation_revenue",
    "gridData": {"w": 20, "h": 9},
    "params": [REGION_PARAM],
    "data": {
        "table": {
            "showAll": True,
            "chartView": {"enabled": True, "chartType": "bar"},
            "columnsDefs": [
                {"headerName": "Nation", "field": "nation"},
                {"headerName": "Region", "field": "region"},
                {"headerName": "Orders", "field": "orders", "cellDataType": "number", "formatterFn": "int"},
                {"headerName": "Revenue ($M)", "field": "revenue_m", "cellDataType": "number"},
            ],
        }
    },
})
@router.get("/tpch/nation-revenue")
def tpch_nation_revenue(region: str = Query("")):
    flt = region_filter(region)
    return query(f"""
        SELECT
            INITCAP(n.n_name) AS nation,
            INITCAP(r.r_name) AS region,
            COUNT(*) AS orders,
            ROUND(SUM(o.o_totalprice) / 1e6, 1) AS revenue_m
        FROM samples.tpch.orders o
        JOIN samples.tpch.customer c ON o.o_custkey = c.c_custkey
        JOIN samples.tpch.nation n ON c.c_nationkey = n.n_nationkey
        JOIN samples.tpch.region r ON n.n_regionkey = r.r_regionkey
        WHERE 1=1 {flt}
        GROUP BY n.n_name, r.r_name
        ORDER BY revenue_m DESC
    """)


@register_widget({
    "name": "TPC-H Market Segments",
    "description": "Order revenue by customer market segment",
    "category": "database",
    "endpoint": "tpch/segment-revenue",
    "widgetId": "tpch_segment_revenue",
    "gridData": {"w": 20, "h": 9},
    "params": [REGION_PARAM],
    "data": {
        "table": {
            "showAll": True,
            "chartView": {"enabled": True, "chartType": "bar"},
            "columnsDefs": [
                {"headerName": "Segment", "field": "segment"},
                {"headerName": "Orders", "field": "orders", "cellDataType": "number", "formatterFn": "int"},
                {"headerName": "Revenue ($M)", "field": "revenue_m", "cellDataType": "number"},
                {"headerName": "Avg Order ($)", "field": "avg_order", "cellDataType": "number", "formatterFn": "int"},
            ],
        }
    },
})
@router.get("/tpch/segment-revenue")
def tpch_segment_revenue(region: str = Query("")):
    flt = region_filter(region)
    return query(f"""
        SELECT
            INITCAP(c.c_mktsegment) AS segment,
            COUNT(*) AS orders,
            ROUND(SUM(o.o_totalprice) / 1e6, 1) AS revenue_m,
            ROUND(AVG(o.o_totalprice)) AS avg_order
        FROM samples.tpch.orders o
        JOIN samples.tpch.customer c ON o.o_custkey = c.c_custkey
        JOIN samples.tpch.nation n ON c.c_nationkey = n.n_nationkey
        JOIN samples.tpch.region r ON n.n_regionkey = r.r_regionkey
        WHERE 1=1 {flt}
        GROUP BY c.c_mktsegment
        ORDER BY revenue_m DESC
    """)
