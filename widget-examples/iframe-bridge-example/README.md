# Workspace Parameter Bridge — Iframe & HtmlViewer

A minimal, self-contained backend (mock data, no API keys) showing how a widget
can **push parameter updates back to OpenBB Workspace**. Workspace persists the
update and re-sends it to every widget grouped on that parameter — so one widget
can drive the rest of the dashboard.

This is the **outbound** direction (widget → Workspace). The inbound direction
(Workspace → iframe, where Workspace sends params *into* an embedded app) is shown
in the [`streamlit`](../streamlit) example.

## Setup

```bash
pip install -r requirements.txt
uvicorn main:app --port 5050 --reload
```

Then in OpenBB Workspace: **Apps → Connect backend →** `http://localhost:5050`.
Open the **Bridge Demo** app/tab.

> **Serving on a different port or host?** The `iframe` widget needs an absolute
> URL, built from `PUBLIC_URL` (default `http://localhost:5050`). Behind a tunnel,
> set it: `PUBLIC_URL=https://abc123.ngrok.io uvicorn main:app --port 5050`.

## How it works

Two widget types are demonstrated because they forward the update differently:

| Widget type | How it sends the update |
|-------------|-------------------------|
| `iframe`    | The embedded page posts the message **directly**: `window.parent.postMessage(...)` |
| `html`      | The page dispatches a **CustomEvent**; the bridge script Workspace injects into the HtmlViewer forwards it for you (you do **not** postMessage) |

Both paths use the same payload — send all params at once, or a single named param:

```js
{ type: "openbb:widget-params:update", params: { ticker: "NVDA" } }
{ type: "openbb:widget-params:update", paramName: "ticker", value: "NVDA" }
```

The demo app has three widgets grouped on `ticker` (a mock **Quote** plus the two
bridge widgets). Click a ticker in either bridge → Workspace persists the param and
the **Quote** widget re-fetches with it.

## Files

- `main.py` — the entire backend: serves `widgets.json` / `apps.json`, the mock
  data widget, and the two bridge pages.
- `requirements.txt` — FastAPI + Uvicorn.
