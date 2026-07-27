"""
OpenBB Workspace — iframe widgets that look native.

Two `type: "iframe"` widgets (a table and a multi-series chart) rendered with
plain HTML/CSS/SVG, styled with the exact colors Workspace uses, so an embedded
page is visually indistinguishable from a built-in widget in either theme.

What it demonstrates:

  - Theme sync      — Workspace appends `theme=light|dark` to the iframe URL and
                      re-sends it via `openbb-params-update`. The page restyles
                      itself with no reload.
  - Param controls  — the `openbb-connect` handshake declares param defs, which
                      Workspace renders as controls in the widget navbar.
  - Widget groups   — clicking a table row pushes `ticker` back to Workspace,
                      which drives the chart through the app's param group.
  - Copilot access  — the handshake manifest lets the AI request the widget's
                      current data via `openbb-request`.

Run:
    pip install -r requirements.txt
    uvicorn main:app --port 5051 --reload

Then in OpenBB Workspace: Apps -> Connect backend -> http://localhost:5051
"""

import os

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

import mock_data

# An `iframe` widget needs an ABSOLUTE URL Workspace can load. Override when
# serving elsewhere: `PUBLIC_URL=https://abc123.ngrok.io uvicorn main:app`.
PUBLIC_URL = os.environ.get("PUBLIC_URL", "http://localhost:5051")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI(title="OpenBB Workspace Native-UI Iframe Example")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://pro.openbb.co",
        "https://pro.openbb.dev",
        "http://localhost:1420",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")


# ---------------------------------------------------------------------------
# Widget + app configuration
# ---------------------------------------------------------------------------

# Shared param: the table pushes it, the chart consumes it, the group syncs them.
TICKER_PARAM = {
    "paramName": "ticker",
    "type": "text",
    "label": "Ticker",
    "value": "NVDA",
    "description": "Selected ticker (synced across the group)",
}


def widgets_json() -> dict:
    return {
        "native_table": {
            "name": "Positions",
            "description": "Iframe table styled with the Workspace table palette. Click a row to sync the group.",
            "category": "Native UI",
            "type": "iframe",
            "endpoint": f"{PUBLIC_URL}/pages/table.html",
            "gridData": {"w": 22, "h": 13},
            "params": [TICKER_PARAM],
        },
        "native_chart": {
            "name": "Relative performance",
            "description": "Iframe SVG chart using the Workspace chart palette, gridlines and legend.",
            "category": "Native UI",
            "type": "iframe",
            "endpoint": f"{PUBLIC_URL}/pages/chart.html",
            "gridData": {"w": 18, "h": 13},
            "params": [TICKER_PARAM],
        },
    }


def apps_json() -> list:
    return [
        {
            # App ids must start with `custom-` — Workspace rejects anything else.
            "id": "custom-native-ui-iframes",
            "name": "Native UI Iframes",
            "description": "Iframe widgets styled to match the Workspace UI in both themes.",
            "img": "",
            "img_dark": "",
            "img_light": "",
            "allowCustomization": True,
            "tabs": {
                "native_ui": {
                    "id": "native_ui",
                    "name": "Native UI",
                    "layout": [
                        {"i": "native_table", "x": 0, "y": 0, "w": 22, "h": 13, "groups": ["Group 1"]},
                        {"i": "native_chart", "x": 22, "y": 0, "w": 18, "h": 13, "groups": ["Group 1"]},
                    ],
                }
            },
            "groups": [
                {
                    "name": "Group 1",
                    "type": "param",
                    "paramName": "ticker",
                    "widgetIds": ["native_table", "native_chart"],
                    "defaultValue": "NVDA",
                }
            ],
            "prompts": [],
        }
    ]


@app.get("/")
def root():
    return {"message": "OpenBB Workspace native-UI iframe example"}


@app.get("/widgets.json")
def get_widgets():
    return JSONResponse(content=widgets_json())


@app.get("/apps.json")
def get_apps():
    return JSONResponse(content=apps_json())


# ---------------------------------------------------------------------------
# Pages loaded by the iframe widgets
# ---------------------------------------------------------------------------

@app.get("/pages/{name}.html")
def page(name: str):
    path = os.path.join(BASE_DIR, "pages", f"{name}.html")
    if not os.path.isfile(path):
        return JSONResponse({"error": "not found"}, status_code=404)
    # No caching: the page is edited live while you iterate on the styling.
    return FileResponse(path, headers={"Cache-Control": "no-store"})


# ---------------------------------------------------------------------------
# Data the pages fetch (same origin as the page, so no CORS involved)
# ---------------------------------------------------------------------------

@app.get("/api/positions")
def api_positions(sector: str = Query("All")):
    return mock_data.positions(sector)


@app.get("/api/series")
def api_series(ticker: str = Query("NVDA"), count: int = Query(4, ge=1, le=12)):
    return mock_data.series(mock_data.peers(ticker, count))
