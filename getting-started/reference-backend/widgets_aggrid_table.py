from datetime import datetime
from fastapi import APIRouter

from core import register_widget, WIDGETS

router = APIRouter()

@register_widget({
    "name": "Table Widget with Column Definitions",
    "description": "A table widget with custom column definitions",
    "type": "table",
    "endpoint": "table_widget_with_column_definitions",
    "gridData": {"w": 20, "h": 6},
    "data": {
        "table": {
            "columnsDefs": [
                {
                    "field": "stock",
                    "headerName": "Stock",
                    "cellDataType": "text",
                    "chartDataType": "category",
                },
                {
                    "field": "price",
                    "headerName": "Price ($)",
                    "cellDataType": "number",
                    "chartDataType": "series",
                },
                {
                    "field": "change",
                    "headerName": "24h Change",
                    "cellDataType": "number",
                    "chartDataType": "series",
                },
            ]
        }
    },
})
@router.get("/table_widget_with_column_definitions")
def table_widget_with_column_definitions():
    """Returns mock data with specified columns"""
    mock_data = [
        {"stock": "AAPL", "price": 150.25, "change": 2.5},
        {"stock": "GOOGL", "price": 2800.75, "change": -1.2},
        {"stock": "MSFT", "price": 340.50, "change": 0.8},
    ]
    return mock_data


@register_widget({
    "name": "Table Widget with Render Functions",
    "description": "A table widget with render functions",
    "type": "table",
    "endpoint": "table_widget_with_render_functions",
    "gridData": {"w": 20, "h": 6},
    "data": {
        "table": {
            "columnsDefs": [
                {
                    "field": "name",
                    "headerName": "Asset",
                    "cellDataType": "text",
                    "formatterFn": "none",
                    "renderFn": "titleCase",
                    "width": 120,
                    "pinned": "left"
                },
                {
                    "field": "tvl",
                    "headerName": "TVL (USD)",
                    "headerTooltip": "Total Value Locked",
                    "cellDataType": "number",
                    "formatterFn": "int",
                    "width": 150,
                    "renderFn": "columnColor",
                    "renderFnParams": {
                        "colorRules": [
                            {
                                "condition": "between",
                                "range": {
                                    "min": 30000000000,
                                    "max": 40000000000
                                },
                                "color": "blue",
                                "fill": False
                            },
                            {
                                "condition": "lt",
                                "value": 10000000000,
                                "color": "#FFA500",
                                "fill": False
                            },
                            {
                                "condition": "gt",
                                "value": 40000000000,
                                "color": "green",
                                "fill": True
                            }
                        ]
                    }
                },
                {
                    "field": "change_1d",
                    "headerName": "24h Change",
                    "cellDataType": "number",
                    "formatterFn": "percent",
                    "renderFn": "greenRed",
                    "width": 120,
                    "maxWidth": 150,
                    "minWidth": 70,
                },
                {
                    "field": "change_7d",
                    "headerName": "7d Change",
                    "cellDataType": "number",
                    "formatterFn": "percent",
                    "renderFn": "greenRed",
                    "width": 120,
                    "maxWidth": 150,
                    "minWidth": 70,
                }
            ]
        }
    },
})
@router.get("/table_widget_with_render_functions")
def table_widget_with_render_functions():
    """Returns a mock table data for demonstration"""
    mock_data = [
        {
            "name": "Ethereum",
            "tvl": 45000000000,
            "change_1d": 2.5,
            "change_7d": 5.2
        },
        {
            "name": "Bitcoin",
            "tvl": 35000000000,
            "change_1d": 1.2,
            "change_7d": 4.8
        },
        {
            "name": "Solana",
            "tvl": 8000000000,
            "change_1d": -0.5,
            "change_7d": 2.1
        }
    ]
    return mock_data


