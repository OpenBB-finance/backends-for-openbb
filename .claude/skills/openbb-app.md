---
name: openbb-app
description: Build custom backends and widgets for OpenBB Workspace
triggers:
  - openbb
  - openbb app
  - openbb widget
  - openbb backend
  - workspace widget
  - workspace backend
  - build widget
  - create widget
  - widgets.json
  - apps.json
---

# OpenBB App Development Skill

You are an expert OpenBB app developer. Your role is to help users quickly build custom backends and widgets for OpenBB Workspace. You have complete knowledge of all widget types, parameters, configurations, and JSON specifications embedded in this skill.

**Language Flexibility**: While this skill uses Python/FastAPI for examples (recommended for most users due to extensive examples in this repository), OpenBB backends can be built in **any language or framework** that can serve HTTP endpoints with JSON responses. The core requirements are language-agnostic.

## Additional Documentation

For the latest and most comprehensive documentation, fetch the LLM-optimized docs:

```
https://docs.openbb.co/workspace/llms-full.txt
```

Use WebFetch to query this URL when you need:
- Latest API changes or new features
- Detailed explanations not covered in this skill
- Clarification on specific widget behaviors
- Up-to-date configuration options

## Open Source Examples

For a curated list of open source OpenBB app examples to help users get started:

```
https://github.com/OpenBB-finance/awesome-openbb
```

## Core Requirements (Any Language)

Regardless of your chosen language/framework, your backend must:

1. **Serve HTTP endpoints** returning JSON responses
2. **Enable CORS** for these origins:
   - `https://pro.openbb.co`
   - `https://pro.openbb.dev`
   - `http://localhost:1420`
3. **Implement required endpoints**:
   - `GET /widgets.json` - Return array of widget configurations
   - `GET /apps.json` - (Optional) Return array of app/dashboard configurations
4. **Return proper Content-Type**: `application/json` for data endpoints

**Choosing a Language:**
- **Python/FastAPI** (Recommended) - Most examples available, quickest start
- **Node.js/Express, Go, Rust, etc.** - All work fine if you're comfortable with them

The examples below use Python/FastAPI as the reference implementation. The JSON structures and widget configurations are identical regardless of language.

## Repository Reference Examples

This repository contains working examples you can reference:

```
getting-started/
├── hello-world/              # Minimal starter template
└── reference-backend/        # Comprehensive reference with all widget types

widget-examples/
├── widget-types/             # Examples for each widget type
│   ├── chart_widget/         # Plotly charts
│   ├── table_widget/         # AgGrid tables
│   ├── markdown_widget/      # Markdown content
│   ├── metric_widget/        # KPI metrics
│   ├── news_widget/          # Newsfeed
│   ├── html_widget/          # Custom HTML
│   ├── pdf_widget/           # PDF viewer
│   ├── multi_file_viewer/    # Multiple file viewer
│   ├── omni_widget/          # Dynamic content type
│   ├── live_grid_widget/     # WebSocket real-time
│   └── advanced_charting/    # TradingView charts
├── parameters-types/         # Parameter examples
│   ├── parameters_example/   # All parameter types
│   ├── tabs_parameter/       # Tab navigation
│   ├── form_parameter/       # Form inputs
│   ├── grouping_widgets/     # Parameter grouping
│   └── column_and_cell_rendering/  # Render functions
├── ssrm_mode/               # Server-Side Row Model for large datasets
├── matching-widget-mcp-tool/ # MCP tool integration
└── database-connectors/      # Database integration examples
    ├── snowflake_connector_python/
    ├── supabase_python/
    ├── clickhouse_python/
    ├── elasticsearch_python/
    ├── arcticdb_python/
    └── mindsdb_python/
```

## Quick Start

When a user wants to build an OpenBB app:
1. Ask what language/framework they prefer (recommend Python/FastAPI if unsure)
2. Ask what data they want to display and what interactions they need
3. **Propose a layout for approval BEFORE writing any code** (see below)
4. Recommend appropriate widget types based on their use case
5. Generate a complete backend with all necessary endpoints
6. Create the apps.json configuration if they want a custom dashboard layout

## Propose Layout Before Implementation

**CRITICAL**: Before writing any code, present a visual layout proposal to the user for approval. This prevents wasted effort and ensures alignment on the dashboard structure.

### Layout Proposal Format

Use ASCII art with `|_` notation to represent widget positions in each tab:

```
### Tab 1: Overview
|‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾|
|  [Metric 1]  [Metric 2]  [Metric 3]  [Metric 4]  [Metric 5]                  |
|_______________________________________________________________________________|
|                                                                               |
|                         Main Chart (full width)                               |
|_______________________________________________________________________________|
|                                   |                                           |
|       Left Widget                 |           Right Widget                    |
|      (half width)                 |          (half width)                     |
|___________________________________|___________________________________________|

### Tab 2: Details
|‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾|
|                                                                               |
|                          Data Table (full width)                              |
|_______________________________________________________________________________|
```

### What to Include in the Proposal

1. **Global Parameters** - Shared dropdowns/inputs across widgets
   ```markdown
   ### Global Parameters (shared across widgets)
   | Parameter | Type | Description |
   |-----------|------|-------------|
   | `symbol` | dropdown | Stock ticker selection |
   | `start_date` | date picker | Analysis start date |
   ```

2. **Tab Structure** - Each tab with ASCII layout showing widget positions

3. **Widget Summary Table** - List all widgets with type and tab
   ```markdown
   | Widget | Type | Tab |
   |--------|------|-----|
   | `key_metrics` | metric | Overview |
   | `price_chart` | chart | Overview |
   | `data_table` | table | Details |
   ```

4. **Clarifying Questions** - Ask about:
   - Predefined options vs free-text inputs
   - Fixed defaults vs user-adjustable parameters
   - Scope (core features vs advanced features)
   - Data sources and API availability

### Example Proposal Flow

```markdown
## My App - Layout Proposal

### Predefined Options (dropdown)
| Option | Value 1 | Value 2 | Category |
|--------|---------|---------|----------|
| Option A | X | Y | Type 1 |
| Option B | Z | W | Type 2 |

### Fixed Defaults
- Window: 30 days
- Initial Value: $100,000

### Tab 1: Overview
[ASCII layout here]

### Tab 2: Analysis
[ASCII layout here]

### Widget Summary (8 total)
| Widget | Type | Tab |
|--------|------|-----|
...

### Questions for Discussion
1. Should X be predefined or free-text?
2. Should Y be user-adjustable or fixed?
3. Do you want feature Z included?
```

### Why This Matters

- **Prevents rework** - User approves structure before coding starts
- **Clarifies requirements** - Questions surface ambiguities early
- **Sets expectations** - User knows exactly what they'll get
- **Enables collaboration** - User can request changes before implementation

**Only proceed with implementation after receiving explicit approval** (e.g., "Yes, this layout works for you").

## Building Apps from Existing Websites

When recreating an existing website/dashboard as an OpenBB app:

1. **Explore the UI** - Understand what data is displayed and how it's organized
2. **Find data sources** - Look for:
   - API endpoints in browser Network tab
   - Parquet/CSV files being loaded
   - Schema files (e.g., `schema.json`)
   - GitHub repos for the original project
3. **Map UI components to widget types**:
   - KPI cards → `metric` widget
   - Time series charts → `chart` widget (Plotly) OR `table` with `chartView`
   - Data tables → `table` widget
   - Donut/pie charts → `chart` widget or `table` with `chartView` pie type
4. **Identify parameters** - Filters, dropdowns, date ranges in the original UI become widget params
5. **Design tab structure** - Group related widgets into logical tabs (Overview, Details, Analysis, etc.)

---

# BEST PRACTICES

## Widget Configuration Defaults

### runButton: false by default
**Do NOT set `runButton: true` unless the endpoint performs heavy computation** like Monte Carlo simulations, complex ML inference, or queries that take >5 seconds. Most data fetches should auto-run.

```python
# BAD - unnecessary runButton for simple data fetch
@register_widget({
    "name": "Stock Prices",
    "runButton": True  # Don't do this!
})

# GOOD - no runButton needed, data loads automatically
@register_widget({
    "name": "Stock Prices"
    # runButton defaults to false
})

# GOOD - runButton appropriate for heavy computation
@register_widget({
    "name": "Monte Carlo Simulation",
    "runButton": True  # Appropriate here - heavy computation
})
```

