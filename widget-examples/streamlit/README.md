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

### 2. MCP server

In a separate terminal:

```bash
uv run python mcp_server.py            # default port 7769
uv run python mcp_server.py --port 7762 # custom port
```

This starts an MCP server on `http://localhost:<port>/mcp` (default `7769`) that exposes portfolio data as tools (`get_portfolio_holdings`, `get_sector_allocation`, `get_market_summary`, `rebalance_portfolio`).

## Connecting to OpenBB Workspace

### 1. Add the Iframe widget

1. In Workspace, add an **Iframe** widget
2. Paste the Streamlit URL: `http://localhost:8501` (adjust port if you used a different `--server.port`)
3. A grid icon with a count badge appears in the widget navbar — click it to see available sub-widgets
4. Click **Add** to export a sub-widget as a standalone table or note on your dashboard

### 2. Connect the MCP server to the Iframe widget

1. On the Iframe widget, click the **MCP** icon in the widget navbar
2. Enter the MCP server URL: `http://127.0.0.1:7769/mcp` (adjust port if you used a different `--port`)
3. The MCP tools (`get_portfolio_holdings`, `get_sector_allocation`, etc.) are now available to the Copilot when this widget is in context

## Available Sub-Widgets

| Widget | Type | Description |
|--------|------|-------------|
| Portfolio Holdings | Table | Current positions with PnL |
| Sector Allocation | Table | Allocation breakdown by sector |
| Market Summary | Markdown | Weekly market analysis and outlook |

## MCP Tools

| Tool | Description |
|------|-------------|
| `get_portfolio_holdings` | Positions with filters (sector, min shares, PnL %) |
| `get_sector_allocation` | Allocation breakdown by sector |
| `get_market_summary` | Weekly market analysis and outlook |
| `rebalance_portfolio` | Randomly rebalance and simulate market movement |

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
| `mcp_server.py` | MCP server exposing portfolio tools |
| `portfolio.py` | Shared portfolio data module |
| `pyproject.toml` | Project dependencies (uv) |
| `requirements.txt` | Project dependencies (pip) |
