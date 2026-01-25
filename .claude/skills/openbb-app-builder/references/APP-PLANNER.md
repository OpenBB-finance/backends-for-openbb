# App Planner Reference

Guide for generating comprehensive implementation plans.

## PLAN.md Structure

Create `{app-name}/PLAN.md` with these sections:

```markdown
# Implementation Plan: {App Name}

**Generated**: {date}
**Status**: Ready for Implementation

---

## Prerequisites

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

```
{app-name}/
├── main.py              # FastAPI application
├── widgets.json         # Widget configurations
├── apps.json            # Dashboard layout
├── requirements.txt     # Python dependencies
├── Dockerfile           # Docker configuration
├── .env.example         # Environment template
└── README.md            # Documentation
```

---

## Core Implementation

### main.py Base Structure

```python
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional
import json

app = FastAPI(title="{App Name}")

# CORS Configuration
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
    return {"status": "ok", "app": "{App Name}"}

@app.get("/widgets.json")
def get_widgets():
    with open("widgets.json") as f:
        return json.load(f)

@app.get("/apps.json")
def get_apps():
    with open("apps.json") as f:
        return json.load(f)
```

### Theme Colors Helper

```python
def get_theme_colors(theme: str = "dark"):
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

## Widget Endpoint Templates

### Table Widget
```python
@app.get("/my_table")
def my_table(
    param1: str = Query("default"),
    limit: int = Query(100)
):
    # Fetch/compute data
    data = [
        {"col1": "value1", "col2": 123},
        {"col1": "value2", "col2": 456},
    ]
    return data
```

### Chart Widget
```python
import plotly.graph_objects as go

@app.get("/my_chart")
def my_chart(
    symbol: str = Query("AAPL"),
    theme: str = Query("dark"),
    raw: bool = Query(False)
):
    # Fetch data
    dates = ["2024-01-01", "2024-01-02"]
    prices = [100, 105]

    # Return raw data for AI
    if raw:
        return [{"date": d, "price": p} for d, p in zip(dates, prices)]

    # Build Plotly figure (NO title - widget provides it)
    colors = get_theme_colors(theme)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=prices, mode="lines"))
    fig.update_layout(
        template="plotly_dark" if theme == "dark" else "plotly_white",
        paper_bgcolor=colors["background"],
        plot_bgcolor=colors["background"],
    )

    return JSONResponse(content=json.loads(fig.to_json()))
```

### Metric Widget
```python
@app.get("/my_metrics")
def my_metrics():
    return [
        {"label": "Total Value", "value": "$1.5M", "delta": "+2.5%"},
        {"label": "Daily Change", "value": "$25K", "delta": "-1.2%"},
    ]
```

---

## Configuration Files

### requirements.txt
```
fastapi>=0.100.0
uvicorn>=0.22.0
plotly>=5.15.0
pandas>=2.0.0
requests>=2.31.0
python-dotenv>=1.0.0
```

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 7779

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7779"]
```

### .env.example
```bash
# API Configuration
API_KEY=your_api_key_here

# Server Configuration
PORT=7779
HOST=0.0.0.0
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
- [ ] Run `python scripts/validate_widgets.py {app-path}/`
- [ ] Run `python scripts/validate_apps.py {app-path}/`

### Endpoint Testing
- [ ] GET / returns status ok
- [ ] GET /widgets.json returns valid dict
- [ ] GET /apps.json returns valid config
- [ ] All widget endpoints return expected data

---

## Execution Order

1. Create folder structure
2. Create main.py with base structure
3. Add widget endpoints one by one
4. Create widgets.json
5. Create apps.json
6. Create requirements.txt
7. Create Dockerfile and .env.example
8. Run validation scripts
9. Test locally with uvicorn
```

---

## Error Handling Template

For each endpoint:

```python
try:
    data = fetch_data(params)
    return data
except ExternalAPIError as e:
    raise HTTPException(status_code=502, detail=f"External API error: {e}")
except ValidationError as e:
    raise HTTPException(status_code=400, detail=f"Invalid parameters: {e}")
except Exception as e:
    raise HTTPException(status_code=500, detail=f"Internal error: {e}")
```
