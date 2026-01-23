---
name: openbb-app-builder
description: Master orchestrator for one-shot OpenBB app creation pipeline - from requirements to tested deployment
---

# OpenBB App Builder - Master Orchestration Skill

You are the master orchestrator for building OpenBB Workspace apps. This skill coordinates the entire pipeline from requirements gathering to testing, enabling "one-shot" app creation.

## Pipeline Overview

```
┌────────────────────────────────────────────────────────────────────────────┐
│                      OPENBB APP BUILDER PIPELINE v2.0                      │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                  │
│  │   PHASE 1   │     │   PHASE 2   │     │   PHASE 3   │                  │
│  │  INTERVIEW  │────▶│   WIDGETS   │────▶│   LAYOUT    │                  │
│  │             │     │   METADATA  │     │   DESIGN    │                  │
│  └─────────────┘     └─────────────┘     └─────────────┘                  │
│        │                   │                   │                          │
│        │   Accepts:        │                   │                          │
│        │   - Description   │                   │                          │
│        │   - Streamlit     │                   │                          │
│        │   - React code    │                   │                          │
│        │   - Screenshots   │                   │                          │
│        ▼                   ▼                   ▼                          │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                        APP-SPEC.md                                  │  │
│  │  Requirements + Widget Definitions + Layout + Groups               │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                    │                                       │
│                                    ▼                                       │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                  │
│  │   PHASE 4   │     │   PHASE 5   │     │   PHASE 6   │                  │
│  │   PLANNER   │────▶│   BUILDER   │────▶│ VALIDATION  │                  │
│  │             │     │             │     │             │                  │
│  └─────────────┘     └─────────────┘     └─────────────┘                  │
│        │                   │                   │                          │
│        ▼                   ▼                   ▼                          │
│    PLAN.md            main.py          validate_widgets.py               │
│                       widgets.json     validate_apps.py                   │
│                       apps.json        validate_endpoints.py              │
│                       requirements.txt                                     │
│                       Dockerfile                                           │
│                                    │                                       │
│                          ┌─────────┴─────────┐                            │
│                          │                   │                            │
│                     ┌────▼────┐         ┌────▼────┐                       │
│                     │  PASS   │         │  FAIL   │                       │
│                     └────┬────┘         └────┬────┘                       │
│                          │                   │                            │
│                          ▼                   ▼                            │
│  ┌─────────────┐    ┌─────────────────────────────────────┐              │
│  │   PHASE 7   │    │  AUTO-FIX: Analyze error, fix code, │              │
│  │   TESTER    │◀───│  re-run validation (max 3 retries)  │              │
│  │             │    └─────────────────────────────────────┘              │
│  └─────────────┘                                                          │
│        │                                                                   │
│        │  Browser Automation:                                              │
│        │  - Start backend                                                  │
│        │  - Add to OpenBB Workspace                                        │
│        │  - Verify widgets load                                            │
│        │  - Take screenshots                                               │
│        ▼                                                                   │
│  ┌─────────────┐                                                          │
│  │  SUCCESS!   │  → App ready for deployment                              │
│  └─────────────┘                                                          │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Quick Start Commands

Users can trigger this pipeline with:

| Command | Description |
|---------|-------------|
| "Build an OpenBB app for X" | Full pipeline with interview |
| "Convert this Streamlit app to OpenBB" | Reference-based pipeline |
| "Quick mode: build stock tracker" | Minimal interruptions |
| "Verbose mode: teach me OpenBB" | Explain each step |

---

## Phase Execution

### Phase 1: APP-INTERVIEW

**Goal**: Gather complete requirements before any code

**Two Modes**:
1. **Interactive Interview** - Ask structured questions
2. **Reference Analysis** - Parse Streamlit/Gradio/React code

**Process**:
1. Detect if user provided reference code/screenshots
2. If reference: Analyze and extract components
3. If description: Run structured interview
4. Create `apps/{app-name}/APP-SPEC.md`

**Exit Criteria**:
- APP-SPEC.md exists with all sections
- User confirmed requirements

**Smart Detection**:
```python
# Detect reference examples
if "import streamlit" in user_input:
    mode = "streamlit_reference"
