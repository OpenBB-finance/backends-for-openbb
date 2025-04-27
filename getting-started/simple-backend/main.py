# Import required libraries
import json
import base64
import requests
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from registry import register_widget, WIDGETS
from datetime import datetime, timedelta

# Initialize FastAPI application with metadata
app = FastAPI(
    title="Simple Backend",
    description="Simple backend app for OpenBB Workspace",
    version="0.0.1"
)

# Define allowed origins for CORS (Cross-Origin Resource Sharing)
# This restricts which domains can access the API
origins = [
    "https://pro.openbb.co",
]

# Configure CORS middleware to handle cross-origin requests
# This allows the specified origins to make requests to the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

ROOT_PATH = Path(__file__).parent.resolve()

@app.get("/")
def read_root():
    """Root endpoint that returns basic information about the API"""
    return {"Info": "Hello World"}


# Endpoint that returns the registered widgets configuration
# The WIDGETS dictionary is maintained by the registry.py helper
# which automatically registers widgets when using the @register_widget decorator
@app.get("/widgets.json")
def get_widgets():
    """Returns the configuration of all registered widgets
    
    The widgets are automatically registered through the @register_widget decorator
    and stored in the WIDGETS dictionary from registry.py
    
    Returns:
        dict: The configuration of all registered widgets
    """
    return WIDGETS


# Templates configuration file for the OpenBB Workspace
# it contains the information and configuration about all the
# templates that will be displayed in the OpenBB Workspace
@app.get("/templates.json")
def get_templates():
    """Templates configuration file for the OpenBB Workspace
    
    Returns:
        JSONResponse: The contents of templates.json file
    """
    # Read and return the templates configuration file
    return JSONResponse(
        content=json.load((Path(__file__).parent.resolve() / "templates.json").open())
    )


# Simple markdown widget
# Note that the gridData specifies the size of the widget in the OpenBB Workspace
@register_widget({
    "name": "Markdown Widget",
    "description": "A markdown widget",
    "type": "markdown",
    "endpoint": "markdown_widget",
    "gridData": {"w": 12, "h": 4},
})
@app.get("/markdown_widget")
def markdown_widget():
    """Returns a markdown widget"""
    return f"# Markdown Widget"

# Simple markdown widget with category and subcategory
# Note that the category and subcategory specify the category and subcategory of the widget in the OpenBB Workspace
# This is important to organize the widgets in the OpenBB Workspace, but also for AI agents to find the best 
# widgets to utilize for a given task
@register_widget({
    "name": "Markdown Widget with Category and Subcategory",
    "description": "A markdown widget with category and subcategory",
    "type": "markdown",
    "category": "Widgets",
    "subcategory": "Markdown Widgets",
    "endpoint": "markdown_widget_with_category_and_subcategory",
    "gridData": {"w": 12, "h": 4},
})
@app.get("/markdown_widget_with_category_and_subcategory")
def markdown_widget_with_category_and_subcategory():
    """Returns a markdown widget with category and subcategory"""
    return f"# Markdown Widget with Category and Subcategory"


# Markdown Widget with Error Handling
# This is a simple widget that demonstrates how to handle errors
@register_widget({
    "name": "Markdown Widget with Error Handling",
    "description": "A markdown widget with error handling",
    "type": "markdown",
    "endpoint": "markdown_widget_with_error_handling",
    "gridData": {"w": 12, "h": 4},
})
@app.get("/markdown_widget_with_error_handling")
def markdown_widget_with_error_handling():
    """Returns a markdown widget with error handling"""
    raise HTTPException(
        status_code=500,
        detail="Error that just occurred"
    )


@register_widget({
    "name": "Metric Widget",
    "description": "A metric widget",
    "endpoint": "metric_widget",
    "gridData": {
      "w": 5,
      "h": 5
    },
    "type": "metric"
})
@app.get("/metric_widget")
def metric_widget():
    # Data structure
    data = [
        {
            "label": "Total Users",
            "value": "1,234,567",
            "delta": "12.5"
        },
        {
            "label": "Active Sessions",
            "value": "45,678",
            "delta": "-2.3"
        },
        {
            "label": "Revenue (USD)",
            "value": "$89,432",
            "delta": "8.9"
        },
        {
            "label": "Conversion Rate",
            "value": "3.2%",
            "delta": "0.0"
        },
        {
            "label": "Avg. Session Duration",
            "value": "4m 32s",
            "delta": "0.5"
        }
    ]

    return JSONResponse(content=data)

