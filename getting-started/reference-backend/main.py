# Import required libraries
import json
import base64
import requests
from pathlib import Path
from fastapi import FastAPI, HTTPException, Body, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly_config import get_theme_colors, base_layout, get_toolbar_config
import random
from pydantic import BaseModel, Field
from uuid import UUID
from typing import Any, List, Literal, List
from functools import wraps
import asyncio


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
    "https://pro.openbb.dev"
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

# Initialize empty dictionary for widgets
WIDGETS = {}


def register_widget(widget_config):
    """
    Decorator that registers a widget configuration in the WIDGETS dictionary.

    Args:
        widget_config (dict): The widget configuration to add to the WIDGETS 
            dictionary. This should follow the same structure as other entries 
            in WIDGETS.

    Returns:
        function: The decorated function.
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Call the original function
            return await func(*args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Call the original function
            return func(*args, **kwargs)

        # Extract the endpoint from the widget_config
        endpoint = widget_config.get("endpoint")
        if endpoint:
            # Add an id field to the widget_config if not already present
            if "id" not in widget_config:
                widget_config["id"] = endpoint

            WIDGETS[endpoint] = widget_config

        # Return the appropriate wrapper based on whether the function is async
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    return decorator


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


# Apps configuration file for the OpenBB Workspace
# it contains the information and configuration about all the
# apps that will be displayed in the OpenBB Workspace
@app.get("/apps.json")
def get_apps():
    """Apps configuration file for the OpenBB Workspace
    
    Returns:
        JSONResponse: The contents of apps.json file
    """
    # Read and return the apps configuration file
    return JSONResponse(
        content=json.load((Path(__file__).parent.resolve() / "apps.json").open())
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
    return "# Markdown Widget"

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

# Markdown Widget with a Run button
# The run button is a button that will execute the code in the widget
# this is useful for widgets that are not static and require some computation
# that may take a while to complete - e.g. running a model, fetching data, etc.
@register_widget({
    "name": "Markdown Widget with Run Button",
    "description": "A markdown widget with a run button",
    "type": "markdown",
    "endpoint": "markdown_widget_with_run_button",
    "gridData": {"w": 12, "h": 4},
    "runButton": True,
})
@app.get("/markdown_widget_with_run_button")
def markdown_widget_with_run_button():
    """Returns a markdown widget with current time"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"### Current time: {current_time}"

# Markdown Widget with a Short Refetch Interval
# The refetch interval is the interval at which the widget will be refreshed
# Use lower values for real-time data (e.g., 60000 for 1-minute updates)
# Higher values recommended for static or slowly changing data
@register_widget({
    "name": "Markdown Widget with Short Refetch Interval",
    "description": "A markdown widget with a short refetch interval",
    "type": "markdown",
    "endpoint": "markdown_widget_with_short_refetch_interval",
    "gridData": {"w": 12, "h": 4},
    "refetchInterval": 1000
})
@app.get("/markdown_widget_with_short_refetch_interval")
def markdown_widget_with_short_refetch_interval():
    """Returns a markdown widget with current time"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"### Current time: {current_time}"

# Markdown Widget with a Short Refetch Interval and a Run Button
# The refresh interval is set to 10000ms (10 seconds) but the run button is enabled
# which means that the user can refresh the widget manually
@register_widget({
    "name": "Markdown Widget with Short Refetch Interval and a Run Button",
    "description": "A markdown widget with a short refetch interval and a run button",
    "type": "markdown",
    "endpoint": "markdown_widget_with_short_refetch_interval_and_run_button",
    "gridData": {"w": 12, "h": 4},
    "refetchInterval": 10000,
    "runButton": True
})
@app.get("/markdown_widget_with_short_refetch_interval_and_run_button")
def markdown_widget_with_short_refetch_interval_and_run_button():
    """Returns a markdown widget with current time"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"### Current time: {current_time}"

# Structured API Widget Example
# Demonstrates how to organize API endpoints by vendor/domain for better maintainability
# Benefits:
# - Clear separation of concerns
# - Reusable parameter names and options across related endpoints
# - Easier to manage vendor-specific configurations
# - Improved code organization and readability
# Example structure: /vendor1/endpoint1, /vendor1/endpoint2, /vendor2/endpoint1, /vendor2/endpoint2, ...
# This can be done not only based on vendors, but also based on the type of data, e.g. /stocks/endpoint1, /commodities/endpoint2, etc.
@register_widget({
    "name": "Markdown Widget with better structured API",
    "description": "A simple markdown widget with a better structured API",
    "type": "markdown",
    "endpoint": "/vendor1/markdown_widget_with_better_structured_api",
    "gridData": {"w": 12, "h": 4},
    "refetchInterval": 10000,
    "runButton": True
})
@app.get("/vendor1/markdown_widget_with_better_structured_api")
def markdown_widget_with_better_structured_api():
    """Returns a markdown widget with current time"""
    return "vendor1/markdown_widget_with_better_structured_api"

# Markdown Widget with Stale Time
# The stale time is the time after which the data will be considered stale
# and you will see a refresh button in the widget becoming orange to indicate that the data is stale
@register_widget({
    "name": "Markdown Widget with Stale Time",
    "description": "A markdown widget with stale time",
    "type": "markdown",
    "endpoint": "markdown_widget_with_stale_time",
    "gridData": {"w": 12, "h": 4},
    "staleTime": 5000
})
@app.get("/markdown_widget_with_stale_time")
def markdown_widget_with_stale_time():
    """Returns a markdown widget with current time"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"### Current time: {current_time}"

# Markdown Widget with Refetch Interval and Stale Time
# The refetch interval is set to 10000ms (10 seconds) and the stale time is set to 5000ms (5 seconds)
# Data older than stale time will make the refresh button in the widget become orange to indicate that the data is stale
# and once it reaches the refetch interval, the widget will be refreshed and the indicator will turn green again
@register_widget({
    "name": "Markdown Widget with Refetch Interval and Shorter Stale Time",
    "description": "A markdown widget with a short refetch interval and a shorter stale time",
    "type": "markdown",
    "endpoint": "markdown_widget_with_refetch_interval_and_shorter_stale_time",
    "gridData": {"w": 12, "h": 4},
    "refetchInterval": 10000,
    "staleTime": 5000
})
@app.get("/markdown_widget_with_refetch_interval_and_shorter_stale_time")
def markdown_widget_with_refetch_interval_and_shorter_stale_time():
    """Returns a markdown widget with current time"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"### Current time: {current_time}"

# Markdown Widget with Image from URL
# This is a simple widget that demonstrates how to display an image from a URL
@register_widget({
    "name": "Markdown Widget with Image from URL",
    "description": "A markdown widget with an image from a URL",
    "type": "markdown",
    "endpoint": "markdown_widget_with_image_from_url",
    "gridData": {"w": 20, "h": 20},
})
@app.get("/markdown_widget_with_image_from_url")
def markdown_widget_with_image_from_url():
    """Returns a markdown widget with an image from a URL"""
    # Use a simpler, more reliable image URL
    image_url = "https://api.star-history.com/svg?repos=openbb-finance/OpenBB&type=Date&theme=dark"
    
    try:
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Verify the response is actually an image
        content_type = response.headers.get('content-type', '')
        if not content_type.startswith('image/'):
            raise HTTPException(
                status_code=500,
                detail=f"URL did not return an image. Content-Type: {content_type}"
            )

        # Convert the image to base64
        image_base64 = base64.b64encode(response.content).decode('utf-8')
        
        # Return the markdown with the base64 image
        return f"![OpenBB Logo](data:{content_type};base64,{image_base64})"
        
    except requests.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch image: {str(e)}"
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing image: {str(e)}"
        ) from e


# Markdown Widget with Local Image
# This is a simple widget that demonstrates how to display a local image
@register_widget({
    "name": "Markdown Widget with Local Image",
    "description": "A markdown widget with a local image",
    "type": "markdown",
    "endpoint": "markdown_widget_with_local_image",
    "gridData": {"w": 20, "h": 20},
})
@app.get("/markdown_widget_with_local_image")
def markdown_widget_with_local_image():
    """Returns a markdown widget with a local image"""
    # Read the local image file
    try:
        with open("img.png", "rb") as image_file:
            # Convert the image to base64
            image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
            return f"![Local Image](data:image/png;base64,{image_base64})"
    except FileNotFoundError:
        raise HTTPException(
            status_code=500,
            detail="Image file not found"
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error reading image: {str(e)}"
        ) from e


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
                    "headerName": "7d Change",
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
    },
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
            "url": file_reference,
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
            "show": False,
            "value": ["Bitcoin Whitepaper"],
            "multiSelect": True,
            "roles": ["fileSelector"]
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
            "value": ["Sample"],
            "show": False,
            "multiSelect": True,
            "roles": ["fileSelector"]
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
            "url": pdf["url"],
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


