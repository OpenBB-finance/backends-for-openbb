"""
Input Parameters for OpenBB Workspace Widgets

This module demonstrates various input parameter types for widgets:
- Text input: Basic text fields
- Number input: Numeric fields with min/max constraints
- Date input: Date pickers with various formats
- Dropdown/Select: Single and multi-select options
- Parameter grouping: Organizing parameters visually
- Dynamic options: Dropdowns populated from endpoints
- Boolean toggles: On/off switches
- Cell click interactions: Parameters managed by table clicks
- Widget groups: Multiple widgets sharing parameters

These parameters allow users to customize widget behavior and data queries.
"""

from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, Query

from core import register_widget, WIDGETS, FileOption

router = APIRouter()


# ============================================================================
# TEXT INPUT PARAMETERS
# ============================================================================

@register_widget({
    "name": "Markdown Widget with Text Input",
    "description": "A markdown widget with a text input parameter",
    "type": "markdown",
    "endpoint": "markdown_widget_with_text_input",
    "gridData": {"w": 20, "h": 6},
    "params": [{
        "paramName": "name",
        "description": "Enter your name",
        "value": "OpenBB",
        "label": "Name",
        "type": "text",
    }],
})
@router.get("/markdown_widget_with_text_input")
def markdown_widget_with_text_input(name: str = "OpenBB"):
    """Returns a markdown widget with a text input parameter"""
    return f"# Hello {name}!"


# ============================================================================
# NUMBER INPUT PARAMETERS
# ============================================================================

@register_widget({
    "name": "Markdown Widget with Number Input",
    "description": "A markdown widget with a number input parameter",
    "type": "markdown",
    "endpoint": "markdown_widget_with_number_input",
    "gridData": {"w": 20, "h": 5},
    "params": [{
        "paramName": "value",
        "description": "Enter the amount",
        "value": 100,
        "label": "Amount",
        "type": "number",
    }],
})
@router.get("/markdown_widget_with_number_input")
def markdown_widget_with_number_input(value: int = 100):
    """Returns a markdown widget with a number input parameter"""
    return f"# The amount is {value}"


# ============================================================================
# DATE INPUT PARAMETERS
# ============================================================================

@register_widget({
    "name": "Markdown Widget with Date Picker",
    "description": "A markdown widget with a date picker parameter",
    "type": "markdown",
    "endpoint": "markdown_widget_with_date_picker",
    "gridData": {"w": 20, "h": 5},
    "params": [{
        "paramName": "date",
        "description": "Select a date",
        "value": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
        "label": "Date",
        "type": "date",
    }],
})
@router.get("/markdown_widget_with_date_picker")
def markdown_widget_with_date_picker(
    date: str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
):
    """Returns a markdown widget with a date picker parameter"""
    return f"# The selected date is {date}"


# ============================================================================
# DROPDOWN/SELECT PARAMETERS
# ============================================================================

@register_widget({
    "name": "Markdown Widget with Dropdown",
    "description": "A markdown widget with a dropdown parameter",
    "type": "markdown",
    "endpoint": "markdown_widget_with_dropdown",
    "gridData": {"w": 20, "h": 5},
    "params": [{
        "paramName": "days_picker",
        "description": "Select number of days",
        "value": "1",
        "label": "Days",
        "type": "text",
        "options": [
            {"label": "1 Day", "value": "1"},
            {"label": "7 Days", "value": "7"},
            {"label": "30 Days", "value": "30"},
            {"label": "90 Days", "value": "90"},
        ],
    }],
})
@router.get("/markdown_widget_with_dropdown")
def markdown_widget_with_dropdown(days_picker: str = "1"):
    """Returns a markdown widget with a dropdown parameter"""
    return f"# Selected: {days_picker} day(s)"


@register_widget({
    "name": "Markdown Widget with Multi-Select Advanced Dropdown",
    "description": "A markdown widget with a multi-select advanced dropdown parameter",
    "type": "markdown",
    "endpoint": "markdown_widget_with_multi_select_advanced_dropdown",
    "gridData": {"w": 20, "h": 6},
    "params": [{
        "paramName": "stock_picker",
        "description": "Select stocks",
        "value": "AAPL",
        "label": "Stocks",
        "type": "text",
        "multiSelect": True,
        "options": [
            {"label": "Apple Inc.", "value": "AAPL"},
            {"label": "Microsoft Corporation", "value": "MSFT"},
            {"label": "Amazon.com Inc.", "value": "AMZN"},
            {"label": "Alphabet Inc.", "value": "GOOGL"},
            {"label": "NVIDIA Corporation", "value": "NVDA"},
        ],
    }],
})
@router.get("/markdown_widget_with_multi_select_advanced_dropdown")
def markdown_widget_with_multi_select_advanced_dropdown(stock_picker: str = "AAPL"):
    """Returns a markdown widget with a multi-select dropdown parameter"""
    return f"# Selected stocks: {stock_picker}"


