---
name: widget-metadata
description: Define complete widget metadata for each widget in the app
---

# Widget Metadata Skill

You are helping define the complete metadata for each widget in an OpenBB app. This happens after requirements gathering (app-interview) and before layout design (dashboard-layout).

**Implementation Note**: The `@register_widget` decorator pattern is recommended as it keeps widget metadata next to endpoint code for better maintainability. However, a separate `widgets.json` file is also valid if the user prefers that approach.

## Prerequisites

Before starting, read the APP-SPEC.md file to understand:
- What data is being displayed
- What the data source provides
- Authentication requirements
- Feature requirements (SSRM, WebSocket, etc.)

## Widget Types Reference

Choose the appropriate widget type for each data view:

| Type | Use Case | Example | Grouping Support |
|------|----------|---------|------------------|
| `table` | Tabular data with rows/columns | Holdings, Transactions, Stock lists | ✅ Yes |
| `chart` | Plotly visualizations | Price charts, Performance graphs | ✅ Yes |
| `chart-highcharts` | Highcharts visualizations | Alternative to Plotly | ✅ Yes |
| `markdown` | Formatted text content | Summaries, Reports, Analysis | ✅ Yes |
| `metric` | KPI values with deltas | Portfolio value, Daily P&L | ✅ Yes |
| `newsfeed` | Article lists | News, Research reports | ✅ Yes |
| `html` | Custom HTML (no JS) | Custom visualizations | ✅ Yes |
| `pdf` | PDF viewer | Documents, Reports | ✅ Yes |
| `multi_file_viewer` | Multiple files | Document library | ✅ Yes |
| `advanced_charting` | TradingView charts | Professional charting | ❌ **NO** |
| `live_grid` | Real-time table | Live prices, Order book | ✅ Yes |
| `omni` | Dynamic content | AI responses, Mixed content | ✅ Yes |
| `ssrm_table` | Large datasets (100k+ rows) | Historical data, Logs | ✅ Yes |

**⚠️ TradingView Limitation**: The `advanced_charting` widget type does NOT support parameter-based grouping. If you need a chart that updates when clicking a watchlist row, use `chart` (Plotly) instead.

## Widget Definition Template

For each widget, define:

```markdown
### Widget: {widget_id}

#### Basic Info
- **Name**: {Display name}
- **Description**: {Brief description}
- **Type**: {widget type}
- **Category**: {Category name}
- **Subcategory**: {Optional subcategory}

#### Layout
- **Default Width (w)**: {10-40}
- **Default Height (h)**: {4-100}
- **Min Width**: {optional}
- **Max Width**: {optional}

#### Endpoint
- **HTTP Method**: {GET | POST}
- **Path**: /{widget_id}
- **Parameters**: {see params section}

#### Parameters
| Name | Type | Label | Default | Required | Options/Details |
|------|------|-------|---------|----------|-----------------|
| symbol | endpoint | Symbol | AAPL | Yes | optionsEndpoint: /symbols |
| period | text | Period | 1M | No | options: 1D,1W,1M,3M,1Y |
| theme | text | Theme | dark | No | Auto-injected by OpenBB |

#### Data Format

**Response Type**: {JSON Array | JSON Object | Plotly JSON | HTML}

**Example Response**:
```json
{example response}
```

#### For Table Widgets: Column Definitions

| Field | Header | Data Type | Format | Render | Other |
|-------|--------|-----------|--------|--------|-------|
| symbol | Symbol | text | - | pinned: left | - |
| price | Price | number | int | - | - |
| change | Change % | number | percent | greenRed | - |

#### For Chart Widgets: Chart Config
- **Chart Library**: Plotly
- **Chart Type**: Line, Bar, Candlestick, etc.
- **Theme Support**: Yes (receives theme param)
- **Raw Mode**: Yes (receives raw param)

#### Special Features
- **MCP Tool Matching**: {mcp_server, tool_id}
- **WebSocket Endpoint**: {/ws path if live}
- **Auto-refresh**: {interval in ms}
- **Run Button**: {true | false}
- **Stale Time**: {ms}
```

