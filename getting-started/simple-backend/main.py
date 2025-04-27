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
    return {"Info": "Hello World example"}


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


# Simple markdown widget example
# Note that the gridData specifies the size of the widget in the OpenBB Workspace
@register_widget({
    "name": "Markdown Widget Example",
    "description": "A markdown widget example",
    "type": "markdown",
    "endpoint": "markdown_widget_example",
    "gridData": {"w": 12, "h": 4},
})
@app.get("/markdown_widget_example")
def markdown_widget_example():
    """Returns a markdown widget example"""
    return f"# Markdown Widget Example"

# Simple markdown widget example
# Note that the category and subcategory specify the category and subcategory of the widget in the OpenBB Workspace
# This is important to organize the widgets in the OpenBB Workspace, but also for AI agents to find the best 
# widgets to utilize for a given task
@register_widget({
    "name": "Markdown Widget Example with Category and Subcategory",
    "description": "A markdown widget example with category and subcategory",
    "type": "markdown",
    "category": "Widget Examples",
    "subcategory": "Markdown Widgets",
    "endpoint": "markdown_widget_example_with_category_and_subcategory",
    "gridData": {"w": 12, "h": 4},
})
@app.get("/markdown_widget_example_with_category_and_subcategory")
def markdown_widget_example_with_category_and_subcategory():
    """Returns a markdown widget example with category and subcategory"""
    return f"# Markdown Widget Example with Category and Subcategory"


# Markdown Widget Example with Error Handling
# This is a simple example of how to handle errors in a widget
@register_widget({
    "name": "Markdown Widget Example with Error Handling",
    "description": "A markdown widget example with error handling",
    "type": "markdown",
    "endpoint": "markdown_widget_example_with_error_handling",
    "gridData": {"w": 12, "h": 4},
})
@app.get("/markdown_widget_example_with_error_handling")
def markdown_widget_example_with_error_handling():
    """Returns a markdown widget example with error handling"""
    raise HTTPException(
        status_code=500,
        detail="Error that just occurred"
    )


@register_widget({
    "name": "Metric Widget",
    "description": "A metric widget example",
    "endpoint": "metric_widget",
    "gridData": {
      "w": 5,
      "h": 5
    },
    "type": "metric"
})
@app.get("/metric_widget")
def metric_widget():
    # Example data structure
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

# Simple table widget example
# Utilize mock data for demonstration purposes on how a table widget can be used
@register_widget({
    "name": "Table Widget Example",
    "description": "A table widget example",
    "type": "table",
    "endpoint": "table_widget_example",
    "gridData": {"w": 12, "h": 4},
})
@app.get("/table_widget_example")
def table_widget_example():
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


# Simple table widget example with column definitions
# The most important part of this example is the "columnsDefs" key in the data object
# Here's what you can find in this example:
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
    "name": "Table Widget Example with Column Definitions",
    "description": "A table widget example with column definitions",
    "type": "table",
    "endpoint": "table_widget_example_with_column_definitions",
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
@app.get("/table_widget_example_with_column_definitions")
def table_widget_example_with_column_definitions():
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


# Simple table widget example with hover card
# The most important part of this example that hasn't been covered in the previous example is the hover card is the "renderFn" key in the columnsDefs object
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
    "name": "Table Widget Example with Render Functions",
    "description": "A table widget example with render functions",
    "type": "table",
    "endpoint": "table_widget_example_with_render_functions",
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
@app.get("/table_widget_example_with_render_functions")
def table_widget_example_with_render_functions():
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


# Simple table widget example with hover card
# The most important part of this example that hasn't been covered in the previous examples is the hover card
# which is a feature that allows you to display additional information when hovering over a cell
@register_widget({
    "name": "Table Widget Example with Hover Card",
    "description": "A table widget example with hover card",
    "type": "table",
    "endpoint": "table_widget_example_with_hover_card",
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
@app.get("/table_widget_example_with_hover_card")
def table_widget_example_with_hover_card():
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


# Table to Chart Widget Example
# The most important part of this example is that the default view is a chart that comes from the "chartView" key in the data object
# chartDataType: Specifies how data is treated in a chart.
#                Example: "category"
#                Possible values: "category", "series", "time", "excluded"
@register_widget({
    "name": "Table to Chart Widget Example",
    "description": "A table widget example",
    "type": "table",
    "endpoint": "table_to_chart_widget_example",
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
@app.get("/table_to_chart_widget_example")
def table_to_chart_widget_example():
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



# Table to time series Widget Example
# In here we will see how to use a table widget to display a time series chart
@register_widget({
    "name": "Table to Time Series Widget Example",
    "description": "A table widget example",
    "type": "table",
    "endpoint": "table_to_time_series_widget_example",
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
@app.get("/table_to_time_series_widget_example")
def table_to_time_series_widget_example():
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

# Simple table widget example from an API endpoint
# This is a simple example of how to use a table widget from an API endpoint
# Note that the endpoint is the endpoint of the API that will be used to fetch the data
# and the data is returned in the JSON format
@register_widget({
    "name": "Table Widget Example from API Endpoint",
    "description": "A table widget example from an API endpoint",
    "type": "table",
    "endpoint": "table_widget_from_api_endpoint_example",
    "gridData": {"w": 12, "h": 4},
})
@app.get("/table_widget_from_api_endpoint_example")
def table_widget_from_api_endpoint_example():
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
# This is a simple example of how to use an endpoint to get the list of available PDFs
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

# This is a simple example of how to use a markdown widget with a date picker parameter
# The date picker parameter is a date picker that allows users to select a specific date
# and we pass this parameter to the widget as the date_picker parameter 
@register_widget({
    "name": "Markdown Widget with Date Picker",
    "description": "A markdown widget example with a date picker parameter",
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
    """Returns a markdown widget example with date picker parameter"""
    return f"""# Date Picker Example
Selected date: {date_picker}
"""

# This is a simple example of how to use a markdown widget with a text input parameter
# The text input parameter is a text input that allows users to enter a specific text
# and we pass this parameter to the widget as the textBox1 parameter
@register_widget({
    "name": "Markdown Widget with Text Input",
    "description": "A markdown widget example with a text input parameter",
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
    """Returns a markdown widget example with text input parameter"""
    return f"""# Text Input Example
Entered text: {text_box}
"""

# This is a simple example of how to use a markdown widget with a boolean parameter
# The boolean parameter is a boolean parameter that allows users to enable or disable a feature
# and we pass this parameter to the widget as the condition parameter
@register_widget({
    "name": "Markdown Widget with Boolean Toggle",
    "description": "A markdown widget example with a boolean parameter",
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
    """Returns a markdown widget example with boolean parameter"""
    return f"""# Boolean Toggle Example
Current state: {'Enabled' if condition else 'Disabled'}
"""

# This is a simple example of how to use a markdown widget with a dropdown parameter
# The dropdown parameter is a dropdown parameter that allows users to select a specific option
# and we pass this parameter to the widget as the daysPicker1 parameter
@register_widget({
    "name": "Markdown Widget with Dropdown",
    "description": "A markdown widget example with a dropdown parameter",
    "endpoint": "markdown_widget_with_dropdown",
    "gridData": {"w": 16, "h": 6},
    "type": "markdown",
    "params": [
        {
            "paramName": "days_picker",
            "value": "1",
            "label": "Select Days",
            "type": "text",
            "multiSelect": True,
            "description": "Number of days to look back",
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
    """Returns a markdown widget example with dropdown parameter"""
    return f"""# Dropdown Example
Selected days: {days_picker}
"""