# Simple table widget
# Utilize mock data for demonstration purposes on how a table widget can be used
@register_widget({
    "name": "Table Widget",
    "description": "A table widget",
    "type": "table",
    "endpoint": "table_widget",
    "gridData": {"w": 12, "h": 4},
})
@app.get("/table_widget")
def table_widget():
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


# Simple table widget with column definitions
# The most important part of this widget is the "columnsDefs" key in the data object
# Here's what you can find in this widget:
# field: The name of the field from the JSON data.
#        Example: "column1"
# headerName: The display name of the column header.
#             Example: "Column 1"
# cellDataType: Specifies the data type of the cell - this is important to know what data type is expected in the cell
# as it allows the OpenBB Workspace to know how to display the data in the cell and filter/sort the data accordingly
#               Possible values: "text", "number", "boolean", "date", "dateString", "object"
# formatterFn (optional): Specifies the function used to format the data in the table. The following values are allowed:
#                       - int: Formats the number as an integer
#                       - none: Does not format the number
#                       - percent: Adds % to the number
#                       - normalized: Multiplies the number by 100
#                       - normalizedPercent: Multiplies the number by 100 and adds % (e.g., 0.5 becomes 50 %)
#                       - dateToYear: Converts a date to just the year
# width: Specifies the width of the column in pixels.
#        Example: 100
# maxWidth: Specifies the maximum width of the column in pixels.
#           Example: 200
# minWidth: Specifies the minimum width of the column in pixels.
#           Example: 50
# hide: Hides the column from the table.
#       Example: false
# pinned: Pins the column to the left or right of the table.
#         Example: "left""right"
# headerTooltip: Tooltip text for the column header.
#                Example: "This is a tooltip"
@register_widget({
    "name": "Table Widget with Column Definitions",
    "description": "A table widget with column definitions",
    "type": "table",
    "endpoint": "table_widget_with_column_definitions",
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
                    "width": 150
                },
                {
                    "field": "change_1d",
                    "headerName": "24h Change",
                    "cellDataType": "number",
                    "formatterFn": "percent",
                    "width": 120,
                    "maxWidth": 150,
                    "minWidth": 70,
                },
                {
                    "field": "change_7d",
                    "headerName": "24h Change",
                    "cellDataType": "number",
                    "formatterFn": "percent",
                    "width": 120,
                    "maxWidth": 150,
                    "minWidth": 70,
                    "hide": True
                },
            ]
        }
    },
})
@app.get("/table_widget_with_column_definitions")
def table_widget_with_column_definitions():
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


# Simple table widget with hover card
# The most important part of this widget that hasn't been covered in the previous widget is the hover card is the "renderFn" key in the columnsDefs object
# renderFn: Specifies a rendering function for cell data.
#           Example: "titleCase"Possible values: 
#           - greenRed: Applies a green or red color based on conditions
#           - titleCase: Converts text to title case
#           - hoverCard: Displays additional information when hovering over a cell
#           - cellOnClick: Triggers an action when a cell is clicked
#           - columnColor: Changes the color of a column based on specified rules
#           - showCellChange: Highlights cells when their values change via WebSocket updates (Live Grid Widget only)
# renderFnParams: Required if renderFn is used with a specifc value. Specifies the parameters for the render function.
#                 Example:
#                 - if renderFn is "columnColor", then renderFnParams is required and must be a "colorRules" dictionary with the following keys: condition, color, range, fill.
#                 - if renderFn is "hoverCard", then renderFnParams is required and must be a "hoverCard" dictionary with the following keys: cellField, title, markdown.
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
@app.get("/table_widget_with_render_functions")
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


