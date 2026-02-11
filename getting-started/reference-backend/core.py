"""
Core Components for OpenBB Workspace Reference Backend

This module contains shared components used across all widget modules:
- FastAPI application instance
- Widget registry (WIDGETS dictionary and register_widget decorator)
- Pydantic models for API responses
- Common utilities

Import from this module in widget files to avoid circular imports.
"""

import json
import asyncio
from pathlib import Path
from functools import wraps
from pydantic import BaseModel, Field
from typing import Any, Literal, List
from uuid import UUID
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class FileOption(BaseModel):
    """File option for multi-file viewer selection"""
    label: str
    value: str


class FileRequest(BaseModel):
    """Request model for multi-file viewer POST endpoints"""
    filenames: List[str]


class FileDataFormat(BaseModel):
    """Data format specification for files"""
    data_type: str
    filename: str


class DataContent(BaseModel):
    """Response model for file content in base64 format"""
    content: str
    data_format: FileDataFormat


class DataUrl(BaseModel):
    """Response model for file URL"""
    url: str
    data_format: FileDataFormat


class DataError(BaseModel):
    """Error response model for file requests"""
    error_type: str
    content: str


# Omni widget response models
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
        description="Additional metadata (eg. the selected ticker, endpoint used, etc.).",
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


# ============================================================================
# FASTAPI APPLICATION SETUP
# ============================================================================

app = FastAPI(
    title="Simple Backend",
    description="Simple backend app for OpenBB Workspace",
    version="0.0.1",
)

# Define allowed origins for CORS (Cross-Origin Resource Sharing)
origins = ["https://pro.openbb.co", "https://pro.openbb.dev", "http://localhost:1420"]

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ROOT_PATH = Path(__file__).parent.resolve()


# ============================================================================
# WIDGET REGISTRY
# ============================================================================

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
            return await func(*args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        endpoint = widget_config.get("endpoint")
        if endpoint:
            if "widgetId" not in widget_config:
                widget_config["widgetId"] = endpoint
            widget_id = widget_config["widgetId"]
            WIDGETS[widget_id] = widget_config

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator
