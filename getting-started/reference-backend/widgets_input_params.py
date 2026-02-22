from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, Query

from core import register_widget, WIDGETS, FileOption

router = APIRouter()

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
    return f"**Text:** {name}"


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
    return f"**Number:** {value}"


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
        return "**Toggle:** enabled"
    return "**Toggle:** disabled"


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
    return f"**Date:** {date}"


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
    return f"**Selection of Days:** {days_picker}"


@register_widget({
    "name": "Markdown Widget with Multi-Select Dropdown",
    "description": "A markdown widget with a multi-select dropdown parameter",
    "type": "markdown",
    "endpoint": "markdown_widget_with_multi_select_dropdown",
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
@router.get("/markdown_widget_with_multi_select_dropdown")
def markdown_widget_with_multi_select_dropdown(stock_picker: str = "AAPL"):
    """Returns a markdown widget with a multi-select dropdown parameter"""
    return f"**Selected tickers:** {stock_picker}"


@register_widget({
    "name": "Markdown Widget with Multi Text Input",
    "description": "A markdown widget with a text input parameter",
    "endpoint": "markdown_widget_with_multi_text_input",
    "gridData": {"w": 16, "h": 6},
    "type": "markdown",
    "params": [
        {
            "paramName": "text_box",
            "value": "var1,var2,var3",
            "label": "Enter Text",
            "description": "Type something to display",
            "multiple": True,
            "type": "text"
        }
    ]
})
@router.get("/markdown_widget_with_multi_text_input")
def markdown_widget_with_multi_text_input(text_box: str):
    """Returns a markdown widget with text input parameter"""
    return f"**Vars:** {text_box}"


@router.get("/advanced_dropdown_options")
def advanced_dropdown_options():
    """Returns a list of stocks with their details"""
    return [
        {
            "label": "Apple Inc.",
            "value": "AAPL",
            "extraInfo": {
                "description": "Technology Company",
                "rightOfDescription": "NASDAQ"
            }
        },
        {
            "label": "Microsoft Corporation",
            "value": "MSFT",
            "extraInfo": {
                "description": "Software Company",
                "rightOfDescription": "NASDAQ"
            }
        },
        {
            "label": "Google",
            "value": "GOOGL",
            "extraInfo": {
                "description": "Search Engine",
                "rightOfDescription": "NASDAQ"
            }
        }
    ]


@register_widget({
    "name": "Markdown Widget with Multi Select Advanced Dropdown",
    "description": "A markdown widget with a multi select advanced dropdown parameter",
    "endpoint": "markdown_widget_with_multi_select_advanced_dropdown",
    "gridData": {"w": 16, "h": 6},
    "type": "markdown",
    "params": [
        {
            "paramName": "stock_picker",
            "description": "Select a stock to analyze",
            "value": "AAPL",
            "label": "Select Stock",
            "type": "endpoint",
            "multiSelect": True,
            "optionsEndpoint": "/advanced_dropdown_options",
            "style": {
                "popupWidth": 450
            }
        }
    ]
})
@router.get("/markdown_widget_with_multi_select_advanced_dropdown")
def markdown_widget_with_multi_select_advanced_dropdown(stock_picker: str):
    """Returns a markdown widget with multi select advanced dropdown parameter"""
    return f"**Selected stocks:** {stock_picker}"


@register_widget({
    "name": "Markdown Widget with String and Int",
    "description": "Markdown widget with string and integer parameters",
    "type": "markdown",
    "endpoint": "markdown_widget_with_str_and_int",
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
@router.get("/markdown_widget_with_str_and_int")
def markdown_widget_with_str_and_int(text_param: str = "Hello", number_param: int = 42):
    """Returns a vendor-prefixed markdown widget"""
    return f"- Text: {text_param}\n- Number: {number_param}"



VENDOR_TABLE_DATA = [
    {"name": "Alpha", "value": 100, "category": "A"},
    {"name": "Beta", "value": 200, "category": "B"},
    {"name": "Charlie", "value": 150, "category": "C"},
    {"name": "Delta", "value": 300, "category": "A"},
]


@register_widget({
    "name": "Table Widget with String Filter",
    "description": "Table widget with a string filter parameter",
    "type": "table",
    "endpoint": "table_widget_with_str_filter_param",
    "gridData": {"w": 20, "h": 8},
    "params": [{
        "paramName": "filter_text",
        "description": "Filter by category",
        "value": "",
        "label": "Filter",
        "type": "text",
    }],
})
@router.get("/table_widget_with_str_filter_param")
def vendor1_table_widget_with_str_param(filter_text: str = ""):
    """Returns filtered vendor table data"""
    if filter_text:
        return [row for row in VENDOR_TABLE_DATA if filter_text.upper() in row["category"]]
    return VENDOR_TABLE_DATA


@router.get("/document_options")
def get_document_options(category: str = "all"):
    """Get filtered list of documents based on category"""
    SAMPLE_DOCUMENTS = [
        {
            "name": "Q1 Report",
            "category": "reports"
        },
        {
            "name": "Q2 Report",
            "category": "reports"
        },
        {
            "name": "Investor Presentation",
            "category": "presentations"
        },
        {
            "name": "Product Roadmap",
            "category": "presentations"
        }
    ]

    filtered_docs = (
        SAMPLE_DOCUMENTS if category == "all"
        else [doc for doc in SAMPLE_DOCUMENTS if doc["category"] == category]
    )

    return [
        {
            "label": doc["name"],
            "value": doc["name"]
        }
        for doc in filtered_docs
    ]


@register_widget({
    "name": "Dropdown Dependent Widget",
    "description": "A simple widget with a dropdown depending on another dropdown",
    "endpoint": "dropdown_dependent_widget",
    "gridData": {"w": 16, "h": 6},
    "type": "markdown",
    "params": [
        {
            "paramName": "category",
            "description": "Category of documents to fetch",
            "value": "all",
            "label": "Category",
            "type": "text",
            "options": [
                {"label": "All", "value": "all"},
                {"label": "Reports", "value": "reports"},
                {"label": "Presentations", "value": "presentations"}
            ]
        },
        {
            "paramName": "document_type",
            "description": "Document to display",
            "label": "Select Document",
            "type": "endpoint",
            "optionsEndpoint": "/document_options",
            "optionsParams": {
                "category": "$category"
            }
        },
    ]
})
@router.get("/dropdown_dependent_widget")
def dropdown_dependent_widget(category: str = "all", document_type: str = "all"):
    """Returns a dropdown dependent widget"""
    return f"""
- Selected category: **{category}**
- Selected document: **{document_type}**
"""


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

    return f"""
- **Feature Enabled:** {'Yes' if enable_feature else 'No'}
\n
- **Selected Date:** {formatted_date}
- **Analysis Type:** {analysis_type_label}
- **Lookback Period:** {lookback_period} days
\n
- **Notes:** {analysis_notes if analysis_notes else "*No additional notes provided*"}
"""