@register_widget({
    "name": "Dropdown Dependent Widget",
    "description": "A widget that depends on a dropdown selection from another widget or source",
    "type": "markdown",
    "endpoint": "dropdown_dependent_widget",
    "gridData": {"w": 20, "h": 5},
    "params": [{
        "paramName": "category",
        "description": "Select a category",
        "value": "tech",
        "label": "Category",
        "type": "text",
        "options": [
            {"label": "Technology", "value": "tech"},
            {"label": "Healthcare", "value": "health"},
            {"label": "Finance", "value": "finance"},
        ],
    }],
})
@router.get("/dropdown_dependent_widget")
def dropdown_dependent_widget(category: str = "tech"):
    """Returns a widget that shows category-dependent content"""
    content_map = {
        "tech": "# Technology Sector\n\nShowing tech stocks and news.",
        "health": "# Healthcare Sector\n\nShowing healthcare stocks and news.",
        "finance": "# Finance Sector\n\nShowing financial stocks and news.",
    }
    return content_map.get(category, "# Unknown Category")


# ============================================================================
# BOOLEAN PARAMETERS
# ============================================================================

@register_widget({
    "name": "Markdown Widget with Boolean",
    "description": "A markdown widget with a boolean toggle parameter",
    "type": "markdown",
    "endpoint": "markdown_widget_with_boolean",
    "gridData": {"w": 20, "h": 5},
    "params": [{
        "paramName": "condition",
        "description": "Enable or disable the condition",
        "value": True,
        "label": "Condition",
        "type": "boolean",
    }],
})
@router.get("/markdown_widget_with_boolean")
def markdown_widget_with_boolean(condition: bool = True):
    """Returns a markdown widget with a boolean parameter"""
    if condition:
        return "# Condition is TRUE\n\nThe toggle is enabled."
    return "# Condition is FALSE\n\nThe toggle is disabled."


# ============================================================================
# CELL CLICK INTERACTION WIDGETS
# ============================================================================

STOCK_DATA = [
    {"symbol": "AAPL", "price": 178.50, "change": 2.35, "volume": 52000000},
    {"symbol": "MSFT", "price": 338.20, "change": -1.45, "volume": 28000000},
    {"symbol": "AMZN", "price": 145.80, "change": 3.20, "volume": 45000000},
    {"symbol": "GOOGL", "price": 142.65, "change": -0.85, "volume": 18000000},
]


@register_widget({
    "name": "Table Widget with Grouping by Cell Click",
    "description": "Click on a cell to filter/group data across widgets",
    "type": "table",
    "endpoint": "table_widget_with_grouping_by_cell_click",
    "gridData": {"w": 20, "h": 8},
    "columnsDefs": [
        {"field": "symbol", "headerName": "Symbol", "cellDataType": "text", "renderFn": "cellOnClick"},
        {"field": "price", "headerName": "Price", "cellDataType": "number"},
        {"field": "change", "headerName": "Change", "cellDataType": "number", "renderFn": "greenRed"},
        {"field": "volume", "headerName": "Volume", "cellDataType": "number"},
    ],
})
@router.get("/table_widget_with_grouping_by_cell_click")
def table_widget_with_grouping_by_cell_click():
    """Returns stock data for cell click grouping demo"""
    return STOCK_DATA


@register_widget({
    "name": "Widget Managed by Parameter from Cell Click on Table Widget",
    "description": "This widget displays details based on symbol selected from table click",
    "type": "markdown",
    "endpoint": "widget_managed_by_parameter_from_cell_click_on_table_widget",
    "gridData": {"w": 20, "h": 8},
    "params": [{
        "paramName": "symbol",
        "description": "Stock symbol from cell click",
        "value": "AAPL",
        "label": "Symbol",
        "type": "text",
    }],
})
@router.get("/widget_managed_by_parameter_from_cell_click_on_table_widget")
def widget_managed_by_parameter_from_cell_click_on_table_widget(symbol: str = "AAPL"):
    """Returns details for a selected stock symbol"""
    stock = next((s for s in STOCK_DATA if s["symbol"] == symbol), None)
    if stock:
        return f"""# {symbol} Details

- **Price:** ${stock['price']:.2f}
- **Change:** {stock['change']:+.2f}
- **Volume:** {stock['volume']:,}

*Click on a symbol in the table to update this widget.*
"""
    return f"# {symbol}\n\nNo data available for this symbol."


# ============================================================================
# WIDGET GROUPS (Company Performance Example)
# ============================================================================

COMPANY_PERFORMANCE_DATA = [
    {"metric": "Revenue", "value": 394328, "change": 8.1},
    {"metric": "Net Income", "value": 96995, "change": 5.4},
    {"metric": "EPS", "value": 6.13, "change": 8.9},
    {"metric": "Market Cap", "value": 2850000, "change": 12.3},
]


@register_widget({
    "name": "Company Performance",
    "description": "Shows company performance metrics (grouped widget example)",
    "type": "table",
    "endpoint": "company_performance",
    "gridData": {"w": 20, "h": 8},
    "params": [
        {
            "paramName": "company",
            "description": "Company ticker",
            "value": "AAPL",
            "label": "Company",
            "type": "text",
        },
        {
            "paramName": "year",
            "description": "Fiscal year",
            "value": "2024",
            "label": "Year",
            "type": "text",
            "options": [
                {"label": "2024", "value": "2024"},
                {"label": "2023", "value": "2023"},
                {"label": "2022", "value": "2022"},
            ],
        },
    ],
    "columnsDefs": [
        {"field": "metric", "headerName": "Metric", "cellDataType": "text"},
        {"field": "value", "headerName": "Value", "cellDataType": "number"},
        {"field": "change", "headerName": "Change %", "cellDataType": "number", "renderFn": "greenRed"},
    ],
})
@router.get("/company_performance")
def company_performance(company: str = "AAPL", year: str = "2024"):
    """Returns company performance data"""
    return COMPANY_PERFORMANCE_DATA


@register_widget({
    "name": "Company Details",
    "description": "Shows company details (grouped widget example)",
    "type": "markdown",
    "endpoint": "company_details",
    "gridData": {"w": 20, "h": 8},
    "params": [
        {
            "paramName": "company",
            "description": "Company ticker",
            "value": "AAPL",
            "label": "Company",
            "type": "text",
        },
        {
            "paramName": "year",
            "description": "Fiscal year",
            "value": "2024",
            "label": "Year",
            "type": "text",
            "options": [
                {"label": "2024", "value": "2024"},
                {"label": "2023", "value": "2023"},
                {"label": "2022", "value": "2022"},
            ],
        },
    ],
})
@router.get("/company_details")
def company_details(company: str = "AAPL", year: str = "2024"):
    """Returns company details markdown"""
    company_info = {
        "AAPL": {"name": "Apple Inc.", "sector": "Technology", "industry": "Consumer Electronics"},
        "MSFT": {"name": "Microsoft Corporation", "sector": "Technology", "industry": "Software"},
        "TM": {"name": "Toyota Motor Corp", "sector": "Consumer Cyclical", "industry": "Auto Manufacturers"},
    }
    info = company_info.get(company, {"name": company, "sector": "Unknown", "industry": "Unknown"})
    return f"""# {info['name']} ({company})

**Fiscal Year:** {year}

## Company Information
- **Sector:** {info['sector']}
- **Industry:** {info['industry']}

*This widget is grouped with Company Performance and shares the company/year parameters.*
"""


# ============================================================================
# ORGANIZED PARAMETERS EXAMPLE
# ============================================================================