### Reasonable Widget Heights
Keep widget heights reasonable. Default recommendations:
- **Metrics**: h=4-6
- **Tables**: h=12-18 (not 20+)
- **Charts**: h=12-15 (not 20+)
- **Markdown**: h=6-10

```python
# BAD - too tall
"gridData": {"w": 40, "h": 25}

# GOOD - reasonable height
"gridData": {"w": 40, "h": 15}
```

### Widget params vs Endpoint parameters

**CRITICAL**: Defining a parameter in your FastAPI endpoint does NOT automatically create a UI dropdown. You must define `params` in BOTH places:

1. **Endpoint** - Handles the backend request
2. **Widget config `params`** - Creates the UI dropdown

```python
# BAD - endpoint has parameter but NO UI dropdown will appear!
@register_widget({
    "name": "Stock Data",
    "type": "table",
    "endpoint": "stock_data",
    # Missing params! No dropdown in UI
})
@app.get("/stock_data")
def stock_data(symbol: str = Query("AAPL")):  # This alone won't show UI
    return fetch_data(symbol)

# GOOD - both endpoint AND widget params defined
@register_widget({
    "name": "Stock Data",
    "type": "table",
    "endpoint": "stock_data",
    "params": [  # This creates the UI dropdown
        {
            "paramName": "symbol",
            "type": "endpoint",
            "label": "Symbol",
            "optionsEndpoint": "symbol_options",
            "value": "AAPL"
        }
    ],
})
@app.get("/stock_data")
def stock_data(symbol: str = Query("AAPL")):
    return fetch_data(symbol)
```

**Common symptom**: Backend works perfectly when testing with curl/browser, but the OpenBB Workspace widget shows no dropdown controls.

**Tip for multiple widgets sharing the same parameter**: Define a common param dict and reuse it:

```python
# Define once
SYMBOL_PARAM = {
    "paramName": "symbol",
    "type": "endpoint",
    "label": "Symbol",
    "optionsEndpoint": "symbol_options",
    "value": "AAPL"
}

# Reuse across widgets
@register_widget({
    "name": "Price Chart",
    "params": [SYMBOL_PARAM],
    ...
})

@register_widget({
    "name": "Company Info",
    "params": [SYMBOL_PARAM],
    ...
})
```

## Charts: Prefer AgGrid Charts Over Plotly

**When displaying chart data, prefer using a table widget with chart view enabled.** This allows users to:
- Access the underlying raw data directly from the workspace
- Switch between table and chart views
- Use AgGrid's built-in chart types

```python
# PREFERRED - Table with chart view (user can access raw data)
@register_widget({
    "name": "Price History",
    "type": "table",
    "endpoint": "price_history",
    "gridData": {"w": 20, "h": 15},
    "data": {
        "table": {"enableCharts": True},
        "chartView": {
            "enabled": True,  # Start in chart view
            "chartType": "line"
        },
        "columnsDefs": [
            {"field": "date", "headerName": "Date", "chartDataType": "time"},
            {"field": "price", "headerName": "Price", "chartDataType": "series"}
        ]
    }
})
@app.get("/price_history")
def price_history():
    return [
        {"date": "2024-01-01", "price": 150},
        {"date": "2024-01-02", "price": 152}
    ]
```

### When to Use Plotly Charts
Use Plotly (`type: "chart"`) only when you need:
- Complex multi-axis charts
- Specialized chart types not in AgGrid (waterfall, sankey, etc.)
- Heavy customization of chart appearance

When using Plotly:
1. **Don't add a title** - the widget name already displays as the title
2. **Always add `raw: True`** in widget config for AI data access
3. **Support the `raw` query parameter** to return raw data

```python
# Plotly chart with raw support
@register_widget({
    "name": "Custom Chart",
    "type": "chart",
    "endpoint": "custom_chart",
    "gridData": {"w": 20, "h": 15},
    "raw": True  # REQUIRED - enables raw data access
})
@app.get("/custom_chart")
def custom_chart(theme: str = "dark", raw: bool = False):
    data = [{"date": "2024-01-01", "value": 100}]

    # Return raw data if requested
    if raw:
        return data

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[d["date"] for d in data], y=[d["value"] for d in data]))

    # NO TITLE - widget name is the title
    fig.update_layout(
        # title="..." # DON'T ADD TITLE
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=50, r=20, t=20, b=50)  # Small top margin since no title
    )

    return json.loads(fig.to_json())
```

## widgets.json Format

**CRITICAL**: widgets.json must be an **object** with widget IDs as keys, NOT an array.

```json
// CORRECT - object format
{
    "stock_prices": {
        "name": "Stock Prices",
        "type": "table",
        "endpoint": "stock_prices"
    }
}

// WRONG - array format (OpenBB will reject this)
[
    {
        "name": "Stock Prices",
        "type": "table",
        "endpoint": "stock_prices"
    }
]
```

---

# BACKEND ARCHITECTURE (Python/FastAPI Reference)

## Core Structure

```python
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from functools import wraps
from pathlib import Path
import asyncio
import json
import base64

app = FastAPI()

# CORS - Required for OpenBB Workspace
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://pro.openbb.co",
        "https://pro.openbb.dev",
        "http://localhost:1420"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Widget registry
WIDGETS = {}

def register_widget(widget_config):
    """Decorator to register widget configuration and link it to the endpoint."""
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
            WIDGETS[widget_config["widgetId"]] = widget_config

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

# Required endpoints
@app.get("/")
def root():
    return {"message": "OpenBB Custom Backend"}

@app.get("/widgets.json")
def get_widgets():
    return WIDGETS  # Return as dict with widget IDs as keys

@app.get("/apps.json")
def get_apps():
    # Return your apps.json configuration here
    return []
```

## Running the Backend

```bash
pip install fastapi uvicorn plotly pandas requests
uvicorn main:app --reload --host 0.0.0.0 --port 7779
```

### Dependency Installation Requires Server Restart

The `--reload` flag only watches for code changes, NOT new package installations. When adding new dependencies while the server is running:

```bash
# Install new dependency
pip install pyarrow

# --reload does NOT detect new packages!
# You must restart the server:
lsof -ti:7779 | xargs kill -9
uvicorn main:app --reload --port 7779
```

**Common symptom**: ImportError or "unable to find engine" errors even after pip install succeeds.

---

# WIDGET TYPES

## 1. Table Widget (type: "table")

Display tabular data with sorting, filtering, and chart conversion.

```python
@register_widget({
    "name": "Stock Data",
    "description": "Display stock information",
    "type": "table",
    "endpoint": "stock_data",
    "category": "Stocks",
    "subCategory": "Overview",
    "gridData": {"w": 20, "h": 8},
    "data": {
        "table": {
            "enableCharts": True,  # Allow chart visualization
            "showAll": True
        },
        "columnsDefs": [
            {
                "field": "symbol",
                "headerName": "Symbol",
                "cellDataType": "text",
                "pinned": "left"
            },
            {
                "field": "price",
                "headerName": "Price",
                "cellDataType": "number",
                "formatterFn": "int"
            },
            {
                "field": "change",
                "headerName": "Change %",
                "cellDataType": "number",
                "renderFn": "greenRed"
            }
        ]
    }
})
@app.get("/stock_data")
def stock_data():
    return [
        {"symbol": "AAPL", "price": 150.25, "change": 2.5},
        {"symbol": "GOOGL", "price": 140.50, "change": -1.2},
        {"symbol": "MSFT", "price": 380.00, "change": 0.8},
    ]
```

### Column Definition Properties

| Property | Type | Description |
|----------|------|-------------|
| `field` | string | JSON data field name |
| `headerName` | string | Column header display name |
| `cellDataType` | string | `text`, `number`, `boolean`, `date`, `dateString`, `object` |
| `chartDataType` | string | `category`, `series`, `time`, `excluded` |
| `formatterFn` | string | `int`, `none`, `percent`, `normalized`, `normalizedPercent`, `dateToYear` |
| `renderFn` | string/array | `greenRed`, `titleCase`, `hoverCard`, `cellOnClick`, `columnColor`, `showCellChange` |
| `pinned` | string | `left` or `right` |
| `hide` | boolean | Hide column from display |
| `width` | number | Column width in pixels |
| `align` | string | `left`, `center`, `right` |

