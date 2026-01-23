---
name: dashboard-layout
description: Design the visual dashboard layout with tabs and widget positioning
---

# Dashboard Layout Skill

You are helping design the visual layout of an OpenBB Workspace dashboard. This happens after widget metadata definition (widget-metadata) and before implementation planning (app-planner).

## Prerequisites

Before starting, read APP-SPEC.md to understand:
- All defined widgets with their grid sizes
- Widget categories and relationships
- Parameter grouping needs

## Layout Concepts

### Grid System
- OpenBB Workspace uses a 40-column grid
- Widgets snap to grid positions
- Minimum widget width: 10 columns
- Maximum widget width: 40 columns (full width)
- Height is flexible (minimum 4 rows)

### Tabs
- Organize widgets into logical tabs
- Each tab has its own layout
- Users can customize within allowed bounds

### Parameter Groups
- Widgets with same parameter can be synced
- Groups appear in dashboard header
- Changing one updates all synced widgets

**Two group types:**

1. **`type: "param"`** - Static dropdown with hardcoded options
   - Uses `widgetIds` array to specify which widgets sync
   - Example: `{"type": "param", "paramName": "period", "defaultValue": "1M", "widgetIds": ["chart1", "chart2"]}`

2. **`type: "endpointParam"`** - Dynamic dropdown from API endpoint
   - Widgets reference the group via `groups: ["Group 1"]` in their layout items
   - Options come from the widget's `optionsEndpoint` parameter
   - Example: `{"type": "endpointParam", "paramName": "symbol", "defaultValue": "AAPL"}`

**CRITICAL - Group Naming Pattern**:
- Group names **MUST** follow the "Group N" pattern: `"Group 1"`, `"Group 2"`, `"Group 3"`, etc.
- Custom names like `"symbol-group"` or `"my-group"` will **fail silently** - widgets won't sync
- This is a common gotcha that causes hours of debugging

**IMPORTANT**: Always set `defaultValue` to a valid option value. Without it, widgets load with no selection and users must manually pick a value before seeing data.

**Widget Type Limitations for Grouping**:
- `advanced_charting` (TradingView) does **NOT** support parameter grouping
- If you need a chart that updates when clicking a watchlist row, use `chart` (Plotly) instead

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

### Tab 3: News
- Purpose: Market news and updates
- Widgets: market_news, analysis_reports
```

### Step 2: Create ASCII Layout

Use ASCII art to visualize each tab:

```
Grid: 40 columns wide
      0         10        20        30        40
      |---------|---------|---------|---------|

Row 0 ┌─────────────────────────────────────────┐
      │            [1: market_stats]            │
      │               w=40, h=4                 │
Row 4 ├────────────────────┬────────────────────┤
      │                    │                    │
      │  [2: price_chart]  │ [3: crypto_prices] │
      │     w=20, h=15     │     w=20, h=15     │
      │                    │                    │
      │                    │                    │
Row 19└────────────────────┴────────────────────┘
```

### Step 3: Calculate Positions

Convert ASCII to coordinates:

| Widget | x | y | w | h |
|--------|---|---|---|---|
| market_stats | 0 | 0 | 40 | 4 |
| price_chart | 0 | 4 | 20 | 15 |
| crypto_prices | 20 | 4 | 20 | 15 |

### Step 4: Define Parameter Groups

Identify widgets that should share parameters:

```markdown
## Groups

### Group: Symbol
- **Parameter**: symbol
- **Type**: param
- **Default**: BTC
- **Synced Widgets**: price_chart, holdings_table, transaction_history

### Group: Date Range
- **Parameter**: date_range
- **Type**: param
- **Default**: 1M
- **Synced Widgets**: price_chart, volume_chart
```

## Layout Templates

### Template: Overview Dashboard
```
┌─────────────────────────────────────────┐
│              [Metrics Bar]              │  <- w=40, h=4
│                 w=40, h=4               │
├───────────────────┬─────────────────────┤
│                   │                     │
│   [Main Chart]    │   [Data Table]      │  <- w=20 each, h=15
│     w=20, h=15    │     w=20, h=15      │
│                   │                     │
└───────────────────┴─────────────────────┘
```

### Template: Data Analysis
```
┌───────────────────┬─────────────────────┐
│                   │                     │
│   [Main Table]    │   [Summary Panel]   │  <- w=25, w=15
│     w=25, h=20    │     w=15, h=20      │
│                   │                     │
│                   ├─────────────────────┤
│                   │   [Quick Stats]     │
│                   │     w=15, h=8       │
└───────────────────┴─────────────────────┘
```

### Template: Multi-Chart
```
┌───────────────────┬─────────────────────┐
│   [Chart 1]       │   [Chart 2]         │
│     w=20, h=12    │     w=20, h=12      │
├───────────────────┼─────────────────────┤
│   [Chart 3]       │   [Chart 4]         │
│     w=20, h=12    │     w=20, h=12      │
└───────────────────┴─────────────────────┘
```

### Template: Full-Width Content
```
┌─────────────────────────────────────────┐
│              [Wide Table]               │
│                w=40, h=8                │
├─────────────────────────────────────────┤
│              [Wide Chart]               │
│                w=40, h=15               │
└─────────────────────────────────────────┘
```

### Template: Watchlist + Chart (Interactive)
```
┌─────────────────────────────────────────┐
│          [Watchlist Table]              │  <- w=40, h=8
│   Click ticker to update chart below    │     cellOnClick with groupBy
├─────────────────────────────────────────┤
│                                         │
│          [Price Chart]                  │  <- w=40, h=15
│   Updates when ticker clicked above     │     MUST be Plotly, not TradingView
│                                         │
└─────────────────────────────────────────┘
```

**Key requirements for this pattern:**
1. Both widgets in same group: `"groups": ["Group 1"]`
2. Watchlist symbol column has `renderFn: "cellOnClick"` with `groupByParamName`
3. Chart MUST be `type: "chart"` (Plotly) - TradingView doesn't support grouping
4. Both widgets have matching `paramName` and `optionsEndpoint`

### Template: News Feed
```
┌─────────────────────────────────────────┐
│              [News Feed]                │
│                w=40, h=25               │
│                                         │
│                                         │
│                                         │
└─────────────────────────────────────────┘
```

## Output Format

Append layout to APP-SPEC.md:

```markdown
## Dashboard Layout