## Parameter Types Guide

### Text Input
```json
{
  "paramName": "query",
  "type": "text",
  "label": "Search Query",
  "description": "Enter search term",
  "value": ""
}
```

### Number Input
```json
{
  "paramName": "limit",
  "type": "number",
  "label": "Limit",
  "value": 10
}
```

### Boolean Toggle
```json
{
  "paramName": "include_extended",
  "type": "boolean",
  "label": "Include Extended Hours",
  "value": false
}
```

### Date Picker
```json
{
  "paramName": "start_date",
  "type": "date",
  "label": "Start Date",
  "value": "$currentDate-1M"
}
```
Date modifiers: `$currentDate`, `$currentDate-1d`, `$currentDate-1w`, `$currentDate-1M`, `$currentDate-1y`

### Static Dropdown
```json
{
  "paramName": "interval",
  "type": "text",
  "label": "Interval",
  "value": "1d",
  "options": [
    {"label": "1 Day", "value": "1d"},
    {"label": "1 Week", "value": "1w"},
    {"label": "1 Month", "value": "1m"}
  ]
}
```

### Dynamic Dropdown (from endpoint)
```json
{
  "paramName": "symbol",
  "type": "endpoint",
  "label": "Select Symbol",
  "optionsEndpoint": "/symbols",
  "multiSelect": false,
  "style": {"popupWidth": 450}
}
```

### Dependent Dropdown
```json
{
  "paramName": "city",
  "type": "endpoint",
  "label": "City",
  "optionsEndpoint": "/cities",
  "optionsParams": {"country": "$country"}
}
```

### Tabs Parameter
```json
{
  "paramName": "category",
  "type": "tabs",
  "label": "Category",
  "value": "overview",
  "options": [
    {"label": "Overview", "value": "overview"},
    {"label": "Details", "value": "details"}
  ]
}
```

## Column Definition Guide

### Cell Data Types
- `text` - String values
- `number` - Numeric values
- `boolean` - True/false
- `date` - Date objects
- `dateString` - Date as string
- `object` - Complex objects

### Formatter Functions

**CRITICAL**: Only these values are valid for `formatterFn`:
- `int` - Integer formatting
- `none` - No formatting (use for currency/decimal display)
- `percent` - Percentage formatting
- `normalized` - Normalize to scale
- `normalizedPercent` - Normalized percentage
- `dateToYear` - Extract year from date

**Common Error**: `"currency"` is NOT a valid formatterFn value:
```
Invalid enum value. Expected: 'int' | 'none' | 'percent' | 'normalized' | 'normalizedPercent' | 'dateToYear' Received: 'currency'
```
Use `"none"` for currency values instead.

### Render Functions
- `greenRed` - Positive=green, Negative=red
- `titleCase` - Capitalize words
- `hoverCard` - Show markdown on hover (requires special config, see below)
- `cellOnClick` - Action on click (commonly used for watchlist pattern)
- `columnColor` - Conditional coloring
- `showCellChange` - Animate value changes

### hoverCard Configuration

The `hoverCard` renderFn requires `renderFnParams` and nested object data:

```json
{
    "field": "name",
    "renderFn": "hoverCard",
    "renderFnParams": {
        "hoverCard": {
            "cellField": "value",           // Which nested field to display in cell
            "title": "Details",             // Hover card popup title
            "markdown": "### {value}\n**Description:** {description}"
        }
    }
}
```

**Data structure** - the field value must be a nested object:
```python
{
    "name": {
        "value": "Display Text",        # Shown in cell (via cellField)
        "description": "Full details",  # Available as {description} in markdown
    },
    "other_columns": ...
}
```

The markdown template uses `{placeholder}` syntax to reference nested object properties.

### cellOnClick with groupBy (Watchlist Pattern)

Make table cells clickable to update other widgets in the same group:

```json
{
    "field": "symbol",
    "headerName": "Symbol",
    "cellDataType": "text",
    "pinned": "left",
    "renderFn": "cellOnClick",
    "renderFnParams": {
        "actionType": "groupBy",
        "groupByParamName": "symbol"
    }
}
```