### Render Functions

**greenRed** - Color based on positive/negative values:
```python
"renderFn": "greenRed"
```

**columnColor** - Conditional coloring with rules:
```python
"renderFn": "columnColor",
"renderFnParams": {
    "colorRules": [
        {"condition": "gt", "value": 0, "color": "#00AA44", "fill": True},
        {"condition": "lt", "value": 0, "color": "#CC0000", "fill": True}
    ]
}
```

**hoverCard** - Show markdown on hover:
```python
"renderFn": "hoverCard",
"renderFnParams": {
    "hoverCard": {
        "markdown": "**{symbol}**\nPrice: ${price}\nChange: {change}%"
    }
}
```

**cellOnClick** - Action on click:
```python
"renderFn": "cellOnClick",
"renderFnParams": {
    "actionType": "groupBy",
    "groupBy": {
        "paramName": "symbol"
    }
}
```

### Sparklines in Tables

```python
"columnsDefs": [
    {
        "field": "trend",
        "headerName": "7D Trend",
        "sparkline": {
            "type": "line",  # line, area, bar
            "dataField": "trend_data",
            "options": {
                "stroke": "#3b82f6",
                "fill": "rgba(34, 197, 94, 0.3)",
                "markers": {"enabled": True, "size": 2},
                "pointsOfInterest": {
                    "maximum": {"fill": "#ffd700", "size": 6},
                    "minimum": {"fill": "#ef4444", "size": 6}
                }
            }
        }
    }
]
```

### Chart View for Tables

```python
"data": {
    "table": {"enableCharts": True},
    "chartView": {
        "enabled": True,  # Set chart as default view
        "chartType": "line",
        "cellRangeCols": ["date", "price", "volume"]
    }
}
```

**Supported Chart Types**: column, groupedColumn, stackedColumn, bar, groupedBar, stackedBar, line, scatter, bubble, pie, donut, area, histogram, radarLine, boxPlot, sunburst, heatmap, waterfall, treemap, rangeBar

### Complete Table with Chart View Example

```python
@register_widget({
    "name": "Top Wells by Oil",
    "type": "table",
    "endpoint": "top_wells",
    "gridData": {"w": 20, "h": 14},
    "data": {
        "table": {"enableCharts": True},
        "chartView": {
            "enabled": True,      # Start in chart view (user can toggle to table)
            "chartType": "bar",   # bar, line, pie, donut, etc.
        },
        "columnsDefs": [
            {"field": "name", "headerName": "Name", "chartDataType": "category"},
            {"field": "oil_volume", "headerName": "Oil (sm³)", "cellDataType": "number", "formatterFn": "int", "chartDataType": "series"},
            {"field": "water_volume", "headerName": "Water (sm³)", "cellDataType": "number", "formatterFn": "int", "chartDataType": "series"},
            {"field": "notes", "headerName": "Notes", "chartDataType": "excluded"},  # Won't appear in chart
        ],
    },
})
@app.get("/top_wells")
def top_wells():
    return [
        {"name": "Well A", "oil_volume": 45800, "water_volume": 68300, "notes": "Primary producer"},
        {"name": "Well B", "oil_volume": 32100, "water_volume": 41200, "notes": "Secondary"},
    ]
```

**chartDataType values**:
- `category` - X-axis labels (usually first column)
- `series` - Y-axis values (plotted data)
- `time` - Time-based X-axis (for time series)
- `excluded` - Column visible in table but NOT in chart

---

## 2. Chart Widget (type: "chart")

Interactive Plotly charts with theme support.

```python
import plotly.graph_objects as go

@register_widget({
    "name": "Price Chart",
    "description": "Stock price over time",
    "type": "chart",
    "endpoint": "price_chart",
    "gridData": {"w": 40, "h": 15},
    "raw": True  # Enable raw data toggle for AI
})
@app.get("/price_chart")
def price_chart(theme: str = "dark", raw: bool = False):
    dates = ["2024-01-01", "2024-01-02", "2024-01-03"]
    prices = [150, 152, 148]

    if raw:
        return [{"date": d, "price": p} for d, p in zip(dates, prices)]

    colors = get_theme_colors(theme)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates,
        y=prices,
        mode='lines',
        name='Price',
        line=dict(color=colors["main_line"])
    ))

    fig.update_layout(
        paper_bgcolor=colors["background"],
        plot_bgcolor=colors["background"],
        font=dict(color=colors["text"]),
        xaxis=dict(showgrid=False, color=colors["text"]),
        yaxis=dict(showgrid=True, gridcolor=colors["grid"], color=colors["text"]),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        hovermode="x unified"
    )

    return json.loads(fig.to_json())

def get_theme_colors(theme="dark"):
    if theme == "light":
        return {
            "text": "#333333",
            "grid": "rgba(128, 128, 128, 0.2)",
            "background": "rgba(255,255,255,0)",
            "main_line": "#2E5090",
            "positive": "#00AA44",
            "negative": "#CC0000"
        }
    return {
        "text": "#ffffff",
        "grid": "rgba(128, 128, 128, 0.2)",
        "background": "rgba(0,0,0,0)",
        "main_line": "#FF8000",
        "positive": "#00B140",
        "negative": "#F4284D"
    }
```

### Toolbar Configuration

```python
figure_json = json.loads(fig.to_json())
figure_json['config'] = {
    "displayModeBar": True,
    "responsive": True,
    "scrollZoom": True,
    "modeBarButtonsToRemove": [
        "lasso2d", "select2d", "autoScale2d",
        "toggleSpikelines", "hoverClosestCartesian"
    ],
    "doubleClick": "reset+autosize"
}
return figure_json
```

---

## 3. Markdown Widget (type: "markdown")

Display formatted text content.

```python
@register_widget({
    "name": "Market Summary",
    "description": "Daily market overview",
    "type": "markdown",
    "endpoint": "market_summary",
    "gridData": {"w": 12, "h": 6}
})
@app.get("/market_summary")
def market_summary():
    return """# Market Summary

**Status:** Open

## Key Indices
- S&P 500: +1.2%
- NASDAQ: +0.8%
- DOW: +0.5%

## Headlines
> Fed signals potential rate pause in upcoming meeting
"""
```

### Markdown with Images

```python
@app.get("/markdown_with_image")
def markdown_with_image():
    # Local image (base64)
    with open("chart.png", "rb") as f:
        img_base64 = base64.b64encode(f.read()).decode('utf-8')

    return f"""# Analysis Report

![Chart](data:image/png;base64,{img_base64})

The chart above shows...
"""
```

---

## 4. Metric Widget (type: "metric")

Display KPIs with labels, values, and deltas.

```python
@register_widget({
    "name": "Portfolio Metrics",
    "description": "Key portfolio statistics",
    "type": "metric",
    "endpoint": "portfolio_metrics",
    "gridData": {"w": 20, "h": 4}
})
@app.get("/portfolio_metrics")
def portfolio_metrics():
    return JSONResponse(content=[
        {"label": "Total Value", "value": "$1,234,567", "delta": "+5.2%"},
        {"label": "Daily P&L", "value": "$15,432", "delta": "-2.1%"},
        {"label": "Positions", "value": "24", "delta": "+3"}
    ])
```

---

## 5. Newsfeed Widget (type: "newsfeed")

Display articles with title, date, author, excerpt, and body.

```python
@register_widget({
    "name": "Market News",
    "description": "Latest financial news",
    "type": "newsfeed",
    "endpoint": "market_news",
    "gridData": {"w": 20, "h": 15},
    "params": [
        {
            "paramName": "category",
            "type": "text",
            "label": "Category",
            "value": "all",
            "options": [
                {"label": "All", "value": "all"},
                {"label": "Stocks", "value": "stocks"},
                {"label": "Crypto", "value": "crypto"}
            ]
        }
    ]
})
@app.get("/market_news")
def market_news(category: str = "all", limit: int = 10):
    return [
        {
            "title": "Fed Announces Rate Decision",
            "date": "2024-01-15T10:30:00Z",
            "author": "Reuters",
            "excerpt": "The Federal Reserve announced today that it will...",
            "body": """# Fed Rate Decision

The Federal Reserve announced today that it will maintain current interest rates...

## Key Points
- Rates unchanged at 5.25-5.50%
- Inflation trending toward target
- Labor market remains strong
"""
        }
    ]
```

