"""
AgGrid Table Widgets for OpenBB Workspace

This module demonstrates advanced table features using AG Grid:
- Column definitions: Custom column headers, widths, and types
- Cell data types: text, number, boolean, date, dateString, object
- Render functions: greenRed, titleCase, hoverCard, cellOnClick, columnColor, showCellChange
- Formatter functions: int, none, percent, normalized, normalizedPercent, dateToYear
- Hover cards: Expandable detail views on cell hover
- Column pinning: Fix columns to left or right side
- Charts integration: Built-in charting capabilities

Valid cellDataType values: text, number, boolean, date, dateString, object
Valid renderFn values: greenRed, titleCase, hoverCard, cellOnClick, columnColor, showCellChange
Valid formatterFn values: int, none, percent, normalized, normalizedPercent, dateToYear

HOVER CARD CONFIGURATION:
-------------------------
The hoverCard renderFn requires special configuration via renderFnParams and nested object data.

Column definition example:
    {
        "field": "name",
        "renderFn": "hoverCard",
        "renderFnParams": {
            "hoverCard": {
                "cellField": "value",           # Which nested field to display in the cell
                "title": "Details",             # Hover card popup title
                "markdown": "### {value}\\n**Description:** {description}",  # Template with {placeholders}
            }
        },
    }

Data structure - the field value must be a nested object:
    {
        "name": {
            "value": "Display Text",        # Shown in the cell (via cellField)
            "description": "Full details",  # Available as {description} in markdown
            "otherField": "More data",      # Available as {otherField} in markdown
        },
        "otherColumns": ...
    }

The markdown template uses {placeholder} syntax to reference properties from the nested object.
All properties in the nested object are available as placeholders in the markdown template.
"""

from datetime import datetime
from fastapi import APIRouter

from core import register_widget, WIDGETS

router = APIRouter()


# ============================================================================
# BASIC TABLE WITH COLUMN DEFINITIONS
# ============================================================================

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


# ============================================================================
# TABLE WITH RENDER FUNCTIONS
# ============================================================================

@register_widget({
    "name": "Table Widget with Render Functions",
    "description": "A table widget demonstrating various render functions",
    "type": "table",
    "endpoint": "table_widget_with_render_functions",
    "gridData": {"w": 15, "h": 7},
    "data": {
        "table": {
            "enableCharts": True,
            "showAll": True,
            "columnsDefs": [
                {
                    "field": "name",
                    "headerName": "Name",
                    "cellDataType": "text",
                    "chartDataType": "category",
                    "pinned": "left",
                    "width": 120,
                },
                {
                    "field": "price",
                    "headerName": "Price",
                    "cellDataType": "number",
                    "chartDataType": "series",
                },
                {
                    "field": "change",
                    "headerName": "Change",
                    "cellDataType": "number",
                    "chartDataType": "series",
                    "renderFn": "greenRed",
                },
                {
                    "field": "status",
                    "headerName": "Status",
                    "cellDataType": "text",
                    "renderFn": "titleCase",
                },
            ],
        }
    },
})
@router.get("/table_widget_with_render_functions")
def table_widget_with_render_functions():
    """Returns mock data demonstrating render functions"""
    mock_data = [
        {"name": "Apple Inc.", "price": 178.50, "change": 2.5, "status": "active_trading"},
        {"name": "Microsoft", "price": 378.80, "change": -1.2, "status": "market_open"},
        {"name": "Google", "price": 141.20, "change": 0.8, "status": "pre_market"},
        {"name": "Amazon", "price": 178.25, "change": -0.5, "status": "after_hours"},
    ]
    return mock_data


# ============================================================================
# TABLE TO CHART WIDGETS
# ============================================================================

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


# ============================================================================
# TABLE WITH GREEN/RED RENDER FUNCTION
# ============================================================================

