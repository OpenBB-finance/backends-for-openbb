# OpenBB App Builder Skill

A comprehensive skill for building OpenBB Workspace apps in a single shot.

## File Structure

| File | Purpose | Audience |
|------|---------|----------|
| `skills/openbb-app-builder/SKILL.md` | Main orchestrator - Claude reads this | Claude |
| `skills/openbb-app-builder/references/*.md` | Phase-specific reference docs | Claude (on-demand) |
| `skills/openbb-app-builder/README.md` | Skill documentation for skills.sh | Humans |
| `README.md` | This quick start guide | Humans |

## Install via skills.sh

```bash
npx skills add OpenBB-finance/backends-for-openbb
```

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
Phase 1: Interview    → Gather requirements, analyze references
Phase 2: Widgets      → Define widget metadata
Phase 3: Layout       → Design dashboard layout
Phase 4: Plan         → Generate implementation plan
Phase 5: Build        → Create all files
Phase 6: Validate     → Run validation scripts
Phase 7: Test         → Browser testing (optional)
```

## Skill Structure

The skill uses **progressive disclosure** - Claude loads reference files only when needed:

```
.claude/skills/openbb-app-builder/
├── SKILL.md              # Main orchestrator (loaded when skill triggers)
├── APP-INTERVIEW.md      # Phase 1: Requirements gathering
├── WIDGET-METADATA.md    # Phase 2: Widget definitions
├── DASHBOARD-LAYOUT.md   # Phase 3: Layout design
├── APP-PLANNER.md        # Phase 4: Implementation planning
├── OPENBB-APP.md         # Phase 5: Core implementation reference
└── APP-TESTER.md         # Phase 7: Browser testing
```

When the main SKILL.md says `see [APP-INTERVIEW.md](APP-INTERVIEW.md)`, Claude reads that file via bash when it needs the detailed instructions.

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

## Generated App Structure

```
{app-name}/
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

## Error Recovery

The skill includes automatic error recovery:

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

- [HARNESS_ARCHITECTURE.md](./HARNESS_ARCHITECTURE.md) - Detailed architecture documentation
- [OpenBB Workspace Docs](https://docs.openbb.co/workspace)
- [Backend Examples](../getting-started/)