# This is a simple markdown widget with an editable text input parameter
# The editable text input parameter is a text input that allows users to enter a specific text
# and we pass all of them as a list to the widget as the text_box parameter
# The user is able to add more by just typing a new variable and pressing enter
@register_widget({
    "name": "Markdown Widget with Editable Text Input",
    "description": "A markdown widget with an editable text input parameter",
    "endpoint": "markdown_widget_with_editable_text_input",
    "gridData": {"w": 16, "h": 6},
    "type": "markdown",
    "params": [
        {
            "paramName": "text_box",
            "value": "var1,var2,var3",
            "label": "Enter Text",
            "description": "Type something to display",
            "editable": True,
            "type": "text"
        }
    ]
})
@app.get("/markdown_widget_with_editable_text_input")
def markdown_widget_with_editable_text_input(text_box: str):
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

    # Filter documents based on category
    filtered_docs = (
        SAMPLE_DOCUMENTS if category == "all"
        else [doc for doc in SAMPLE_DOCUMENTS if doc["category"] == category]
    )
    
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


# This endpoint provides the list of car manufacturers that can be selected
# It is used by both the performance and details widgets to ensure they share the same options
# This is an example of parameter grouping - both widgets use the same "company" paramName
# which allows them to be grouped together in the UI
@app.get("/company_options")
def get_company_options():
    """Returns a list of available car manufacturers"""
    return [
        {"label": "Toyota Motor Corporation", "value": "TM"},
        {"label": "Volkswagen Group", "value": "VWAGY"},
        {"label": "General Motors", "value": "GM"},
        {"label": "Ford Motor Company", "value": "F"},
        {"label": "Tesla Inc.", "value": "TSLA"}
    ]


# This widget demonstrates parameter grouping through shared paramNames
# Both this widget and the company_details widget below use the same paramNames:
# - "company" for manufacturer selection
# - "year" for model year selection
# When widgets share the same paramName, they can be grouped together in the UI
# This grouping can be configured in the apps.json file or through the UI
# When grouped, changing a parameter in one widget will automatically update the other
# Note that both widgets also share the same optionsEndpoint ("/company_options")
# which ensures they have identical options in their dropdowns
@register_widget({
    "name": "Car Manufacturer Performance",
    "description": "Displays performance metrics for the selected car manufacturer",
    "type": "table",
    "endpoint": "company_performance",
    "gridData": {"w": 16, "h": 8},
    "params": [
        {
            "paramName": "company",  # Shared paramName with company_details widget
            "description": "Select a car manufacturer to view performance",
            "value": "TM",
            "label": "Manufacturer",
            "type": "endpoint",
            "optionsEndpoint": "/company_options"  # Shared endpoint with company_details widget
        },
        {
            "paramName": "year",  # Shared paramName with company_details widget
            "description": "Select model year to view performance",
            "value": "2024",
            "label": "Model Year",
            "type": "text",
            "options": [
                {"label": "2024", "value": "2024"},
                {"label": "2023", "value": "2023"},
                {"label": "2022", "value": "2022"}
            ]
        }
    ],
    "data": {
        "table": {
            "showAll": True,
            "columnsDefs": [
                {
                    "field": "metric",
                    "headerName": "Metric",
                    "cellDataType": "text",
                    "width": 150
                },
                {
                    "field": "value",
                    "headerName": "Value",
                    "cellDataType": "text",
                    "width": 150
                },
                {
                    "field": "change",
                    "headerName": "Change",
                    "cellDataType": "number",
                    "formatterFn": "percent",
                    "renderFn": "greenRed",
                    "width": 150
                }
            ]
        }
    }
})
@app.get("/company_performance")
def get_company_performance(company: str, year: str = "2024"):
    """Returns car manufacturer performance metrics"""
    performance_data = {
        "TM": {
            "2024": [
                {"metric": "Global Sales", "value": "10.5M", "change": 5.2},
                {"metric": "EV Sales", "value": "1.2M", "change": 45.8},
                {"metric": "Operating Margin", "value": "8.5%", "change": 1.2},
                {"metric": "R&D Investment", "value": "$12.5B", "change": 15.3}
            ],
            "2023": [
                {"metric": "Global Sales", "value": "9.98M", "change": 3.1},
                {"metric": "EV Sales", "value": "0.82M", "change": 35.2},
                {"metric": "Operating Margin", "value": "7.3%", "change": 0.8},
                {"metric": "R&D Investment", "value": "$10.8B", "change": 12.5}
            ],
            "2022": [
                {"metric": "Global Sales", "value": "9.67M", "change": 1.2},
                {"metric": "EV Sales", "value": "0.61M", "change": 25.4},
                {"metric": "Operating Margin", "value": "6.5%", "change": -0.5},
                {"metric": "R&D Investment", "value": "$9.6B", "change": 8.7}
            ]
        },
        "VWAGY": {
            "2024": [
                {"metric": "Global Sales", "value": "9.2M", "change": 4.8},
                {"metric": "EV Sales", "value": "1.5M", "change": 52.3},
                {"metric": "Operating Margin", "value": "7.8%", "change": 1.5},
                {"metric": "R&D Investment", "value": "$15.2B", "change": 18.5}
            ],
            "2023": [
                {"metric": "Global Sales", "value": "8.78M", "change": 3.2},
                {"metric": "EV Sales", "value": "0.98M", "change": 42.1},
                {"metric": "Operating Margin", "value": "6.3%", "change": 0.9},
                {"metric": "R&D Investment", "value": "$12.8B", "change": 15.2}
            ],
            "2022": [
                {"metric": "Global Sales", "value": "8.5M", "change": 1.8},
                {"metric": "EV Sales", "value": "0.69M", "change": 32.5},
                {"metric": "Operating Margin", "value": "5.4%", "change": -0.7},
                {"metric": "R&D Investment", "value": "$11.1B", "change": 10.8}
            ]
        },
        "GM": {
            "2024": [
                {"metric": "Global Sales", "value": "6.8M", "change": 3.5},
                {"metric": "EV Sales", "value": "0.8M", "change": 48.2},
                {"metric": "Operating Margin", "value": "8.2%", "change": 1.8},
                {"metric": "R&D Investment", "value": "$9.5B", "change": 16.5}
            ],
            "2023": [
                {"metric": "Global Sales", "value": "6.57M", "change": 2.1},
                {"metric": "EV Sales", "value": "0.54M", "change": 38.5},
                {"metric": "Operating Margin", "value": "6.4%", "change": 1.2},
                {"metric": "R&D Investment", "value": "$8.15B", "change": 14.2}
            ],
            "2022": [
                {"metric": "Global Sales", "value": "6.43M", "change": 0.8},
                {"metric": "EV Sales", "value": "0.39M", "change": 28.7},
                {"metric": "Operating Margin", "value": "5.2%", "change": -0.5},
                {"metric": "R&D Investment", "value": "$7.13B", "change": 9.8}
            ]
        },
        "F": {
            "2024": [
                {"metric": "Global Sales", "value": "4.2M", "change": 2.8},
                {"metric": "EV Sales", "value": "0.6M", "change": 42.5},
                {"metric": "Operating Margin", "value": "7.5%", "change": 1.5},
                {"metric": "R&D Investment", "value": "$8.2B", "change": 15.8}
            ],
            "2023": [
                {"metric": "Global Sales", "value": "4.08M", "change": 1.5},
                {"metric": "EV Sales", "value": "0.42M", "change": 35.2},
                {"metric": "Operating Margin", "value": "6.0%", "change": 1.0},
                {"metric": "R&D Investment", "value": "$7.08B", "change": 13.5}
            ],
            "2022": [
                {"metric": "Global Sales", "value": "4.02M", "change": 0.5},
                {"metric": "EV Sales", "value": "0.31M", "change": 25.8},
                {"metric": "Operating Margin", "value": "5.0%", "change": -0.8},
                {"metric": "R&D Investment", "value": "$6.24B", "change": 8.9}
            ]
        },
        "TSLA": {
            "2024": [
                {"metric": "Global Sales", "value": "2.1M", "change": 35.2},
                {"metric": "EV Sales", "value": "2.1M", "change": 35.2},
                {"metric": "Operating Margin", "value": "15.5%", "change": 3.7},
                {"metric": "R&D Investment", "value": "$4.5B", "change": 25.8}
            ],
            "2023": [
                {"metric": "Global Sales", "value": "1.55M", "change": 28.5},
                {"metric": "EV Sales", "value": "1.55M", "change": 28.5},
                {"metric": "Operating Margin", "value": "11.8%", "change": 2.5},
                {"metric": "R&D Investment", "value": "$3.58B", "change": 22.3}
            ],
            "2022": [
                {"metric": "Global Sales", "value": "1.21M", "change": 21.8},
                {"metric": "EV Sales", "value": "1.21M", "change": 21.8},
                {"metric": "Operating Margin", "value": "9.3%", "change": 1.8},
                {"metric": "R&D Investment", "value": "$2.93B", "change": 18.5}
            ]
        }
    }
    
    return performance_data.get(company, {}).get(year, [
        {"metric": "No Data", "value": "N/A", "change": 0}
    ])

