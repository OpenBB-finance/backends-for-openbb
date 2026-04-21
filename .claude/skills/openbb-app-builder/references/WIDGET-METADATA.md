# Widget Metadata Reference

Complete guide for defining widget metadata specifications.

## Widget Types Reference

Use the exact widget type strings from the current OpenBB docs. Do not invent aliases.

Choose the appropriate widget type for each data view:

| Type | Use Case | Example | Grouping Support |
|------|----------|---------|------------------|
| `table` | Standard AgGrid table for sortable/filterable tabular data | Holdings, transactions, stock lists | Yes |
| `chart` | Plotly visualization with raw-data toggle support | Price charts, performance graphs, time series | Yes |
| `table_ssrm` | Large or server-side table datasets | Paged screener results, large audit logs | Yes, but use only when SSRM behavior is needed |
| `metric` | KPI values and compact stat cards | Portfolio value, daily P&L, win rate | Usually yes, if driven by params |
| `markdown` | Formatted analysis or summaries | Summaries, reports, generated commentary | Usually yes, if driven by params |
| `note` | Simple static or semi-static text blocks | Instructions, disclaimers, quick context | Usually unnecessary |
| `newsfeed` | Article and update lists | News, research reports, filings feed | Usually yes, if filtered by params |
| `live_grid` | Real-time table with websocket updates | Live prices, order book, streaming tape | Yes |
| `advanced-chart` | TradingView-style charting experience | Technical charting, trading-focused views | Avoid for watchlist-style group sync |
| `chart-highcharts` | Highcharts visualization | Specialized chart packages, dashboard charts | Likely yes, but prefer `chart` unless needed |
| `multi_file_viewer` | File/document collection viewer | Multi-document review, attachments, reports | Parameter support is possible; grouping is uncommon |
| `youtube` | Embedded video content | Walkthroughs, explainers, tutorials | Grouping is uncommon |

**Common mistakes to avoid:**
- Use `advanced-chart`, not `advanced_charting`
- Use `table_ssrm`, not `ssrm_table`
- Do not add unofficial types unless the current docs explicitly allow them

**Grouping Support meaning**:
- This column is practical planning guidance for app design, not a hard schema enum
- Most widgets can participate in app-level param sync if they expose matching params
- For click-through watchlist flows, the safest recommended pattern is `table` -> `chart`

**Watchlist/grouping note**: If a chart needs to update from table cell clicks, prefer `chart` over `advanced-chart`.

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
  "multiple": false
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

For table widgets, column definitions belong at:

```json
{
  "data": {
    "table": {
      "columnsDefs": []
    }
  }
}
```

Do not place `columnsDefs` directly under `data`, and do not use a top-level `columns` key.

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
  "field": "companyName",
  "headerName": "Company",
  "cellDataType": "text",
  "pinned": "left",
  "renderFn": "cellOnClick",
  "renderFnParams": {
    "actionType": "groupBy",
    "groupBy": {
      "paramName": "companyId",
      "valueField": "companyId"
    }
  }
}
```

**Requirements for this pattern:**
1. Both table and target widget must be in the same group (`"groups": ["Group 1"]`)
2. The target widget must have a matching parameter name
3. Use `renderFnParams.groupBy.paramName`, not `groupByParamName`
4. Use `valueField` when the displayed cell value differs from the parameter value

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

#### For Table Widgets: Exact JSON Shape

```json
{
  "data": {
    "table": {
      "enableCharts": true,
      "columnsDefs": [
        {
          "field": "symbol",
          "headerName": "Symbol",
          "chartDataType": "category",
          "cellDataType": "text",
          "pinned": "left"
        },
        {
          "field": "price",
          "headerName": "Price",
          "chartDataType": "series",
          "cellDataType": "number",
          "formatterFn": "int",
          "decimalPlaces": 2
        },
        {
          "field": "change_pct",
          "headerName": "Change %",
          "chartDataType": "series",
          "cellDataType": "number",
          "formatterFn": "percent",
          "renderFn": "greenRed"
        }
      ]
    }
  }
}
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
- Table metadata belongs under `data.table.columnsDefs`
- `source` is an array of strings, e.g. `["API"]`
