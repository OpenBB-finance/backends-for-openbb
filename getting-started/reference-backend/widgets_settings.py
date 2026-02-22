from datetime import datetime
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from core import register_widget, WIDGETS

router = APIRouter()

@register_widget({
    "name": "Markdown Widget with Stale Time",
    "description": "A markdown widget with stale time. The widget will show stale data before fetching new data.",
    "type": "markdown",
    "endpoint": "markdown_widget_with_stale_time",
    "staleTime": 10000,  # 10000 milliseconds = 10 seconds
    "gridData": {"w": 20, "h": 5},
})
@router.get("/markdown_widget_with_stale_time")
def markdown_widget_with_stale_time():
    """Returns a markdown widget with stale time"""
    return f"# Stale 10s Time\n\n{datetime.now().replace(microsecond=0)}"


@register_widget({
    "name": "Markdown Widget with Short Refetch Interval",
    "description": "A markdown widget that auto-refreshes at a short interval",
    "type": "markdown",
    "endpoint": "markdown_widget_with_short_refetch_interval",
    "refetchInterval": 5000,  # 5000 milliseconds = 5 seconds
    "gridData": {"w": 20, "h": 5},
})
@router.get("/markdown_widget_with_short_refetch_interval")
def markdown_widget_with_short_refetch_interval():
    """Returns a markdown widget that auto-refreshes every 5 seconds"""
    return f"# Short 5s Refetch Interval\n\n{datetime.now().replace(microsecond=0)}"


@register_widget({
    "name": "Markdown Widget with Refetch Interval and Shorter Stale Time",
    "description": "A markdown widget with both refetch interval and shorter stale time",
    "type": "markdown",
    "endpoint": "markdown_widget_with_refetch_interval_and_shorter_stale_time",
    "refetchInterval": 10000,  # 10 seconds
    "staleTime": 5000,  # 5 seconds - shorter than refetch interval
    "gridData": {"w": 20, "h": 5},
})
@router.get("/markdown_widget_with_refetch_interval_and_shorter_stale_time")
def markdown_widget_with_refetch_interval_and_shorter_stale_time():
    """Returns a markdown widget with refetch interval and shorter stale time"""
    return f"# Refetch 10s Interval and Shorter 5s Stale Time\n\n{datetime.now().replace(microsecond=0)}"


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
    return f"# Run Button\n\n{datetime.now().replace(microsecond=0)}"


@register_widget({
    "name": "Markdown Widget with Short Refetch Interval and Run Button",
    "description": "A markdown widget with both short refetch interval and a run button",
    "type": "markdown",
    "endpoint": "markdown_widget_with_short_refetch_interval_and_run_button",
    "refetchInterval": 5000,
    "runButton": True,
    "gridData": {"w": 20, "h": 5},
})
@router.get("/markdown_widget_with_short_refetch_interval_and_run_button")
def markdown_widget_with_short_refetch_interval_and_run_button():
    """Returns a markdown widget with short refetch interval and run button"""
    return f"# Short 5s Refetch Interval and Run Button\n\n{datetime.now().replace(microsecond=0)}"