# This widget is grouped with the company_performance widget above
# They share the same paramNames ("company" and "year")
# When these widgets are grouped in the UI or apps.json:
# 1. Selecting a manufacturer in either widget updates both
# 2. Changing the year in either widget updates both
# This creates a synchronized view of both performance metrics and company details
# The key to making this work is:
# 1. Using identical paramNames in both widgets
# 2. Using the same optionsEndpoint for shared parameters
# 3. Configuring the grouping in apps.json or through the UI
@register_widget({
    "name": "Car Manufacturer Details",
    "description": "Displays detailed information about the selected car manufacturer",
    "type": "markdown",
    "endpoint": "company_details",
    "gridData": {"w": 16, "h": 8},
    "params": [
        {
            "paramName": "company",  # Shared paramName with company_performance widget
            "description": "Select a car manufacturer to view details",
            "value": "TM",
            "label": "Manufacturer",
            "type": "endpoint",
            "optionsEndpoint": "/company_options"  # Shared endpoint with company_performance widget
        },
        {
            "paramName": "year",  # Shared paramName with company_performance widget
            "description": "Select model year to view details",
            "value": "2024",
            "label": "Model Year",
            "type": "text",
            "options": [
                {"label": "2024", "value": "2024"},
                {"label": "2023", "value": "2023"},
                {"label": "2022", "value": "2022"}
            ]
        }
    ]
})
@app.get("/company_details")
def get_company_details(company: str, year: str = "2024"):
    """Returns car manufacturer details in markdown format"""
    company_info = {
        "TM": {
            "name": "Toyota Motor Corporation",
            "sector": "Automotive",
            "market_cap": "280B",
            "pe_ratio": 9.5,
            "dividend_yield": 2.1,
            "description": "Toyota Motor Corporation designs, manufactures, assembles, and sells passenger vehicles, minivans, commercial vehicles, and related parts and accessories worldwide.",
            "models": {
                "2024": ["Camry", "Corolla", "RAV4", "Highlander"],
                "2023": ["Camry", "Corolla", "RAV4", "Highlander"],
                "2022": ["Camry", "Corolla", "RAV4", "Highlander"]
            }
        },
        "VWAGY": {
            "name": "Volkswagen Group",
            "sector": "Automotive",
            "market_cap": "75B",
            "pe_ratio": 4.2,
            "dividend_yield": 3.5,
            "description": "Volkswagen Group manufactures and sells automobiles worldwide. The company offers passenger cars, commercial vehicles, and power engineering systems.",
            "models": {
                "2024": ["Golf", "Passat", "Tiguan", "ID.4"],
                "2023": ["Golf", "Passat", "Tiguan", "ID.4"],
                "2022": ["Golf", "Passat", "Tiguan", "ID.4"]
            }
        },
        "GM": {
            "name": "General Motors",
            "sector": "Automotive",
            "market_cap": "45B",
            "pe_ratio": 5.8,
            "dividend_yield": 1.2,
            "description": "General Motors designs, builds, and sells cars, trucks, crossovers, and automobile parts worldwide.",
            "models": {
                "2024": ["Silverado", "Equinox", "Malibu", "Corvette"],
                "2023": ["Silverado", "Equinox", "Malibu", "Corvette"],
                "2022": ["Silverado", "Equinox", "Malibu", "Corvette"]
            }
        },
        "F": {
            "name": "Ford Motor Company",
            "sector": "Automotive",
            "market_cap": "48B",
            "pe_ratio": 7.2,
            "dividend_yield": 4.8,
            "description": "Ford Motor Company designs, manufactures, markets, and services a line of Ford trucks, cars, sport utility vehicles, electrified vehicles, and Lincoln luxury vehicles.",
            "models": {
                "2024": ["F-150", "Mustang", "Explorer", "Mach-E"],
                "2023": ["F-150", "Mustang", "Explorer", "Mach-E"],
                "2022": ["F-150", "Mustang", "Explorer", "Mach-E"]
            }
        },
        "TSLA": {
            "name": "Tesla Inc.",
            "sector": "Automotive",
            "market_cap": "800B",
            "pe_ratio": 65.3,
            "dividend_yield": 0.0,
            "description": "Tesla Inc. designs, develops, manufactures, leases, and sells electric vehicles, and energy generation and storage systems in the United States, China, and internationally.",
            "models": {
                "2024": ["Model 3", "Model Y", "Model S", "Model X"],
                "2023": ["Model 3", "Model Y", "Model S", "Model X"],
                "2022": ["Model 3", "Model Y", "Model S", "Model X"]
            }
        }
    }
    
    details = company_info.get(company, {
        "name": "Unknown",
        "sector": "Unknown",
        "market_cap": "N/A",
        "pe_ratio": 0,
        "dividend_yield": 0,
        "description": "No information available for this manufacturer.",
        "models": {"2024": [], "2023": [], "2022": []}
    })
    
    models = details['models'].get(year, [])
    
    return f"""# {details['name']} ({company}) - {year} Models
**Sector:** {details['sector']}
**Market Cap:** ${details['market_cap']}
**P/E Ratio:** {details['pe_ratio']}
**Dividend Yield:** {details['dividend_yield']}%

{details['description']}

## {year} Model Lineup
{', '.join(models)}
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

# Plotly chart
# This widget demonstrates how to use the Plotly library to create a chart
# this gives you the ability to create any interactive type of charts with unlimited flexibility
@register_widget({
    "name": "Plotly Chart",
    "description": "Plotly chart",
    "type": "chart",
    "endpoint": "plotly_chart",
    "gridData": {"w": 40, "h": 15}
})

@app.get("/plotly_chart")
def get_plotly_chart():
    # Generate mock time series data
    mock_data = [
        {"date": "2023-01-01", "return": 2.5, "transactions": 1250},
        {"date": "2023-01-02", "return": -1.2, "transactions": 1580},
        {"date": "2023-01-03", "return": 3.1, "transactions": 1820},
        {"date": "2023-01-04", "return": 0.8, "transactions": 1450},
        {"date": "2023-01-05", "return": -2.3, "transactions": 1650},
        {"date": "2023-01-06", "return": 1.5, "transactions": 1550},
        {"date": "2023-01-07", "return": 2.8, "transactions": 1780},
        {"date": "2023-01-08", "return": -0.9, "transactions": 1620},
        {"date": "2023-01-09", "return": 1.2, "transactions": 1480},
        {"date": "2023-01-10", "return": 3.5, "transactions": 1920}
    ]
    
    dates = [datetime.strptime(d["date"], "%Y-%m-%d") for d in mock_data]
    returns = [d["return"] for d in mock_data]
    transactions = [d["transactions"] for d in mock_data]
    
    # Create the figure with secondary y-axis
    fig = go.Figure()
    
    # Add the line trace for returns
    fig.add_trace(go.Scatter(
        x=dates,
        y=returns,
        mode='lines',
        name='Returns',
        line=dict(width=2)
    ))
    
    # Add the bar trace for transactions
    fig.add_trace(go.Bar(
        x=dates,
        y=transactions,
        name='Transactions',
        opacity=0.5
    ))
    
    # Update layout with axis titles and secondary y-axis
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Returns (%)',
        yaxis2=dict(
            title="Transactions",
            overlaying="y",
            side="right"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Update the bar trace to use secondary y-axis
    fig.data[1].update(yaxis="y2")
    
    return json.loads(fig.to_json())


# Plotly chart with theme
# This endpoint extends the basic Plotly chart by adding theme support.
# The theme parameter is automatically provided by OpenBB Workspace based on the user's
# current display mode (dark/light). This enables dynamic chart styling that matches
# the workspace theme. The theme parameter is optional - if unused, OpenBB will still
# pass it but the endpoint will ignore it.
# Note: OpenBB widget UI dark mode is #151518 and light mode is #FFFFFF, using these
# background colors make the chart look consistent with the widgets in the OpenBB Workspace.
@register_widget({
    "name": "Plotly Chart with Theme",
    "description": "Plotly chart with theme",
    "type": "chart",
    "endpoint": "plotly_chart_with_theme",
    "gridData": {"w": 40, "h": 15}
})

@app.get("/plotly_chart_with_theme")
def get_plotly_chart_with_theme(theme: str = "dark"):
    # Generate mock time series data
    mock_data = [
        {"date": "2023-01-01", "return": 2.5, "transactions": 1250},
        {"date": "2023-01-02", "return": -1.2, "transactions": 1580},
        {"date": "2023-01-03", "return": 3.1, "transactions": 1820},
        {"date": "2023-01-04", "return": 0.8, "transactions": 1450},
        {"date": "2023-01-05", "return": -2.3, "transactions": 1650},
        {"date": "2023-01-06", "return": 1.5, "transactions": 1550},
        {"date": "2023-01-07", "return": 2.8, "transactions": 1780},
        {"date": "2023-01-08", "return": -0.9, "transactions": 1620},
        {"date": "2023-01-09", "return": 1.2, "transactions": 1480},
        {"date": "2023-01-10", "return": 3.5, "transactions": 1920}
    ]
    
    dates = [datetime.strptime(d["date"], "%Y-%m-%d") for d in mock_data]
    returns = [d["return"] for d in mock_data]
    transactions = [d["transactions"] for d in mock_data]
    
    # Create the figure with secondary y-axis
    fig = go.Figure()
    
    if theme == "dark":
        # Dark theme colors and styling
        line_color = "#FF8000"  # Orange
        bar_color = "#2D9BF0"   # Blue
        text_color = "#FFFFFF"  # White
        grid_color = "rgba(51, 51, 51, 0.3)"
        bg_color = "#151518"    # Dark background
    else:
        # Light theme colors and styling
        line_color = "#2E5090"  # Navy blue
        bar_color = "#00AA44"   # Forest green
        text_color = "#333333"  # Dark gray
        grid_color = "rgba(221, 221, 221, 0.3)"
        bg_color = "#FFFFFF"    # White background
    
    # Add the line trace for returns with theme-specific color
    fig.add_trace(go.Scatter(
        x=dates,
        y=returns,
        mode='lines',
        name='Returns',
        line=dict(width=2, color=line_color)
    ))
    
    # Add the bar trace for transactions with theme-specific color
    fig.add_trace(go.Bar(
        x=dates,
        y=transactions,
        name='Transactions',
        opacity=0.5,
        marker_color=bar_color
    ))
    
    # Update layout with theme-specific styling
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Returns (%)',
        yaxis2=dict(
            title="Transactions",
            overlaying="y",
            side="right",
            gridcolor=grid_color,
            tickfont=dict(color=text_color)
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color=text_color)
        ),
        paper_bgcolor=bg_color,
        plot_bgcolor=bg_color,
        font=dict(color=text_color),
        xaxis=dict(
            gridcolor=grid_color,
            tickfont=dict(color=text_color)
        ),
        yaxis=dict(
            gridcolor=grid_color,
            tickfont=dict(color=text_color)
        )
    )
    
    # Update the bar trace to use secondary y-axis
    fig.data[1].update(yaxis="y2")
    
    return json.loads(fig.to_json())



# Plotly chart with theme and toolbar
# This endpoint extends the basic Plotly chart by adding a toolbar to the chart.
# The toolbar is a set of buttons that allows the user to interact with the chart.
# Note: As you can see, all the settings and styling utilized by plotly can be too
# much boilerplate code, so it is recommended to create a plotly_config.py file
# and use the functions defined in that file to create the chart.
@register_widget({
    "name": "Plotly Chart with Theme and Toolbar",
    "description": "Plotly chart with Theme and toolbar",
    "type": "chart",
    "endpoint": "plotly_chart_with_theme_and_toolbar",
    "gridData": {"w": 40, "h": 15}
})

@app.get("/plotly_chart_with_theme_and_toolbar")
def get_plotly_chart_with_theme_and_toolbar(theme: str = "dark"):
    # Generate mock time series data
    mock_data = [
        {"date": "2023-01-01", "return": 2.5, "transactions": 1250},
        {"date": "2023-01-02", "return": -1.2, "transactions": 1580},
        {"date": "2023-01-03", "return": 3.1, "transactions": 1820},
        {"date": "2023-01-04", "return": 0.8, "transactions": 1450},
        {"date": "2023-01-05", "return": -2.3, "transactions": 1650},
        {"date": "2023-01-06", "return": 1.5, "transactions": 1550},
        {"date": "2023-01-07", "return": 2.8, "transactions": 1780},
        {"date": "2023-01-08", "return": -0.9, "transactions": 1620},
        {"date": "2023-01-09", "return": 1.2, "transactions": 1480},
        {"date": "2023-01-10", "return": 3.5, "transactions": 1920}
    ]
    
    dates = [datetime.strptime(d["date"], "%Y-%m-%d") for d in mock_data]
    returns = [d["return"] for d in mock_data]
    transactions = [d["transactions"] for d in mock_data]
    
    # Create the figure with secondary y-axis
    fig = go.Figure()
    
    if theme == "dark":
        # Dark theme colors and styling
        line_color = "#FF8000"  # Orange
        bar_color = "#2D9BF0"   # Blue
        text_color = "#FFFFFF"  # White
        grid_color = "rgba(51, 51, 51, 0.3)"
        bg_color = "#151518"    # Dark background
    else:
        # Light theme colors and styling
        line_color = "#2E5090"  # Navy blue
        bar_color = "#00AA44"   # Forest green
        text_color = "#333333"  # Dark gray
        grid_color = "rgba(221, 221, 221, 0.3)"
        bg_color = "#FFFFFF"    # White background
    
    # Add the line trace for returns with theme-specific color
    fig.add_trace(go.Scatter(
        x=dates,
        y=returns,
        mode='lines',
        name='Returns',
        line=dict(width=2, color=line_color)
    ))
    
    # Add the bar trace for transactions with theme-specific color
    fig.add_trace(go.Bar(
        x=dates,
        y=transactions,
        name='Transactions',
        opacity=0.5,
        marker_color=bar_color
    ))
    
    # Update layout with theme-specific styling
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Returns (%)',
        yaxis2=dict(
            title="Transactions",
            overlaying="y",
            side="right",
            gridcolor=grid_color,
            tickfont=dict(color=text_color)
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color=text_color)
        ),
        paper_bgcolor=bg_color,
        plot_bgcolor=bg_color,
        font=dict(color=text_color),
        xaxis=dict(
            gridcolor=grid_color,
            tickfont=dict(color=text_color)
        ),
        yaxis=dict(
            gridcolor=grid_color,
            tickfont=dict(color=text_color)
        )
    )
    
    # Update the bar trace to use secondary y-axis
    fig.data[1].update(yaxis="y2")
    
    # Configure the toolbar and other display settings
    toolbar_config = {
        'displayModeBar': True,
        'responsive': True,
        'scrollZoom': True,
        'modeBarButtonsToRemove': [
            'lasso2d',
            'select2d',
            'autoScale2d',
            'toggleSpikelines',
            'hoverClosestCartesian',
            'hoverCompareCartesian'
        ],
        'modeBarButtonsToAdd': [
            'drawline',
            'drawcircle',
            'drawrect',
            'eraseshape'
        ],
        'doubleClick': 'reset+autosize',
        'showTips': True,
        'watermark': False,
        'staticPlot': False,
        'locale': 'en',
        'showAxisDragHandles': True,
        'showAxisRangeEntryBoxes': True,
        'displaylogo': False,
        'modeBar': {
            'bgcolor': 'rgba(0, 0, 0, 0.1)' if theme == 'light' else 'rgba(255, 255, 255, 0.1)',
            'color': text_color,
            'activecolor': line_color,
            'orientation': 'v',
            'yanchor': 'top',
            'xanchor': 'right',
            'x': 1.05,  # Increased spacing from chart
            'y': 1,
            'opacity': 0,  # Start hidden
            'hovermode': True,  # Show on hover
            'hoverdelay': 0,  # No delay on hover
            'hoverduration': 0  # No delay on hover out
        }
    }
    
    # Convert figure to JSON and add config
    figure_json = json.loads(fig.to_json())
    figure_json['config'] = toolbar_config
    
    return figure_json


# Plotly chart with theme and config file
# This widget demonstrates how to create a chart using the Plotly library
# and use the config file to minimize the amount of code needed to create the chart.
@register_widget({
    "name": "Plotly Chart with Theme and Toolbar using Config File",
    "description": "Plotly chart with theme and toolbar using config file",
    "type": "chart",
    "endpoint": "plotly_chart_with_theme_and_toolbar_using_config_file",
    "gridData": {"w": 40, "h": 15}
})

@app.get("/plotly_chart_with_theme_and_toolbar_using_config_file")
def get_plotly_chart_with_theme_and_toolbar_using_config_file(theme: str = "dark"):
    # Generate mock time series data
    mock_data = [
        {"date": "2023-01-01", "return": 2.5, "transactions": 1250},
        {"date": "2023-01-02", "return": -1.2, "transactions": 1580},
        {"date": "2023-01-03", "return": 3.1, "transactions": 1820},
        {"date": "2023-01-04", "return": 0.8, "transactions": 1450},
        {"date": "2023-01-05", "return": -2.3, "transactions": 1650},
        {"date": "2023-01-06", "return": 1.5, "transactions": 1550},
        {"date": "2023-01-07", "return": 2.8, "transactions": 1780},
        {"date": "2023-01-08", "return": -0.9, "transactions": 1620},
        {"date": "2023-01-09", "return": 1.2, "transactions": 1480},
        {"date": "2023-01-10", "return": 3.5, "transactions": 1920}
    ]
    
    dates = [datetime.strptime(d["date"], "%Y-%m-%d") for d in mock_data]
    returns = [d["return"] for d in mock_data]
    transactions = [d["transactions"] for d in mock_data]
    
    # Get theme colors
    colors = get_theme_colors(theme)
    
    # Create the figure
    fig = go.Figure()
    
    # Add the line trace for returns
    fig.add_trace(go.Scatter(
        x=dates,
        y=returns,
        mode='lines',
        name='Returns',
        line=dict(width=2, color=colors["main_line"])
    ))
    
    # Add the bar trace for transactions
    fig.add_trace(go.Bar(
        x=dates,
        y=transactions,
        name='Transactions',
        opacity=0.5,
        marker_color=colors["neutral"]
    ))
    
    fig.update_layout(**base_layout(theme=theme))
    
    # Add secondary y-axis for transactions
    fig.update_layout(
        yaxis2=dict(
            title="Transactions",
            overlaying="y",
            side="right",
            gridcolor=colors["grid"],
            tickfont=dict(color=colors["text"])
        )
    )
    
    # Update the bar trace to use secondary y-axis
    fig.data[1].update(yaxis="y2")

    figure_json = json.loads(fig.to_json())
    figure_json['config'] = get_toolbar_config()
    
    return figure_json


# Plotly heatmap
# This widget demonstrates that with Plotly you can create any type of chart
# including heatmaps, scatter plots, line charts, 3d charts, etc.
# and also demonstrates how parameters can influence the a plotly chart.
# Note that the theme parameter always comes at the end of the function.
@register_widget({
    "name": "Plotly Heatmap",
    "description": "Plotly heatmap",
    "type": "chart",
    "endpoint": "plotly_heatmap",
    "gridData": {"w": 40, "h": 15},
    "params": [
        {
            "paramName": "color_scale",
            "description": "Select the color scale for the heatmap",
            "value": "RdBu_r",
            "label": "Color Scale",
            "type": "text",
            "show": True,
            "options": [
                {"label": "Red-Blue (RdBu_r)", "value": "RdBu_r"},
                {"label": "Viridis", "value": "Viridis"},
                {"label": "Plasma", "value": "Plasma"},
                {"label": "Inferno", "value": "Inferno"},
                {"label": "Magma", "value": "Magma"},
                {"label": "Greens", "value": "Greens"},
                {"label": "Blues", "value": "Blues"},
                {"label": "Reds", "value": "Reds"}
            ]
        }
    ]
})
@app.get("/plotly_heatmap")
def get_plotly_heatmap(color_scale: str = "RdBu_r", theme: str = "dark"):
    # Create mock stock symbols
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']

    # Create mock correlation matrix directly
    corr_matrix = [
        [1.00, 0.65, 0.45, 0.30, 0.20],  # AAPL correlations
        [0.65, 1.00, 0.55, 0.40, 0.25],  # MSFT correlations
        [0.45, 0.55, 1.00, 0.35, 0.15],  # GOOGL correlations
        [0.30, 0.40, 0.35, 1.00, 0.10],  # AMZN correlations
        [0.20, 0.25, 0.15, 0.10, 1.00]   # TSLA correlations
    ]

    # Get theme colors
    colors = get_theme_colors(theme)

    # Create the figure
    fig = go.Figure()
    # Apply base layout configuration
    layout_config = base_layout(theme=theme)

    # This allows users to modify the layout configuration further
    # in case they want to steer from the default settings.
    layout_config['title'] = {
        'text': "Correlation Matrix",
        'x': 0.5,
        'y': 0.95,
        'xanchor': 'center',
        'yanchor': 'top',
        'font': {'size': 20}
    }
    layout_config['margin'] = {'t': 50, 'b': 50, 'l': 50, 'r': 50}
    
    # Update figure with complete layout
    fig.update_layout(layout_config)

    # Add the heatmap trace
    fig.add_trace(go.Heatmap(
        z=corr_matrix,
        x=symbols,
        y=symbols,
        colorscale=color_scale,
        zmid=colors["heatmap"]["zmid"],
        text=[[f'{val:.2f}' for val in row] for row in corr_matrix],
        texttemplate='%{text}',
        textfont={"color": colors["heatmap"]["text_color"]},
        hoverongaps=False,
        hovertemplate='%{x} - %{y}<br>Correlation: %{z:.2f}<extra></extra>'
    ))
    
    # Convert figure to JSON and apply config
    figure_json = json.loads(fig.to_json())
    figure_json['config'] = {
        **get_toolbar_config(),
        'scrollZoom': False  # Disable scroll zoom
    }

    return figure_json


# Global variable to store form submissions
# This acts as a simple in-memory database for our form entries
ALL_FORMS = []

# Form submission endpoint
# This endpoint handles both adding new records and updating existing ones
# It receives form data as a dictionary and performs validation before processing
@app.post("/form_submit")
async def form_submit(params: dict) -> JSONResponse:
    global ALL_FORMS
    
    # Validate required fields
    # The form requires first name and last name to be provided
    if not params.get("client_first_name") or not params.get("client_last_name"):
        # Even with a 400 status code, the error message is passed to the frontend
        # and can be displayed to the user in the OpenBB widget
        return JSONResponse(
            status_code=400,
            content={"error": "Client first name and last name are required"}
        )
    
    # Validate investment types and risk profile
    # These fields are also required for a complete form submission
    if not params.get("investment_types") or not params.get("risk_profile"):
        return JSONResponse(
            status_code=400,
            content={"error": "Investment types and risk profile are required"}
        )

    # Handle form submission based on the action (add or update)
    # The form can either add a new record or update an existing one
    # We pop these values from params to avoid storing them in the record
    add_record = params.pop("add_record", None)
    if add_record:
        # For new records, append to the list
        # Convert lists to comma-separated strings for storage
        ALL_FORMS.append(
            {k: ",".join(v) if isinstance(v, list) else v for k, v in params.items()}
        )
    
    update_record = params.pop("update_record", None)
    if update_record:
        # For updates, find the matching record by first and last name
        # and update its fields with the new values
        for record in ALL_FORMS:
            if record["client_first_name"] == params.get("client_first_name") and record[
                "client_last_name"
            ] == params.get("client_last_name"):
                record.update(params)
    
    # Return success response
    # The OpenBB Workspace only checks for a 200 status code from this endpoint
    # The actual content returned doesn't matter for the widget refresh mechanism
    # After a successful submission, Workspace will automatically refresh the widget
    # by calling the GET endpoint defined in the widget configuration
    return JSONResponse(content={"success": True})


# Form Widget Registration
# This decorator registers the form widget with the OpenBB Workspace
# The widget configuration defines how the form will be displayed and behave
@register_widget({
    "name": "Entry Form",
    "description": "Example of a more complex entry form",
    "category": "forms",
    "searchCategory": "form",
    "endpoint": "all_forms",  # The GET endpoint that provides the form data
    "type": "table",  # The form data is displayed in a table format
    "gridData": {
        "w": 20,  # Width of the widget in the grid
        "h": 9    # Height of the widget in the grid
    },
    "params": [
        {
            "paramName": "form",
            "description": "Form example",
            "type": "form",  # This indicates this is a form widget
            "endpoint": "form_submit",  # The POST endpoint that handles form submissions
            "inputParams": [
                # Text input for client's first name
                {
                    "paramName": "client_first_name",
                    "type": "text",
                    "value": "",
                    "label": "First Name",
                    "description": "Client's first name"
                },
                # Text input for client's last name
                {
                    "paramName": "client_last_name",
                    "type": "text",
                    "value": "",
                    "label": "Last Name",
                    "description": "Client's last name"
                },
                # Multi-select dropdown for investment types
                {
                    "paramName": "investment_types",
                    "type": "text",
                    "value": None,
                    "label": "Investment Types",
                    "description": "Selected investment vehicles",
                    "multiSelect": True,  # Allows selecting multiple options
                    "options": [
                        {"label": "Stocks", "value": "stocks"},
                        {"label": "Bonds", "value": "bonds"},
                        {"label": "Mutual Funds", "value": "mutual_funds"},
                        {"label": "ETFs", "value": "etfs"},
                    ]
                },
                # Text input for risk profile
                {
                    "paramName": "risk_profile",
                    "type": "text",
                    "value": "",
                    "label": "Risk Profile",
                    "description": "Client risk tolerance assessment"
                },
                # Button to add a new record
                {
                    "paramName": "add_record",
                    "type": "button",
                    "value": True,
                    "label": "Add Client",
                    "description": "Add client record"
                },
                # Button to update an existing record
                {
                    "paramName": "update_record",
                    "type": "button",
                    "value": True,
                    "label": "Update Client",
                    "description": "Update client record"
                }
            ]
        }
    ]
})
@app.get("/all_forms")
async def all_forms() -> list:
    """Returns all form submissions"""
    # This GET endpoint is called by the OpenBB widget after form submission
    # The widget refresh mechanism works by:
    # 1. User submits form (POST to /form_submit)
    # 2. If POST returns 200, widget automatically refreshes
    # 3. Widget refresh calls this GET endpoint to fetch updated data
    # 4. This function must return ALL data needed to display the updated widget
    
    # Return either the list of form submissions or a default empty record
    # The default record ensures the table has the correct structure even when empty
    return (
        ALL_FORMS
        if ALL_FORMS
        else [
            {
                "client_first_name": None,
                "client_last_name": None,
                "investment_types": None,
                "risk_profile": None
            }
        ]
    )

# Mock data for our symbols
MOCK_SYMBOLS = {
    "AAPL": {
        "name": "Apple Inc.",
        "description": "Apple Inc. Stock",
        "type": "stock",
        "exchange": "NASDAQ",
        "pricescale": 100,
        "minmov": 1,
        "volume_precision": 0
    },
    "MSFT": {
        "name": "Microsoft Corporation",
        "description": "Microsoft Corporation Stock",
        "type": "stock",
        "exchange": "NASDAQ",
        "pricescale": 100,
        "minmov": 1,
        "volume_precision": 0
    },
    "GOOGL": {
        "name": "Alphabet Inc.",
        "description": "Alphabet Inc. Stock",
        "type": "stock",
        "exchange": "NASDAQ",
        "pricescale": 100,
        "minmov": 1,
        "volume_precision": 0
    }
}

def generate_mock_price_data(symbol: str, from_time: int, to_time: int, resolution: str) -> dict:
    """Generate mock OHLCV (Open, High, Low, Close, Volume) data for a symbol

    This function creates realistic-looking price data for the TradingView chart.
    It generates timestamps and corresponding price data based on the requested time range
    and resolution (timeframe).

    Args:
        symbol: The stock symbol to generate data for
        from_time: Start timestamp in seconds
        to_time: End timestamp in seconds
        resolution: Timeframe (1, 5, 15, 30, 60 minutes, D for daily, W for weekly, M for monthly)

    Returns:
        Dictionary containing OHLCV data in TradingView's expected format
    """
    # Convert resolution to minutes for timestamp generation
    # TradingView uses specific resolution codes that we map to minutes
    resolution_minutes = {
        "1": 1, "5": 5, "15": 15, "30": 30, "60": 60,
        "D": 1440, "W": 10080, "M": 43200
    }.get(resolution, 60)

    # Generate timestamps for each candle based on the resolution
    current_time = from_time
    timestamps = []
    while current_time <= to_time:
        timestamps.append(current_time)
        current_time += resolution_minutes * 60

    # Generate base price data with random movements
    # Different symbols have different base prices to make them visually distinct
    base_price = 100.0 if symbol == "AAPL" else 200.0 if symbol == "MSFT" else 150.0
    prices = []
    current_price = base_price

    for _ in timestamps:
        # Add random price movement to create realistic-looking price action
        change = random.uniform(-2, 2)
        current_price += change
        current_price = max(current_price, 1.0)  # Ensure price doesn't go below 1
        prices.append(current_price)

    # Generate OHLCV data with proper bullish/bearish candles
    # This creates realistic-looking candlesticks with proper open, high, low, close values
    opens = []
    highs = []
    lows = []
    closes = []
    volumes = []

    for price in prices:
        # Randomly decide if this is a bullish or bearish candle
        is_bullish = random.random() > 0.5

        if is_bullish:
            # Bullish candle: open < close (green candle)
            open_price = price * 0.99
            close_price = price * 1.01
        else:
            # Bearish candle: open > close (red candle)
            open_price = price * 1.01
            close_price = price * 0.99

        # Add some randomness to high and low prices
        high_price = max(open_price, close_price) * 1.02
        low_price = min(open_price, close_price) * 0.98

        opens.append(open_price)
        highs.append(high_price)
        lows.append(low_price)
        closes.append(close_price)

        # Generate volume that correlates with price movement
        # Higher volume on larger price movements
        price_change = abs(close_price - open_price)
        base_volume = 1000000  # Base volume of 1M shares
        volume_multiplier = 1 + (price_change / open_price) * 10  # Scale volume with price change
        volume = int(base_volume * volume_multiplier * random.uniform(0.8, 1.2))  # Add some randomness
        volumes.append(volume)

    # Return data in TradingView's expected format
    return {
        "s": "ok",  # Status: ok
        "t": timestamps,  # Time array
        "o": opens,  # Open prices array
        "h": highs,  # High prices array
        "l": lows,  # Low prices array
        "c": closes,  # Close prices array
        "v": volumes  # Volume array
    }

@app.get("/udf/config")
async def get_config():
    """UDF configuration endpoint

    This endpoint provides TradingView with the configuration for our data feed.
    It tells TradingView what features we support and what data we can provide.

    Returns:
        Dictionary containing configuration options for the TradingView chart
    """
    return {
        "supported_resolutions": ["1", "5", "15", "30", "60", "D", "W", "M"],  # Timeframes we support
        "supports_group_request": False,  # We don't support requesting multiple symbols at once
        "supports_marks": False,  # We don't support custom marks on the chart
        "supports_search": True,  # We support symbol search
        "supports_timescale_marks": False,  # We don't support marks on the timescale
        "supports_time": True,  # We support server time requests
        "exchanges": [  # Available exchanges
            {"value": "", "name": "All Exchanges", "desc": ""},
            {"value": "NASDAQ", "name": "NASDAQ", "desc": "NASDAQ Stock Exchange"}
        ],
        "symbols_types": [  # Available symbol types
            {"name": "All types", "value": ""},
            {"name": "Stocks", "value": "stock"}
        ]
    }

@app.get("/udf/search")
async def search_symbols(
    query: str = Query("", description="Search query"),
    limit: int = Query(30, description="Limit of results")
):
    """UDF symbol search endpoint

    This endpoint allows TradingView to search for symbols in our data feed.
    It's used when the user types in the symbol search box.

    Args:
        query: Search term entered by user
        limit: Maximum number of results to return

    Returns:
        List of matching symbols with their details
    """
    results = []
    for symbol, info in MOCK_SYMBOLS.items():
        if query.lower() in symbol.lower() or query.lower() in info["name"].lower():
            results.append({
                "symbol": symbol,
                "full_name": f"NASDAQ:{symbol}",
                "description": info["description"],
                "exchange": "NASDAQ",
                "ticker": symbol,
                "type": "stock"
            })
            if len(results) >= limit:
                break
    return results

@app.get("/udf/symbols")
async def get_symbol_info(symbol: str = Query(..., description="Symbol to get info for")):
    """UDF symbol info endpoint

    This endpoint provides TradingView with detailed information about a specific symbol.
    It's called when a symbol is selected in the chart.

    Args:
        symbol: The symbol to get info for

    Returns:
        Dictionary containing symbol information in TradingView's expected format
    """
    # Clean the symbol (remove exchange prefix if present)
    clean_symbol = symbol.split(":")[-1]

    # Check if we have info for this symbol
    if clean_symbol not in MOCK_SYMBOLS:
        raise HTTPException(status_code=404, detail="Symbol not found")

    # Get the symbol info
    info = MOCK_SYMBOLS[clean_symbol]

    # Return the symbol info in TradingView's expected format
    return {
        "name": clean_symbol,
        "description": info["name"],
        "type": info["type"],
        "exchange": info["exchange"],
        "pricescale": info["pricescale"],
        "minmov": info["minmov"],
        "volume_precision": info["volume_precision"],
        "has_volume": True,  # Explicitly indicate that we provide volume data
        "has_intraday": True,  # We support intraday data
        "has_daily": True,  # We support daily data
        "has_weekly_and_monthly": True,  # We support weekly and monthly data
        "supported_resolutions": ["1", "5", "15", "30", "60", "D", "W", "M"],
        "session-regular": "0930-1600",  # Regular trading hours
        "timezone": "America/New_York"  # Timezone for the exchange
    }

@app.get("/udf/history")
async def get_history(
    symbol: str = Query(..., description="Symbol"),
    resolution: str = Query(..., description="Resolution"),
    from_time: int = Query(..., alias="from", description="From timestamp"),
    to_time: int = Query(..., alias="to", description="To timestamp")
):
    """UDF historical data endpoint

    This endpoint provides TradingView with the actual price data for the chart.
    It's called when the chart needs to load or update its data.

    Args:
        symbol: The symbol to get data for
        resolution: The timeframe (1, 5, 15, 30, 60, D, W, M)
        from_time: Start timestamp in seconds
        to_time: End timestamp in seconds

    Returns:
        Dictionary containing OHLCV data for the requested period
    """
    clean_symbol = symbol.split(":")[-1] if ":" in symbol else symbol

    if clean_symbol not in MOCK_SYMBOLS:
        return {"s": "error", "errmsg": "Symbol not found"}

    return generate_mock_price_data(clean_symbol, from_time, to_time, resolution)

@app.get("/udf/time")
async def get_server_time():
    """UDF server time endpoint

    This endpoint provides TradingView with the current server time.
    It's used to synchronize the chart with the server.

    Returns:
        Current server timestamp in seconds
    """
    return int(datetime.now().timestamp())

# Register the TradingView UDF widget
# This widget provides advanced charting capabilities using TradingView's charting library
# The widget is configured to use our UDF endpoints for data
@register_widget({
    "name": "TradingView Chart",
    "description": "Advanced charting with TradingView using mock data",
    "category": "Finance",
    "type": "advanced_charting",
    "endpoint": "/udf",  # Base endpoint for all UDF requests
    "gridData": {
        "w": 20,
        "h": 20
    },
    "data": {
        "defaultSymbol": "AAPL",  # Default symbol to display
        "updateFrequency": 60000,  # Update every minute
        "chartConfig": {  # Chart appearance configuration
            "upColor": "#26a69a",  # Color for bullish candles
            "downColor": "#ef5350",  # Color for bearish candles
            "borderUpColor": "#26a69a",  # Border color for bullish candles
            "borderDownColor": "#ef5350",  # Border color for bearish candles
            "wickUpColor": "#26a69a",  # Wick color for bullish candles
            "wickDownColor": "#ef5350",  # Wick color for bearish candles
            "volumeUpColor": "#26a69a",  # Color for volume bars on up days
            "volumeDownColor": "#ef5350",  # Color for volume bars on down days
            "showVolume": True  # Enable volume display
        }
    }
})
def tradingview_chart():
    """Dummy function for TradingView chart widget registration"""
    pass


class DataFormat(BaseModel):
    """Data format for the widget"""
    data_type: str
    parse_as: Literal["text", "table", "chart"]


class SourceInfo(BaseModel):
    """Source information for the widget"""
    type: Literal["widget"]
    uuid: UUID | None = Field(default=None)
    origin: str | None = Field(default=None)
    widget_id: str | None = Field(default=None)
    name: str
    description: str | None = Field(default=None)
    metadata: dict[str, Any] | None = Field(
        default=None,
        description="Additional metadata (eg. the selected ticker, endpoint used, etc.).",  # noqa: E501
    )


class ExtraCitation(BaseModel):
    """Extra citation for the widget"""
    source_info: SourceInfo | None = Field(default=None)
    details: List[dict] | None = Field(default=None)


class OmniWidgetResponse(BaseModel):
    """Omni widget response for the widget"""
    content: Any
    data_format: DataFormat
    extra_citations: list[ExtraCitation] | None = Field(default_factory=list)
    citable: bool = Field(
        default=True,
        description="Whether the source is citable.",
    )


@register_widget({
    "name": "Basic Omni Widget",
    "description": "A versatile omni widget that can display multiple types of content",
    "category": "General",
    "type": "omni",
    "endpoint": "omni-widget",
    "params": [
        {
            "paramName": "prompt",
            "type": "text",
            "description": "The prompt to send to the LLM to make queries or ask questions.",
            "label": "Prompt",
            "show": False
        },
        {
            "paramName": "type",
            "type": "text",
            "description": "Type of content to return",
            "label": "Content Type",
            "show": True,
            "options": [
                {"value": "markdown", "label": "Markdown"},
                {"value": "chart", "label": "Chart"},
                {"value": "table", "label": "Table"}
            ]
        }
    ],
    "gridData": {"w": 30, "h": 12}
})
@app.post("/omni-widget")
async def get_omni_widget_post(
    data: str | dict = Body(...)
):
    """Basic Omni Widget example showing different return types without citations"""
    if isinstance(data, str):
        data = json.loads(data)

    if data.get("type") == "table":
        content = [
                {"col1": "value1", "col2": "value2", "col3": "value3", "col4": "value4"},
                {"col1": "value1", "col2": "value2", "col3": "value3", "col4": "value4"},
                {"col1": "value1", "col2": "value2", "col3": "value3", "col4": "value4"},
                {"col1": "value1", "col2": "value2", "col3": "value3", "col4": "value4"},
                {"col1": "value1", "col2": "value2", "col3": "value3", "col4": "value4"},
                {"col1": "value1", "col2": "value2", "col3": "value3", "col4": "value4"},
                {"col1": "value1", "col2": "value2", "col3": "value3", "col4": "value4"},
                {"col1": "value1", "col2": "value2", "col3": "value3", "col4": "value4"},
                {"col1": "value1", "col2": "value2", "col3": "value3", "col4": "value4"},
            ]

        return OmniWidgetResponse(
                content=content,
                data_format=DataFormat(data_type="object", parse_as="table"),
                citable=False
            )

    if data.get("type") == "chart":

        # Create figure with base layout
        fig = go.Figure()
        
        # Add traces with themed colors
        fig.add_trace(go.Bar(
            x=["A", "B", "C"],
            y=[4, 1, 2],
            name="Series 1",
            marker_color="#26a69a"
        ))
        fig.add_trace(go.Bar(
            x=["A", "B", "C"],
            y=[2, 4, 5],
            name="Series 2",
            marker_color="#ef5350"
        ))
        fig.add_trace(go.Bar(
            x=["A", "B", "C"],
            y=[2, 3, 6],
            name="Series 3",
            marker_color="#f0a500"
        ))
        
        # Apply base layout with theme
        base_layout_config = base_layout(theme="dark")
        # Override text colors with #216df1
        base_layout_config.update({
            'font': {'color': '#216df1'},
            'title': {'font': {'color': '#216df1'}},
            'xaxis': {'tickfont': {'color': '#216df1'}, 'title': {'font': {'color': '#216df1'}}},
            'yaxis': {'tickfont': {'color': '#216df1'}, 'title': {'font': {'color': '#216df1'}}}
        })
        fig.update_layout(**base_layout_config)
        
        # Add specific layout updates for this chart
        fig.update_layout(
            title="Plotly Chart example",
            bargap=0.15,
            bargroupgap=0.1,
            margin=dict(t=50),  # Add 50px top margin
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.2,  # Position below the chart
                xanchor="center",
                x=0.5,  # Center horizontally
                font=dict(color='#216df1'),  # Update legend text color
                bgcolor='rgba(0,0,0,0)'  # Transparent background
            )
        )
        
        # Convert to JSON and add toolbar config
        content = json.loads(fig.to_json())
        content["config"] = get_toolbar_config()

        return OmniWidgetResponse(
            content=content,
            data_format=DataFormat(data_type="object", parse_as="chart"),
            citable=False
        )

    # Default to markdown without citations
    content = f"""### Basic Omni Widget Response