elif "import gradio" in user_input:
    mode = "gradio_reference"
elif "from flask import" in user_input or "@app.route" in user_input:
    mode = "flask_reference"
elif "React" in user_input or "useState" in user_input:
    mode = "react_reference"
else:
    mode = "interactive_interview"
```

---

### Phase 2: WIDGET-METADATA

**Goal**: Define every widget with complete specifications

**Process**:
1. Read APP-SPEC.md requirements
2. For each data view, propose a widget type
3. Define: type, params, columns, data format
4. Append widget definitions to APP-SPEC.md

**Exit Criteria**:
- All widgets defined in APP-SPEC.md
- User confirmed widget list

---

### Phase 3: DASHBOARD-LAYOUT

**Goal**: Design the visual dashboard layout

**Process**:
1. Review widgets from APP-SPEC.md
2. Propose tab structure
3. Create ASCII layout for each tab
4. Define parameter groups
5. Append layout to APP-SPEC.md

**Exit Criteria**:
- Layout defined in APP-SPEC.md
- User confirmed layout

---

### Phase 4: APP-PLANNER

**Goal**: Generate detailed implementation plan

**Process**:
1. Read complete APP-SPEC.md
2. Generate `apps/{app-name}/PLAN.md`
3. Include step-by-step instructions

**Exit Criteria**:
- PLAN.md exists with all steps
- User approved the plan

---

### Phase 5: APP-BUILDER

**Goal**: Create all files according to the plan

**Process**:
1. Follow PLAN.md step by step
2. Create files:
   - `main.py` (FastAPI app with `@register_widget` decorators)
   - `apps.json` (dashboard layout)
   - `requirements.txt`
   - `Dockerfile`
   - `.env.example`
   - `README.md`
3. Use openbb-app.md skill knowledge

**Note**: `@register_widget` decorators recommended, but separate `widgets.json` is also valid if user prefers

**Exit Criteria**:
- All files created
- No syntax errors

---

### Phase 6: VALIDATION

**Goal**: Validate all generated files

**Process**:
1. Run `python scripts/validate_widgets.py apps/{app-name}/`
2. Run `python scripts/validate_apps.py apps/{app-name}/`
3. If errors, fix and re-validate (max 3 retries)

**Scripts Available**:
```bash
# Validate widget configurations
python scripts/validate_widgets.py apps/{app-name}/

# Validate dashboard layout
python scripts/validate_apps.py apps/{app-name}/

# Run both validations
python scripts/validate_app.py apps/{app-name}/

# Test live endpoints (requires running server)
python scripts/validate_endpoints.py apps/{app-name}/ --base-url http://localhost:7779
```

**Exit Criteria**:
- Both scripts pass (exit code 0)
- Only acceptable warnings

**If Validation Fails**:
```
Validation found {n} errors:
- {error 1}
- {error 2}

Analyzing errors...
Applying fixes...
Re-running validation...
[Retry up to 3 times]
```

---

### Phase 7: APP-TESTER (Optional but Recommended)

**Goal**: Test the app in a real browser

**Process**:
1. Start backend server (`uvicorn main:app --port 7779`)
2. Verify endpoints with curl
3. Use Claude-in-Chrome to:
   - Navigate to OpenBB Workspace
   - Add backend to Data Connectors
   - Open app dashboard
   - Verify widgets load
   - Take screenshots
4. Generate test report

**Exit Criteria**:
- All widgets load successfully
- No console errors
- Screenshots captured

**If Testing Fails**:
```
Testing found issues:
- Widget X not loading: {error}
- {other issues}

Analyzing the problem...
Suggested fix: {diagnosis}

Would you like me to fix and re-test?
```

---

## Mode Configurations

### Standard Mode (Default)
- User confirmation at each phase transition
- Detailed explanations
- Best for first-time users

### Quick Mode
Triggered by: "quick mode", "fast", "minimal"
- Make reasonable defaults
- Only ask critical questions
- Single confirmation at end

```
User: Build a crypto tracker app, quick mode