@register_widget({
    "name": "Table Widget with Green/Red Color Coding",
    "description": "A table widget with greenRed render function for positive/negative values",
    "type": "table",
    "endpoint": "table_widget_with_green_red_render",
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
                    "renderFn": "greenRed",
                },
            ]
        }
    },
})
@router.get("/table_widget_with_green_red_render")
def table_widget_with_green_red_render():
    """Returns mock data with greenRed render function for change column"""
    mock_data = [
        {"stock": "AAPL", "price": 150.25, "change": 2.5},
        {"stock": "GOOGL", "price": 2800.75, "change": -1.2},
        {"stock": "MSFT", "price": 340.50, "change": 0.8},
        {"stock": "TSLA", "price": 248.42, "change": -3.5},
        {"stock": "NVDA", "price": 875.28, "change": 5.2},
    ]
    return mock_data


# ============================================================================
# TABLE WITH HOVER CARD
# ============================================================================

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


# ============================================================================
# TABLE WITH CELL DATA TYPES
# ============================================================================

@register_widget({
    "name": "Table Widget with Various Cell Data Types",
    "description": "A table widget showing all available cell data types",
    "type": "table",
    "endpoint": "table_widget_with_various_cell_data_types",
    "gridData": {"w": 40, "h": 10},
    "data": {
        "table": {
            "showAll": True,
            "columnsDefs": [
                {
                    "field": "text_field",
                    "headerName": "Text",
                    "cellDataType": "text",
                },
                {
                    "field": "number_field",
                    "headerName": "Number",
                    "cellDataType": "number",
                },
                {
                    "field": "date_field",
                    "headerName": "Date",
                    "cellDataType": "date",
                },
                {
                    "field": "boolean_field",
                    "headerName": "Boolean",
                    "cellDataType": "boolean",
                },
                {
                    "field": "percent_field",
                    "headerName": "Percent Change",
                    "cellDataType": "number",
                    "formatterFn": "percent",
                },
            ],
        }
    },
})
@router.get("/table_widget_with_various_cell_data_types")
def table_widget_with_various_cell_data_types():
    """Returns mock data demonstrating various cell data types"""
    mock_data = [
        {
            "text_field": "Apple Inc.",
            "number_field": 150.25,
            "date_field": "2024-01-15",
            "boolean_field": True,
            "percent_field": 0.025,
        },
        {
            "text_field": "Microsoft",
            "number_field": 340.50,
            "date_field": "2024-01-16",
            "boolean_field": False,
            "percent_field": -0.012,
        },
        {
            "text_field": "Google",
            "number_field": 2800.75,
            "date_field": "2024-01-17",
            "boolean_field": True,
            "percent_field": 0.008,
        },
    ]
    return mock_data


# ============================================================================
# TABLE WITH FORMATTER FUNCTIONS
# ============================================================================

@register_widget({
    "name": "Table Widget with Formatter Functions",
    "description": "A table widget demonstrating various formatter functions",
    "type": "table",
    "endpoint": "table_widget_with_formatter_functions",
    "gridData": {"w": 30, "h": 8},
    "data": {
        "table": {
            "showAll": True,
            "columnsDefs": [
                {
                    "field": "stock",
                    "headerName": "Stock",
                    "cellDataType": "text",
                },
                {
                    "field": "price",
                    "headerName": "Price",
                    "cellDataType": "number",
                },
                {
                    "field": "shares",
                    "headerName": "Shares (int)",
                    "cellDataType": "number",
                    "formatterFn": "int",
                },
                {
                    "field": "change_pct",
                    "headerName": "Change %",
                    "cellDataType": "number",
                    "formatterFn": "percent",
                },
                {
                    "field": "normalized",
                    "headerName": "Normalized",
                    "cellDataType": "number",
                    "formatterFn": "normalized",
                },
            ],
        }
    },
})
@router.get("/table_widget_with_formatter_functions")
def table_widget_with_formatter_functions():
    """Returns mock data demonstrating formatter functions"""
    mock_data = [
        {"stock": "AAPL", "price": 150.25, "shares": 1000.5, "change_pct": 0.025, "normalized": 0.75},
        {"stock": "GOOGL", "price": 2800.75, "shares": 500.8, "change_pct": -0.012, "normalized": 0.45},
        {"stock": "MSFT", "price": 340.50, "shares": 750.3, "change_pct": 0.008, "normalized": 0.60},
        {"stock": "AMZN", "price": 178.25, "shares": 250.9, "change_pct": -0.035, "normalized": 0.30},
    ]
    return mock_data


