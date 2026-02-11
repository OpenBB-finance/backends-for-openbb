"""
Widget Settings for OpenBB Workspace

This module demonstrates various widget configuration options:
- Auto-refresh with configurable intervals (refetch_interval)
- Data freshness control (stale_time)
- Manual run button for on-demand updates
- Structured API output formats

These settings control widget behavior and data fetching patterns.
"""

from datetime import datetime
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from core import register_widget, WIDGETS

router = APIRouter()


# ============================================================================
# STALE TIME SETTINGS
# ============================================================================

@register_widget({
    "name": "Markdown Widget with Stale Time",
    "description": "A markdown widget with stale time. The widget will show stale data before fetching new data.",
    "type": "markdown",
    "endpoint": "markdown_widget_with_stale_time",
    "stale_time": 10000,  # 10000 milliseconds = 10 seconds
    "gridData": {"w": 20, "h": 5},
})
@router.get("/markdown_widget_with_stale_time")
def markdown_widget_with_stale_time():
    """Returns a markdown widget with stale time"""
    return f"# Markdown Widget with Stale Time\n\n{datetime.now()}"


# ============================================================================
# AUTO-REFRESH SETTINGS
# ============================================================================

@register_widget({
    "name": "Markdown Widget with Short Refetch Interval",
    "description": "A markdown widget that auto-refreshes at a short interval",
    "type": "markdown",
    "endpoint": "markdown_widget_with_short_refetch_interval",
    "refetch_interval": 5000,  # 5000 milliseconds = 5 seconds
    "gridData": {"w": 20, "h": 5},
})
@router.get("/markdown_widget_with_short_refetch_interval")
def markdown_widget_with_short_refetch_interval():
    """Returns a markdown widget that auto-refreshes every 5 seconds"""
    return f"# Markdown Widget with Short Refetch Interval\n\n{datetime.now()}"


@register_widget({
    "name": "Markdown Widget with Refetch Interval and Shorter Stale Time",
    "description": "A markdown widget with both refetch interval and shorter stale time",
    "type": "markdown",
    "endpoint": "markdown_widget_with_refetch_interval_and_shorter_stale_time",
    "refetch_interval": 10000,  # 10 seconds
    "stale_time": 5000,  # 5 seconds - shorter than refetch interval
    "gridData": {"w": 20, "h": 5},
})
@router.get("/markdown_widget_with_refetch_interval_and_shorter_stale_time")
def markdown_widget_with_refetch_interval_and_shorter_stale_time():
    """Returns a markdown widget with refetch interval and shorter stale time"""
    return f"# Markdown Widget with Refetch Interval and Shorter Stale Time\n\n{datetime.now()}"


# ============================================================================
# RUN BUTTON SETTINGS
# ============================================================================

@register_widget({
    "name": "Markdown Widget with Run Button",
    "description": "A markdown widget with a run button that requires manual execution",
    "type": "markdown",
    "endpoint": "markdown_widget_with_run_button",
    "runButton": True,
    "gridData": {"w": 20, "h": 5},
})
@router.get("/markdown_widget_with_run_button")
def markdown_widget_with_run_button():
    """Returns a markdown widget with a run button"""
    return f"# Markdown Widget with Run Button\n\n{datetime.now()}"


@register_widget({
    "name": "Markdown Widget with Short Refetch Interval and Run Button",
    "description": "A markdown widget with both short refetch interval and a run button",
    "type": "markdown",
    "endpoint": "markdown_widget_with_short_refetch_interval_and_run_button",
    "refetch_interval": 5000,
    "runButton": True,
    "gridData": {"w": 20, "h": 5},
})
@router.get("/markdown_widget_with_short_refetch_interval_and_run_button")
def markdown_widget_with_short_refetch_interval_and_run_button():
    """Returns a markdown widget with short refetch interval and run button"""
    return f"# Markdown Widget with Short Refetch Interval and Run Button\n\n{datetime.now()}"


# ============================================================================
# VENDOR PREFIXED WIDGETS (Structured API)
# ============================================================================

@register_widget({
    "name": "Markdown Widget with Better Structured API",
    "description": "A markdown widget with structured API output format (vendor prefixed)",
    "type": "markdown",
    "endpoint": "/vendor1/markdown_widget_with_better_structured_api",
    "gridData": {"w": 20, "h": 5},
})
@router.get("/vendor1/markdown_widget_with_better_structured_api")
def markdown_widget_with_better_structured_api():
    """Returns a markdown widget with structured API output"""
    response = {
        "content": f"# Markdown Widget with Better Structured API\n\n{datetime.now()}",
        "data_format": {"data_type": "string", "parse_as": "text"},
    }
    return JSONResponse(content=response)
