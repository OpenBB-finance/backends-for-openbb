# Native-looking Iframe Widgets

A self-contained backend (mock data, no API keys) with two `type: "iframe"`
widgets — a table and a multi-series chart — styled with the exact colors OpenBB
Workspace uses, so an embedded page is indistinguishable from a built-in widget
in both light and dark themes.

Use it as a starting point when you already have a web app and want it to *look*
like it belongs inside Workspace.

## Setup

```bash
pip install -r requirements.txt
uvicorn main:app --port 5051 --reload
```

Then in OpenBB Workspace: **Apps → Connect backend →** `http://localhost:5051`,
and open the **Native UI Iframes** app.

> **Serving elsewhere?** An `iframe` widget needs an absolute URL, built from
> `PUBLIC_URL` (default `http://localhost:5051`). Behind a tunnel:
> `PUBLIC_URL=https://abc123.ngrok.io uvicorn main:app --port 5051`.

## What it demonstrates

| | |
|---|---|
| **Theme sync** | Workspace appends `theme=light\|dark` to the iframe URL *and* re-sends it via `openbb-params-update`. Toggle the theme — the pages restyle instantly. |
| **Navbar params** | The `openbb-connect` handshake declares param defs (`sector` on the table, `count` on the chart); Workspace renders them as controls in the widget navbar. |
| **Widget groups** | Clicking a table row pushes `ticker` back to Workspace, which drives the chart through the app's param group. |
| **Copilot access** | The handshake manifest lets the AI request each widget's current data via `openbb-request`. |

## The styling rules

Both pages follow the same rules — the first one is the one people get wrong.

**1. Put the theme background on `html`/`body`, not on an inner card.** Styling
only the table or chart container leaves a white frame around the widget in dark
mode. Also `margin: 0`, wrapper `width: 100%` / `min-height: 100%`, and keep the
wrapper padding small (`8px 12px`) so content sits close to the widget chrome.

**2. Use the Workspace colors** (all in [`static/openbb-theme.css`](static/openbb-theme.css)):

| | Light | Dark |
|---|---|---|
| Page / chart background | `#FFFFFF` | `#151518` |
| Table row | `#FFFFFF` | `#1F1E23` |
| Table alternating row | `#F6F6F6` | `#2A2A31` |
| Table header | `#EBEBED` | `#36363E` |
| Text | `#191D1F` | `#FFFFFF` |
| Gridlines | `#E8E8E9` | `#515153` |

**3. No borders in tables.** Rows separate by alternating fill only — no divider
lines between rows or columns.

**4. One fixed series palette, identical in both themes**, assigned in order and
cycled past 10 series (set the chart's **Series** control above 10 to see it):

`#5F8ED6` · `#F2A450` · `#5D9B5C` · `#61BCDD` · `#DECD43` · `#8F6BC5` ·
`#B5B5B5` · `#B060A3` · `#846430` · `#DD5F58`

**5. No heading inside the page.** Workspace already renders the widget `name`
in its title bar; repeating it shows the title twice. A short subtitle is fine.

**6. Legend** is a small line swatch plus a label in the axis text color, wrapping
across rows — no box, border or background fill.

## Files

- `main.py` — serves `widgets.json` / `apps.json`, the two pages, and the mock data API.
- `mock_data.py` — deterministic sample positions and price series.
- `static/openbb-theme.css` — the Workspace palette and table/chart chrome.
- `static/openbb-iframe.js` — ~90 lines handling the whole iframe protocol: theme,
  params, handshake, copilot data requests, and pushing params back.
- `pages/table.html`, `pages/chart.html` — the widgets themselves.