@register_widget({
    "name": "Table Widget with Hover Card",
    "description": "A table widget with a hover card for expandable content",
    "type": "table",
    "endpoint": "table_widget_with_hover_card",
    "gridData": {"w": 20, "h": 6},
    "data": {
        "table": {
            "columnsDefs": [
                {
                    "field": "name",
                    "headerName": "Asset",
                    "cellDataType": "text",
                    "formatterFn": "none",
                    "width": 120,
                    "pinned": "left",
                    "renderFn": "hoverCard",
                    "renderFnParams": {
                        "hoverCard": {
                            "cellField": "value",
                            "title": "Project Details",
                            "markdown": "### {value} (since {foundedDate})\n**Description:** {description}",
                        }
                    },
                },
                {
                    "field": "tvl",
                    "headerName": "TVL (USD)",
                    "headerTooltip": "Total Value Locked",
                    "cellDataType": "number",
                    "formatterFn": "int",
                    "width": 150,
                    "renderFn": "columnColor",
                },
                {
                    "field": "change_1d",
                    "headerName": "24h Change",
                    "cellDataType": "number",
                    "formatterFn": "percent",
                    "renderFn": "greenRed",
                    "width": 120,
                    "maxWidth": 150,
                    "minWidth": 70,
                },
                {
                    "field": "change_7d",
                    "headerName": "7d Change",
                    "cellDataType": "number",
                    "formatterFn": "percent",
                    "renderFn": "greenRed",
                    "width": 120,
                    "maxWidth": 150,
                    "minWidth": 70,
                },
            ]
        }
    },
})
@router.get("/table_widget_with_hover_card")
def table_widget_with_hover_card():
    """Returns data with hover card descriptions"""
    mock_data = [
        {
            "name": {
                "value": "Ethereum",
                "description": "A decentralized, open-source blockchain with smart contract functionality",
                "foundedDate": "2015-07-30",
            },
            "tvl": 45000000000,
            "change_1d": 2.5,
            "change_7d": 5.2,
        },
        {
            "name": {
                "value": "Bitcoin",
                "description": "The first decentralized cryptocurrency",
                "foundedDate": "2009-01-03",
            },
            "tvl": 35000000000,
            "change_1d": 1.2,
            "change_7d": 4.8,
        },
        {
            "name": {
                "value": "Solana",
                "description": "A high-performance blockchain supporting builders around the world",
                "foundedDate": "2020-03-16",
            },
            "tvl": 8000000000,
            "change_1d": -0.5,
            "change_7d": 2.1,
        },
    ]
    return mock_data


@register_widget({
    "name": "Table to Chart Widget",
    "description": "A table widget that can be converted to a chart view",
    "type": "table",
    "endpoint": "table_to_chart_widget",
    "gridData": {"w": 20, "h": 12},
    "data": {
        "table": {
            "enableCharts": True,
            "showAll": True,
            "columnsDefs": [
                {
                    "field": "category",
                    "headerName": "Category",
                    "cellDataType": "text",
                    "chartDataType": "category",
                },
                {
                    "field": "value",
                    "headerName": "Value",
                    "cellDataType": "number",
                    "chartDataType": "series",
                },
                {
                    "field": "target",
                    "headerName": "Target",
                    "cellDataType": "number",
                    "chartDataType": "series",
                },
            ],
        }
    },
})
@router.get("/table_to_chart_widget")
def table_to_chart_widget():
    """Returns data suitable for table-to-chart conversion"""
    mock_data = [
        {"category": "Q1", "value": 125000, "target": 120000},
        {"category": "Q2", "value": 148000, "target": 140000},
        {"category": "Q3", "value": 167000, "target": 160000},
        {"category": "Q4", "value": 195000, "target": 180000},
    ]
    return mock_data


@register_widget({
    "name": "Table to Time Series Widget",
    "description": "A table widget with time series data for line chart conversion",
    "type": "table",
    "endpoint": "table_to_time_series_widget",
    "gridData": {"w": 20, "h": 12},
    "data": {
        "table": {
            "enableCharts": True,
            "showAll": True,
            "columnsDefs": [
                {
                    "field": "date",
                    "headerName": "Date",
                    "cellDataType": "dateString",
                    "chartDataType": "category",
                },
                {
                    "field": "revenue",
                    "headerName": "Revenue",
                    "cellDataType": "number",
                    "chartDataType": "series",
                },
                {
                    "field": "profit",
                    "headerName": "Profit",
                    "cellDataType": "number",
                    "chartDataType": "series",
                },
            ],
        }
    },
})
@router.get("/table_to_time_series_widget")
def table_to_time_series_widget():
    """Returns time series data for line chart conversion"""
    mock_data = [
        {"date": "2024-01-01", "revenue": 100000, "profit": 25000},
        {"date": "2024-02-01", "revenue": 115000, "profit": 28000},
        {"date": "2024-03-01", "revenue": 125000, "profit": 32000},
        {"date": "2024-04-01", "revenue": 140000, "profit": 35000},
        {"date": "2024-05-01", "revenue": 155000, "profit": 40000},
        {"date": "2024-06-01", "revenue": 170000, "profit": 45000},
    ]
    return mock_data