---

## 6. HTML Widget (type: "html")

Custom HTML content (no JavaScript execution for security).

```python
@register_widget({
    "name": "Custom Dashboard",
    "description": "HTML-based visualization",
    "type": "html",
    "endpoint": "custom_html",
    "gridData": {"w": 40, "h": 20}
})
@app.get("/custom_html", response_class=HTMLResponse)
def custom_html():
    return HTMLResponse(content="""
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial; padding: 20px; background: transparent; color: white; }
        .card { background: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px; margin: 10px 0; }
        .value { font-size: 24px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="card">
        <div>Portfolio Value</div>
        <div class="value">$1,234,567</div>
    </div>
</body>
</html>
""")
```

---

## 7. PDF/File Viewer Widget (type: "pdf" / "multi_file_viewer")

Display PDF files via base64 or URL.

```python
@register_widget({
    "name": "Report Viewer",
    "description": "View PDF reports",
    "type": "pdf",
    "endpoint": "report_pdf",
    "gridData": {"w": 30, "h": 20}
})
@app.get("/report_pdf")
def report_pdf():
    # Base64 method
    with open("report.pdf", "rb") as f:
        content = base64.b64encode(f.read()).decode("utf-8")

    return JSONResponse(content={
        "data_format": {"data_type": "pdf", "filename": "report.pdf"},
        "content": content
    })

# URL method
@app.get("/report_pdf_url")
def report_pdf_url():
    return JSONResponse(content={
        "data_format": {"data_type": "pdf", "filename": "report.pdf"},
        "url": "https://example.com/reports/annual-2024.pdf"
    })
```

### Multi-File Viewer

```python
from pydantic import BaseModel
from typing import List

class FileOption(BaseModel):
    label: str
    value: str

@register_widget({
    "name": "Document Library",
    "type": "multi_file_viewer",
    "endpoint": "/documents",
    "params": [{
        "paramName": "doc_name",
        "type": "endpoint",
        "optionsEndpoint": "/document_options",
        "multiSelect": True,
        "roles": ["fileSelector"]
    }]
})
@app.get("/document_options")
def document_options():
    return [
        {"label": "Q1 Report", "value": "q1_report.pdf"},
        {"label": "Q2 Report", "value": "q2_report.pdf"}
    ]

@app.post("/documents")
async def get_documents(doc_name: List[str] = Body(...)):
    files = []
    for name in doc_name:
        with open(f"docs/{name}", "rb") as f:
            files.append({
                "data_format": {"data_type": "pdf", "filename": name},
                "content": base64.b64encode(f.read()).decode("utf-8")
            })
    return JSONResponse(content=files)
```

---

## 8. TradingView Chart (type: "advanced_charting")

Professional charting with UDF protocol.

```python
@register_widget({
    "name": "Advanced Chart",
    "type": "advanced_charting",
    "endpoint": "/udf",
    "data": {"defaultSymbol": "AAPL", "updateFrequency": 60000}
})

@app.get("/udf/config")
def udf_config():
    return {
        "supported_resolutions": ["1", "5", "15", "30", "60", "D", "W", "M"],
        "supports_search": True,
        "supports_group_request": False,
        "supports_marks": False,
        "supports_timescale_marks": False,
        "exchanges": [{"value": "", "name": "All Exchanges", "desc": ""}],
        "symbols_types": [{"name": "All types", "value": ""}]
    }

@app.get("/udf/search")
def udf_search(query: str, limit: int = 30):
    # Return matching symbols
    return [
        {"symbol": "AAPL", "full_name": "AAPL", "description": "Apple Inc.",
         "exchange": "NASDAQ", "type": "stock"}
    ]

@app.get("/udf/symbols")
def udf_symbols(symbol: str):
    return {
        "name": symbol,
        "ticker": symbol,
        "description": f"{symbol} Stock",
        "type": "stock",
        "session": "0930-1600",
        "timezone": "America/New_York",
        "exchange": "NASDAQ",
        "minmov": 1,
        "pricescale": 100,
        "has_intraday": True,
        "supported_resolutions": ["1", "5", "15", "30", "60", "D", "W", "M"]
    }

@app.get("/udf/history")
def udf_history(symbol: str, resolution: str, from_time: int, to_time: int):
    # Return OHLCV data
    return {
        "s": "ok",
        "t": [1704067200, 1704153600],  # timestamps
        "o": [150.0, 151.5],  # opens
        "h": [152.0, 153.0],  # highs
        "l": [149.0, 150.5],  # lows
        "c": [151.5, 152.5],  # closes
        "v": [1000000, 1200000]  # volumes
    }

@app.get("/udf/time")
def udf_time():
    import time
    return int(time.time())
```

---

## 9. Highcharts Widget (type: "chart-highcharts")

Alternative charting library.

```python
from highcharts_core.chart import Chart
from highcharts_core.options import HighchartsOptions

@register_widget({
    "name": "Highcharts Demo",
    "type": "chart-highcharts",
    "endpoint": "highcharts_demo",
    "gridData": {"w": 20, "h": 10}
})
@app.get("/highcharts_demo")
def highcharts_demo(theme: str = "dark"):
    text_color = "#ffffff" if theme == "dark" else "#000000"

    options = {
        "chart": {"type": "column", "backgroundColor": "transparent"},
        "title": {"text": "Monthly Sales", "style": {"color": text_color}},
        "xAxis": {"categories": ["Jan", "Feb", "Mar"], "labels": {"style": {"color": text_color}}},
        "yAxis": {"title": {"text": "Sales ($)", "style": {"color": text_color}}},
        "series": [{"name": "2024", "data": [100, 150, 120]}]
    }

    chart = Chart.from_options(HighchartsOptions.from_dict(options))
    return chart.to_dict()
```

---

## 10. Live Grid Widget (WebSocket)

Real-time data updates via WebSocket.

```python
from fastapi import WebSocket
import asyncio

@register_widget({
    "name": "Live Prices",
    "type": "table",
    "endpoint": "live_prices",
    "wsEndpoint": "/ws",
    "gridData": {"w": 20, "h": 10},
    "data": {
        "wsRowIdColumn": "symbol",  # Match updates by this field
        "columnsDefs": [
            {"field": "symbol", "headerName": "Symbol"},
            {"field": "price", "headerName": "Price", "renderFn": "showCellChange"},
            {"field": "change", "headerName": "Change", "renderFn": ["showCellChange", "greenRed"]}
        ]
    }
})
@app.get("/live_prices")
def live_prices():
    return [
        {"symbol": "AAPL", "price": 150.25, "change": 2.5},
        {"symbol": "GOOGL", "price": 140.50, "change": -1.2}
    ]

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    subscriptions = set()

    async def send_updates():
        while True:
            for symbol in subscriptions:
                # Send price update
                await websocket.send_json({
                    "symbol": symbol,
                    "price": 150 + random.random() * 5,
                    "change": random.uniform(-2, 2)
                })
            await asyncio.sleep(1)

    update_task = asyncio.create_task(send_updates())

    try:
        while True:
            data = await websocket.receive_json()
            if data.get("action") == "subscribe":
                subscriptions.add(data["symbol"])
            elif data.get("action") == "unsubscribe":
                subscriptions.discard(data["symbol"])
    finally:
        update_task.cancel()
```

---

## 11. Omni Widget (type: "omni")

Dynamic content type based on response. Uses POST method.

