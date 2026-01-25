# App Interview Reference

Detailed guide for gathering requirements through structured interview or reference example analysis.

## Two Modes of Operation

### Mode 1: Interactive Interview
When the user describes what they want in natural language, guide them through structured questions.

### Mode 2: Reference Example Analysis
When the user provides:
- A Streamlit/Gradio/Flask/FastAPI app
- A React/Vue/Angular dashboard
- A screenshot or mockup
- An existing codebase URL or files

Analyze the reference and extract requirements automatically.

---

## Reference Example Analysis

### Detecting Reference Examples

Look for these indicators:
1. Code snippets with `import streamlit`, `import gradio`, `from flask import`, etc.
2. URLs to GitHub repos, Streamlit Cloud, HuggingFace Spaces
3. Uploaded files or file paths mentioned
4. Screenshots or images of dashboards
5. Phrases like "convert this", "like this app", "similar to", "based on this"

### Analyzing Streamlit Apps

When given Streamlit code, identify:

```python
# UI Components -> Widget Types
st.dataframe() / st.table()     -> table widget
st.line_chart() / st.plotly_chart() -> chart widget
st.metric()                      -> metric widget
st.markdown() / st.text()        -> markdown widget
st.image()                       -> html or markdown widget
st.selectbox() / st.multiselect() -> endpoint param dropdown
st.slider() / st.number_input()  -> number param
st.text_input()                  -> text param
st.date_input()                  -> date param
st.checkbox() / st.toggle()      -> boolean param
st.tabs()                        -> dashboard tabs
st.columns()                     -> layout structure
st.sidebar                       -> parameter groups
```

### Analyzing Gradio Apps

```python
# Gradio Components -> Widget Types
gr.Dataframe()                   -> table widget
gr.Plot()                        -> chart widget
gr.Markdown() / gr.HTML()        -> markdown/html widget
gr.Textbox()                     -> text param
gr.Number()                      -> number param
gr.Dropdown()                    -> endpoint/static dropdown
gr.Checkbox()                    -> boolean param
gr.Slider()                      -> number param with range
gr.Tab()                         -> dashboard tabs
```

### Analyzing Flask/FastAPI Apps

Look for:
- Route definitions (`@app.route`, `@app.get`, `@app.post`)
- Return types (JSON, HTML, files)
- Query parameters and request bodies
- Database connections
- External API calls

### Reference Analysis Output

After analyzing a reference, present:

```markdown
## Reference Analysis: {App Name}

### Detected Framework
{Streamlit | Gradio | Flask | FastAPI | React | Vue | Other}

### Identified Components

| # | Original Component | OpenBB Widget Type | Description |
|---|-------------------|-------------------|-------------|
| 1 | st.dataframe() | table | Stock holdings data |
| 2 | st.line_chart() | chart | Price history chart |
| 3 | st.metric() x3 | metric | Portfolio KPIs |
| 4 | st.selectbox() | param (endpoint) | Stock selector |

### Data Sources Detected
- External API: {url if found}
- Database: {type if found}
- Static data: {yes/no}

### Parameters Identified
| Parameter | Original | OpenBB Type | Default |
|-----------|----------|-------------|---------|
| symbol | st.selectbox | endpoint | AAPL |
| period | st.radio | text (options) | 1M |

### Layout Structure
{describe columns, tabs, sections}

### Missing Information Needed
1. {list questions to ask user}
2. {data source details}
3. {authentication requirements}
```

Then ask: "I've analyzed the reference app. Does this mapping look correct? What adjustments would you like to make?"

---

## Interactive Interview Flow

Ask questions in phases, waiting for user confirmation before proceeding.

### Phase 1: App Identity

Ask about:
1. **App Name**: What should the app be called?
2. **Description**: What does the app do in 1-2 sentences?
3. **Purpose**: What problem does this solve? Who is the target user?
4. **Category**: What category does this fit? (Portfolio, Analytics, News, Research, Trading, etc.)

