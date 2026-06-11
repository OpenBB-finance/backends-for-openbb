"""
OpenBB Workspace — Iframe & HtmlViewer parameter bridge example.

Demonstrates the *outbound* direction of the Workspace parameter bridge: a widget
pushing a parameter update back to Workspace, which then persists it and updates
any widget group synced on that parameter. (The inbound direction — Workspace
sending params *into* an iframe — is covered by the `streamlit` example.)

Two widget types are shown, because they forward params differently:

  - type "iframe":  the embedded page posts `openbb:widget-params:update`
                    DIRECTLY to the parent window via window.parent.postMessage.

  - type "html":    the returned HTML dispatches an `openbb:widget-params:update`
                    CustomEvent. The page does NOT postMessage — the bridge
                    script Workspace injects into the HtmlViewer forwards it.

A small mock "Quote" widget reads the `ticker` param, so when you click a ticker
inside either bridge widget you can watch every widget grouped on `ticker` update
live — proof the round-trip works end to end.

Run:
    pip install -r requirements.txt
    uvicorn main:app --port 5050 --reload

Then in OpenBB Workspace: Apps -> Connect backend -> http://localhost:5050
"""

import os

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse

# The iframe widget needs an ABSOLUTE URL Workspace can load, so it is built from
# this base. Override with PUBLIC_URL if you serve on a different port or behind
# a tunnel (e.g. ngrok): `PUBLIC_URL=https://abc123.ngrok.io uvicorn main:app`.
PUBLIC_URL = os.environ.get("PUBLIC_URL", "http://localhost:5050")

app = FastAPI(title="OpenBB Workspace Bridge Example")

# Workspace runs in the browser at these origins; allow them to fetch the backend.
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


# ---------------------------------------------------------------------------
# Mock data — no external API, no keys. Just enough to prove the bridge.
# ---------------------------------------------------------------------------

MOCK_QUOTES = {
    "AAPL": {"name": "Apple Inc.", "price": 228.52, "change_pct": 0.84},
    "NVDA": {"name": "NVIDIA Corp.", "price": 132.40, "change_pct": 2.13},
    "MSFT": {"name": "Microsoft Corp.", "price": 451.10, "change_pct": -0.32},
    "TSLA": {"name": "Tesla Inc.", "price": 251.77, "change_pct": 1.55},
}
TICKERS = list(MOCK_QUOTES)


# ---------------------------------------------------------------------------
# Widget + app configuration (served as JSON Workspace reads on connect).
# ---------------------------------------------------------------------------

def widgets_json() -> dict:
    # The shared `ticker` param + group type "param" is what lets the bridge's
    # outbound update propagate to every widget below.
    ticker_param = {
        "paramName": "ticker",
        "type": "text",
        "label": "Ticker",
        "value": "AAPL",
        "description": "Stock ticker (synced across the group)",
    }
    return {
        "mock_quote": {
            "name": "Quote (mock, synced on ticker)",
            "description": "Reads the `ticker` param. Updates when you click a ticker in either bridge widget.",
            "category": "Bridge Example",
            "type": "metric",
            "endpoint": "mock_quote",
            "gridData": {"w": 40, "h": 5},
            "params": [ticker_param],
        },
        "bridge_iframe": {
            "name": "Iframe Bridge",
            "description": "Embedded page posts openbb:widget-params:update directly to the parent (outbound iframe bridge).",
            "category": "Bridge Example",
            "type": "iframe",
            "endpoint": f"{PUBLIC_URL}/bridge_iframe_page",
            "gridData": {"w": 20, "h": 12},
            "params": [ticker_param],
        },
        "bridge_html": {
            "name": "HtmlViewer Bridge",
            "description": "Returned HTML dispatches an openbb:widget-params:update CustomEvent; the injected bridge forwards it.",
            "category": "Bridge Example",
            "type": "html",
            "endpoint": "bridge_html",
            "gridData": {"w": 20, "h": 12},
            "params": [ticker_param],
        },
    }


def apps_json() -> list:
    return [
        {
            "id": "bridge-example",
            "name": "Workspace Bridge Example",
            "description": "Push parameter updates from a widget back to Workspace (iframe + HtmlViewer).",
            "img": "",
            "img_dark": "",
            "img_light": "",
            "allowCustomization": True,
            "tabs": {
                "bridge_demo": {
                    "id": "bridge_demo",
                    "name": "Bridge Demo",
                    "layout": [
                        {"i": "mock_quote", "x": 0, "y": 0, "w": 40, "h": 5, "groups": ["Group 1"]},
                        {"i": "bridge_iframe", "x": 0, "y": 5, "w": 20, "h": 12, "groups": ["Group 1"]},
                        {"i": "bridge_html", "x": 20, "y": 5, "w": 20, "h": 12, "groups": ["Group 1"]},
                    ],
                }
            },
            # The group syncs every member on `ticker`. When a bridge widget pushes
            # a new ticker, Workspace writes it here and re-sends to the group.
            "groups": [
                {
                    "name": "Group 1",
                    "type": "param",
                    "paramName": "ticker",
                    "widgetIds": ["mock_quote", "bridge_iframe", "bridge_html"],
                    "defaultValue": "AAPL",
                }
            ],
            "prompts": [],
        }
    ]