# Simple table widget with hover card
# The most important part of this widget that hasn't been covered in the previous widgets is the hover card
# which is a feature that allows you to display additional information when hovering over a cell
@register_widget({
    "name": "Table Widget with Hover Card",
    "description": "A table widget with hover card",
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
                            "markdown": "### {value} (since {foundedDate})\n**Description:** {description}"
                        }
                    }
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
                }
            ]
        }
    },
})
@app.get("/table_widget_with_hover_card")
def table_widget_with_hover_card():
    """Returns a mock table data for demonstration"""
    mock_data = [
        {
            "name": {
                "value": "Ethereum",
                "description": "A decentralized, open-source blockchain with smart contract functionality",
                "foundedDate": "2015-07-30"
            },
            "tvl": 45000000000,
            "change_1d": 2.5,
            "change_7d": 5.2
        },
        {
            "name": {
                "value": "Bitcoin",
                "description": "The first decentralized cryptocurrency",
                "foundedDate": "2009-01-03"
            },
            "tvl": 35000000000,
            "change_1d": 1.2,
            "change_7d": 4.8
        },
        {
            "name": {
                "value": "Solana",
                "description": "A high-performance blockchain supporting builders around the world",
                "foundedDate": "2020-03-16"
            },
            "tvl": 8000000000,
            "change_1d": -0.5,
            "change_7d": 2.1
        }
    ]
    return mock_data


# Table to Chart Widget
# The most important part of this widget is that the default view is a chart that comes from the "chartView" key in the data object
# chartDataType: Specifies how data is treated in a chart.
#                Example: "category"
#                Possible values: "category", "series", "time", "excluded"
@register_widget({
    "name": "Table to Chart Widget",
    "description": "A table widget",
    "type": "table",
    "endpoint": "table_to_chart_widget",
    "gridData": {"w": 20, "h": 12},
    "data": {
        "table": {
            "enableCharts": True,
            "showAll": False,
            "chartView": {
                "enabled": True,
                "chartType": "column"
            },
            "columnsDefs": [
                {
                    "field": "name",
                    "headerName": "Asset",
                    "chartDataType": "category",
                },
                {
                    "field": "tvl",
                    "headerName": "TVL (USD)",
                    "chartDataType": "series",
                },
            ]
        }
    },
})
@app.get("/table_to_chart_widget")
def table_to_chart_widget():
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



# Table to time series Widget
# In here we will see how to use a table widget to display a time series chart
@register_widget({
    "name": "Table to Time Series Widget",
    "description": "A table widget",
    "type": "table",
    "endpoint": "table_to_time_series_widget",
    "gridData": {"w": 20, "h": 12},
    "data": {
        "table": {
            "enableCharts": True,
            "showAll": False,
            "chartView": {
                "enabled": True,
                "chartType": "line"
            },
            "columnsDefs": [
                {
                    "field": "date",
                    "headerName": "Date",
                    "chartDataType": "time",
                },
                {
                    "field": "Ethereum",
                    "headerName": "Ethereum",
                    "chartDataType": "series",
                },
                {
                    "field": "Bitcoin",
                    "headerName": "Bitcoin",
                    "chartDataType": "series",
                },
                {
                    "field": "Solana",
                    "headerName": "Solana",
                    "chartDataType": "series",
                }
            ]
        }
    },
})
@app.get("/table_to_time_series_widget")
def table_to_time_series_widget():
    """Returns a mock table data for demonstration"""
    mock_data = [
        {
            "date": "2024-06-06",
            "Ethereum": 1.0000,
            "Bitcoin": 1.0000,
            "Solana": 1.0000
        },
        {
            "date": "2024-06-07",
            "Ethereum": 1.0235,
            "Bitcoin": 0.9822,
            "Solana": 1.0148
        },
        {
            "date": "2024-06-08",
            "Ethereum": 0.9945,
            "Bitcoin": 1.0072,
            "Solana": 0.9764
        },
        {
            "date": "2024-06-09",
            "Ethereum": 1.0205,
            "Bitcoin": 0.9856,
            "Solana": 1.0300
        },
        {
            "date": "2024-06-10",
            "Ethereum": 0.9847,
            "Bitcoin": 1.0195,
            "Solana": 0.9897
        }
    ]
    return mock_data