# ============================================================================
# TABLE WITH COLOR CODING (GREEN/RED)
# ============================================================================

@register_widget({
    "name": "Table Widget with Color Coded Values",
    "description": "A table widget with greenRed render function for color formatting",
    "type": "table",
    "endpoint": "table_widget_with_color_coding",
    "gridData": {"w": 25, "h": 8},
    "data": {
        "table": {
            "showAll": True,
            "columnsDefs": [
                {
                    "field": "symbol",
                    "headerName": "Symbol",
                    "cellDataType": "text",
                    "pinned": "left",
                    "width": 100,
                },
                {
                    "field": "name",
                    "headerName": "Company",
                    "cellDataType": "text",
                    "width": 150,
                },
                {
                    "field": "price",
                    "headerName": "Price",
                    "cellDataType": "number",
                },
                {
                    "field": "change_1d",
                    "headerName": "1D Change",
                    "cellDataType": "number",
                    "renderFn": "greenRed",
                },
                {
                    "field": "change_7d",
                    "headerName": "7D Change",
                    "cellDataType": "number",
                    "renderFn": "greenRed",
                },
                {
                    "field": "volume",
                    "headerName": "Volume",
                    "cellDataType": "number",
                },
            ],
        }
    },
})
@router.get("/table_widget_with_color_coding")
def table_widget_with_color_coding():
    """Returns mock data with change values for color coding"""
    mock_data = [
        {"symbol": "AAPL", "name": "Apple Inc.", "price": 178.50, "change_1d": 2.5, "change_7d": 5.2, "volume": 57807909},
        {"symbol": "MSFT", "name": "Microsoft", "price": 378.80, "change_1d": -1.2, "change_7d": 3.5, "volume": 32145678},
        {"symbol": "GOOGL", "name": "Alphabet", "price": 141.20, "change_1d": 1.8, "change_7d": -2.1, "volume": 28967543},
        {"symbol": "AMZN", "name": "Amazon", "price": 178.25, "change_1d": -0.8, "change_7d": 1.5, "volume": 45678901},
        {"symbol": "TSLA", "name": "Tesla", "price": 248.42, "change_1d": 3.5, "change_7d": -4.2, "volume": 89123456},
    ]
    return mock_data


# ============================================================================
# TABLE WITH TITLE CASE RENDER
# ============================================================================

@register_widget({
    "name": "Table Widget with Title Case Render",
    "description": "A table widget with titleCase render function",
    "type": "table",
    "endpoint": "table_widget_with_title_case",
    "gridData": {"w": 25, "h": 6},
    "data": {
        "table": {
            "showAll": True,
            "columnsDefs": [
                {
                    "field": "id",
                    "headerName": "ID",
                    "cellDataType": "number",
                    "width": 80,
                },
                {
                    "field": "status",
                    "headerName": "Status",
                    "cellDataType": "text",
                    "renderFn": "titleCase",
                },
                {
                    "field": "category",
                    "headerName": "Category",
                    "cellDataType": "text",
                    "renderFn": "titleCase",
                },
                {
                    "field": "value",
                    "headerName": "Value",
                    "cellDataType": "number",
                },
            ],
        }
    },
})
@router.get("/table_widget_with_title_case")
def table_widget_with_title_case():
    """Returns mock data with titleCase render function"""
    mock_data = [
        {"id": 1, "status": "pending_review", "category": "high_priority", "value": 1500},
        {"id": 2, "status": "approved", "category": "medium_priority", "value": 2300},
        {"id": 3, "status": "in_progress", "category": "low_priority", "value": 890},
        {"id": 4, "status": "completed", "category": "urgent_action", "value": 4200},
    ]
    return mock_data


# ============================================================================
# TABLE WITH CHARTS ENABLED
# ============================================================================

