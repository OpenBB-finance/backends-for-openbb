# Import required libraries
import json
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse


# Initialize FastAPI application with metadata
app = FastAPI(
    title="Hello World",
    description="Hello World app for OpenBB Workspace",
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


# Widgets configuration file for the OpenBB Workspace
# it contains the information and configuration about all the
# widgets that will be displayed in the OpenBB Workspace
@app.get("/widgets.json")
def get_widgets():
    """Widgets configuration file for the OpenBB Workspace
    
    Returns:
        JSONResponse: The contents of widgets.json file
    """
    # Read and return the widgets configuration file
    return JSONResponse(
        content=json.load((Path(__file__).parent.resolve() / "widgets.json").open())
    )


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


# Hello World endpoint - for it to be recognized by the OpenBB Workspace
# it needs to be added to the widgets.json file endpoint
@app.get("/hello_world")
def hello_world(name: str = ""):
    """Returns a personalized greeting message.

    Args:
        name (str, optional): Name to include in the greeting. Defaults to empty string.

    Returns:
        str: A greeting message with the provided name in markdown format.
    """
    # Return a markdown-formatted greeting with the provided name
    return f"# Hello World {name}"
