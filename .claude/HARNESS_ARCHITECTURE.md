# OpenBB App Builder Harness - Architecture Document v2.0

## Overview

This document describes a comprehensive harness for building OpenBB Workspace apps in a single shot. The harness consists of multiple interconnected skills and validation tools that guide the user through the entire app creation lifecycle.

## Key Features

- **Reference Example Support**: Accept Streamlit, Gradio, React, Flask code and convert to OpenBB
- **Smart Interview**: Structured requirements gathering with sensible defaults
- **Automated Validation**: Scripts to validate widgets.json, apps.json, and live endpoints
- **Browser Testing**: Claude-in-Chrome integration for end-to-end testing
- **Error Recovery**: Auto-fix common issues with retry logic

---

## Harness Philosophy

The goal is to transform app creation from a confusing multi-step journey into a guided, repeatable pipeline that:

1. **Accepts multiple input types** - Description, code, screenshots
2. **Gathers complete requirements upfront** - No surprises later
3. **Validates at each stage** - Catch errors early
4. **Provides confirmable artifacts** - User signs off before proceeding
5. **Tests automatically** - Verify before declaring success
6. **Self-corrects** - Loop back on failures

---

## Pipeline Architecture

```
┌────────────────────────────────────────────────────────────────────────────┐
│                      OPENBB APP BUILDER HARNESS v2.0                       │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  INPUT TYPES SUPPORTED                                                     │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │ Description │ │  Streamlit  │ │   Gradio    │ │ React/Vue   │          │
│  │   "Build    │ │   import    │ │   import    │ │  useState   │          │
│  │    app..."  │ │  streamlit  │ │   gradio    │ │  useEffect  │          │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └──────┬──────┘          │
│         │               │               │               │                  │
│         └───────────────┴───────────────┴───────────────┘                  │
│                                    │                                       │
│                                    ▼                                       │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                         PHASE 1: INTERVIEW                           │  │
│  │  ┌─────────────────────┐    ┌─────────────────────────────────────┐  │  │
│  │  │ Interactive Mode    │ OR │ Reference Analysis Mode             │  │  │
│  │  │ - Ask questions     │    │ - Parse code/screenshots            │  │  │
│  │  │ - Suggest defaults  │    │ - Extract components                │  │  │
│  │  │ - Gather specs      │    │ - Map to OpenBB widgets             │  │  │
│  │  └─────────────────────┘    └─────────────────────────────────────┘  │  │
│  │                                    │                                  │  │
│  │                                    ▼                                  │  │
│  │                           APP-SPEC.md (Artifact)                      │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                    │                                       │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                  │
│  │   PHASE 2   │────▶│   PHASE 3   │────▶│   PHASE 4   │                  │
│  │   WIDGET    │     │  DASHBOARD  │     │   PLANNER   │                  │
│  │  METADATA   │     │   LAYOUT    │     │             │                  │
│  └─────────────┘     └─────────────┘     └─────────────┘                  │
│        │                   │                   │                          │
│        ▼                   ▼                   ▼                          │
│  Widget specs        Tab structure         PLAN.md                        │
│  appended to         appended to           Step-by-step                   │
│  APP-SPEC.md         APP-SPEC.md           implementation                 │
│                                                                            │
│                                    │                                       │
│                                    ▼                                       │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                         PHASE 5: BUILDER                             │  │
│  │                                                                       │  │
│  │  Creates:   main.py │ widgets.json │ apps.json │ requirements.txt   │  │
│  │             Dockerfile │ .env.example │ README.md                    │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                    │                                       │
│                                    ▼                                       │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                       PHASE 6: VALIDATION                            │  │
│  │                                                                       │  │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐   │  │
│  │  │ validate_       │  │ validate_       │  │ validate_           │   │  │
│  │  │ widgets.py      │  │ apps.py         │  │ endpoints.py        │   │  │
│  │  │                 │  │                 │  │ (live testing)      │   │  │
│  │  │ • Schema check  │  │ • Tab structure │  │ • HTTP requests     │   │  │
│  │  │ • Valid types   │  │ • Layout grid   │  │ • Response format   │   │  │
│  │  │ • Params valid  │  │ • Widget refs   │  │ • Error handling    │   │  │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────────┘   │  │
│  │                                                                       │  │
│  │           ┌────────────────────────────────────────────────┐          │  │
│  │           │  If validation fails:                          │          │  │
│  │           │  1. Analyze errors                             │          │  │
│  │           │  2. Apply auto-fixes                           │          │  │
│  │           │  3. Re-run validation (max 3 retries)          │          │  │
│  │           │  4. Ask user if still failing                  │          │  │
│  │           └────────────────────────────────────────────────┘          │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                    │                                       │
│                                    ▼                                       │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                       PHASE 7: TESTING                               │  │
│  │                   (Claude-in-Chrome Browser Automation)              │  │
│  │                                                                       │  │
│  │  1. Start backend server (uvicorn main:app --port 7779)              │  │
│  │  2. Navigate to OpenBB Workspace (pro.openbb.dev)                    │  │
│  │  3. Add backend to Data Connectors                                   │  │
│  │  4. Open app dashboard                                               │  │
│  │  5. Verify each widget loads                                         │  │
│  │  6. Check console for errors                                         │  │
│  │  7. Take screenshots                                                 │  │
│  │  8. Generate test report                                             │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                    │                                       │
│                          ┌─────────┴─────────┐                            │
│                          │                   │                            │
│                     ┌────▼────┐         ┌────▼────┐                       │
│                     │ SUCCESS │         │  FAIL   │                       │
│                     └────┬────┘         └────┬────┘                       │
│                          │                   │                            │
│                          ▼                   ▼                            │
│                    App ready!          Loop back with                     │
│                    Deploy to           error context                      │
│                    Fly.dev             for auto-fix                       │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Skills Reference

| Skill | File | Triggers | Purpose |
|-------|------|----------|---------|
| `openbb-app-builder` | `openbb-app-builder.md` | "build openbb app", "convert to openbb" | Master orchestrator |
| `app-interview` | `app-interview.md` | "app interview", "convert streamlit" | Requirements + reference analysis |
| `widget-metadata` | `widget-metadata.md` | "define widgets" | Widget specifications |
| `dashboard-layout` | `dashboard-layout.md` | "dashboard layout" | Layout design |
| `app-planner` | `app-planner.md` | "implementation plan" | Generate PLAN.md |
| `openbb-app` | `openbb-app.md` | "openbb widget" | Core implementation knowledge |
| `app-tester` | `app-tester.md` | "test app", "add backend" | Browser-based testing |

---

## Validation Scripts

### validate_widgets.py

Validates `widgets.json` against the OpenBB schema.

```bash
python scripts/validate_widgets.py apps/my-app/
```

**Checks:**
- Required fields (name, type, endpoint)
- Valid widget types (table, chart, metric, etc.)
- Parameter configurations
- Column definitions for tables
- Grid data ranges (10-40 width, 4-100 height)
- Render and formatter function names

### validate_apps.py

Validates `apps.json` against the OpenBB schema.

```bash
python scripts/validate_apps.py apps/my-app/
```

**Checks:**
- Tab structure and naming
- Layout positions (x, y, w, h)
- Widget references exist in widgets.json
- No overlapping widgets
- Group configurations

### validate_app.py

Runs both validators in sequence.

```bash
python scripts/validate_app.py apps/my-app/
```

### validate_endpoints.py

Tests live endpoint responses (requires running server).

```bash
# Start server first
uvicorn apps/my-app/main:app --port 7779 &