# Simple table widget from an API endpoint
# This is a simple widget that demonstrates how to use a table widget from an API endpoint
# Note that the endpoint is the endpoint of the API that will be used to fetch the data
# and the data is returned in the JSON format
@register_widget({
    "name": "Table Widget from API Endpoint",
    "description": "A table widget from an API endpoint",
    "type": "table",
    "endpoint": "table_widget_from_api_endpoint",
    "gridData": {"w": 12, "h": 4},
})
@app.get("/table_widget_from_api_endpoint")
def table_widget_from_api_endpoint():
    """Get current TVL of all chains using Defi LLama"""
    response = requests.get("https://api.llama.fi/v2/chains")

    if response.status_code == 200:
        return response.json()

    print(f"Request error {response.status_code}: {response.text}")
    raise HTTPException(
        status_code=response.status_code,
        detail=response.text
    )



@register_widget({
    "name": "PDF Widget with Base64",
    "description": "Display a PDF file with base64 encoding",
    "endpoint": "pdf_widget_base64",
    "gridData": {
        "w": 20,
        "h": 20
    },
    "type": "pdf",
})
@app.get("/pdf_widget_base64")
def get_pdf_widget_base64():
    """Serve a file through base64 encoding."""
    try:
        name = "sample.pdf"
        with open(ROOT_PATH / name, "rb") as file:
            file_data = file.read()
            encoded_data = base64.b64encode(file_data)
            content = encoded_data.decode("utf-8")
    
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail="File not found"
        ) from exc
    
    return JSONResponse(
        headers={"Content-Type": "application/json"},
        content={
            "data_format": {
                "data_type": "pdf",
                "filename": name,
            },
            "content": content,
        },
    )


@register_widget({
    "name": "PDF Widget with URL",
    "description": "Display a PDF file",
    "type": "pdf", 
    "endpoint": "pdf_widget_url",
    "gridData": {
        "w": 20,
        "h": 20
    }
})
@app.get("/pdf_widget_url")
def get_pdf_widget_url():
    """Serve a file through URL."""
    file_reference = "https://openbb-assets.s3.us-east-1.amazonaws.com/testing/sample.pdf"
    if not file_reference:
        raise HTTPException(status_code=404, detail="File not found")
    return JSONResponse(
        headers={"Content-Type": "application/json"},
        content={
            "data_format": {
                "data_type": "pdf",
                "filename": "Sample.pdf",
            },
            "file_reference": file_reference,
        },
    )

# Sample PDF files data
SAMPLE_PDFS = [
    {
        "name": "Sample",
        "location": "sample.pdf",
        "url": "https://openbb-assets.s3.us-east-1.amazonaws.com/testing/sample.pdf",
    },
    {
        "name": "Bitcoin Whitepaper", 
        "location": "bitcoin.pdf",
        "url": "https://openbb-assets.s3.us-east-1.amazonaws.com/testing/bitcoin.pdf",
    }
]

# Sample PDF options endpoint
# This is a simple endpoint to get the list of available PDFs
# and return it in the JSON format. The reason why we need this endpoint is because the multi_file_viewer widget
# needs to know the list of available PDFs to display and we pass this endpoint to the widget as the optionsEndpoint
@app.get("/get_pdf_options")
async def get_pdf_options():
    """Get list of available PDFs"""
    return [
        {
            "label": pdf["name"],
            "value": pdf["name"]
        } for pdf in SAMPLE_PDFS
    ]

@register_widget({
    "name": "Multi PDF Viewer - Base64",
    "description": "View multiple PDF files using base64 encoding",
    "type": "multi_file_viewer",
    "endpoint": "multi_pdf_base64",
    "gridData": {
        "w": 20,
        "h": 10
    },
    "params": [
        {
            "paramName": "pdf_name",
            "description": "PDF file to display",
            "type": "endpoint",
            "label": "PDF File",
            "optionsEndpoint": "/get_pdf_options",
            "show": False
        }
    ]
})
@app.get("/multi_pdf_base64")
async def get_multi_pdf_base64(pdf_name: str):
    """Get PDF content in base64 format"""
    pdf = next((p for p in SAMPLE_PDFS if p["name"] == pdf_name), None)
    if not pdf:
        raise HTTPException(status_code=404, detail="PDF not found")

    file_path = ROOT_PATH / pdf["location"]
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="PDF file not found")

    with open(file_path, "rb") as file:
        base64_content = base64.b64encode(file.read()).decode("utf-8")

    return JSONResponse(
        headers={"Content-Type": "application/json"},
        content={
            "data_format": {
                "data_type": "pdf",
                "filename": f"{pdf['name']}.pdf"
            },
            "content": base64_content,
        },
    )