**Input Parameters:**
- **Prompt:** `{data.get('prompt', 'No prompt provided')}`
- **Type:** `{data.get('type', 'markdown')}`

#### Raw Data:
```json
{json.dumps(data, indent=2)}
```

This is a basic omni widget response without citation tracking.
"""

    return OmniWidgetResponse(
        content=content,
        data_format=DataFormat(data_type="object", parse_as="text"),
        citable=False
    )


# This is an example of an omni widget that includes citation information for data tracking
# This is useful when you are interacting with an AI Agent and want to pass citations in the chat.
@register_widget({
    "name": "Omni Widget with Citations",
    "description": "An omni widget that includes citation information for data tracking",
    "category": "General",
    "type": "omni",
    "endpoint": "omni-widget-with-citations",
    "params": [
        {
            "paramName": "prompt",
            "type": "text",
            "description": "The prompt to send to the LLM to make queries or ask questions.",
            "label": "Prompt",
            "show": False
        },
        {
            "paramName": "type",
            "type": "text",
            "description": "Type of content to return",
            "label": "Content Type",
            "show": True,
            "options": [
                {"value": "markdown", "label": "Markdown"},
                {"value": "chart", "label": "Chart"},
                {"value": "table", "label": "Table"}
            ]
        },
        {
            "paramName": "include_metadata",
            "type": "boolean",
            "description": "Include metadata in response",
            "label": "Include Metadata",
            "show": True,
            "value": True
        }
    ],
    "gridData": {"w": 30, "h": 15}
})
@app.post("/omni-widget-with-citations")
async def get_omni_widget_with_citations(
    data: str | dict = Body(...)
):
    """Omni Widget example with citation support"""
    if isinstance(data, str):
        data = json.loads(data)

    # Create citation information
    source_info = SourceInfo(
        type="widget",
        widget_id=data.get("widget_id", "omni_widget_citations"),
        origin=data.get("widget_origin", "omni_widget"),
        name="Omni Widget with Citations",
        description="Example widget demonstrating citation functionality",
        metadata={
            "filename": "omni_widget_response.md",
            "extension": "md",
            "input_args": data,
            "timestamp": data.get("timestamp", "")
        }
    )

    extra_citation = ExtraCitation(
        source_info=source_info,
        details=[
            {
                "Name": "Omni Widget with Citations",
                "Query": data.get("prompt"),
                "Type": data.get("type"),
                "Timestamp": data.get("timestamp", ""),
                "Data": json.dumps(data, indent=2)
            }
        ]
    )

    if data.get("type") == "table":
        content = [
            {"source": "Citation Example", "value": "123", "description": "Sample data with citation"},
            {"source": "Citation Example", "value": "456", "description": "More sample data"},
            {"source": "Citation Example", "value": "789", "description": "Additional sample data"},
        ]

        return OmniWidgetResponse(
            content=content,
            data_format=DataFormat(data_type="object", parse_as="table"),
            extra_citations=[extra_citation],
            citable=True
        )

    if data.get("type") == "chart":
        # Create figure with base layout
        fig = go.Figure()
        
        # Add traces with themed colors
        fig.add_trace(go.Bar(
            x=["A", "B", "C"],
            y=[4, 1, 2],
            name="Cited Data Series 1",
            marker_color="#26a69a"
        ))
        fig.add_trace(go.Bar(
            x=["A", "B", "C"],
            y=[2, 4, 5],
            name="Cited Data Series 2",
            marker_color="#ef5350"
        ))
        fig.add_trace(go.Bar(
            x=["A", "B", "C"],
            y=[2, 3, 6],
            name="Cited Data Series 3",
            marker_color="#f0a500"
        ))
        
        # Apply base layout with theme
        base_layout_config = base_layout(theme="dark")
        # Override text colors with #216df1
        base_layout_config.update({
            'font': {'color': '#216df1'},
            'title': {'font': {'color': '#216df1'}},
            'xaxis': {'tickfont': {'color': '#216df1'}, 'title': {'font': {'color': '#216df1'}}},
            'yaxis': {'tickfont': {'color': '#216df1'}, 'title': {'font': {'color': '#216df1'}}}
        })
        fig.update_layout(**base_layout_config)
        
        # Add specific layout updates for this chart
        fig.update_layout(
            title="Chart with Citation Support",
            bargap=0.15,
            bargroupgap=0.1,
            margin=dict(t=50),  # Add 50px top margin
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.2,  # Position below the chart
                xanchor="center",
                x=0.5,  # Center horizontally
                font=dict(color='#216df1'),  # Update legend text color
                bgcolor='rgba(0,0,0,0)'  # Transparent background
            )
        )
        
        # Convert to JSON and add toolbar config
        content = json.loads(fig.to_json())
        content["config"] = get_toolbar_config()

        return OmniWidgetResponse(
            content=content,
            data_format=DataFormat(data_type="object", parse_as="chart"),
            extra_citations=[extra_citation],
            citable=True
        )

    # Default to markdown with citations
    content = f"""### Omni Widget with Citation Support
