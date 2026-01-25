# Dashboard Layout Reference

Guide for designing visual dashboard layouts with tabs and widget positioning.

## Layout Concepts

### Grid System
- OpenBB Workspace uses a **40-column grid**
- Widgets snap to grid positions
- Minimum widget width: 10 columns
- Maximum widget width: 40 columns (full width)
- Height is flexible (minimum 4 rows)

### Tabs
- Organize widgets into logical tabs
- Each tab has its own layout
- Users can customize within allowed bounds

### Parameter Groups

**CRITICAL - Group Naming Pattern**:
- Group names **MUST** follow the "Group N" pattern: `"Group 1"`, `"Group 2"`, `"Group 3"`, etc.
- Custom names like `"symbol-group"` or `"my-group"` will **fail silently** - widgets won't sync

**Two group types:**

1. **`type: "param"`** - Static dropdown with hardcoded options
   - Uses `widgetIds` array to specify which widgets sync
   - Example: `{"type": "param", "paramName": "period", "defaultValue": "1M", "widgetIds": ["chart1", "chart2"]}`

2. **`type: "endpointParam"`** - Dynamic dropdown from API endpoint
   - Widgets reference the group via `groups: ["Group 1"]` in their layout items
   - Options come from the widget's `optionsEndpoint` parameter
   - Example: `{"type": "endpointParam", "paramName": "symbol", "defaultValue": "AAPL"}`

**IMPORTANT**: Always set `defaultValue` to a valid option value.

---

## Layout Design Process

### Step 1: Define Tabs

Group widgets logically:

```markdown
## Tabs

### Tab 1: Overview
- Purpose: High-level dashboard summary
- Widgets: market_stats, crypto_prices, price_chart

### Tab 2: Details
- Purpose: Detailed analysis
- Widgets: transactions, holdings_breakdown
```

### Step 2: Create ASCII Layout

Use ASCII art to visualize each tab:

```
Grid: 40 columns wide
      0         10        20        30        40
      |---------|---------|---------|---------|

Row 0 +-------------------------------------------+
      |            [1: market_stats]              |
      |               w=40, h=4                   |
Row 4 +--------------------+----------------------+
      |                    |                      |
      |  [2: price_chart]  |  [3: crypto_prices]  |
      |     w=20, h=15     |      w=20, h=15      |
      |                    |                      |
Row 19+--------------------+----------------------+
```

### Step 3: Calculate Positions

Convert ASCII to coordinates:

| Widget | x | y | w | h |
|--------|---|---|---|---|
| market_stats | 0 | 0 | 40 | 4 |
| price_chart | 0 | 4 | 20 | 15 |
| crypto_prices | 20 | 4 | 20 | 15 |

---

## Layout Templates

### Template: Overview Dashboard
```
+-------------------------------------------+
|              [Metrics Bar]                |  <- w=40, h=4
|                 w=40, h=4                 |
+--------------------+----------------------+
|                    |                      |
|   [Main Chart]     |    [Data Table]      |  <- w=20 each, h=15
|     w=20, h=15     |      w=20, h=15      |
|                    |                      |
+--------------------+----------------------+
```

### Template: Watchlist + Chart (Interactive)
```
+-------------------------------------------+
|          [Watchlist Table]                |  <- w=40, h=8
|   Click ticker to update chart below      |     cellOnClick with groupBy
+-------------------------------------------+
|                                           |
|          [Price Chart]                    |  <- w=40, h=15
|   Updates when ticker clicked above       |     MUST be Plotly, not TradingView
|                                           |
+-------------------------------------------+
```

**Key requirements for this pattern:**
1. Both widgets in same group: `"groups": ["Group 1"]`
2. Watchlist symbol column has `renderFn: "cellOnClick"` with `groupByParamName`
3. Chart MUST be `type: "chart"` (Plotly) - TradingView doesn't support grouping
4. Both widgets have matching `paramName` and `optionsEndpoint`

### Template: Data Analysis
```
+--------------------+----------------------+
|                    |                      |
|   [Main Table]     |   [Summary Panel]    |  <- w=25, w=15
|     w=25, h=20     |     w=15, h=12       |
|                    +----------------------+
|                    |   [Quick Stats]      |
|                    |     w=15, h=8        |
+--------------------+----------------------+
```

### Template: Full-Width Content
```
+-------------------------------------------+
|              [Wide Table]                 |
|                w=40, h=8                  |
+-------------------------------------------+
|              [Wide Chart]                 |
|                w=40, h=15                 |
+-------------------------------------------+
```

---

## apps.json Structure

For complete apps.json structure, required fields, and JSON examples, see [OPENBB-APP.md](OPENBB-APP.md#appsjson-structure).

**Quick reference for layout items:**
- Use `i` for widget ID (not `id`)
- Use `x`, `y`, `w`, `h` directly (not nested in `gridData`)
- Add `"groups": ["Group 1"]` to sync widgets

---

## Design Best Practices

### Layout Guidelines
1. **Most important widgets at top-left** - Users scan left-to-right, top-to-bottom
2. **Related widgets adjacent** - Group by function or data relationship
3. **Consistent sizing** - Use similar sizes for similar widget types
4. **Balance the layout** - Avoid lopsided designs
5. **Consider mobile** - Width 20 works well on smaller screens

### Tab Guidelines
1. **Overview first** - Start with high-level summary
2. **Logical grouping** - Group by workflow or data type
3. **Limit tabs** - 3-5 tabs is ideal
4. **Clear naming** - Tab names should be obvious

### Group Guidelines
1. **Common filters first** - Symbol, date range, etc.
2. **Limit groups** - 2-4 groups maximum
3. **Logical relationships** - Only group widgets that truly need sync
