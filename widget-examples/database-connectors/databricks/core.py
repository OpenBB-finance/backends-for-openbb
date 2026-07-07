import asyncio
import os
import threading
import time
from functools import wraps
from typing import Any, List, Literal

from databricks import sql
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

load_dotenv()

app = FastAPI(
    title="Databricks Explorer",
    description="Explore the Databricks sample datasets in OpenBB Workspace",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://pro.openbb.co",
        "https://pro.openbb.dev",
        "https://excel.openbb.co",
        "https://excel.openbb.dev",
        "http://localhost",
        "http://localhost:1420",
        "http://localhost:5050",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CATALOG = os.getenv("DATABRICKS_CATALOG", "samples")

WIDGETS = {}

_conn = None
_conn_lock = threading.Lock()
_cache = {}
CACHE_TTL = 300


def _get_connection():
    global _conn
    if _conn is None:
        _conn = sql.connect(
            server_hostname=os.getenv("DATABRICKS_SERVER_HOSTNAME"),
            http_path=os.getenv("DATABRICKS_HTTP_PATH"),
            access_token=os.getenv("DATABRICKS_ACCESS_TOKEN"),
        )
    return _conn


def query(sql_text: str, ttl: int = CACHE_TTL) -> list[dict]:
    """Run a query against Databricks, caching results for `ttl` seconds."""
    global _conn
    now = time.time()
    if ttl and sql_text in _cache:
        cached_time, cached_data = _cache[sql_text]
        if now - cached_time < ttl:
            return cached_data

    with _conn_lock:
        try:
            cursor = _get_connection().cursor()
        except Exception:
            _conn = None
            cursor = _get_connection().cursor()
        try:
            cursor.execute(sql_text)
            columns = [c[0] for c in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception:
            # Drop the session on failure so the next call reconnects
            try:
                _conn.close()
            except Exception:
                pass
            _conn = None
            raise
        finally:
            try:
                cursor.close()
            except Exception:
                pass

    if ttl:
        _cache[sql_text] = (now, data)
    return data


def register_widget(widget_config):
    """Register a widget configuration so it is served from /widgets.json."""

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
            widget_config.setdefault("source", "Databricks samples catalog")
            WIDGETS[widget_config["widgetId"]] = widget_config

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


class DataFormat(BaseModel):
    """Data format for an omni widget response"""

    data_type: str
    parse_as: Literal["text", "table", "chart"]


class SourceInfo(BaseModel):
    type: Literal["widget"] = "widget"
    name: str
    description: str | None = Field(default=None)
    metadata: dict[str, Any] | None = Field(default=None)


class ExtraCitation(BaseModel):
    source_info: SourceInfo | None = Field(default=None)
    details: List[dict] | None = Field(default=None)


class OmniWidgetResponse(BaseModel):
    """Response envelope for omni widgets"""

    content: Any
    data_format: DataFormat
    extra_citations: list[ExtraCitation] | None = Field(default_factory=list)
    citable: bool = Field(default=True)