@register_widget({
    "name": "Table Widget with Charts Enabled",
    "description": "A table widget with built-in charting capabilities",
    "type": "table",
    "endpoint": "table_widget_with_charts_enabled",
    "gridData": {"w": 30, "h": 10},
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
                    "field": "q1",
                    "headerName": "Q1 Revenue",
                    "cellDataType": "number",
                    "chartDataType": "series",
                },
                {
                    "field": "q2",
                    "headerName": "Q2 Revenue",
                    "cellDataType": "number",
                    "chartDataType": "series",
                },
                {
                    "field": "q3",
                    "headerName": "Q3 Revenue",
                    "cellDataType": "number",
                    "chartDataType": "series",
                },
                {
                    "field": "q4",
                    "headerName": "Q4 Revenue",
                    "cellDataType": "number",
                    "chartDataType": "series",
                },
            ],
        }
    },
})
@router.get("/table_widget_with_charts_enabled")
def table_widget_with_charts_enabled():
    """Returns quarterly revenue data for charting"""
    mock_data = [
        {"category": "Product A", "q1": 125000, "q2": 148000, "q3": 167000, "q4": 195000},
        {"category": "Product B", "q1": 89000, "q2": 112000, "q3": 134000, "q4": 156000},
        {"category": "Product C", "q1": 67000, "q2": 78000, "q3": 92000, "q4": 118000},
        {"category": "Services", "q1": 234000, "q2": 267000, "q3": 289000, "q4": 312000},
    ]
    return mock_data


# ============================================================================
# TABLE WITH SHOW CELL CHANGE
# ============================================================================

@register_widget({
    "name": "Table Widget with Show Cell Change",
    "description": "A table widget with showCellChange render function",
    "type": "table",
    "endpoint": "table_widget_with_show_cell_change",
    "gridData": {"w": 25, "h": 6},
    "data": {
        "table": {
            "showAll": True,
            "columnsDefs": [
                {
                    "field": "symbol",
                    "headerName": "Symbol",
                    "cellDataType": "text",
                },
                {
                    "field": "price",
                    "headerName": "Price",
                    "cellDataType": "number",
                    "renderFn": "showCellChange",
                },
                {
                    "field": "volume",
                    "headerName": "Volume",
                    "cellDataType": "number",
                    "renderFn": "showCellChange",
                },
            ],
        }
    },
})
@router.get("/table_widget_with_show_cell_change")
def table_widget_with_show_cell_change():
    """Returns mock data with showCellChange render function"""
    mock_data = [
        {"symbol": "AAPL", "price": 178.50, "volume": 57807909},
        {"symbol": "MSFT", "price": 378.80, "volume": 32145678},
        {"symbol": "GOOGL", "price": 141.20, "volume": 28967543},
        {"symbol": "AMZN", "price": 178.25, "volume": 45678901},
    ]
    return mock_data


# ============================================================================
# TABLE WITH DATE FORMATTING
# ============================================================================

@register_widget({
    "name": "Table Widget with Date Formatting",
    "description": "A table widget with date and dateToYear formatter",
    "type": "table",
    "endpoint": "table_widget_with_date_formatting",
    "gridData": {"w": 30, "h": 6},
    "data": {
        "table": {
            "showAll": True,
            "columnsDefs": [
                {
                    "field": "company",
                    "headerName": "Company",
                    "cellDataType": "text",
                },
                {
                    "field": "founded",
                    "headerName": "Founded (Full)",
                    "cellDataType": "date",
                },
                {
                    "field": "founded_year",
                    "headerName": "Founded (Year)",
                    "cellDataType": "number",
                    "formatterFn": "dateToYear",
                },
                {
                    "field": "ipo_date",
                    "headerName": "IPO Date",
                    "cellDataType": "dateString",
                },
            ],
        }
    },
})
@router.get("/table_widget_with_date_formatting")
def table_widget_with_date_formatting():
    """Returns mock data with date formatting"""
    mock_data = [
        {"company": "Apple Inc.", "founded": "1976-04-01", "founded_year": 1976, "ipo_date": "1980-12-12"},
        {"company": "Microsoft", "founded": "1975-04-04", "founded_year": 1975, "ipo_date": "1986-03-13"},
        {"company": "Amazon", "founded": "1994-07-05", "founded_year": 1994, "ipo_date": "1997-05-15"},
        {"company": "Google", "founded": "1998-09-04", "founded_year": 1998, "ipo_date": "2004-08-19"},
    ]
    return mock_data
