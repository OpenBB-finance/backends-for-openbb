# Import required libraries
import json
import requests
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from registry import register_widget, WIDGETS


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