Claude: [Makes defaults, minimal interruptions]
- App name: crypto-tracker
- Widgets: prices table, chart, metrics
- Data source: CoinGecko API (free)
- Layout: 1 tab, standard arrangement

Building... [Shows progress]

Done! App created at apps/crypto-tracker/
```

### Verbose Mode
Triggered by: "verbose", "teach me", "explain"
- Detailed explanations at each step
- Educational approach
- Best for learning OpenBB development

```
User: Build a stock screener, verbose mode

Claude: Let's build this step by step. I'll explain each decision.

**Phase 1: Requirements**

First, we need to understand your data source. OpenBB supports
several ways to get data:

1. **External APIs** - Third-party services like Alpha Vantage
2. **Databases** - PostgreSQL, Snowflake, etc.
3. **Static data** - Mock data for prototyping

Which would you like to use?

[Explains each option in detail...]
```

### Reference Mode
Triggered by: Code snippets, "convert this", "like this app"
- Analyze provided reference
- Extract components automatically
- Map to OpenBB equivalents

```
User: Convert this Streamlit app to OpenBB:
[Streamlit code]

Claude: I've analyzed your Streamlit app:

**Components Detected:**
| Streamlit | OpenBB | Notes |
|-----------|--------|-------|
| st.dataframe | table | Stock data display |
| st.line_chart | chart | Price visualization |
| st.selectbox | param | Symbol selector |

Shall I proceed with this mapping?
```

---

## Progress Tracking

Use todo list to track pipeline progress:

```markdown
Pipeline Progress: {App Name}

1. ✅ Requirements Interview - APP-SPEC.md created
2. ✅ Widget Definitions - 5 widgets defined
3. ✅ Dashboard Layout - 2 tabs designed
4. ✅ Implementation Plan - PLAN.md created
5. ✅ Build & Create Files - 7 files created
6. ⏳ Validation - Running...
7. ⏳ Testing - Pending

Current: Running validate_widgets.py...
```

---

## Directory Structure Created

```
apps/{app-name}/
├── APP-SPEC.md        # Requirements and specifications
├── PLAN.md            # Implementation plan
├── main.py            # FastAPI app with @register_widget decorators
├── apps.json          # Dashboard layout
├── requirements.txt   # Python dependencies
├── Dockerfile         # Docker configuration
├── .env.example       # Environment template
└── README.md          # App documentation
```

**Note**: `@register_widget` decorator pattern is recommended (config close to code), but separate `widgets.json` is also valid.

---

## Error Recovery

### Retry Logic

```python
MAX_RETRIES = 3

for attempt in range(MAX_RETRIES):
    success = run_phase()
    if success:
        break
    else:
        error = diagnose_error()
        fix = generate_fix(error)
        apply_fix(fix)

        if attempt == MAX_RETRIES - 1:
            ask_user_for_guidance()
```

### Common Fixes

| Error | Auto-Fix |
|-------|----------|
| Missing required field in widget | Add with sensible default |
| Invalid widget type | Correct to closest valid type |
| Widget ID not in widgets.json | Add widget or fix reference |
| Overlapping widgets | Adjust positions |
| CORS error | Check origins configuration |
| Endpoint 404 | Verify route registration |

---

## Completion Messages

### On Success

```markdown
# 🎉 App Created Successfully!

**App Name**: {name}
**Location**: apps/{app-name}/

## Files Created
- main.py (FastAPI app with {n} widgets via @register_widget)
- apps.json ({n} tabs)
- requirements.txt
- Dockerfile
- .env.example
- README.md

## Validation
✅ widgets.json - Passed
✅ apps.json - Passed
✅ Endpoints - All responding

## Test Results
✅ All {n} widgets loaded successfully
[Screenshots attached]

## Next Steps

### Run Locally
```bash
cd apps/{app-name}
pip install -r requirements.txt
uvicorn main:app --reload --port 7779
```