# Run endpoint validation
python scripts/validate_endpoints.py apps/my-app/ --base-url http://localhost:7779
```

**Checks:**
- Server is running
- /widgets.json returns valid array
- /apps.json returns valid config
- Each widget endpoint responds
- Response format matches widget type
- Response times

---

## Reference Example Support

### Supported Frameworks

| Framework | Detection | Component Mapping |
|-----------|-----------|-------------------|
| Streamlit | `import streamlit` | st.dataframe→table, st.line_chart→chart |
| Gradio | `import gradio` | gr.Dataframe→table, gr.Plot→chart |
| Flask | `from flask import` | Route analysis, return type inference |
| FastAPI | `from fastapi import` | Endpoint extraction, param mapping |
| React | `useState`, `useEffect` | Component structure, fetch analysis |

### Mapping Rules

```
Streamlit                    OpenBB Widget Type
─────────────────────────────────────────────────
st.dataframe()        →      table
st.table()            →      table
st.line_chart()       →      chart
st.area_chart()       →      chart
st.bar_chart()        →      chart
st.plotly_chart()     →      chart
st.metric()           →      metric
st.markdown()         →      markdown
st.text()             →      markdown
st.image()            →      html/markdown
st.selectbox()        →      param (endpoint)
st.multiselect()      →      param (endpoint, multiSelect)
st.slider()           →      param (number)
st.number_input()     →      param (number)
st.text_input()       →      param (text)
st.date_input()       →      param (date)
st.checkbox()         →      param (boolean)
st.tabs()             →      dashboard tabs
st.columns()          →      layout structure
st.sidebar            →      parameter groups
```

---

## Directory Structure

### Harness Structure

```
.claude/
├── README.md                    # Quick start guide
├── HARNESS_ARCHITECTURE.md      # This document
└── skills/
    ├── openbb-app.md           # Core OpenBB implementation knowledge
    ├── openbb-app-builder.md   # Master orchestrator
    ├── app-interview.md        # Requirements + reference analysis
    ├── widget-metadata.md      # Widget definitions
    ├── dashboard-layout.md     # Layout design
    ├── app-planner.md          # Plan generation
    └── app-tester.md           # Browser testing