```python
from pydantic import BaseModel, Field
from typing import Any, List, Optional

class DataFormat(BaseModel):
    data_type: str  # "object"
    parse_as: str   # "text", "table", "chart"

class OmniWidgetResponse(BaseModel):
    content: Any
    data_format: DataFormat
    extra_citations: Optional[List] = Field(default_factory=list)
    citable: bool = Field(default=True)

@register_widget({
    "name": "AI Response",
    "description": "Dynamic AI-generated content",
    "type": "omni",
    "endpoint": "ai_response",
    "params": [
        {"paramName": "prompt", "type": "text", "label": "Ask a question", "value": ""}
    ]
})
@app.post("/ai_response")
async def ai_response(data: dict = Body(...)):
    prompt = data.get("prompt", "")

    # Return text
    return {
        "content": f"# Response\n\nYou asked: {prompt}\n\nHere's the analysis...",
        "data_format": {"data_type": "object", "parse_as": "text"},
        "citable": True
    }

    # Or return table
    # return {
    #     "content": [{"col1": "val1", "col2": "val2"}],
    #     "data_format": {"data_type": "object", "parse_as": "table"},
    #     "citable": True
    # }

    # Or return chart (Plotly JSON)
    # return {
    #     "content": json.loads(fig.to_json()),
    #     "data_format": {"data_type": "object", "parse_as": "chart"},
    #     "citable": True
    # }
```

---

# ADDITIONAL WIDGET TYPES

## 12. SSRM Table (Server-Side Row Model)

For large datasets (200,000+ rows) with server-side sorting, filtering, pagination, and grouping.

```python
# widgets.json configuration
{
    "name": "Large Dataset Table",
    "description": "Server-side data processing for large datasets",
    "type": "ssrm_table",  # Special type for SSRM
    "endpoint": "data-ssrm",
    "category": "Data",
    "gridData": {"w": 24, "h": 16}
}
```

### SSRM Endpoint Implementation

```python
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class SSRMRequest(BaseModel):
    startRow: int
    endRow: int
    sortModel: List[Dict[str, str]] = []
    filterModel: Dict[str, Any] = {}
    rowGroupCols: List[Dict[str, str]] = []
    groupKeys: List[str] = []

@app.post("/data-ssrm")
async def get_ssrm_data(request: SSRMRequest):
    # Build query with sorting
    query = "SELECT * FROM your_table"

    # Apply filters
    if request.filterModel:
        conditions = []
        for field, filter_config in request.filterModel.items():
            filter_type = filter_config.get("filterType")
            if filter_type == "text":
                conditions.append(f"{field} LIKE '%{filter_config['filter']}%'")
            elif filter_type == "number":
                conditions.append(f"{field} {filter_config['type']} {filter_config['filter']}")
        if conditions:
            query += " WHERE " + " AND ".join(conditions)

    # Apply sorting
    if request.sortModel:
        order_clauses = [f"{s['colId']} {s['sort'].upper()}" for s in request.sortModel]
        query += " ORDER BY " + ", ".join(order_clauses)

    # Apply pagination
    query += f" LIMIT {request.endRow - request.startRow} OFFSET {request.startRow}"

    # Execute query and get results
    rows = execute_query(query)
    total_count = get_total_count()

    return {
        "rowData": rows,
        "rowCount": total_count
    }
```

### Database Manager Pattern

```python
# For SQLite
from helpers import create_database_manager

db_manager = create_database_manager(
    database_type="sqlite",
    file_path=Path(__file__).parent / "data.db",
    table_name="your_table"
)

# For MySQL
db_manager = create_database_manager(
    database_type="mysql",
    connection_config={
        "host": "localhost",
        "database": "your_db",
        "user": "username",
        "password": "password",
        "port": 3306
    },
    table_name="your_table"
)

# For Snowflake
db_manager = create_database_manager(
    database_type="snowflake",
    connection_config={
        "account": "your_account",
        "user": "username",
        "password": "password",
        "warehouse": "COMPUTE_WH",
        "database": "your_db",
        "schema": "PUBLIC"
    },
    table_name="your_table"
)
```

---

## MCP Tool Matching

Link widgets to MCP tools so Copilot can cite widgets when using MCP tools.

```python
@register_widget({
    "name": "Company Revenue Dashboard",
    "description": "Revenue metrics with ticker selection",
    "type": "table",
    "endpoint": "revenue_data",
    "mcp_tool": {
        "mcp_server": "Financial Data",  # Must match MCP server name exactly
        "tool_id": "get_company_revenue_data"  # Must match MCP tool name exactly
    },
    "params": [
        {"paramName": "ticker", "type": "text", "value": "AAPL"}
    ]
})
@app.get("/revenue_data")
def revenue_data(ticker: str = "AAPL"):
    return [{"ticker": ticker, "revenue": 1000000}]
```

When the Copilot uses the matching MCP tool, it will:
1. Show a toast notification that a matching widget was found
2. Add a citation with `*` in the response
3. Allow users to add the widget to their dashboard

---

## Database Connectors

The repository includes examples for connecting to various databases:

### Supported Databases
- **SQLite** - Local development and small datasets
- **MySQL** - Production environments
- **Snowflake** - Enterprise analytics
- **ClickHouse** - High-performance analytics
- **Elasticsearch** - Search and logging
- **Supabase** - PostgreSQL with REST API
- **ArcticDB** - Time-series data
- **MindsDB** - AI/ML predictions

### Example: Snowflake Connection

```python
import snowflake.connector

def get_snowflake_connection():
    return snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA")
    )

@app.get("/snowflake_data")
def snowflake_data():
    conn = get_snowflake_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM your_table LIMIT 100")
    columns = [desc[0] for desc in cursor.description]
    rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return rows
```

### Example: Supabase Connection

```python
from supabase import create_client

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

@app.get("/supabase_data")
def supabase_data():
    response = supabase.table("your_table").select("*").limit(100).execute()
    return response.data
```

---

# WIDGET PARAMETERS

## Text Input

```python
"params": [
    {
        "paramName": "ticker",
        "type": "text",
        "label": "Ticker Symbol",
        "description": "Enter stock ticker",
        "value": "AAPL"
    }
]

# Multiple values (comma-separated)
"params": [
    {
        "paramName": "tickers",
        "type": "text",
        "label": "Tickers",
        "value": "AAPL,GOOGL,MSFT",
        "multiple": True
    }
]
```

## Number Input

```python
"params": [
    {
        "paramName": "limit",
        "type": "number",
        "label": "Number of Results",
        "description": "How many results to show",
        "value": 10
    }
]
```

## Boolean Toggle

```python
"params": [
    {
        "paramName": "include_extended",
        "type": "boolean",
        "label": "Include Extended Hours",
        "description": "Include pre/post market data",
        "value": False
    }
]
```

## Date Picker

```python
"params": [
    {
        "paramName": "start_date",
        "type": "date",
        "label": "Start Date",
        "description": "Select start date",
        "value": "$currentDate-1y"  # Dynamic: 1 year ago
    }
]
```

**Date Modifiers**: `$currentDate`, `$currentDate-1d`, `$currentDate-1w`, `$currentDate-1M`, `$currentDate-1y`

## Static Dropdown

```python
"params": [
    {
        "paramName": "interval",
        "type": "text",
        "label": "Interval",
        "value": "1d",
        "options": [
            {"label": "1 Minute", "value": "1m"},
            {"label": "5 Minutes", "value": "5m"},
            {"label": "1 Hour", "value": "1h"},
            {"label": "1 Day", "value": "1d"}
        ]
    }
]

# With extra info
"options": [
    {
        "label": "Apple Inc.",
        "value": "AAPL",
        "extraInfo": {
            "description": "Technology",
            "rightOfDescription": "NASDAQ"
        }
    }
]
```

## Dynamic Dropdown (from endpoint)

```python
"params": [
    {
        "paramName": "symbol",
        "type": "endpoint",
        "label": "Select Stock",
        "optionsEndpoint": "/stock_options",
        "multiSelect": False,
        "style": {"popupWidth": 450}
    }
]

@app.get("/stock_options")
def stock_options():
    return [
        {"label": "Apple Inc.", "value": "AAPL"},
        {"label": "Google", "value": "GOOGL"},
        {"label": "Microsoft", "value": "MSFT"}
    ]
```

### Handling multiSelect Parameter Values

When `multiSelect: True`, selected values arrive as a **comma-separated string**:

```python
# Widget config
"params": [
    {
        "paramName": "wells",
        "type": "endpoint",
        "optionsEndpoint": "/well_options",
        "multiSelect": True,  # User can select multiple
        "value": ""
    }
]

# Endpoint handling
@app.get("/data")
def get_data(wells: str = Query("")):
    if wells:
        # Split comma-separated values
        well_list = [w.strip() for w in wells.split(",") if w.strip()]

        # For numeric IDs
        well_ids = [int(w) for w in wells.split(",") if w]
        df = df[df["well_id"].isin(well_ids)]

    return data
```