**Requirements for this pattern:**
1. Both table and target widget must be in the same group (`"groups": ["Group 1"]`)
2. Target widget MUST support param grouping (NOT `advanced_charting`)
3. Both widgets need matching `paramName` with `type: "endpoint"`
4. Group names MUST follow "Group N" pattern

### Sparkline Columns
```json
{
  "field": "trend",
  "headerName": "7D Trend",
  "sparkline": {
    "type": "line",
    "dataField": "trend_data",
    "options": {
      "stroke": "#3b82f6",
      "fill": "rgba(34, 197, 94, 0.3)",
      "markers": {"enabled": true, "size": 2},
      "pointsOfInterest": {
        "maximum": {"fill": "#ffd700", "size": 6},
        "minimum": {"fill": "#ef4444", "size": 6}
      }
    }
  }
}
```

## Process

1. **Review APP-SPEC.md** - Understand what data is available
2. **Identify data views** - What views does the user need?
3. **Choose widget types** - Match each view to a widget type
4. **Define parameters** - What should users be able to filter/configure?
5. **Define columns** (tables) - What columns should be displayed?
6. **Define chart config** (charts) - What should the chart show?
7. **Consider grouping** - Which widgets should share parameters?

## Output Format

Append the widget definitions to APP-SPEC.md:

```markdown
## Widgets

### Widget 1: {widget_id}
{full widget definition}

### Widget 2: {widget_id}
{full widget definition}

### Supporting Endpoints

#### Endpoint: /symbols
- **Purpose**: Provide symbol options for dropdowns
- **Response**: `[{"label": "Apple Inc.", "value": "AAPL"}, ...]`

#### Endpoint: /categories
- **Purpose**: Provide category options
- **Response**: `[{"label": "Technology", "value": "tech"}, ...]`

---

## Parameter Grouping Preview

These widgets will share synchronized parameters:

| Group Name | Parameter | Widgets |
|------------|-----------|---------|
| Symbol | symbol | price_chart, holdings_table, company_info |
| Date Range | start_date, end_date | price_chart, transactions_table |
```

## Example Widget Definitions

### Example 1: Price Table
```markdown
### Widget: crypto_prices

#### Basic Info
- **Name**: Crypto Prices
- **Description**: Live cryptocurrency prices
- **Type**: table
- **Category**: Prices

#### Layout
- **Width**: 20
- **Height**: 12

#### Endpoint
- **Method**: GET
- **Path**: /crypto_prices
- **Parameters**: limit (number, default 100)

#### Columns
| Field | Header | Type | Format | Render |
|-------|--------|------|--------|--------|
| rank | # | number | int | - |
| symbol | Symbol | text | - | pinned: left |
| name | Name | text | - | - |
| price | Price | number | int | - |
| change_24h | 24h % | number | percent | greenRed |
| volume | Volume | number | int | - |
| market_cap | Market Cap | number | int | - |

#### Data Format
```json
[
  {
    "rank": 1,
    "symbol": "BTC",
    "name": "Bitcoin",
    "price": 42500.50,
    "change_24h": 2.5,
    "volume": 25000000000,
    "market_cap": 850000000000
  }
]
```
```

### Example 2: Metric Widget
```markdown
### Widget: market_stats

#### Basic Info
- **Name**: Market Statistics
- **Description**: Key market metrics
- **Type**: metric
- **Category**: Overview

#### Layout
- **Width**: 20
- **Height**: 4

#### Endpoint
- **Method**: GET
- **Path**: /market_stats

#### Data Format
```json
[
  {"label": "Total Market Cap", "value": "$1.5T", "delta": "+2.5%"},
  {"label": "24h Volume", "value": "$85B", "delta": "-5.2%"},
  {"label": "BTC Dominance", "value": "48.5%", "delta": "+0.3%"}
]
```
```