@app.get("/")
def root():
    return {"message": "OpenBB Workspace Bridge Example backend"}


@app.get("/widgets.json")
def get_widgets():
    return JSONResponse(content=widgets_json())


@app.get("/apps.json")
def get_apps():
    return JSONResponse(content=apps_json())


# ---------------------------------------------------------------------------
# Data widget — reads the synced `ticker` param.
# ---------------------------------------------------------------------------

@app.get("/mock_quote")
def mock_quote(ticker: str = Query("AAPL")):
    """Mock quote for the selected ticker — the widget that proves the sync."""
    q = MOCK_QUOTES.get(ticker.upper())
    if not q:
        return [
            {"label": ticker.upper(), "value": "no mock data", "subvalue": f"try {', '.join(TICKERS)}"},
        ]
    return [
        {"label": q["name"], "value": f"${q['price']:.2f}", "subvalue": f"{q['change_pct']:+.2f}% today"},
        {"label": "Ticker (via bridge)", "value": ticker.upper(), "subvalue": "Pushed from a bridge widget"},
    ]


# ---------------------------------------------------------------------------
# Bridge widget pages.
# ---------------------------------------------------------------------------

_BUTTONS = "".join(f"<button onclick=\"pick('{t}')\">{t}</button>" for t in TICKERS)

# type "iframe": the page posts the update DIRECTLY to the parent window.
BRIDGE_IFRAME_HTML = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>Iframe Bridge</title>
<style>
  body {{ font-family: system-ui, sans-serif; background: #0d1117; color: #e6edf3;
         margin: 0; padding: 16px; }}
  button {{ background: #1f6feb; color: #fff; border: 0; border-radius: 6px;
            padding: 8px 14px; margin: 4px; font-size: 14px; cursor: pointer; }}
  #log {{ margin-top: 12px; padding: 8px; background: #161b22; border-radius: 6px;
          font-family: monospace; font-size: 12px; white-space: pre-wrap;
          max-height: 150px; overflow: auto; }}
</style></head>
<body>
  <h3>Iframe Bridge</h3>
  <p>Current ticker: <b id="cur">-</b></p>
  <div>{_BUTTONS}</div>
  <div id="log"></div>
  <script>
    function log(m) {{
      const el = document.getElementById("log");
      el.textContent = m + "\\n" + el.textContent;
    }}
    // OUTBOUND: post the param update straight to the parent (Workspace).
    function pick(t) {{
      const msg = {{ type: "openbb:widget-params:update", params: {{ ticker: t }} }};
      (window.top || window.parent).postMessage(msg, "*");
      log("-> sent " + JSON.stringify(msg.params));
    }}
    // INBOUND (optional): show the round-trip when Workspace echoes the param.
    window.addEventListener("message", function(e) {{
      if (!e.data || !e.data.type) return;
      if (e.data.type === "openbb-params-update" ||
          e.data.type === "openbb:widget-params:update") {{
        const p = e.data.params || {{}};
        if (p.ticker) document.getElementById("cur").textContent = p.ticker;
        log("<- recv " + e.data.type + " " + JSON.stringify(p));
      }}
    }});
  </script>
</body></html>"""

# type "html": the page only DISPATCHES a CustomEvent. The bridge script that
# Workspace injects into the HtmlViewer is what forwards it via postMessage
# (with the security token) — so this page must NOT postMessage itself.
BRIDGE_HTML_INNER = f"""<div style="font-family: system-ui, sans-serif; padding: 12px;">
  <h3>HtmlViewer Bridge</h3>
  <p>Click a ticker. The page dispatches an <code>openbb:widget-params:update</code>
     CustomEvent; the injected bridge forwards it to Workspace.</p>
  <div>{_BUTTONS}</div>
  <script>
    function pick(t) {{
      window.dispatchEvent(new CustomEvent("openbb:widget-params:update", {{
        detail: {{ type: "openbb:widget-params:update", params: {{ ticker: t }} }}
      }}));
    }}
  </script>
</div>"""


@app.get("/bridge_iframe_page")
def bridge_iframe_page():
    """Standalone page embedded by the `iframe` widget."""
    return HTMLResponse(BRIDGE_IFRAME_HTML)


@app.get("/bridge_html")
def bridge_html():
    """HTML returned to the `html` (HtmlViewer) widget."""
    return HTMLResponse(BRIDGE_HTML_INNER)