@register_widget({
    "name": "Markdown Widget with Organized Parameters",
    "description": "A markdown widget demonstrating various parameter types organized in a clean way",
    "type": "markdown",
    "endpoint": "markdown_widget_with_organized_params",
    "gridData": {"w": 40, "h": 13},
    "params": [
        [
            {
                "paramName": "enable_feature",
                "description": "Enable or disable the main feature",
                "label": "Enable Feature",
                "type": "boolean",
                "value": True,
            }
        ],
        [
            {
                "paramName": "selected_date",
                "description": "Select a date for analysis",
                "value": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
                "label": "Analysis Date",
                "type": "date",
            },
            {
                "paramName": "analysis_type",
                "description": "Select the type of analysis to perform",
                "value": "technical",
                "label": "Analysis Type",
                "type": "text",
                "options": [
                    {"label": "Technical Analysis", "value": "technical"},
                    {"label": "Fundamental Analysis", "value": "fundamental"},
                    {"label": "Sentiment Analysis", "value": "sentiment"},
                    {"label": "Risk Analysis", "value": "risk"},
                ],
            },
            {
                "paramName": "lookback_period",
                "description": "Number of days to look back",
                "value": 30,
                "label": "Lookback Period (days)",
                "type": "number",
                "min": 1,
                "max": 365,
            },
        ],
        [
            {
                "paramName": "analysis_notes",
                "description": "Additional notes for the analysis",
                "value": "",
                "label": "Analysis Notes",
                "type": "text",
            }
        ],
    ],
})
@router.get("/markdown_widget_with_organized_params")
def markdown_widget_with_organized_params(
    enable_feature: bool = True,
    selected_date: str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
    analysis_type: str = "technical",
    lookback_period: int = 30,
    analysis_notes: str = "",
):
    """Returns a markdown widget with organized parameters"""
    formatted_date = datetime.strptime(selected_date, "%Y-%m-%d").strftime("%B %d, %Y")

    analysis_type_label = next(
        (opt["label"] for opt in [
            {"label": "Technical Analysis", "value": "technical"},
            {"label": "Fundamental Analysis", "value": "fundamental"},
            {"label": "Sentiment Analysis", "value": "sentiment"},
            {"label": "Risk Analysis", "value": "risk"},
        ] if opt["value"] == analysis_type),
        analysis_type,
    )

    return f"""# Analysis Configuration
*This widget demonstrates various parameter types including boolean toggles, date pickers, dropdowns, number inputs, and text fields.*

## Feature Status
- **Feature Enabled:** {'Yes' if enable_feature else 'No'}

## Analysis Parameters
- **Selected Date:** {formatted_date}
- **Analysis Type:** {analysis_type_label}
- **Lookback Period:** {lookback_period} days

## Additional Notes
{analysis_notes if analysis_notes else "*No additional notes provided*"}
"""


# ============================================================================
# VENDOR PREFIXED WIDGETS
# ============================================================================

@register_widget({
    "name": "Vendor1 Markdown Widget with String and Int",
    "description": "A vendor-prefixed markdown widget with string and integer parameters",
    "type": "markdown",
    "endpoint": "/vendor1/markdown_widget_with_str_and_int",
    "gridData": {"w": 20, "h": 8},
    "params": [
        {
            "paramName": "text_param",
            "description": "A text parameter",
            "value": "Hello",
            "label": "Text",
            "type": "text",
        },
        {
            "paramName": "number_param",
            "description": "A number parameter",
            "value": 42,
            "label": "Number",
            "type": "number",
        },
    ],
})
@router.get("/vendor1/markdown_widget_with_str_and_int")
def vendor1_markdown_widget_with_str_and_int(text_param: str = "Hello", number_param: int = 42):
    """Returns a vendor-prefixed markdown widget"""
    return f"# Vendor1 Widget\n\n- Text: {text_param}\n- Number: {number_param}"


VENDOR_TABLE_DATA = [
    {"name": "Alpha", "value": 100, "category": "A"},
    {"name": "Beta", "value": 200, "category": "B"},
    {"name": "Charlie", "value": 150, "category": "C"},
    {"name": "Delta", "value": 300, "category": "A"},
]


@register_widget({
    "name": "Vendor1 Table Widget with String Parameter",
    "description": "A vendor-prefixed table widget with a string filter parameter",
    "type": "table",
    "endpoint": "/vendor1/table_widget_with_str_param",
    "gridData": {"w": 20, "h": 8},
    "params": [{
        "paramName": "filter_text",
        "description": "Filter by category",
        "value": "",
        "label": "Filter",
        "type": "text",
    }],
})
@router.get("/vendor1/table_widget_with_str_param")
def vendor1_table_widget_with_str_param(filter_text: str = ""):
    """Returns filtered vendor table data"""
    if filter_text:
        return [row for row in VENDOR_TABLE_DATA if filter_text.upper() in row["category"]]
    return VENDOR_TABLE_DATA