## Dependent Dropdown

Second dropdown filtered by first dropdown's selection.

```python
"params": [
    {
        "paramName": "country",
        "type": "endpoint",
        "label": "Country",
        "optionsEndpoint": "/countries"
    },
    {
        "paramName": "city",
        "type": "endpoint",
        "label": "City",
        "optionsEndpoint": "/cities",
        "optionsParams": {"country": "$country"}  # Pass country value
    }
]

@app.get("/countries")
def countries():
    return [{"label": "USA", "value": "usa"}, {"label": "UK", "value": "uk"}]

@app.get("/cities")
def cities(country: str = "usa"):
    cities_data = {
        "usa": [{"label": "New York", "value": "nyc"}, {"label": "Los Angeles", "value": "la"}],
        "uk": [{"label": "London", "value": "lon"}, {"label": "Manchester", "value": "man"}]
    }
    return cities_data.get(country, [])
```

## Input Form (POST submission)

```python
"params": [
    {
        "paramName": "form",
        "type": "form",
        "endpoint": "/submit_order",
        "inputParams": [
            {"paramName": "symbol", "type": "text", "label": "Symbol"},
            {"paramName": "quantity", "type": "number", "label": "Quantity"},
            {"paramName": "order_type", "type": "text", "label": "Type",
             "options": [{"label": "Buy", "value": "buy"}, {"label": "Sell", "value": "sell"}]},
            {"paramName": "submit", "type": "button", "label": "Submit Order"}
        ]
    }
]

@app.post("/submit_order")
async def submit_order(data: dict = Body(...)):
    if not data.get("symbol"):
        return JSONResponse(status_code=400, content={"error": "Symbol required"})
    # Process order...
    return JSONResponse(status_code=200, content={"success": True})
```

## Tabs Parameter

Display tabbed interface for switching between data views.

```python
"params": [
    {
        "paramName": "category",
        "type": "tabs",  # Special type for tab navigation
        "value": "liquidity",
        "label": "Ratio Category",
        "description": "Select the financial ratio category",
        "options": [
            {"label": "Liquidity", "value": "liquidity"},
            {"label": "Efficiency", "value": "efficiency"},
            {"label": "Profitability", "value": "profitability"},
            {"label": "Leverage", "value": "leverage"}
        ]
    }
]
```

### Dynamic Columns per Tab

