# OpenBB App Builder Harness v2.0

A comprehensive pipeline for building OpenBB Workspace apps in a single shot.

## What's New in v2.0

- **Reference Example Support** - Convert Streamlit, Gradio, React, Flask apps to OpenBB
- **Smart Interview** - Structured requirements gathering with sensible defaults
- **Automated Validation** - 4 validation scripts for complete coverage
- **Browser Testing** - Claude-in-Chrome integration for end-to-end verification
- **Error Recovery** - Auto-fix common issues with retry logic

## Quick Start

### Option 1: Build from Description
```
"Build an OpenBB app that shows crypto prices from CoinGecko"
```

### Option 2: Convert Existing App
```
"Convert this Streamlit app to OpenBB:

import streamlit as st
import yfinance as yf

symbol = st.selectbox("Symbol", ["AAPL", "GOOGL"])
data = yf.download(symbol)
st.line_chart(data["Close"])
st.dataframe(data)
"
```

### Option 3: Quick Mode (Minimal Questions)
```
"Build a stock screener app, quick mode"
```

## Pipeline Phases

```
┌────────────────────────────────────────────────────────────────────────────┐
│                      OPENBB APP BUILDER PIPELINE v2.0                      │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  INPUT TYPES SUPPORTED                                                     │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │ Description │ │  Streamlit  │ │   Gradio    │ │ React/Vue   │          │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └──────┬──────┘          │
│         └───────────────┴───────────────┴───────────────┘                  │
│                                    │                                       │
│                                    ▼                                       │
│                                                                            │
│   PHASE 1      PHASE 2       PHASE 3      PHASE 4      PHASE 5            │
│  ┌────────┐  ┌──────────┐  ┌─────────┐  ┌────────┐  ┌─────────┐           │
│  │Interview│->│Widget    │->│Dashboard│->│Planner │->│Builder  │           │
│  │         │  │Metadata  │  │Layout   │  │        │  │         │           │
│  └────────┘  └──────────┘  └─────────┘  └────────┘  └─────────┘           │
│       │           │             │            │           │                 │
│       v           v             v            v           v                 │
│   APP-SPEC.md (requirements + widgets + layout)      main.py              │
│                                             PLAN.md   widgets.json         │
│                                                       apps.json            │
│                                                                            │
│   PHASE 6           PHASE 7                                                │
│  ┌───────────┐    ┌──────────┐                                            │
│  │Validation │ -> │Tester    │ -> SUCCESS!                                │
│  │           │    │(Browser) │                                            │
│  └───────────┘    └──────────┘                                            │
│       │                │                                                   │
│       v                v                                                   │
│   Pass/Fail        Screenshots + Test Report                              │
│       │                                                                    │
│       └── If fail: Auto-fix → Retry (max 3x)                              │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

## Validation Scripts

```bash
# Validate widgets.json
python scripts/validate_widgets.py apps/my-app/

# Validate apps.json
python scripts/validate_apps.py apps/my-app/

# Run both validations
python scripts/validate_app.py apps/my-app/

# Test live endpoints (requires running server)
python scripts/validate_endpoints.py apps/my-app/ --base-url http://localhost:7779
```

## Supported Reference Frameworks

| Framework | Detection | Example Mapping |
|-----------|-----------|-----------------|
| Streamlit | `import streamlit` | st.dataframe → table widget |
| Gradio | `import gradio` | gr.Dataframe → table widget |
| Flask | `from flask import` | Route → endpoint |
| FastAPI | `from fastapi import` | Endpoint extraction |
| React | `useState`, `useEffect` | Component mapping |

## Mode Options

| Mode | Trigger | Behavior |
|------|---------|----------|
| Standard | (default) | User confirmation at each phase |
| Quick | "quick mode" | Sensible defaults, minimal questions |
| Verbose | "verbose" | Detailed explanations, educational |
| Reference | Code snippets | Auto-analyze and convert |

## Skills Reference

| Skill | Purpose |
|-------|---------|
| `openbb-app-builder` | Master orchestrator for entire pipeline |
| `app-interview` | Requirements gathering + reference analysis |
| `widget-metadata` | Widget specification definitions |
| `dashboard-layout` | Dashboard layout design |
| `app-planner` | Generate PLAN.md |
| `openbb-app` | Core OpenBB implementation knowledge |
| `app-tester` | Browser-based testing with Claude-in-Chrome |

## Directory Structure

```
.claude/
├── README.md                    # This file
├── HARNESS_ARCHITECTURE.md      # Detailed architecture documentation
└── skills/
    ├── openbb-app.md           # Core OpenBB implementation knowledge
    ├── openbb-app-builder.md   # Master orchestrator
    ├── app-interview.md        # Requirements + reference analysis
    ├── widget-metadata.md      # Widget definitions
    ├── dashboard-layout.md     # Layout design
    ├── app-planner.md          # Plan generation
    └── app-tester.md           # Browser testing

scripts/
├── validate_widgets.py         # Widget configuration validation
├── validate_apps.py            # Dashboard layout validation
├── validate_app.py             # Combined validation
└── validate_endpoints.py       # Live endpoint testing
```

## Generated App Structure

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

## Using Individual Skills

You can invoke skills individually:

```
# Just interview
"Let's do an app interview for my new idea"

# Just widget design
"Help me define the widgets for my app"

# Just validation
"Validate my widgets.json"

# Just testing
"Test my app in the browser"
```

## Error Recovery

The harness includes automatic error recovery:

1. **Validation Errors**: Automatically fixes and re-validates
2. **Build Errors**: Diagnoses and corrects issues
3. **Test Failures**: Analyzes and suggests fixes
4. **Maximum 3 retries** per phase before asking user

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Widget not loading | Check endpoint response format |
| CORS error | Add origin to FastAPI CORS config |
| 404 on endpoint | Verify @app.get decorator |
| Validation fails | Run validation script for details |
| Browser test fails | Ensure backend is running |

## Related Resources

- [HARNESS_ARCHITECTURE.md](./HARNESS_ARCHITECTURE.md) - Detailed architecture and flow diagrams
- [OpenBB Workspace Docs](https://docs.openbb.co/workspace)
- [Backend Examples](../getting-started/)
