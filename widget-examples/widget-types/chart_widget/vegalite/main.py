# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "fastapi>=0.115",
#   "uvicorn>=0.32",
# ]
# ///
"""Minimal OpenBB Workspace backend serving Vega-Lite chart widgets.

Run: `uv run main.py`
Then add `http://localhost:8765` as a Data Connector in OpenBB Workspace.
"""

from __future__ import annotations

import math
import random
from datetime import date, timedelta

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Vega-Lite Demo Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

WIDGETS = {
    "vega_bar_demo": {
        "name": "Vega-Lite Bar Demo",
        "description": "A minimal Vega-Lite bar chart to validate the chart-vegalite widget type.",
        "category": "Demo",
        "subCategory": "Vega-Lite",
        "type": "chart-vegalite",
        "endpoint": "vega_bar",
        "gridData": {"w": 20, "h": 12},
        "source": ["Vega-Lite Demo"],
    },
    "vega_line_demo": {
        "name": "Vega-Lite Line Demo",
        "description": "Time-series line chart rendered from a Vega-Lite spec.",
        "category": "Demo",
        "subCategory": "Vega-Lite",
        "type": "chart-vegalite",
        "endpoint": "vega_line",
        "gridData": {"w": 20, "h": 12},
        "source": ["Vega-Lite Demo"],
    },
    "vega_scatter_demo": {
        "name": "Vega-Lite Scatter Demo",
        "description": "Scatter plot with 200 points rendered from a Vega-Lite spec.",
        "category": "Demo",
        "subCategory": "Vega-Lite",
        "type": "chart-vegalite",
        "endpoint": "vega_scatter",
        "gridData": {"w": 20, "h": 12},
        "source": ["Vega-Lite Demo"],
    },
}


def _theme_colors(theme: str) -> dict[str, str]:
    if theme == "light":
        return {
            "bg": "transparent",
            "fg": "#1a1a1a",
            "grid": "#e5e5e5",
            "mark": "#2563eb",
        }
    return {
        "bg": "transparent",
        "fg": "#e5e7eb",
        "grid": "#2a2a2a",
        "mark": "#60a5fa",
    }


def _base_config(theme: str) -> dict:
    c = _theme_colors(theme)
    return {
        "background": c["bg"],
        "axis": {
            "labelColor": c["fg"],
            "titleColor": c["fg"],
            "gridColor": c["grid"],
            "domainColor": c["grid"],
            "tickColor": c["grid"],
        },
        "legend": {"labelColor": c["fg"], "titleColor": c["fg"]},
        "title": {"color": c["fg"]},
        "view": {"stroke": "transparent"},
    }


@app.get("/widgets.json")
def widgets_json():
    return WIDGETS


@app.get("/vega_bar")
def vega_bar(theme: str = "dark"):
    c = _theme_colors(theme)
    return {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "title": "Top chains by TVL (mock)",
        "width": "container",
        "height": "container",
        "autosize": {"type": "fit", "contains": "padding"},
        "config": _base_config(theme),
        "data": {
            "values": [
                {"chain": "Ethereum", "tvl": 68.4},
                {"chain": "Tron", "tvl": 29.1},
                {"chain": "Solana", "tvl": 12.7},
                {"chain": "BSC", "tvl": 10.3},
                {"chain": "Base", "tvl": 8.9},
                {"chain": "Arbitrum", "tvl": 6.2},
                {"chain": "Polygon", "tvl": 4.8},
                {"chain": "Avalanche", "tvl": 1.6},
            ]
        },
        "mark": {"type": "bar", "color": c["mark"], "tooltip": True},
        "encoding": {
            "x": {"field": "chain", "type": "nominal", "sort": "-y", "title": "Chain"},
            "y": {"field": "tvl", "type": "quantitative", "title": "TVL (B USD)"},
        },
    }


@app.get("/vega_line")
def vega_line(theme: str = "dark"):
    c = _theme_colors(theme)
    start = date(2024, 1, 1)
    random.seed(42)
    price = 100.0
    values = []
    for i in range(120):
        price *= 1 + random.uniform(-0.02, 0.025)
        values.append(
            {
                "date": (start + timedelta(days=i)).isoformat(),
                "price": round(price, 2),
            }
        )
    return {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "title": "Synthetic price series",
        "width": "container",
        "height": "container",
        "autosize": {"type": "fit", "contains": "padding"},
        "config": _base_config(theme),
        "data": {"values": values},
        "mark": {"type": "line", "color": c["mark"], "tooltip": True},
        "encoding": {
            "x": {"field": "date", "type": "temporal", "title": "Date"},
            "y": {
                "field": "price",
                "type": "quantitative",
                "title": "Price",
                "scale": {"zero": False},
            },
        },
    }


@app.get("/vega_scatter")
def vega_scatter(theme: str = "dark"):
    c = _theme_colors(theme)
    random.seed(7)
    values = []
    for _ in range(200):
        x = random.gauss(0, 1)
        y = 0.6 * x + random.gauss(0, 0.8)
        group = "A" if math.sin(x) > 0 else "B"
        values.append({"x": round(x, 3), "y": round(y, 3), "group": group})
    return {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "title": "Correlated noise",
        "width": "container",
        "height": "container",
        "autosize": {"type": "fit", "contains": "padding"},
        "config": _base_config(theme),
        "data": {"values": values},
        "mark": {"type": "circle", "size": 60, "opacity": 0.75, "tooltip": True},
        "encoding": {
            "x": {"field": "x", "type": "quantitative"},
            "y": {"field": "y", "type": "quantitative"},
            "color": {
                "field": "group",
                "type": "nominal",
                "scale": {"range": [c["mark"], "#f59e0b"]},
                "legend": {"title": "Group"},
            },
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8765)