### App Configuration
- **allowCustomization**: true
- **Image URL**: {optional icon URL}
- **Prompts**: {optional AI prompts for users}

### Tab: overview

**Purpose**: Main dashboard overview

**ASCII Layout**:
```
┌─────────────────────────────────────────┐
│            [1: market_stats]            │
│               w=40, h=4                 │
├────────────────────┬────────────────────┤
│                    │                    │
│  [2: price_chart]  │ [3: crypto_prices] │
│     w=20, h=15     │     w=20, h=15     │
│                    │                    │
└────────────────────┴────────────────────┘
```

**Layout Positions**:
| # | Widget ID | x | y | w | h |
|---|-----------|---|---|---|---|
| 1 | market_stats | 0 | 0 | 40 | 4 |
| 2 | price_chart | 0 | 4 | 20 | 15 |
| 3 | crypto_prices | 20 | 4 | 20 | 15 |

### Tab: news

**Purpose**: Market news and analysis

**ASCII Layout**:
```
┌─────────────────────────────────────────┐
│            [4: market_news]             │
│               w=40, h=20                │
│                                         │
│                                         │
└─────────────────────────────────────────┘
```

**Layout Positions**:
| # | Widget ID | x | y | w | h |
|---|-----------|---|---|---|---|
| 4 | market_news | 0 | 0 | 40 | 20 |

---

## Widget Reference

| # | Widget ID | Name | Type |
|---|-----------|------|------|
| 1 | market_stats | Market Statistics | metric |
| 2 | price_chart | Price Chart | chart |
| 3 | crypto_prices | Crypto Prices | table |
| 4 | market_news | Market News | newsfeed |

---

## Parameter Groups

| Group Name | Type | Parameter | Default | Widgets |
|------------|------|-----------|---------|---------|
| Symbol | param | symbol | BTC | price_chart, crypto_prices |

---

## Widget State (Optional Pre-configuration)

### price_chart
- **Default Params**: {symbol: "BTC", period: "1M"}
- **Default Chart View**: {enabled: false}

### crypto_prices
- **Default Params**: {limit: 50}
- **Column State**: {show all columns}
```

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

## Interactive Design

Ask user about preferences:

1. **Tab structure**: "I've suggested X tabs based on your widgets. Does this organization work, or would you prefer a different grouping?"

2. **Widget placement**: "I've placed [widget] at [position]. Would you like it in a different location?"

3. **Synced parameters**: "These widgets share the 'symbol' parameter. Should they be synced so changing one updates all of them?"

4. **Sizing**: "The default size for [widget] is [WxH]. Would you prefer it larger or smaller?"

## User Confirmation

Present final layout summary:

```markdown
## Layout Summary

### Tabs (2)
1. **Overview** - 3 widgets
2. **News** - 1 widget

### Total Widgets: 4

### Parameter Groups (1)
- Symbol (syncs 2 widgets)

### Visual Preview

**Overview Tab:**
┌─────────────────────────────────────────┐
│            [market_stats]               │
├────────────────────┬────────────────────┤
│   [price_chart]    │   [crypto_prices]  │
└────────────────────┴────────────────────┘

**News Tab:**
┌─────────────────────────────────────────┐
│            [market_news]                │
└─────────────────────────────────────────┘
```

Ask: "Does this layout work for your needs? Would you like any adjustments before we generate the implementation plan?"

## Next Step

After confirmation:

"Dashboard layout saved to APP-SPEC.md. Ready for the next step: **Implementation Planning**. Would you like to continue to generate the implementation plan?"

This allows the pipeline to continue to the app-planner skill.

## apps.json Preview

Show what the final apps.json will look like:

```json
{
  "name": "CryptoTracker",
  "description": "Cryptocurrency prices and market data",
  "allowCustomization": true,
  "tabs": {
    "overview": {
      "id": "overview",
      "name": "Overview",
      "layout": [
        {"i": "market_stats", "x": 0, "y": 0, "w": 40, "h": 4},
        {"i": "price_chart", "x": 0, "y": 4, "w": 20, "h": 15, "groups": ["Group 1"]},
        {"i": "crypto_prices", "x": 20, "y": 4, "w": 20, "h": 15, "groups": ["Group 1"]}
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
      "name": "Group 1",
      "type": "endpointParam",
      "paramName": "symbol",
      "defaultValue": "BTC"
    }
  ],
  "prompts": [
    "What's the current price of Bitcoin?",
    "Show me the top gainers today",
    "Analyze the market trends"
  ]
}
```

**CRITICAL**: Note that group names use "Group 1" pattern, NOT custom names like "Symbol" or "Account".

**Group Types Explained:**

| Type | Use Case | Widget Association | Options Source |
|------|----------|-------------------|----------------|
| `param` | Static dropdown | `widgetIds` in group | `options` in widget param |
| `endpointParam` | Dynamic dropdown | `groups` in layout items | `optionsEndpoint` in widget param |

**Note**: For `endpointParam`, widgets must have a matching parameter with `type: "endpoint"` and `optionsEndpoint` defined in their metadata.