Columns can change based on selected tab (don't define columnsDefs):

```python
@app.get("/financial_ratios")
def financial_ratios(category: str = "liquidity"):
    if category == "liquidity":
        return [
            {"symbol": "AAPL", "current_ratio": 1.5, "quick_ratio": 1.2, "cash_ratio": 0.8}
        ]
    elif category == "profitability":
        return [
            {"symbol": "AAPL", "gross_margin": 45.2, "net_margin": 25.1, "roe": 150.3}
        ]
    # Different columns per tab
```

### Static Columns with Tabs

Same columns for all tabs (define columnsDefs):

```python
"data": {
    "table": {
        "columnsDefs": [
            {"field": "symbol", "headerName": "Symbol"},
            {"field": "metric_1", "headerName": "Metric 1"},
            {"field": "metric_2", "headerName": "Metric 2"}
        ]
    }
}
```

### Combining Tabs with Other Parameters

```python
"params": [
    {
        "paramName": "period",
        "type": "text",
        "value": "annual",
        "options": [{"label": "Annual", "value": "annual"}, {"label": "Quarterly", "value": "quarterly"}]
    },
    {
        "paramName": "category",
        "type": "tabs",
        "value": "liquidity",
        "options": [
            {"label": "Liquidity", "value": "liquidity"},
            {"label": "Profitability", "value": "profitability"}
        ]
    }
]
```

---

## Parameter Positioning (Multiple Rows)

```python
# Single row (default)
"params": [param1, param2, param3]

# Multiple rows using nested arrays
"params": [
    [{"paramName": "toggle", "type": "boolean", "value": True}],
    [{"paramName": "date", "type": "date"}, {"paramName": "interval", "type": "text"}],
    [{"paramName": "notes", "type": "text"}]
]
```

## Parameter Grouping

Widgets share parameters when they have identical `paramName` and `options`:

```python
# Widget 1
@register_widget({
    "name": "Price Chart",
    "params": [{"paramName": "symbol", "type": "endpoint", "optionsEndpoint": "/symbols"}]
})

# Widget 2 - automatically synced with Widget 1
@register_widget({
    "name": "Company Info",
    "params": [{"paramName": "symbol", "type": "endpoint", "optionsEndpoint": "/symbols"}]
})
```

---

# WIDGET CONFIGURATION

## Grid Size

```python
"gridData": {
    "w": 20,      # Width (10-40 units, default 12)
    "h": 10,      # Height (4-100 units)
    "minW": 10,   # Minimum width
    "minH": 4,    # Minimum height
    "maxW": 40,   # Maximum width
    "maxH": 50    # Maximum height
}
```

## Auto-Refresh (refetchInterval)

```python
"refetchInterval": 60000  # Milliseconds (60 seconds)
# Minimum: 1000ms, Default: 900000ms (15 minutes)
# Set to false to disable
```

## Stale Time

```python
"staleTime": 300000  # 5 minutes - button turns orange when exceeded
# Default: 300000ms (5 minutes)
```

## Run Button (Manual Refresh)

```python
"runButton": True  # Show run button instead of auto-refresh
```

## Category & Subcategory

```python
"category": "Stocks",
"subCategory": "Options"
```

## Raw Data Mode (for AI)

```python
"raw": True  # Adds ?raw=true parameter for AI-friendly data

@app.get("/endpoint")
def endpoint(raw: bool = False):
    if raw:
        return {"data": [...]}  # Raw data for AI
    return fig_json  # Chart for display
```

## Error Handling

```python
from fastapi import HTTPException

@app.get("/endpoint")
def endpoint():
    try:
        data = fetch_data()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

# APPS.JSON SPECIFICATION

Define custom dashboard layouts.

```json
{
    "name": "My Dashboard",
    "description": "Custom financial dashboard",
    "img": "https://example.com/icon.png",
    "img_dark": "https://example.com/icon-dark.png",
    "img_light": "https://example.com/icon-light.png",
    "allowCustomization": true,
    "tabs": {
        "overview": {
            "id": "overview",
            "name": "Overview",
            "layout": [
                {"i": "portfolio_metrics", "x": 0, "y": 0, "w": 20, "h": 4},
                {"i": "price_chart", "x": 0, "y": 4, "w": 20, "h": 12},
                {"i": "stock_data", "x": 20, "y": 0, "w": 20, "h": 16}
            ]
        },
        "news": {
            "id": "news",
            "name": "News",
            "layout": [
                {"i": "market_news", "x": 0, "y": 0, "w": 40, "h": 20}
            ]
        }
    },
    "groups": [
        {
            "name": "Symbol",
            "type": "param",
            "paramName": "symbol",
            "defaultValue": "AAPL",
            "widgetIds": ["price_chart", "stock_data"]
        }
    ],
    "prompts": [
        "What is the current market sentiment?",
        "Show me the top gainers today",
        "Analyze the portfolio performance"
    ]
}
```

### Layout Properties

| Property | Description |
|----------|-------------|
| `i` | Widget ID (endpoint with / replaced by _) |
| `x` | Horizontal position (0-40) |
| `y` | Vertical position |
| `w` | Width |
| `h` | Height |
| `state` | Widget state (params, chartView, columnState) |
| `groups` | Array of group names this widget belongs to |

### Best Practices for apps.json

#### 1. Match Heights for Side-by-Side Widgets

When placing widgets next to each other (same y position, different x positions), ensure they have the **same height** to avoid awkward empty spaces in the dashboard.

```json
// BAD - creates empty space below the shorter widget
{
    "layout": [
        {"i": "chart", "x": 0, "y": 0, "w": 20, "h": 14},
        {"i": "table", "x": 20, "y": 0, "w": 20, "h": 12}  // Different height!
    ]
}

// GOOD - widgets align perfectly
{
    "layout": [
        {"i": "chart", "x": 0, "y": 0, "w": 20, "h": 14},
        {"i": "table", "x": 20, "y": 0, "w": 20, "h": 14}  // Same height
    ]
}
```

#### 2. Group Widgets with Shared Parameters

When multiple widgets use the same parameter (e.g., `symbol`), define a group so changing one updates all others. This is essential for creating a cohesive dashboard experience.

**Step 1: Define the group at app level:**
```json
{
    "groups": [
        {
            "name": "Group 1",         // MUST follow "Group N" pattern
            "type": "endpointParam",   // Use "endpointParam" for dropdown params with optionsEndpoint
            "paramName": "symbol",     // The parameter name to sync
            "defaultValue": "AAPL"     // Default value when dashboard loads
        }
    ]
}
```

**Step 2: Add each widget to the group in the layout:**
```json
{
    "layout": [
        {
            "i": "company_metrics",
            "x": 0,
            "y": 0,
            "w": 40,
            "h": 5,
            "groups": ["Group 1"]      // Assign widget to group(s)
        },
        {
            "i": "price_chart",
            "x": 0,
            "y": 5,
            "w": 20,
            "h": 14,
            "groups": ["Group 1"]      // Same group = synced parameters
        }
    ]
}
```

**Critical**:
- Group names **MUST** follow the "Group N" pattern (e.g., "Group 1", "Group 2", "Group 3"). Custom names will not work.
- Use `type: "endpointParam"` for parameters that use `optionsEndpoint` (dropdowns fetched from an endpoint)
- Use `type: "param"` for parameters with static options
- Each widget must have `"groups": ["Group 1"]` in its layout definition to be included
- When grouping is active, a chain link icon (🔗) appears next to each grouped dropdown.

**CRITICAL ERROR**: If you define `groups` at app level but only SOME widgets have `"groups": ["Group 1"]` in their layout, you will get a JavaScript error:

```
TypeError: Cannot read properties of undefined (reading 'includes')
```

**Solution**: Either add `"groups": ["Group 1"]` to ALL widgets that use the grouped parameter, OR remove the groups configuration entirely if widgets don't share parameters.

```json
// BAD - causes JavaScript error (widget2 missing groups)
{
    "groups": [{"name": "Group 1", "paramName": "symbol", ...}],
    "tabs": {
        "main": {
            "layout": [
                {"i": "widget1", "x": 0, "y": 0, "w": 20, "h": 10, "groups": ["Group 1"]},
                {"i": "widget2", "x": 20, "y": 0, "w": 20, "h": 10}  // Missing groups!
            ]
        }
    }
}

// GOOD - all grouped widgets have groups array
{
    "groups": [{"name": "Group 1", "paramName": "symbol", ...}],
    "tabs": {
        "main": {
            "layout": [
                {"i": "widget1", "x": 0, "y": 0, "w": 20, "h": 10, "groups": ["Group 1"]},
                {"i": "widget2", "x": 20, "y": 0, "w": 20, "h": 10, "groups": ["Group 1"]}
            ]
        }
    }
}

// GOOD - no groups if widgets don't share parameters
{
    "tabs": {
        "main": {
            "layout": [
                {"i": "widget1", "x": 0, "y": 0, "w": 20, "h": 10},
                {"i": "widget2", "x": 20, "y": 0, "w": 20, "h": 10}
            ]
        }
    }
}
```

#### 3. Add Helpful AI Prompts

Include prompts that the AI agent can actually answer based on your widget data. Prompts should be:
- Specific to your data (not generic questions)
- Answerable using the widgets you've created
- Actionable and useful for the end user

```json
{
    "prompts": [
        "What is the current P/E ratio and how does it compare to the industry average?",
        "Analyze the quarterly revenue trend over the last 4 quarters",
        "What is the shareholding pattern and how has promoter holding changed?",
        "Summarize the key financial ratios and highlight any concerns",
        "Compare the profit margins year over year"
    ]
}
```

**Bad prompts** (too generic or unanswerable):
- "Tell me about the stock" (too vague)
- "What will the price be tomorrow?" (can't predict)
- "Show me insider trading" (data not available in widgets)

#### 4. apps.json Must Be an Array

The apps.json file must be an **array** of app objects, even if you only have one app:

```json
// CORRECT - array format
[
    {
        "name": "My Dashboard",
        "tabs": { ... }
    }
]

// WRONG - single object (will be rejected)
{
    "name": "My Dashboard",
    "tabs": { ... }
}
```

---

# AGENTS.JSON SPECIFICATION

Define custom AI agents.

```json
[
    {
        "agent_id": "financial-analyst",
        "name": "Financial Analyst",
        "description": "Analyzes financial data and provides insights",
        "image": "https://example.com/agent-logo.png",
        "endpoints": {
            "query": "/agent/query"
        },
        "features": {
            "streaming": true,
            "widget-dashboard-select": true,
            "widget-dashboard-search": false
        }
    }
]
```

### Agent Endpoint

```python
@app.post("/agent/query")
async def agent_query(request: dict = Body(...)):
    messages = request.get("messages", [])
    widgets = request.get("widgets", {})

    # Process with your LLM
    response = "Here's my analysis..."

    return {"response": response}
```

---

# COMPLETE EXAMPLE

Here's a full backend template:

```python
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from functools import wraps
import asyncio
import json
import plotly.graph_objects as go

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://pro.openbb.co", "https://pro.openbb.dev", "http://localhost:1420"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

WIDGETS = {}

def register_widget(widget_config):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        endpoint = widget_config.get("endpoint")
        if endpoint:
            widget_config.setdefault("widgetId", endpoint)
            WIDGETS[widget_config["widgetId"]] = widget_config
        return wrapper
    return decorator

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/widgets.json")
def get_widgets():
    return WIDGETS  # Return as dict with widget IDs as keys

# Symbol options endpoint
@app.get("/symbol_options")
def symbol_options():
    return [
        {"label": "Apple Inc.", "value": "AAPL"},
        {"label": "Google", "value": "GOOGL"},
        {"label": "Microsoft", "value": "MSFT"},
    ]

# Metrics widget
@register_widget({
    "name": "Key Metrics",
    "description": "Portfolio key metrics",
    "type": "metric",
    "endpoint": "key_metrics",
    "category": "Portfolio",
    "gridData": {"w": 20, "h": 4}
})
@app.get("/key_metrics")
def key_metrics():
    return JSONResponse(content=[
        {"label": "Total Value", "value": "$1.2M", "delta": "+5.2%"},
        {"label": "Daily P&L", "value": "$15K", "delta": "-2.1%"},
    ])

# Table widget
@register_widget({
    "name": "Holdings",
    "description": "Current portfolio holdings",
    "type": "table",
    "endpoint": "holdings",
    "category": "Portfolio",
    "gridData": {"w": 20, "h": 10},
    "data": {
        "columnsDefs": [
            {"field": "symbol", "headerName": "Symbol", "cellDataType": "text"},
            {"field": "shares", "headerName": "Shares", "cellDataType": "number"},
            {"field": "price", "headerName": "Price", "cellDataType": "number", "formatterFn": "int"},
            {"field": "change", "headerName": "Change %", "cellDataType": "number", "renderFn": "greenRed"},
        ]
    }
})
@app.get("/holdings")
def holdings():
    return [
        {"symbol": "AAPL", "shares": 100, "price": 150.25, "change": 2.5},
        {"symbol": "GOOGL", "shares": 50, "price": 140.50, "change": -1.2},
    ]

# Chart widget
@register_widget({
    "name": "Price Chart",
    "description": "Stock price over time",
    "type": "chart",
    "endpoint": "price_chart",
    "category": "Charts",
    "gridData": {"w": 20, "h": 12},
    "params": [
        {"paramName": "symbol", "type": "endpoint", "optionsEndpoint": "/symbol_options", "label": "Symbol"}
    ]
})
@app.get("/price_chart")
def price_chart(symbol: str = "AAPL", theme: str = "dark"):
    # Mock data
    dates = ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"]
    prices = [150, 152, 148, 155, 153]

    colors = {"dark": {"text": "#fff", "bg": "rgba(0,0,0,0)"},
              "light": {"text": "#333", "bg": "rgba(255,255,255,0)"}}[theme]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=prices, mode='lines', name=symbol))
    fig.update_layout(
        paper_bgcolor=colors["bg"],
        plot_bgcolor=colors["bg"],
        font=dict(color=colors["text"]),
        margin=dict(l=0, r=0, t=0, b=0)
    )
    return json.loads(fig.to_json())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7779)
