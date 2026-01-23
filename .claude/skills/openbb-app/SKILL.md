---
name: openbb-app
description: Build custom backends and widgets for OpenBB Workspace
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
   - `GET /widgets.json` - Return dict of widget configurations (NOT array)
   - `GET /apps.json` - (Optional) Return array of app/dashboard configurations
4. **Return proper Content-Type**: `application/json` for data endpoints

## Repository Reference Examples

This repository contains working examples you can reference:

```
getting-started/
├── hello-world/              # Minimal starter template
└── reference-backend/        # Comprehensive reference with all widget types

widget-examples/
├── widget-types/             # Examples for each widget type
├── parameters-types/         # Parameter examples
├── ssrm_mode/               # Server-Side Row Model for large datasets
└── database-connectors/      # Database integration examples
```

## Quick Start

When a user wants to build an OpenBB app:
1. Ask what language/framework they prefer (recommend Python/FastAPI if unsure)
2. Ask what data they want to display and what interactions they need
3. **Propose a layout for approval BEFORE writing any code**
4. Recommend appropriate widget types based on their use case
5. Generate a complete backend with all necessary endpoints
6. Create the apps.json configuration if they want a custom dashboard layout

## Best Practices

### runButton: false by default
**Do NOT set `runButton: true` unless the endpoint performs heavy computation** like Monte Carlo simulations, complex ML inference, or queries that take >5 seconds.

### Reasonable Widget Heights
- **Metrics**: h=4-6
- **Tables**: h=12-18 (not 20+)
- **Charts**: h=12-15 (not 20+)
- **Markdown**: h=6-10

### Widget params vs Endpoint parameters

**CRITICAL**: Defining a parameter in your FastAPI endpoint does NOT automatically create a UI dropdown. You must define `params` in BOTH places:

1. **Endpoint** - Handles the backend request
2. **Widget config `params`** - Creates the UI dropdown

### Charts: Prefer AgGrid Charts Over Plotly

When displaying chart data, prefer using a table widget with chart view enabled. This allows users to:
- Access the underlying raw data directly
- Switch between table and chart views
- Use AgGrid's built-in chart types

When using Plotly:
1. **Don't add a title** - the widget name already displays as the title
2. **Always add `raw: True`** in widget config for AI data access
3. **Support the `raw` query parameter** to return raw data

### widgets.json Format

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
```

## Backend Architecture (Python/FastAPI)

```python
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from functools import wraps
import asyncio

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
    """Decorator to register widget configuration."""
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

@app.get("/")
def root():
    return {"message": "OpenBB Custom Backend"}

@app.get("/widgets.json")
def get_widgets():
    return WIDGETS  # Return as dict with widget IDs as keys
```

## Widget Types

### 1. Table Widget (type: "table")
Display tabular data with sorting, filtering, and chart conversion.

### 2. Chart Widget (type: "chart")
Interactive Plotly charts with theme support.

### 3. Markdown Widget (type: "markdown")
Display formatted text content.

### 4. Metric Widget (type: "metric")
Display KPIs with labels, values, and deltas.

### 5. Newsfeed Widget (type: "newsfeed")
Display articles with title, date, author, excerpt, and body.

### 6. HTML Widget (type: "html")
Custom HTML content (no JavaScript execution for security).

### 7. PDF/File Viewer Widget (type: "pdf" / "multi_file_viewer")
Display PDF files via base64 or URL.

### 8. TradingView Chart (type: "advanced_charting")
Professional charting with UDF protocol.
**⚠️ Limitation**: Does NOT support parameter-based grouping.

### 9. Live Grid Widget (WebSocket)
Real-time data updates via WebSocket.

### 10. Omni Widget (type: "omni")
Dynamic content type based on response. Uses POST method.

### 11. SSRM Table (Server-Side Row Model)
For large datasets (200,000+ rows) with server-side sorting, filtering, pagination.

## Widget Type Capabilities for Grouping

| Widget Type | Param Grouping Support |
|-------------|------------------------|
| `table` | ✅ Yes |
| `chart` (Plotly) | ✅ Yes |
| `metric` | ✅ Yes |
| `markdown` | ✅ Yes |
| `newsfeed` | ✅ Yes |
| `advanced_charting` (TradingView) | ❌ **NO** |

## Parameter Types

- **text** - Text input
- **number** - Number input
- **boolean** - Toggle
- **date** - Date picker (supports modifiers like `$currentDate-1M`)
- **endpoint** - Dynamic dropdown from API endpoint
- **tabs** - Tab navigation
- **form** - Input form with POST submission

## Column Definition Properties

| Property | Type | Description |
|----------|------|-------------|
| `field` | string | JSON data field name |
| `headerName` | string | Column header display name |
| `cellDataType` | string | `text`, `number`, `boolean`, `date`, `dateString`, `object` |
| `formatterFn` | string | `int`, `none`, `percent`, `normalized`, `normalizedPercent`, `dateToYear` |
| `renderFn` | string/array | `greenRed`, `titleCase`, `hoverCard`, `cellOnClick`, `columnColor`, `showCellChange` |

**Note**: `"currency"` is NOT a valid formatterFn - use `"none"` instead.

## apps.json Specification

```json
[{
    "name": "My Dashboard",
    "description": "Custom financial dashboard",
    "img": "https://images.unsplash.com/photo-...",
    "allowCustomization": true,
    "tabs": {
        "overview": {
            "id": "overview",
            "name": "Overview",
            "layout": [
                {"i": "widget_id", "x": 0, "y": 0, "w": 20, "h": 10, "groups": ["Group 1"]}
            ]
        }
    },
    "groups": [
        {
            "name": "Group 1",
            "type": "endpointParam",
            "paramName": "symbol",
            "defaultValue": "AAPL"
        }
    ],
    "prompts": [
        "What is the current market sentiment?"
    ]
}]
```

### Group Naming Pattern

**CRITICAL**: Group names **MUST** follow the "Group N" pattern: `"Group 1"`, `"Group 2"`, etc.
Custom names like `"symbol-group"` will **fail silently**.

### Group Types

| Type | Use Case | Widget Association |
|------|----------|-------------------|
| `param` | Static dropdown | `widgetIds` in group |
| `endpointParam` | Dynamic dropdown | `groups` in layout items |

## Watchlist + Chart Pattern

Common pattern for financial apps where clicking a ticker updates a chart:

1. **Watchlist widget**: Table with `cellOnClick` and `groupBy`
2. **Chart widget**: Plotly chart (NOT TradingView)
3. **Both in same group**: Connected via `groups: ["Group 1"]`

```python
# Watchlist column with cellOnClick
{
    "field": "symbol",
    "renderFn": "cellOnClick",
    "renderFnParams": {
        "actionType": "groupBy",
        "groupByParamName": "symbol"
    }
}
```

## Development Workflow

1. Start with the template
2. Define your data sources
3. Choose widget types
4. Configure parameters
5. Test locally: `uvicorn main:app --reload --port 7779`
6. Add to OpenBB Workspace: Apps > Connect Backend

### Refreshing Changes

- **Widget config changes**: Right-click → "Refresh backend"
- **Python code changes**: Restart uvicorn if auto-reload doesn't work
- **Major structure changes**: Open fresh app instance from gallery

## Project Documentation

Every app needs:
- **README.md** - Setup instructions
- **requirements.txt** - All dependencies
- **.env.example** - Environment template (if using external APIs)