scripts/
├── validate_widgets.py         # Widget validation
├── validate_apps.py            # Apps validation
├── validate_app.py             # Combined validation
└── validate_endpoints.py       # Live endpoint testing
```

### Generated App Structure

```
apps/{app-name}/
├── APP-SPEC.md        # Requirements and specifications
├── PLAN.md            # Implementation plan
├── main.py            # FastAPI application
├── widgets.json       # Widget configurations
├── apps.json          # Dashboard layout
├── requirements.txt   # Python dependencies
├── Dockerfile         # Docker configuration
├── .env.example       # Environment template
└── README.md          # App documentation
```

---

## Mode Configurations

### Standard Mode (Default)
- User confirmation at each phase
- Detailed explanations
- Best for first-time users

### Quick Mode
Trigger: "quick mode", "fast", "minimal"
- Sensible defaults
- Minimal interruptions
- Single final confirmation

### Verbose Mode
Trigger: "verbose", "teach me", "explain"
- Detailed explanations
- Educational approach
- Best for learning

### Reference Mode
Trigger: Code snippets, "convert this"
- Analyze provided code
- Auto-extract components
- Map to OpenBB equivalents

---

## Error Recovery

### Auto-Fix Patterns

| Error Type | Detection | Auto-Fix |
|------------|-----------|----------|
| Missing required field | Validation error | Add with sensible default |
| Invalid widget type | Not in VALID_TYPES | Correct to closest match |
| Widget not found | Reference check | Add widget or fix reference |
| Overlapping layout | Position check | Adjust x/y coordinates |
| Invalid param type | Not in VALID_PARAMS | Correct to valid type |
| CORS error | Console/network | Add missing origin |

### Retry Logic

```python
MAX_RETRIES = 3

for attempt in range(MAX_RETRIES):
    result = run_validation()
    if result.success:
        break

    errors = result.errors
    for error in errors:
        fix = identify_fix(error)
        apply_fix(fix)

    if attempt == MAX_RETRIES - 1 and not result.success:
        ask_user_for_guidance()
```

---

## Usage Examples

### Example 1: Description-Based

```
User: Build an OpenBB app that shows crypto prices from CoinGecko

Claude: [Runs interview]
→ Gathers requirements
→ Defines widgets: prices table, chart, metrics
→ Creates 2-tab layout
→ Builds complete app
→ Validates
→ Tests in browser
```

### Example 2: Streamlit Conversion

```
User: Convert this Streamlit app to OpenBB:

import streamlit as st
import yfinance as yf

symbol = st.selectbox("Symbol", ["AAPL", "GOOGL"])
data = yf.download(symbol)
st.line_chart(data["Close"])
st.dataframe(data)

Claude: [Analyzes code]
→ Detects: st.selectbox, st.line_chart, st.dataframe
→ Maps to: param(endpoint), chart, table
→ Creates widgets.json with 2 widgets
→ Builds complete app
```

### Example 3: Quick Mode

```
User: Build a stock screener app, quick mode

Claude: [Minimal questions]
→ Uses defaults: table widget, filter params
→ Single-tab layout
→ Builds and validates
→ Done in one shot
```

---

## Benefits

1. **Consistency**: Every app follows the same structure
2. **Quality**: Multiple validation layers catch errors
3. **Speed**: Automates repetitive tasks
4. **Flexibility**: Accepts multiple input types
5. **Learning**: Users see the full process
6. **Recovery**: Self-correcting on failures
7. **Testing**: Browser automation verifies real behavior
8. **Documentation**: APP-SPEC.md and PLAN.md serve as docs

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Widget not loading | Wrong response format | Check endpoint returns correct type |
| CORS error | Missing origin | Add origin to FastAPI CORS config |
| 404 on endpoint | Route not registered | Verify @app.get decorator |
| Validation fails | Missing field | Run validation, fix reported errors |
| Browser test fails | Server not running | Start uvicorn first |

### Debug Commands

```bash
# Check server health
curl http://localhost:7779/

# Check widgets.json
curl http://localhost:7779/widgets.json | python -m json.tool

# Run full validation
python scripts/validate_app.py apps/my-app/

# Test specific endpoint
curl "http://localhost:7779/my_widget?param=value"
```