### Phase 2: Data Source

Ask about:
1. **Data Origin**: Where does the data come from?
   - External API (URL, documentation link)
   - Database (type: PostgreSQL, MySQL, Snowflake, etc.)
   - Web scraping (source URLs)
   - Static/mock data for prototyping
   - Multiple sources

2. **API Details** (if external API):
   - Base URL
   - Documentation URL
   - Rate limits?
   - Response format (JSON, XML, etc.)

3. **Data Types**: What kinds of data will be displayed?
   - Tables with rows/columns
   - Time-series charts
   - KPI metrics
   - News/articles
   - Documents/PDFs
   - Real-time streaming data

### Phase 3: Authentication

Ask about:
1. **API Authentication**: Does the API require authentication?
   - No authentication
   - API key in header (which header? e.g., `X-API-Key`, `Authorization`)
   - Bearer token
   - OAuth2
   - Basic auth

2. **User-provided keys**: Should users provide their own API keys?
   - Yes - show API key input in OpenBB Workspace settings
   - No - backend uses embedded/environment key

3. **Custom Headers**: Any special headers required by the API?

### Phase 4: Configuration & Behavior

Ask about:
1. **Caching**: How fresh should data be?
   - Real-time (no caching)
   - Short cache (1-5 minutes)
   - Medium cache (5-15 minutes)
   - Long cache (15+ minutes)

2. **Auto-refresh**: Should widgets auto-refresh?
   - Yes - specify interval
   - No - manual refresh only (runButton: true)

3. **Raw Mode**: Should AI be able to access raw data? (Adds ?raw=true support)

### Phase 5: Deployment

Ask about:
1. **Hosting**: Where will this be deployed?
   - Local development only
   - Fly.dev
   - Railway
   - AWS/GCP/Azure
   - Custom server

2. **Docker**: Need Docker configuration?

3. **Environment Variables**: What secrets/config need to be stored in .env?

---

## Smart Defaults

When in doubt, suggest sensible defaults:

| Setting | Default | Reasoning |
|---------|---------|-----------|
| Cache | 5 minutes | Balance between freshness and API limits |
| Grid width | 20 | Half-width works well for most widgets |
| Auth | User provides key | More flexible, respects rate limits |
| Docker | Yes | Easy deployment |
| Raw mode | Yes for charts | Enables AI analysis |

---

## Output Format

After gathering all information, create an APP-SPEC.md file:

```markdown
# App Specification: {App Name}

## Overview
- **Name**: {name}
- **Description**: {description}
- **Category**: {category}

## Data Source

### Type
{API | Database | Scraping | Static}

### Details
- **Base URL**: {url}
- **Documentation**: {docs_url}
- **Rate Limits**: {limits if known}

## Authentication

### API Auth
- **Type**: {none | api_key | bearer | oauth}
- **Header Name**: {header if applicable}
- **User Provides Key**: {yes | no}

## Configuration

### Caching
- **Strategy**: {real-time | short | medium | long}
- **Refetch Interval**: {milliseconds}

### Features
- **Raw Mode**: {yes | no}
- **Auto-refresh**: {yes | no}

## Deployment

### Hosting
- **Platform**: {local | fly.dev | railway | custom}
- **Docker**: {yes | no}
- **Port**: {7779 default}

### Environment Variables
```
{VAR_NAME}=description
```

## Status
- [x] Requirements gathered
- [ ] Widgets defined
- [ ] Layout designed
- [ ] Implementation planned
- [ ] Built
- [ ] Validated
- [ ] Tested
```

---

## Interview Best Practices

1. **Be conversational** - Don't dump all questions at once
2. **Provide defaults** - Suggest common choices
3. **Give examples** - Help users understand options
4. **Validate incrementally** - Confirm each phase before moving on
5. **Be flexible** - Skip sections that don't apply
6. **Summarize** - Recap what you've gathered periodically
7. **Accept references** - If user provides code/screenshots, analyze them