@register_widget({
    "name": "Multi PDF Viewer - URL",
    "description": "View multiple PDF files using URLs",
    "type": "multi_file_viewer", 
    "endpoint": "multi_pdf_url",
    "gridData": {
        "w": 20,
        "h": 10
    },
    "params": [
        {
            "paramName": "pdf_name",
            "description": "PDF file to display",
            "type": "endpoint",
            "label": "PDF File",
            "optionsEndpoint": "/get_pdf_options",
            "show": False
        }
    ]
})
@app.get("/multi_pdf_url")
async def get_multi_pdf_url(pdf_name: str):
    """Get PDF URL"""
    pdf = next((p for p in SAMPLE_PDFS if p["name"] == pdf_name), None)
    if not pdf:
        raise HTTPException(status_code=404, detail="PDF not found")

    return JSONResponse(
        headers={"Content-Type": "application/json"},
        content={
            "data_format": {"data_type": "pdf", "filename": f"{pdf['name']}.pdf"},
            "file_reference": pdf["url"],
        },
    )

# This is a simple markdown widget with a date picker parameter
# The date picker parameter is a date picker that allows users to select a specific date
# and we pass this parameter to the widget as the date_picker parameter 
@register_widget({
    "name": "Markdown Widget with Date Picker",
    "description": "A markdown widget with a date picker parameter",
    "endpoint": "markdown_widget_with_date_picker",
    "gridData": {"w": 16, "h": 6},
    "type": "markdown",
    "params": [
        {
            "paramName": "date_picker",
            "description": "Choose a date to display",
            "value": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
            "label": "Select Date",
            "type": "date"
        }
    ]
})
@app.get("/markdown_widget_with_date_picker")
def markdown_widget_with_date_picker(
    date_picker: str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
):
    """Returns a markdown widget with date picker parameter"""
    return f"""# Date Picker
Selected date: {date_picker}
"""

# This is a simple markdown widget with a text input parameter
# The text input parameter is a text input that allows users to enter a specific text
# and we pass this parameter to the widget as the textBox1 parameter
@register_widget({
    "name": "Markdown Widget with Text Input",
    "description": "A markdown widget with a text input parameter",
    "endpoint": "markdown_widget_with_text_input",
    "gridData": {"w": 16, "h": 6},
    "type": "markdown",
    "params": [
        {
            "paramName": "text_box",
            "value": "hello",
            "label": "Enter Text",
            "description": "Type something to display",
            "type": "text"
        }
    ]
})
@app.get("/markdown_widget_with_text_input")
def markdown_widget_with_text_input(text_box: str):
    """Returns a markdown widget with text input parameter"""
    return f"""# Text Input
Entered text: {text_box}
"""

# This is a simple markdown widget with a boolean parameter
# The boolean parameter is a boolean parameter that allows users to enable or disable a feature
# and we pass this parameter to the widget as the condition parameter
@register_widget({
    "name": "Markdown Widget with Boolean Toggle",
    "description": "A markdown widget with a boolean parameter",
    "endpoint": "markdown_widget_with_boolean",
    "gridData": {"w": 16, "h": 6},
    "type": "markdown",
    "params": [
        {
            "paramName": "condition",
            "description": "Enable or disable this feature",
            "label": "Toggle Option",
            "type": "boolean",
            "value": True,
        }
    ]
})
@app.get("/markdown_widget_with_boolean")
def markdown_widget_with_boolean(condition: bool):
    """Returns a markdown widget with boolean parameter"""
    return f"""# Boolean Toggle
Current state: {'Enabled' if condition else 'Disabled'}
"""

