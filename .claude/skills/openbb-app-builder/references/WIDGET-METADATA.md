# Widget Metadata Reference

Complete guide for defining widget metadata specifications.

## Widget Types Reference

Choose the appropriate widget type for each data view:

| Type | Use Case | Example | Grouping Support |
|------|----------|---------|------------------|
| `table` | Tabular data with rows/columns | Holdings, Transactions, Stock lists | Yes |
| `chart` | Plotly visualizations | Price charts, Performance graphs | Yes |
| `metric` | KPI values with deltas | Portfolio value, Daily P&L | Yes |
| `markdown` | Formatted text content | Summaries, Reports, Analysis | Yes |
| `newsfeed` | Article lists | News, Research reports | Yes |
| `html` | Custom HTML (no JS) | Custom visualizations | Yes |
| `pdf` | PDF viewer | Documents, Reports | Yes |
| `advanced_charting` | TradingView charts | Professional charting | **NO** |
| `live_grid` | Real-time table | Live prices, Order book | Yes |
| `omni` | Dynamic content | AI responses, Mixed content | Yes |

**Warning**: `advanced_charting` (TradingView) does NOT support parameter-based grouping. Use `chart` (Plotly) if you need a chart that updates when clicking a watchlist row.

---

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
  "multiSelect": false
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

---

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

**Common Error**: `"currency"` is NOT a valid formatterFn value. Use `"none"` for currency values instead.

### Render Functions
- `greenRed` - Positive=green, Negative=red
- `titleCase` - Capitalize words
- `hoverCard` - Show markdown on hover
- `cellOnClick` - Action on click (watchlist pattern)
- `columnColor` - Conditional coloring
- `showCellChange` - Animate value changes

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

---

## Widget Definition Template

For each widget, define:

```markdown
### Widget: {widget_id}

#### Basic Info
- **Name**: {Display name}
- **Description**: {Brief description}
- **Type**: {widget type}
- **Category**: {Category name}

#### Layout
- **Default Width (w)**: {10-40}
- **Default Height (h)**: {4-20}

#### Endpoint
- **HTTP Method**: {GET | POST}
- **Path**: /{widget_id}
- **Parameters**: {see params section}

#### Parameters
| Name | Type | Label | Default | Required |
|------|------|-------|---------|----------|
| symbol | endpoint | Symbol | AAPL | Yes |
| period | text | Period | 1M | No |

#### Data Format

**Response Type**: {JSON Array | JSON Object | Plotly JSON}

**Example Response**:
```json
{example response}
```

#### For Table Widgets: Column Definitions

| Field | Header | Type | Format | Render |
|-------|--------|------|--------|--------|
| symbol | Symbol | text | - | pinned: left |
| price | Price | number | int | - |
| change | Change % | number | percent | greenRed |
```

---

## Best Practices

### runButton Configuration
- **Default to `runButton: false`** (or omit entirely)
- Only set `runButton: true` for:
  - Heavy computations (Monte Carlo simulations, complex ML models)
  - Expensive API calls with rate limits
  - Operations that take >5 seconds

### Widget Height Guidelines
| Widget Type | Recommended Height |
|-------------|-------------------|
| metric | 4-6 |
| table (small) | 8-12 |
| table (medium) | 12-15 |
| chart | 12-15 |
| newsfeed | 12-15 |
| markdown | 8-12 |

Avoid heights above 20 unless specifically needed.

### Chart Widget Best Practices

**Prefer AgGrid Charts over Plotly when possible:**
- AgGrid allows users to access underlying raw data
- Users can create their own visualizations from the data

**When using Plotly charts:**
1. **Do NOT include title** - The widget already has a name/title
2. **Always support `raw` parameter** - Return raw data array when `raw=True`
3. **Support `theme` parameter** - Adapt colors for dark/light mode

### widgets.json Format
- **Must be object format**: `{"widget_id": {...}}`
- **NOT array format**: `[{...}]` will be rejected
- Widget IDs become the keys
