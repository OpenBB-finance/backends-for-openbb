---
name: app-planner
description: Generate a comprehensive implementation plan (PLAN.md) for building the app
triggers:
  - app planner
  - implementation plan
  - generate plan
  - plan app
---

# App Planner Skill

You are generating a comprehensive, step-by-step implementation plan for building an OpenBB Workspace app. This happens after all requirements are gathered (app-interview, widget-metadata, dashboard-layout) and before building (app-builder).

## Prerequisites

Read the complete APP-SPEC.md which should contain:
- App requirements and configuration
- Complete widget definitions
- Dashboard layout with tabs and positions
- Parameter groups

## PLAN.md Structure

Create `apps/{app-name}/PLAN.md` with these sections:

```markdown
# Implementation Plan: {App Name}

**Generated**: {date}
**Status**: Ready for Implementation

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Folder Structure](#folder-structure)
3. [Core Implementation](#core-implementation)
4. [Widget Endpoints](#widget-endpoints)
5. [Supporting Endpoints](#supporting-endpoints)
6. [Configuration Files](#configuration-files)
7. [Deployment Files](#deployment-files)
8. [Validation Checklist](#validation-checklist)

---

## Prerequisites

### System Requirements
- Python 3.10+
- pip (Python package manager)

### Dependencies
```bash
pip install fastapi uvicorn plotly pandas requests python-dotenv
```

### Environment Setup
Create `.env` file with:
```
{list environment variables}
```

---

## Folder Structure

Create the following structure:

```
apps/{app-name}/
├── main.py              # FastAPI application with @register_widget decorators
├── apps.json            # Dashboard layout configuration
├── requirements.txt     # Python dependencies
├── Dockerfile           # Docker configuration
├── .env.example         # Environment template
├── .env                 # Local environment (git-ignored)
└── README.md            # App documentation
```

**Note**: The `@register_widget` decorator pattern is recommended (keeps config close to code), but a separate `widgets.json` file is also valid if the user prefers.

### Step 1.1: Create Directory
```bash
mkdir -p apps/{app-name}
cd apps/{app-name}
```

---

## Core Implementation

### Step 2.1: Create main.py Base

```python
"""
{App Name} - OpenBB Workspace Backend

{Description}
"""

from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from functools import wraps
import asyncio
import json
from typing import Optional, List
from datetime import datetime

# Initialize FastAPI app
app = FastAPI(
    title="{App Name}",
    description="{Description}",
    version="1.0.0"
)

