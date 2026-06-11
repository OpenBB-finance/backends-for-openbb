# Workspace Parameter Bridge — Iframe & HtmlViewer

A minimal, self-contained backend (mock data, no API keys) showing how a widget
can **push parameter updates back to OpenBB Workspace**. Workspace persists the
update and re-sends it to every widget grouped on that parameter — so one widget
can drive the rest of the dashboard.

This is the **outbound** direction (widget → Workspace). The inbound direction
(Workspace → iframe, where Workspace sends params *into* an embedded app) is shown
in the [`streamlit`](../streamlit) example.

Two widget types are demonstrated because they forward the update differently:

| Widget type | How it sends the update |
|-------------|-------------------------|
| `iframe`    | The embedded page posts the message **directly**: `window.parent.postMessage(...)` |
| `html`      | The page dispatches a **CustomEvent**; the bridge script Workspace injects into the HtmlViewer forwards it for you (you do **not** postMessage) |

## The message

Both paths use the same payload. Either send all params at once:

```js
{ type: "openbb:widget-params:update", params: { ticker: "NVDA" } }
```

…or a single named param:

```js
{ type: "openbb:widget-params:update", paramName: "ticker", value: "NVDA" }
```

- **Iframe widget** posts it to the parent:
  ```js
  window.parent.postMessage({ type: "openbb:widget-params:update", params: { ticker: "NVDA" } }, "*");
  ```
- **HtmlViewer widget** dispatches it as an event and lets the injected bridge forward it:
  ```js
  window.dispatchEvent(new CustomEvent("openbb:widget-params:update", {
    detail: { type: "openbb:widget-params:update", params: { ticker: "NVDA" } }
  }));
  ```

## Run

```bash
pip install -r requirements.txt
uvicorn main:app --port 5050 --reload
```

Then in OpenBB Workspace: **Apps → Connect backend →** `http://localhost:5050`.
Open the **Bridge Demo** app/tab.

> **Serving on a different port or host?** The `iframe` widget needs an absolute
> URL, built from `PUBLIC_URL` (default `http://localhost:5050`). Behind a tunnel,
> set it: `PUBLIC_URL=https://abc123.ngrok.io uvicorn main:app --port 5050`.

## What to try

The dashboard has three widgets, all grouped on `ticker`:

- **Quote (mock)** — a metric widget that reads `ticker`.
- **Iframe Bridge** — ticker buttons (posts directly to the parent).
- **HtmlViewer Bridge** — ticker buttons (dispatches a CustomEvent).

Click a ticker in either bridge widget → **Quote** updates to that ticker. That
is the full round-trip: widget pushes the param → Workspace persists it and
updates the group → the grouped widget re-fetches.

### Zero-UI smoke test

You can fire the message by hand. Open DevTools on the iframe widget's context and run:

```js
window.parent.postMessage({
  type: "openbb:widget-params:update",
  params: { ticker: "TSLA" }
}, "*");
```

Workspace should persist it and update the group, just like clicking a button.

## Files

- `main.py` — the entire backend: serves `widgets.json` / `apps.json`, the mock
  data widget, and the two bridge pages.
- `requirements.txt` — FastAPI + Uvicorn.