### Add to OpenBB Workspace
1. Go to pro.openbb.co → Settings → Data Connectors
2. Add Custom Backend: http://localhost:7779

### Deploy to Fly.dev
```bash
flyctl launch
flyctl deploy
```

Would you like me to:
1. Run the app and test it in the browser?
2. Deploy it to Fly.dev?
3. Make any modifications?
```

### On Failure (After Retries)

```markdown
# ⚠️ Build Incomplete

The app was created but encountered issues:

## Issues Found
1. {issue 1}
2. {issue 2}

## Files Created
✅ main.py (with @register_widget decorators)
❌ apps.json (validation failed)

## Recommended Actions
1. {action 1}
2. {action 2}

Would you like me to:
1. Try a different approach?
2. Skip the failing component?
3. Get more details about the error?
```

---

## Integration with Skills

This orchestrator uses:

| Skill | Phase | Purpose |
|-------|-------|---------|
| `app-interview` | 1 | Gather requirements, analyze references |
| `widget-metadata` | 2 | Define widget specifications |
| `dashboard-layout` | 3 | Design layout and groups |
| `app-planner` | 4 | Generate PLAN.md |
| `openbb-app` | 5 | Core implementation knowledge |
| `app-tester` | 7 | Browser-based testing |

---

## Best Practices

### Pipeline Best Practices
1. **Don't skip phases** - Each phase builds on the previous
2. **Get user confirmation** - At each phase transition
3. **Save progress** - APP-SPEC.md captures all decisions
4. **Validate early** - Run validation after building
5. **Test when possible** - Browser testing catches real issues
6. **Be recoverable** - If something fails, diagnose and fix
7. **Document everything** - README.md and inline comments

### Widget Configuration Best Practices
1. **Use `@register_widget` decorator** - Keep widget metadata next to endpoint code
2. **No `runButton: true` by default** - Only for heavy computation (Monte Carlo, ML, etc.)
3. **Reasonable widget heights** - Metrics: h=4-6, Tables: h=12-18, Charts: h=12-15
4. **Prefer AgGrid charts over Plotly** - Users can access raw data
5. **For Plotly charts**:
   - Add `"raw": True` in widget config
   - Support `raw` query parameter in endpoint
   - NO title in Plotly figure (widget provides it)
   - Reduce top margin since no title
6. **`/widgets.json` must return dict** - Object format with widget IDs as keys, NOT an array

---

## Example Full Run

```
User: Build me an OpenBB app for tracking my Ethereum portfolio

Claude: Let's build your Ethereum portfolio tracker!

[Phase 1: Interview]
- App Name: Ethereum Portfolio Tracker
- Data Source: Etherscan API
- Auth: API key required (X-ETHERSCAN-API-KEY)
- Widgets needed: Holdings, Value chart, Transactions, Gas tracker

[Phase 2: Widget Metadata]
- holdings_table (table, 8 columns)
- portfolio_value (chart, area with line)
- transactions (table, 6 columns)
- gas_tracker (metric, 3 KPIs)

[Phase 3: Layout]
- Tab 1: Overview (metrics + chart + table)
- Tab 2: Transactions (full-width table)
- Groups: wallet_address syncs all widgets

[Phase 4: Plan]
- PLAN.md with 15 implementation steps

[Phase 5: Build]
- main.py (280 lines, 4 widgets via @register_widget)
- apps.json (2 tabs)
- requirements.txt, Dockerfile, etc.

[Phase 6: Validate]
✅ widgets.json - Passed
✅ apps.json - Passed

[Phase 7: Test]
✅ Backend started on port 7779
✅ Added to OpenBB Workspace
✅ All widgets loading correctly
[Screenshots attached]

🎉 Complete! Your app is ready at apps/ethereum-portfolio-tracker/
```

---

## Triggering Individual Phases

Users can invoke specific phases:

```
"Just interview for my app" → Phase 1 only
"Define widgets for my app" → Phase 2 only
"Design the layout" → Phase 3 only
"Validate my app" → Phase 6 only
"Test my app in browser" → Phase 7 only
```