**Input Parameters:**
- **Prompt:** `{data.get('prompt', 'No prompt provided')}`
- **Type:** `{data.get('type', 'markdown')}`

#### Data with Citation Tracking: 
This response includes citation information that will be automatically tracked and made available to agents and users.

**Citation Details:**
- **Name:** {source_info.name}
- **Origin:** {source_info.origin}
- **Timestamp:** {data.get('timestamp', 'Not provided')}
"""

    if data.get("include_metadata"):
        content += f"""
#### Additional Metadata:
- **Include Metadata:** {data.get('include_metadata')}
- **Full Input Data:**

```json
{json.dumps(data, indent=2)}
```
"""

    return OmniWidgetResponse(
        content=content,
        data_format=DataFormat(data_type="object", parse_as="text"),
        extra_citations=[extra_citation],
        citable=True
    )

@register_widget({
    "name": "Markdown Widget with Organized Parameters",
    "description": "A markdown widget demonstrating various parameter types organized in a clean way",
    "type": "markdown",
    "endpoint": "markdown_widget_with_organized_params",
    "gridData": {"w": 20, "h": 12},
    "params": [
        [
            {
                "paramName": "enable_feature",
                "description": "Enable or disable the main feature",
                "label": "Enable Feature",
                "type": "boolean",
                "value": True
            }
        ],
        [
            {
                "paramName": "selected_date",
                "description": "Select a date for analysis",
                "value": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
                "label": "Analysis Date",
                "type": "date"
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
                    {"label": "Risk Analysis", "value": "risk"}
                ]
            },
            {
                "paramName": "lookback_period",
                "description": "Number of days to look back",
                "value": 30,
                "label": "Lookback Period (days)",
                "type": "number",
                "min": 1,
                "max": 365
            }
        ],
        [
            {
                "paramName": "analysis_notes",
                "description": "Additional notes for the analysis",
                "value": "",
                "label": "Analysis Notes",
                "type": "text"
            }
        ]
    ]
})
@app.get("/markdown_widget_with_organized_params")
def markdown_widget_with_organized_params(
    enable_feature: bool = True,
    selected_date: str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
    analysis_type: str = "technical",
    lookback_period: int = 30,
    analysis_notes: str = ""
):
    """Returns a markdown widget with organized parameters"""
    # Format the date for display
    formatted_date = datetime.strptime(selected_date, "%Y-%m-%d").strftime("%B %d, %Y")
    
    # Get the label for the selected analysis type
    analysis_type_label = next(
        (opt["label"] for opt in [
            {"label": "Technical Analysis", "value": "technical"},
            {"label": "Fundamental Analysis", "value": "fundamental"},
            {"label": "Sentiment Analysis", "value": "sentiment"},
            {"label": "Risk Analysis", "value": "risk"}
        ] if opt["value"] == analysis_type),
        analysis_type
    )
    
    return f"""# Analysis Configuration
*This widget demonstrates various parameter types including boolean toggles, date pickers, dropdowns, number inputs, and text fields.*

## Feature Status
- **Feature Enabled:** {'✅ Yes' if enable_feature else '❌ No'}

## Analysis Parameters
- **Selected Date:** {formatted_date}
- **Analysis Type:** {analysis_type_label}
- **Lookback Period:** {lookback_period} days

## Additional Notes
{analysis_notes if analysis_notes else "*No additional notes provided*"}
"""