# This is a simple markdown widget with a text input parameter
# The text input parameter is a text input that allows users to enter a specific text
# and we pass this parameter to the widget as the textBox1 parameter
@register_widget({
    "name": "Markdown Widget with Number Input",
    "description": "A markdown widget with a number input parameter",
    "endpoint": "markdown_widget_with_number_input",
    "gridData": {"w": 16, "h": 6},
    "type": "markdown",
    "params": [
        {
            "paramName": "number_box",
            "description": "Enter a number",
            "value": 20,
            "label": "Enter Number",
            "type": "number"
        }
    ]
})
@app.get("/markdown_widget_with_number_input")
def markdown_widget_with_number_input(number_box: int):
    """Returns a markdown widget with number input parameter"""
    return f"""# Number Input
Entered number: {number_box}
"""

# This is a simple markdown widget with a dropdown parameter
# The dropdown parameter is a dropdown parameter that allows users to select a specific option
# and we pass this parameter to the widget as the days_picker parameter
# Note that the multiSelect parameter is set to True, so the user can select multiple options
@register_widget({
    "name": "Markdown Widget with Dropdown",
    "description": "A markdown widget with a dropdown parameter",
    "endpoint": "markdown_widget_with_dropdown",
    "gridData": {"w": 16, "h": 6},
    "type": "markdown",
    "params": [
        {
            "paramName": "days_picker",
            "description": "Number of days to look back",
            "value": "1",
            "label": "Select Days",
            "type": "text",
            "multiSelect": True,
            "options": [
                {
                    "value": "1",
                    "label": "1"
                },
                {
                    "value": "5",
                    "label": "5"
                },
                {
                    "value": "10",
                    "label": "10"
                },
                {
                    "value": "20",
                    "label": "20"
                },
                {
                    "value": "30",
                    "label": "30"
                }
            ]
        }
    ]
})
@app.get("/markdown_widget_with_dropdown")
def markdown_widget_with_dropdown(days_picker: str):
    """Returns a markdown widget with dropdown parameter"""
    return f"""# Dropdown
Selected days: {days_picker}
"""


# This is a single endpoint that returns a list of items with their details to be used in the multi select advanced dropdown widget
# The extraInfo is a way to have more information about the item at hand, to provide the user with more context about the item
# Note that since this doesn't has a register_widget decorator, it isn't recognzied as a widget by the OpenBB Workspace
# which is exactly what we want, since we want to use it as a simple endpoint to get the list of items
@app.get("/advanced_dropdown_options")
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


# This is a simple markdown widget with an advanced drodpown with more information and allowed to select multiple options
# It uses the optionsEndpoint to get the list of possible options as opposed to having them hardcoded in the widget
# The style parameter is used to customize the dropdown widget, in this case we are setting the popupWidth to 450px
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
@app.get("/markdown_widget_with_multi_select_advanced_dropdown")
def markdown_widget_with_multi_select_advanced_dropdown(stock_picker: str):
    """Returns a markdown widget with multi select advanced dropdown parameter"""
    return f"""# Multi Select Advanced Dropdown
Selected stocks: {stock_picker}
"""

# This endpoint provides the list of available documents
# It takes a category parameter to filter the documents
# The category parameter comes from the first dropdown in the widget
@app.get("/document_options")
def get_document_options(category: str = "all"):
    """Get filtered list of documents based on category"""
    # Sample documents data - This is our mock database of documents
    # Each document has a name and belongs to a category
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

    # If a specific category is selected, filter the documents
    if category != "all":
        filtered_docs = [
            doc for doc in SAMPLE_DOCUMENTS if doc["category"] == category
        ]
    
    # Return the filtered documents in the format expected by the dropdown
    # Each document needs a label (what the user sees) and a value (what's passed to the backend)
    return [
        {
            "label": doc["name"],
            "value": doc["name"]
        }
        for doc in filtered_docs
    ]