```

---

# ADVANCED IMPLEMENTATION PATTERNS

## Separate Scraper Module

For apps that scrape external data sources, create a separate `scraper.py` module to keep `main.py` clean and focused on endpoint definitions:

```
apps/my-app/
├── main.py          # FastAPI endpoints with @register_widget decorators
├── scraper.py       # Data fetching and parsing logic
├── apps.json
└── requirements.txt
```

```python
# scraper.py
class DataScraper:
    BASE_URL = "https://api.example.com"

    def __init__(self, symbol: str):
        self.symbol = symbol
        self._load_entity()

    def _load_entity(self):
        """Load entity page to extract internal IDs needed for API calls."""
        response = self._request(f"{self.BASE_URL}/entity/{self.symbol}")
        # Extract internal ID from response
        self.entity_id = self._extract_id(response)

    def get_data(self) -> dict:
        """Fetch data using the extracted entity ID."""
        if not self.entity_id:
            return {}
        return self._request_json(f"{self.BASE_URL}/api/{self.entity_id}/data")

# main.py
from scraper import DataScraper

@app.get("/widget_endpoint")
def widget_endpoint(symbol: str = "DEFAULT"):
    scraper = DataScraper(symbol)
    return scraper.get_data()
```

## In-Memory Caching with TTL

Simple caching pattern for rate limiting external API calls:

```python
import time
from typing import Dict, Optional

# Global cache
_cache: Dict[str, tuple] = {}
CACHE_TTL = 60  # seconds

def cached_request(url: str, use_cache: bool = True) -> Optional[str]:
    """Make HTTP request with caching."""
    cache_key = url

    if use_cache and cache_key in _cache:
        cached_time, cached_data = _cache[cache_key]
        if time.time() - cached_time < CACHE_TTL:
            return cached_data

    response = httpx.get(url)
    response.raise_for_status()
    data = response.text

    _cache[cache_key] = (time.time(), data)
    return data
```

## Daily Token/Symbol Caching

For apps that need symbol mappings from external sources:

```python
from pathlib import Path
from datetime import date

TOKENS_DIR = Path(__file__).parent / "tokens"

def get_token_dataframe():
    """Load or download symbol mappings, cached daily."""
    TOKENS_DIR.mkdir(exist_ok=True)

    today = date.today().strftime("%Y%m%d")
    token_file = TOKENS_DIR / f"tokens_{today}.csv"

    if token_file.exists():
        return pd.read_csv(token_file)

    # Download fresh data
    response = httpx.get("https://api.example.com/symbols.json")
    df = pd.DataFrame(response.json())
    df.to_csv(token_file, index=False)

    # Clean up old files
    for old_file in TOKENS_DIR.glob("tokens_*.csv"):
        if old_file != token_file:
            old_file.unlink()

    return df
```

## Generic HTML Table Parser

For scraping HTML tables with BeautifulSoup:

```python
from bs4 import BeautifulSoup

def parse_table(soup: BeautifulSoup, section_id: str) -> list[dict]:
    """Generic table parser that works with multiple table sections."""
    section = soup.find("section", {"id": section_id})
    if not section:
        return []

    table = section.find("table")
    if not table:
        return []

    # Extract headers
    headers = ["metric"]
    thead = table.find("thead")
    if thead:
        for th in thead.find_all("th")[1:]:
            headers.append(th.get_text(strip=True))

    # Extract rows
    rows = []
    tbody = table.find("tbody")
    if tbody:
        for tr in tbody.find_all("tr"):
            cells = tr.find_all(["td", "th"])
            if cells:
                row = {"metric": cells[0].get_text(strip=True)}
                for i, cell in enumerate(cells[1:], 1):
                    if i < len(headers):
                        value = cell.get_text(strip=True)
                        # Convert to number if possible
                        try:
                            value = float(value.replace(",", "").replace("%", ""))
                        except ValueError:
                            pass
                        row[headers[i]] = value
                rows.append(row)

    return rows
```

## Handling Varied API Response Formats

External APIs often return data in unexpected formats. Always inspect the actual response:

```python
# Example: Chart API might return data in different formats

# Format 1: Separate labels array
# {"labels": ["2024-01", "2024-02"], "datasets": [{"values": [100, 200]}]}

# Format 2: Embedded dates in values (common!)
# {"datasets": [{"values": [["2024-01", 100], ["2024-02", 200]]}]}

def parse_chart_data(data: dict) -> list[dict]:
    """Handle both formats gracefully."""
    datasets = data.get("datasets", [])

    # Check if we have a separate labels array
    if "labels" in data and data["labels"]:
        labels = data["labels"]
        values = datasets[0].get("values", []) if datasets else []
        return [{"date": labels[i], "value": values[i]} for i in range(len(labels))]

    # Otherwise, dates are embedded in values as [date, value] pairs
    if datasets and datasets[0].get("values"):
        values = datasets[0]["values"]
        return [{"date": v[0], "value": float(v[1])} for v in values]

    return []
```

## Date Column Handling

Always convert date columns explicitly when loading data, and format consistently for display:

```python
import pandas as pd

def get_data() -> pd.DataFrame:
    df = load_parquet("data.parquet")
    df["date"] = pd.to_datetime(df["date"])  # Explicit conversion
    return df

@app.get("/endpoint")
def endpoint():
    df = get_data()
    return [
        {
            "date": row["date"].strftime("%Y-%m-%d"),  # Daily data
            "month": row["date"].strftime("%Y-%m"),    # Monthly data
            "value": row["value"],
        }
        for _, row in df.iterrows()
    ]
```

## Error Handling in Widget Endpoints

Return errors in the widget's expected data format so the UI displays them gracefully:

```python
# Metric widget - return error as metric
@app.get("/company_metrics")
def company_metrics(symbol: str = "DEFAULT"):
    try:
        data = fetch_metrics(symbol)
        return [
            {"label": "Revenue", "value": data.get("revenue", "N/A")},
            {"label": "Profit", "value": data.get("profit", "N/A")},
        ]
    except Exception as e:
        return [{"label": "Error", "value": str(e)}]

# Table widget - return error as table row
@app.get("/data_table")
def data_table(symbol: str = "DEFAULT"):
    try:
        return fetch_table_data(symbol)
    except Exception as e:
        return [{"error": "Error", "message": str(e)}]

# Chart widget - return empty chart with error in layout
@app.get("/chart_data")
def chart_data(symbol: str = "DEFAULT", raw: bool = False):
    try:
        data = fetch_chart_data(symbol)
        if raw:
            return data
        return build_plotly_chart(data)
    except Exception as e:
        if raw:
            return []
        return {"data": [], "layout": {"title": f"Error: {e}"}}
```

## Popular Symbols List Pattern

For apps with dynamic dropdowns, provide a curated list of popular options:

```python
@app.get("/symbols")
def get_symbols():
    """Return list of popular symbols for dropdown."""
    return [
        {"label": "Apple Inc.", "value": "AAPL"},
        {"label": "Microsoft", "value": "MSFT"},
        {"label": "Google", "value": "GOOGL"},
        # ... more popular symbols
    ]

# Widget uses this endpoint for dropdown
@register_widget({
    "name": "Price Data",
    "params": [{
        "paramName": "symbol",
        "type": "endpoint",
        "optionsEndpoint": "symbols",
        "value": "AAPL"  # Default selection
    }]
})
```

---

# DEVELOPMENT WORKFLOW

1. **Start with this template** - Copy the complete example above
2. **Define your data sources** - APIs, databases, calculations
3. **Choose widget types** - Based on how data should be displayed
4. **Configure parameters** - User inputs for filtering/customization
5. **Test locally** - `uvicorn main:app --reload --port 7779`
6. **Add to OpenBB Workspace** - Apps > Connect Backend

When users ask to build an OpenBB app, guide them through these steps and generate complete, working code based on their requirements.