# CORS Configuration - Required for OpenBB Workspace
origins = [
    "https://pro.openbb.co",
    "https://pro.openbb.dev",
    "http://localhost:1420"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Widget Registry
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
            widget_config.setdefault("widgetId", endpoint)
            WIDGETS[widget_config["widgetId"]] = widget_config

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

# Core Endpoints
@app.get("/")
def root():
    """Health check endpoint."""
    return {"status": "ok", "app": "{App Name}"}

@app.get("/widgets.json")
def get_widgets():
    """Return widget configurations as dict with widget IDs as keys."""
    return WIDGETS  # MUST be dict format, NOT a list

@app.get("/apps.json")
def get_apps():
    """Return dashboard configuration."""
    # Load from apps.json file or return inline config
    return {apps_config}
```

### Step 2.2: Add Theme Colors Helper

```python
def get_theme_colors(theme: str = "dark"):
    """Get color scheme based on theme."""
    if theme == "light":
        return {
            "text": "#333333",
            "grid": "rgba(128, 128, 128, 0.2)",
            "background": "rgba(255,255,255,0)",
            "primary": "#2E5090",
            "positive": "#00AA44",
            "negative": "#CC0000"
        }
    return {
        "text": "#ffffff",
        "grid": "rgba(128, 128, 128, 0.2)",
        "background": "rgba(0,0,0,0)",
        "primary": "#FF8000",
        "positive": "#00B140",
        "negative": "#F4284D"
    }
```

---

## Widget Endpoints

{For each widget, generate a detailed implementation step}

### Step 3.1: Implement {widget_id}

**Widget Configuration:**
```python
@register_widget({
    "name": "{widget_name}",
    "description": "{widget_description}",
    "type": "{widget_type}",
    "endpoint": "{widget_endpoint}",
    "category": "{category}",
    "gridData": {"w": {w}, "h": {h}},
    "params": [
        {param_definitions}
    ],
    {additional_config}
})
```

**Endpoint Implementation:**
```python
@app.get("/{widget_endpoint}")
def {widget_function}({parameters}):
    """
    {widget_description}

    Returns:
        {return_type_description}
    """
    {implementation_logic}

    return {return_statement}
```

**Expected Response Format:**
```json
{example_response}
```

**Notes:**
- {any implementation notes}
- {edge cases to handle}
- {error scenarios}

---

## Supporting Endpoints

{For dropdown endpoints, etc.}

### Step 4.1: Implement Options Endpoints

**Symbol Options:**
```python
@app.get("/symbols")
def get_symbols():
    """Return available symbols for dropdown."""
    return [
        {"label": "Bitcoin", "value": "BTC"},
        {"label": "Ethereum", "value": "ETH"},
        # ... more options
    ]
```

{Additional supporting endpoints}

---

## Configuration Files

### Step 5.1: Widget Configuration (via decorators)

**No separate widgets.json file needed!** Widget metadata is defined via `@register_widget` decorators in `main.py`. This keeps configuration close to code and easier to maintain.

The `/widgets.json` endpoint dynamically returns the WIDGETS registry.

### Step 5.2: Create apps.json

```json
{complete_apps_json}
```

### Step 5.3: Create requirements.txt

```
fastapi>=0.100.0
uvicorn>=0.22.0
plotly>=5.15.0
pandas>=2.0.0
requests>=2.31.0
python-dotenv>=1.0.0
{additional_dependencies}
```

---

## Deployment Files

### Step 6.1: Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 7779

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7779"]
```

### Step 6.2: Create .env.example

```bash
# {App Name} Environment Variables
# Copy this file to .env and fill in values

# API Configuration
{API_KEY}=your_api_key_here

# Server Configuration
PORT=7779
HOST=0.0.0.0
```

### Step 6.3: Create README.md

```markdown
# {App Name}

{Description}

## Setup

1. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your values
   ```

4. Run the server:
   ```bash
   uvicorn main:app --reload --port 7779
   ```

## Adding to OpenBB Workspace

1. Go to Settings > Data Connectors
2. Click "Add Custom Backend"
3. Enter URL: `http://localhost:7779`
4. {Add API key if required}

## Widgets

| Widget | Description | Type |
|--------|-------------|------|
{widget_table}

## API Reference

### GET /
Health check endpoint.

### GET /widgets.json
Returns widget configurations.

### GET /apps.json
Returns dashboard layout.

{endpoint_docs}
```

---

## Validation Checklist

After implementation, verify:

### Best Practices Check
- [ ] No `runButton: true` unless heavy computation needed
- [ ] Widget heights are reasonable (tables: h=12-18, charts: h=12-15, metrics: h=4-6)
- [ ] Chart widgets have `"raw": True` for AI data access
- [ ] Plotly charts have NO title (widget provides it)
- [ ] `/widgets.json` returns dict format (not array)

### Schema Validation
- [ ] Run `python scripts/validate_widgets.py apps/{app-name}/`
- [ ] Run `python scripts/validate_apps.py apps/{app-name}/`

### Endpoint Testing
- [ ] GET / returns status ok
- [ ] GET /widgets.json returns valid array
- [ ] GET /apps.json returns valid config

### Widget Testing
{for each widget}
- [ ] {widget_id}: Returns expected data format
- [ ] {widget_id}: Handles parameters correctly
- [ ] {widget_id}: Error handling works

### Integration Testing
- [ ] Backend added to OpenBB Workspace
- [ ] All widgets visible in widget list
- [ ] Dashboard loads correctly
- [ ] Parameter syncing works

---

## Execution Order

1. Create folder structure
2. Create main.py with base structure
3. Add widget endpoints one by one
4. Add supporting endpoints
5. Create configuration files
6. Create deployment files
7. Run validation scripts
8. Test in browser

---

## Estimated Complexity

- **Lines of Code**: ~{loc} lines
- **Files**: {file_count} files
- **Endpoints**: {endpoint_count} endpoints
- **Widgets**: {widget_count} widgets
```

## Plan Generation Logic

### Analyzing Widgets

For each widget type, generate appropriate implementation:

**Table Widget:**
- Return list of dicts
- Include column definitions
- Handle sorting/filtering params

**Chart Widget:**
- Import plotly
- Create figure with theme support
- Handle raw mode for AI

**Metric Widget:**
- Return JSONResponse with list of metrics
- Include label, value, delta

**Newsfeed Widget:**
- Return list of articles
- Include title, date, author, excerpt, body

**Markdown Widget:**
- Return markdown string
- Handle images if needed

**Omni Widget:**
- Use POST method
- Return data_format specification
- Handle parse_as type

### Dependencies Analysis

Based on widgets, determine requirements:

```python
dependencies = ["fastapi", "uvicorn"]

if has_chart_widgets:
    dependencies.append("plotly")

if uses_dataframes:
    dependencies.append("pandas")

if calls_external_api:
    dependencies.append("requests")

if uses_env_vars:
    dependencies.append("python-dotenv")

if uses_websocket:
    dependencies.append("websockets")
```

### Error Handling Template

For each endpoint:

```python
try:
    # Implementation
    data = fetch_data(params)
    return data
except ExternalAPIError as e:
    raise HTTPException(status_code=502, detail=f"External API error: {e}")
except ValidationError as e:
    raise HTTPException(status_code=400, detail=f"Invalid parameters: {e}")
except Exception as e:
    raise HTTPException(status_code=500, detail=f"Internal error: {e}")
```

## Output

Save the plan to `apps/{app-name}/PLAN.md`

## User Confirmation

After generating the plan:

```markdown
## Plan Generated

**Location**: apps/{app-name}/PLAN.md

**Summary**:
- {widget_count} widgets to implement
- {endpoint_count} endpoints total
- Estimated ~{loc} lines of code

**Files to Create**:
1. main.py - Core application
2. widgets.json - Widget configs
3. apps.json - Dashboard layout
4. requirements.txt - Dependencies
5. Dockerfile - Container config
6. .env.example - Environment template
7. README.md - Documentation

Ready to start implementation?
```

Ask: "Would you like me to proceed with building the app according to this plan?"

## Next Step

After confirmation:

"Plan ready. Proceeding to **App Builder** to implement the plan."

This triggers the actual building phase using the openbb-app skill enhanced with plan execution.