### Example 3: Chart Widget
```markdown
### Widget: price_chart

#### Basic Info
- **Name**: Price Chart
- **Description**: Historical price chart
- **Type**: chart
- **Category**: Charts

#### Layout
- **Width**: 20
- **Height**: 15

#### Endpoint
- **Method**: GET
- **Path**: /price_chart
- **Parameters**:
  - symbol (endpoint, /symbols)
  - period (text, options: 1D,1W,1M,3M,1Y,ALL)
  - theme (injected)
  - raw (injected)

#### Chart Config
- **Library**: Plotly
- **Type**: Line with area fill
- **Theme Support**: Yes
- **Raw Mode**: Returns array of {date, price} objects

#### Data Format (raw=false)
Plotly figure JSON

#### Data Format (raw=true)
```json
[
  {"date": "2024-01-01", "price": 42000},
  {"date": "2024-01-02", "price": 42500}
]
```
```

## User Confirmation

After defining all widgets, present them in a summary table:

```markdown
## Widget Summary

| # | Widget ID | Name | Type | Grid |
|---|-----------|------|------|------|
| 1 | market_stats | Market Statistics | metric | 20x4 |
| 2 | crypto_prices | Crypto Prices | table | 20x12 |
| 3 | price_chart | Price Chart | chart | 20x15 |
| 4 | market_news | Market News | newsfeed | 20x15 |

Total: 4 widgets

Supporting endpoints needed:
- GET /symbols - Symbol dropdown options
```

Ask: "Does this widget list look correct? Would you like to add, remove, or modify any widgets before we design the dashboard layout?"

## Next Step

After confirmation:

"Widget metadata saved to APP-SPEC.md. Ready for the next step: **Dashboard Layout Design**. Would you like to continue to design your dashboard layout?"

This allows the pipeline to continue to the dashboard-layout skill.

## Best Practices

### runButton Configuration
- **Default to `runButton: false`** (or omit entirely)
- Only set `runButton: true` for:
  - Heavy computations (Monte Carlo simulations, complex ML models)
  - Expensive API calls with rate limits
  - Operations that take >5 seconds
- Fast API calls (like fetching prices) should NOT have runButton

### Widget Height Guidelines
| Widget Type | Recommended Height | Notes |
|-------------|-------------------|-------|
| metric | 4-6 | Keep compact, single row of metrics |
| table (small) | 8-12 | For 5-10 rows of data |
| table (medium) | 12-15 | For 10-25 rows of data |
| chart | 12-15 | Standard chart height |
| newsfeed | 12-15 | Shows 5-8 articles |
| markdown | 8-12 | Depends on content |

Avoid heights above 20 unless specifically needed.

### Chart Widget Best Practices

**Prefer AgGrid Charts over Plotly when possible:**
- AgGrid allows users to access underlying raw data
- Users can create their own visualizations from the data
- More interactive out-of-the-box

**When using Plotly charts:**
1. **Do NOT include title** - The widget already has a name/title
2. **Always support `raw` parameter** - Return raw data array when `raw=True`
3. **Support `theme` parameter** - Adapt colors for dark/light mode

```python
# Correct Plotly chart endpoint pattern
@app.get("/price_chart")
async def price_chart(
    symbol: str = "BTC",
    theme: str = Query("dark"),
    raw: bool = Query(False),
):
    data = fetch_data(symbol)

    # Return raw data for AI/export
    if raw:
        return [{"date": d, "price": p} for d, p in data]

    # Build Plotly figure WITHOUT title
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=prices, mode="lines"))

    fig.update_layout(
        # NO title here - widget provides it
        xaxis_title="Date",
        yaxis_title="Price",
        template="plotly_dark" if theme == "dark" else "plotly_white",
        # ... other layout options
    )

    return JSONResponse(content=json.loads(fig.to_json()))
```

### widgets.json Format
- **Must be object format**: `{"widget_id": {...}}`
- **NOT array format**: `[{...}]` will be rejected
- Widget IDs become the keys

```json
{
  "my_widget": {
    "name": "My Widget",
    "type": "table",
    "endpoint": "my_endpoint",
    "gridData": {"w": 20, "h": 12}
  }
}
```