# This widget demonstrates how to create dependent dropdowns
# The first dropdown (category) controls what options are available in the second dropdown (document)
@register_widget({
    "name": "Dropdown Dependent Widget",
    "description": "A simple widget with a dropdown depending on another dropdown",
    "endpoint": "dropdown_dependent_widget",
    "gridData": {"w": 16, "h": 6},
    "type": "markdown",
    "params": [
        # First dropdown - Category selection
        # This is a simple text dropdown with predefined options
        {
            "paramName": "category",
            "description": "Category of documents to fetch",
            "value": "all",  # Default value
            "label": "Category",
            "type": "text",
            "options": [
                {"label": "All", "value": "all"},
                {"label": "Reports", "value": "reports"},
                {"label": "Presentations", "value": "presentations"}
            ]
        },
        # Second dropdown - Document selection
        # This is an endpoint-based dropdown that gets its options from /document_options
        # The optionsParams property tells the endpoint to use the value from the category dropdown
        # The $category syntax means "use the value of the parameter named 'category'"
        {
            "paramName": "document_type",
            "description": "Document to display",
            "label": "Select Document",
            "type": "endpoint",
            "optionsEndpoint": "/document_options",
            "optionsParams": {
                "category": "$category"  # This passes the selected category to the endpoint
            }
        },
    ]
})
@app.get("/dropdown_dependent_widget")
def dropdown_dependent_widget(category: str = "all", document_type: str = "all"):
    """Returns a dropdown dependent widget"""
    return f"""# Dropdown Dependent Widget
- Selected category: **{category}**
- Selected document: **{document_type}**
"""

# This endpoint provides a list of available stock symbols
# This is used by both widgets to populate their dropdown menus
@app.get("/get_tickers_list")
def get_tickers_list():
    """Returns a list of available stock symbols"""
    return [
        {"label": "Apple Inc.", "value": "AAPL"},
        {"label": "Microsoft Corporation", "value": "MSFT"},
        {"label": "Google", "value": "GOOGL"},
        {"label": "Amazon", "value": "AMZN"},
        {"label": "Tesla", "value": "TSLA"}
    ]

# This widget demonstrates how to use cellOnClick with grouping functionality
# The key feature here is the cellOnClick renderFn in the symbol column
# When a user clicks on a symbol cell, it triggers the groupBy action
# This action updates all widgets that use the same parameter name (symbol)
@register_widget({
    "name": "Table widget with grouping by cell click",
    "description": "A table widget that groups data when clicking on symbols. Click on a symbol to update all related widgets.",
    "type": "table",
    "endpoint": "table_widget_with_grouping_by_cell_click",
    "params": [
        {
            "paramName": "symbol",  # This parameter name is crucial - it's used for grouping
            "description": "Select stocks to display",
            "value": "AAPL",
            "label": "Symbol",
            "type": "endpoint",
            "optionsEndpoint": "/get_tickers_list",
            "multiSelect": False,
            "show": True
        }
    ],
    "data": {
        "table": {
            "showAll": True,
            "columnsDefs": [
                {
                    "field": "symbol",
                    "headerName": "Symbol",
                    "cellDataType": "text",
                    "width": 120,
                    "pinned": "left",
                    # The cellOnClick renderFn makes cells clickable
                    "renderFn": "cellOnClick",
                    "renderFnParams": {
                        # groupBy action type means clicking will update all widgets using this parameter
                        "actionType": "groupBy",
                        # This must match the paramName in both widgets for grouping to work
                        "groupByParamName": "symbol"
                    }
                },
                {
                    "field": "price",
                    "headerName": "Price",
                    "cellDataType": "number",
                    "formatterFn": "none",
                    "width": 120
                },
                {
                    "field": "change",
                    "headerName": "Change",
                    "cellDataType": "number",
                    "formatterFn": "percent",
                    "renderFn": "greenRed",  # Shows positive/negative changes in green/red
                    "width": 120
                },
                {
                    "field": "volume",
                    "headerName": "Volume",
                    "cellDataType": "number",
                    "formatterFn": "int",
                    "width": 150
                }
            ]
        }
    },
    "gridData": {
        "w": 20,
        "h": 9
    }
})
@app.get("/table_widget_with_grouping_by_cell_click")
def table_widget_with_grouping_by_cell_click(symbol: str = "AAPL"):
    """Returns stock data that can be grouped by symbol"""
    # Mock data - in a real application, this would come from a data source
    mock_data = [
        {
            "symbol": "AAPL",
            "price": 175.50,
            "change": 0.015,
            "volume": 50000000
        },
        {
            "symbol": "MSFT",
            "price": 380.25,
            "change": -0.008,
            "volume": 25000000
        },
        {
            "symbol": "GOOGL",
            "price": 140.75,
            "change": 0.022,
            "volume": 15000000
        },
        {
            "symbol": "AMZN",
            "price": 175.25,
            "change": 0.005,
            "volume": 30000000
        },
        {
            "symbol": "TSLA",
            "price": 175.50,
            "change": -0.012,
            "volume": 45000000
        }
    ]
    
    return mock_data

