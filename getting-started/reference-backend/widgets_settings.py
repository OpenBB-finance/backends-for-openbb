from datetime import datetime, timedelta
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from core import register_widget, WIDGETS

router = APIRouter()


def last_minute_data_update():
    """Return the latest backend data update boundary for a once-per-minute feed."""
    return datetime.now().replace(second=0, microsecond=0)


def last_daily_data_update(hour: int, minute: int):
    """Return the latest backend data update boundary for a daily feed."""
    now = datetime.now().replace(microsecond=0)
    scheduled_update = now.replace(hour=hour, minute=minute, second=0)

    if now < scheduled_update:
        scheduled_update -= timedelta(days=1)

    return scheduled_update


def data_update_markdown(title: str, updated_at: datetime, schedule: str):
    return (
        f"# {title}\n\n"
        f"Data updated at: {updated_at}\n\n"
        f"Backend data schedule: {schedule}\n\n"
        "This timestamp is controlled by the backend data schedule, not request time."
    )


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
    "name": "Markdown Widget with Cron Refetch Interval",
    "description": "A markdown widget that auto-refreshes on cron schedule boundaries and displays its data update schedule in widget metadata.",
    "type": "markdown",
    "endpoint": "markdown_widget_with_cron_refetch_interval",
    "refetchInterval": "*/1 * * * *",  # Every minute, using standard 5-field cron syntax
    "dataUpdateDisplay": "*/1 * * * *",  # Shows the data update schedule in the refresh indicator tooltip
    "gridData": {"w": 20, "h": 6},
})
@router.get("/markdown_widget_with_cron_refetch_interval")
def markdown_widget_with_cron_refetch_interval():
    """Returns a markdown widget that auto-refreshes every minute via cron"""
    return data_update_markdown(
        "Cron Refetch Interval",
        last_minute_data_update(),
        "Every minute",
    )


@register_widget({
    "name": "Markdown Widget with Data Update Display Only",
    "description": "A markdown widget that displays a data update schedule without configuring automatic refresh.",
    "type": "markdown",
    "endpoint": "markdown_widget_with_data_update_display_only",
    "dataUpdateDisplay": "0 10 * * *",  # Displays as updated every day at 10:00 without driving refetches
    "gridData": {"w": 20, "h": 6},
})
@router.get("/markdown_widget_with_data_update_display_only")
def markdown_widget_with_data_update_display_only():
    """Returns a markdown widget with display-only data update metadata"""
    return data_update_markdown(
        "Data Update Display Only",
        last_daily_data_update(hour=10, minute=0),
        "Every day at 10:00",
    )


@register_widget({
    "name": "Markdown Widget with Cron Refetch Only",
    "description": "A markdown widget that auto-refreshes on cron schedule boundaries without displaying a separate data update schedule.",
    "type": "markdown",
    "endpoint": "markdown_widget_with_cron_refetch_only",
    "refetchInterval": "*/1 * * * *",  # Every minute, using standard 5-field cron syntax
    "gridData": {"w": 20, "h": 6},
})
@router.get("/markdown_widget_with_cron_refetch_only")
def markdown_widget_with_cron_refetch_only():
    """Returns a markdown widget that auto-refreshes every minute via cron without display metadata"""
    return data_update_markdown(
        "Cron Refetch Only",
        last_minute_data_update(),
        "Every minute",
    )


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
