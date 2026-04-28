# Streamlit — OpenBB Iframe Widget Protocol

Demonstrates how a Streamlit app can integrate with OpenBB Workspace using the **Iframe Widget Protocol**. The app declares sub-widgets (tables, markdown) that Workspace can export as standalone dashboard widgets, and includes an MCP server for AI-powered portfolio analysis.

## Setup

```bash
cd widget-examples/streamlit
pip install -r requirements.txt
# or with uv
uv sync
```

## Running

### 1. Streamlit app (iframe widgets)

```bash
uv run streamlit run app.py                        # default port 8501
uv run streamlit run app.py --server.port 8502     # custom port
```

This starts the portfolio dashboard on `http://localhost:8501` (or your custom port).

### 2. MCP server + Workspace backend

In a separate terminal:

```bash
uv run python mcp_server.py            # default port 7769
uv run python mcp_server.py --port 7762 # custom port
```

This single process serves:

| Route | Purpose |
|-------|---------|
| `/mcp` | MCP tools (`get_portfolio_holdings`, `get_sector_allocation`, `get_market_summary`, `rebalance_portfolio`) |
| `/widgets.json` | Widget definitions for OpenBB Workspace |
| `/apps.json` | Pre-built "Streamlit Portfolio" app layout |
| `/portfolio_note` | Markdown content for the dashboard's note widget |

## Connecting to OpenBB Workspace

### Option A — One-click via apps.json (recommended)

1. In Workspace, open the **Connections** panel and add `http://localhost:7769` as a backend
2. Open the apps panel — you'll see **"Streamlit Portfolio"**
3. Click it. The dashboard loads with:
   - A markdown intro note at the top
   - The Streamlit iframe (URL pre-set to `http://localhost:8501`)
   - The MCP server **auto-connected** (no manual URL entry)
4. Ask Copilot: *"rebalance my portfolio"* — the iframe refreshes after the destructive tool call

### Option B — Manual setup

If you want to add an iframe widget manually instead of using the prebuilt app:

1. In Workspace, add a built-in **Iframe** widget
2. Paste the Streamlit URL: `http://localhost:8501`
3. A grid icon with a count badge appears in the widget navbar — click it to see available sub-widgets
4. Click the **MCP** icon, paste `http://localhost:7769/mcp`, and connect

## Available Sub-Widgets

| Widget | Type | Description |
|--------|------|-------------|
| Portfolio Holdings | Table | Current positions with PnL |
| Sector Allocation | Table | Allocation breakdown by sector |
| Market Summary | Markdown | Weekly market analysis and outlook |

## MCP Tools

| Tool | Description | Refreshes iframe |
|------|-------------|:---:|
| `get_portfolio_holdings` | Positions with filters (sector, min shares, PnL %) | — |
| `get_sector_allocation` | Allocation breakdown by sector | — |
| `get_market_summary` | Weekly market analysis and outlook | — |
| `rebalance_portfolio` | Randomly rebalance and simulate market movement | ✓ |

### Auto-refresh on mutating tools

When an MCP tool is connected to an iframe widget, OpenBB Workspace can automatically remount the iframe after a tool call so the UI reflects new state. Mark mutating tools with `destructiveHint=True`:

```python
from mcp.types import ToolAnnotations

# Read-only tools — no annotation needed (default: no refresh)
@mcp.tool()
def get_portfolio_holdings(...): ...

# Mutating tools — opt in to iframe refresh
@mcp.tool(annotations=ToolAnnotations(destructiveHint=True))
def rebalance_portfolio(): ...
```

**Default is no refresh.** Only tools that explicitly set `destructiveHint=True` will trigger an iframe remount after they run. This avoids unwanted reloads during read-only operations.

## Parameters

The iframe widgets support Workspace toolbar parameters:

| Parameter | Type | Description |
|-----------|------|-------------|
| `sector` | Dropdown | Filter holdings by sector |
| `min_shares` | Number | Minimum shares to display |
| `show_pnl_pct` | Boolean | Toggle PnL % column |
| `as_of_date` | Date | Reference date for snapshot |

## Files

| File | Purpose |
|------|---------|
| `app.py` | Streamlit app with iframe widget bridge |
| `mcp_server.py` | Combined MCP server + Workspace backend (`/mcp`, `/widgets.json`, `/apps.json`, `/portfolio_note`) |
| `widgets.json` | Widget definitions consumed by Workspace |
| `apps.json` | Pre-built dashboard layout |
| `portfolio.py` | Shared portfolio data module |
| `pyproject.toml` | Project dependencies (uv) |
| `requirements.txt` | Project dependencies (pip) |

## How auto-config works

The iframe widget definition in `widgets.json` includes two fields read by OpenBB Workspace:

```json
"portfolio_iframe": {
  "type": "iframe",
  "endpoint": "http://localhost:8501",
  "storage": {
    "mcpUrl": "http://localhost:7769/mcp"
  },
  ...
}
```

- `endpoint` — initial iframe `src` (user can still edit it via the widget's URL dialog)
- `storage.mcpUrl` — MCP server to auto-connect when the widget mounts; tools become available immediately