# This widget demonstrates how to use the grouped symbol parameter
# It will update automatically when a symbol is clicked in the stock table
# The key to making this work is using the same paramName ("symbol") as the table widget
# When a user clicks a symbol in the table, this widget will automatically update
# to show details for the selected symbol
@register_widget({
    "name": "Widget managed by parameter from cell click on table widget",
    "description": "This widget demonstrates how to use the grouped symbol parameter from a table widget. When a symbol is clicked in the table, this widget will automatically update to show details for the selected symbol.",
    "type": "markdown",
    "endpoint": "widget_managed_by_parameter_from_cell_click_on_table_widget",
    "params": [
        {
            "paramName": "symbol",  # Must match the groupByParamName in the table widget
            "description": "The symbol to get details for",
            "value": "AAPL",
            "label": "Symbol",
            "type": "endpoint",
            "optionsEndpoint": "/get_tickers_list",
            "show": True
        }
    ],
    "gridData": {
        "w": 20,
        "h": 6
    }
})
@app.get("/widget_managed_by_parameter_from_cell_click_on_table_widget")
def widget_managed_by_parameter_from_cell_click_on_table_widget(symbol: str = "AAPL"):
    """Returns detailed information about the selected stock"""
    # Mock data - in a real application, this would come from a data source
    stock_details = {
        "AAPL": {
            "name": "Apple Inc.",
            "sector": "Technology",
            "market_cap": "2.8T",
            "pe_ratio": 28.5,
            "dividend_yield": 0.5,
            "description": "Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories worldwide."
        },
        "MSFT": {
            "name": "Microsoft Corporation",
            "sector": "Technology",
            "market_cap": "2.5T",
            "pe_ratio": 35.2,
            "dividend_yield": 0.8,
            "description": "Microsoft Corporation develops and supports software, services, devices, and solutions worldwide."
        },
        "GOOGL": {
            "name": "Alphabet Inc.",
            "sector": "Technology",
            "market_cap": "1.8T",
            "pe_ratio": 25.8,
            "dividend_yield": 0.0,
            "description": "Alphabet Inc. provides various products and platforms in the United States, Europe, the Middle East, Africa, the Asia-Pacific, Canada, and Latin America."
        },
        "AMZN": {
            "name": "Amazon.com Inc.",
            "sector": "Consumer Cyclical",
            "market_cap": "1.6T",
            "pe_ratio": 45.2,
            "dividend_yield": 0.0,
            "description": "Amazon.com Inc. engages in the retail sale of consumer products and subscriptions in North America and internationally."
        },
        "TSLA": {
            "name": "Tesla Inc.",
            "sector": "Automotive",
            "market_cap": "800B",
            "pe_ratio": 65.3,
            "dividend_yield": 0.0,
            "description": "Tesla Inc. designs, develops, manufactures, leases, and sells electric vehicles, and energy generation and storage systems in the United States, China, and internationally."
        }
    }
    
    # Get details for the selected symbol
    # If no symbol is selected or symbol doesn't exist, return default values
    details = stock_details.get(symbol, {
        "name": "Unknown",
        "sector": "Unknown",
        "market_cap": "N/A",
        "pe_ratio": 0,
        "dividend_yield": 0,
        "description": "No information available for this symbol."
    })
    
    return f"""# {details['name']} ({symbol})
**Sector:** {details['sector']}\n
**Market Cap:** ${details['market_cap']}\n
**P/E Ratio:** {details['pe_ratio']}\n
**Dividend Yield:** {details['dividend_yield']}%\n\n

{details['description']}
"""

