# OpenBB App Implementation Reference

Core implementation knowledge for building OpenBB Workspace backends.

## Additional Documentation

For the latest documentation, fetch:
```
https://docs.openbb.co/workspace/llms-full.txt
```

## Open Source Examples

Curated examples at:
```
https://github.com/OpenBB-finance/awesome-openbb
```

---

## Core Requirements

Your backend must:

1. **Serve HTTP endpoints** returning JSON responses
2. **Enable CORS** for these origins:
   - `https://pro.openbb.co`
   - `https://pro.openbb.dev`
   - `http://localhost:1420`
3. **Implement required endpoints**:
   - `GET /widgets.json` - Return dict of widget configurations (NOT array)
   - `GET /apps.json` - (Optional) Return dashboard configurations
4. **Return proper Content-Type**: `application/json`

---

## Backend Architecture

```python
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

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

@app.get("/")
def root():
    return {"message": "OpenBB Custom Backend"}

@app.get("/widgets.json")
def get_widgets():
    return {  # MUST be dict with widget IDs as keys
        "my_widget": {
            "name": "My Widget",
            "type": "table",
            "endpoint": "my_endpoint"
        }
    }
```

---

## Widget Types

### 1. Table Widget (type: "table")
Display tabular data with sorting, filtering, and chart conversion.

```python
@app.get("/stock_prices")
def stock_prices():
    return [
        {"symbol": "AAPL", "price": 150.25, "change": 2.5},
        {"symbol": "GOOGL", "price": 140.50, "change": -1.2},
    ]
```

### 2. Chart Widget (type: "chart")
Interactive Plotly charts with theme support.

```python
import plotly.graph_objects as go

@app.get("/price_chart")
def price_chart(
    symbol: str = Query("AAPL"),
    theme: str = Query("dark"),
    raw: bool = Query(False)
):
    dates = ["2024-01-01", "2024-01-02", "2024-01-03"]
    prices = [150, 152, 148]

    if raw:
        return [{"date": d, "price": p} for d, p in zip(dates, prices)]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=prices, mode="lines"))
    # NO title - widget provides it
    fig.update_layout(
        template="plotly_dark" if theme == "dark" else "plotly_white"
    )

    return JSONResponse(content=json.loads(fig.to_json()))
```

### 3. Metric Widget (type: "metric")
Display KPIs with labels, values, and deltas.

```python
@app.get("/portfolio_metrics")
def portfolio_metrics():
    return [
        {"label": "Total Value", "value": "$125,430", "delta": "+5.2%"},
        {"label": "Daily P&L", "value": "$2,340", "delta": "+1.9%"},
        {"label": "Win Rate", "value": "68%", "subvalue": "Last 30 days"},
    ]
```

### 4. Markdown Widget (type: "markdown")
Display formatted text content.

```python
@app.get("/analysis")
def analysis():
    return """
## Market Analysis

The market showed **strong momentum** today with:
- Tech sector up 2.3%
- Energy sector down 0.8%

### Recommendations
Buy: AAPL, MSFT
Sell: XOM
"""
```

### 5. Newsfeed Widget (type: "newsfeed")
Display articles with title, date, author, excerpt, and body.

```python
@app.get("/news")
def news():
    return [
        {
            "title": "Market Rally Continues",
            "date": "2024-01-15",
            "author": "John Smith",
            "excerpt": "Stocks hit new highs...",
            "body": "Full article content here..."
        }
    ]
```

---

## Widget Configuration

### widgets.json Structure

```json
{
  "widget_id": {
    "name": "Display Name",
    "description": "Widget description",
    "category": "Category Name",
    "type": "table",
    "endpoint": "endpoint_path",
    "gridData": {"w": 20, "h": 12},
    "params": [
      {
        "paramName": "symbol",
        "type": "endpoint",
        "label": "Symbol",
        "optionsEndpoint": "/symbols",
        "value": "AAPL"
      }
    ]
  }
}
```

### Parameter Types

| Type | Description | Example |
|------|-------------|---------|
| `text` | Text input | Search query |
| `number` | Number input | Limit, count |
| `boolean` | Toggle | Include extended |
| `date` | Date picker | Start date |
| `endpoint` | Dynamic dropdown | Symbol selector |

---

## apps.json Structure

```json
{
  "my_dashboard": {
    "name": "My Dashboard",
    "description": "Dashboard description",
    "tabs": {
      "overview": {
        "name": "Overview",
        "widgets": {
          "widget_1": {
            "id": "widget_id",
            "gridData": {"x": 0, "y": 0, "w": 20, "h": 12}
          }
        }
      }
    },
    "groups": {
      "Group 1": {
        "paramName": "symbol",
        "widgetIds": ["widget_1", "widget_2"]
      }
    }
  }
}
```

---

## Column Definitions

For table widgets:

```json
{
  "columns": [
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
      "formatterFn": "percent",
      "renderFn": "greenRed"
    }
  ]
}
```

### Valid formatterFn Values
- `int` - Integer formatting
- `none` - No formatting (use for currency)
- `percent` - Percentage formatting
- `normalized` - Normalize to scale
- `normalizedPercent` - Normalized percentage
- `dateToYear` - Extract year from date

**Note**: `"currency"` is NOT valid - use `"none"` instead.

---

## Best Practices

### 1. No runButton by Default
Only use `runButton: true` for heavy computation (>5 seconds).

### 2. Reasonable Widget Heights
- Metrics: h=4-6
- Tables: h=12-18
- Charts: h=12-15

### 3. Charts Without Titles
Plotly charts should NOT include title - widget provides it.

### 4. Support Raw Mode for Charts
Add `raw` query parameter to return raw data for AI analysis.

### 5. Dict Format for widgets.json
Return object with widget IDs as keys, NOT an array.

### 6. Group Names Pattern
Use "Group 1", "Group 2" etc. - custom names fail silently.

---

## Development Workflow

1. Start with template
2. Define data sources
3. Choose widget types
4. Configure parameters
5. Test locally: `uvicorn main:app --reload --port 7779`
6. Add to OpenBB: Settings > Data Connectors > Add Backend

### Refreshing Changes
- **Widget config changes**: Right-click → "Refresh backend"
- **Python code changes**: Restart uvicorn
- **Major changes**: Open fresh app instance from gallery
