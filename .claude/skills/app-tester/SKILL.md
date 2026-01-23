---
name: app-tester
description: Test an OpenBB app in the browser using Claude-in-Chrome automation with specific OpenBB Workspace flows
---

# App Tester Skill

You are testing an OpenBB Workspace app using browser automation. This skill uses Claude-in-Chrome MCP tools to:

1. Start the backend server
2. Verify endpoints work
3. Add the backend to OpenBB Workspace
4. Navigate to the app dashboard
5. Verify widgets load correctly
6. Take screenshots for verification
7. Generate a test report

---

## Prerequisites

Before testing:
- The app must be built (main.py, widgets.json exist)
- Validation scripts must pass
- Claude-in-Chrome browser extension must be available
- User must be logged into OpenBB Workspace

---

## Phase 1: Backend Startup & Verification

### Step 1.1: Start Backend Server

```bash
cd apps/{app-name}
# Install dependencies if needed
pip install -r requirements.txt
# Start server in background
uvicorn main:app --port 7779 &
```

Wait for server to be ready (up to 10 seconds).

### Step 1.2: Verify Health Endpoint

```bash
curl -s http://localhost:7779/
```

Expected: `{"status": "ok"}` or similar JSON response.

### Step 1.3: Verify Core Endpoints

```bash
# Check widgets.json
curl -s http://localhost:7779/widgets.json | python -m json.tool

# Check apps.json (optional)
curl -s http://localhost:7779/apps.json | python -m json.tool
```

### Step 1.4: Verify Widget Endpoints

For each widget in widgets.json, test its endpoint:

```bash
curl -s "http://localhost:7779/{widget_endpoint}" | head -c 500
```

---

## Phase 2: Browser Automation - OpenBB Workspace

### Step 2.1: Get Browser Context

```
Use: mcp__claude-in-chrome__tabs_context_mcp
With: createIfEmpty: true
```

This returns available tabs. Create a new tab if needed.

### Step 2.2: Navigate to OpenBB Workspace

```
Use: mcp__claude-in-chrome__navigate
With: url: "https://pro.openbb.dev/app/data-connectors"
      tabId: {tab_id}
```

Alternative URLs:
- Production: `https://pro.openbb.co/app/data-connectors`
- Dev: `https://pro.openbb.dev/app/data-connectors`

### Step 2.3: Wait for Page Load

```
Use: mcp__claude-in-chrome__computer
With: action: "wait", duration: 3, tabId: {tab_id}
```

Then take a screenshot to verify the page loaded:

```
Use: mcp__claude-in-chrome__computer
With: action: "screenshot", tabId: {tab_id}
```

---

## Phase 3: Add Custom Backend

### Step 3.1: Find "Add Custom Backend" Button

```
Use: mcp__claude-in-chrome__find
With: query: "Add Custom Backend button"
      tabId: {tab_id}
```

Or look for elements containing:
- "Add Custom Backend"
- "Add Backend"
- "+" button near backends list

### Step 3.2: Click Add Backend Button

```
Use: mcp__claude-in-chrome__computer
With: action: "left_click"
      ref: "{button_ref}"
      tabId: {tab_id}
```

### Step 3.3: Enter Backend URL

Find the URL input field:

```
Use: mcp__claude-in-chrome__find
With: query: "backend URL input field"
      tabId: {tab_id}
```

Enter the URL:

```
Use: mcp__claude-in-chrome__form_input
With: ref: "{input_ref}"
      value: "http://localhost:7779"
      tabId: {tab_id}
```

### Step 3.4: Submit/Save Backend

Find and click the submit button:

```
Use: mcp__claude-in-chrome__find
With: query: "Add or Submit button"
      tabId: {tab_id}
```

```
Use: mcp__claude-in-chrome__computer
With: action: "left_click"
      ref: "{submit_ref}"
      tabId: {tab_id}
```

### Step 3.5: Verify Backend Added

Wait for confirmation:

```
Use: mcp__claude-in-chrome__computer
With: action: "wait", duration: 2, tabId: {tab_id}
```

Take a screenshot to verify:

```
Use: mcp__claude-in-chrome__computer
With: action: "screenshot", tabId: {tab_id}
```

Look for:
- Success message/toast
- Backend appearing in list
- No error messages

---

## Phase 4: Configure API Key (If Required)

If the app requires an API key:

### Step 4.1: Find API Key Configuration

Look for:
- "Configure" button next to the backend
- Settings/gear icon
- "API Key" input field

```
Use: mcp__claude-in-chrome__find
With: query: "API key input or configure button"
      tabId: {tab_id}
```

### Step 4.2: Enter API Key

```
Use: mcp__claude-in-chrome__form_input
With: ref: "{api_key_input_ref}"
      value: "{api_key_value}"
      tabId: {tab_id}
```

### Step 4.3: Save Configuration

Find and click save:

```
Use: mcp__claude-in-chrome__computer
With: action: "left_click"
      ref: "{save_ref}"
      tabId: {tab_id}
```

---

## Phase 5: Navigate to App Dashboard

### Step 5.1: Go to Dashboards

Navigate to the dashboards/apps section:

```
Use: mcp__claude-in-chrome__navigate
With: url: "https://pro.openbb.dev/app/dashboards"
      tabId: {tab_id}
```

### Step 5.2: Find the App

Look for the app name in the dashboard list:

```
Use: mcp__claude-in-chrome__find
With: query: "{app_name} dashboard"
      tabId: {tab_id}
```

### Step 5.3: Open the Dashboard

```
Use: mcp__claude-in-chrome__computer
With: action: "left_click"
      ref: "{dashboard_ref}"
      tabId: {tab_id}
```

### Step 5.4: Wait for Widgets to Load

```
Use: mcp__claude-in-chrome__computer
With: action: "wait", duration: 5, tabId: {tab_id}
```

---

## Phase 6: Verify Widgets

### Step 6.1: Take Dashboard Screenshot

```
Use: mcp__claude-in-chrome__computer
With: action: "screenshot", tabId: {tab_id}
```

### Step 6.2: Check for Errors

Read the page to check for error states:

```
Use: mcp__claude-in-chrome__read_page
With: tabId: {tab_id}
```

Look for:
- "Error" text
- Red error indicators
- Loading spinners that don't resolve
- Empty widget states

### Step 6.3: Check Console for Errors

```
Use: mcp__claude-in-chrome__read_console_messages
With: tabId: {tab_id}
      onlyErrors: true
      pattern: "error|Error|failed|Failed"
```

### Step 6.4: Check Network Requests

```
Use: mcp__claude-in-chrome__read_network_requests
With: tabId: {tab_id}
      urlPattern: "localhost:7779"
```

Verify:
- All widget endpoints were called
- Responses were 200 OK
- No failed requests

---

## Phase 7: Test Widget Interactions

### Step 7.1: Test Parameters

If widgets have parameters:

1. Find a parameter dropdown/input:
```
Use: mcp__claude-in-chrome__find
With: query: "parameter dropdown or input"
      tabId: {tab_id}
```

2. Change the value:
```
Use: mcp__claude-in-chrome__computer
With: action: "left_click"
      ref: "{param_ref}"
      tabId: {tab_id}
```

3. Wait for refresh:
```
Use: mcp__claude-in-chrome__computer
With: action: "wait", duration: 2, tabId: {tab_id}
```

4. Take screenshot:
```
Use: mcp__claude-in-chrome__computer
With: action: "screenshot", tabId: {tab_id}
```

### Step 7.2: Test Tab Navigation

If multiple tabs exist:

1. Find tab buttons
2. Click each tab
3. Verify widgets load
4. Take screenshots

---

## Phase 8: Generate Test Report

Create a comprehensive test report:

```markdown
# Test Report: {App Name}

**Date**: {test_date}
**Tester**: Claude (Automated)
**Environment**: {pro.openbb.dev | pro.openbb.co}
**Backend URL**: http://localhost:7779

---

## Summary

| Category | Status | Details |
|----------|--------|---------|
| Backend Startup | ✅ Pass | Server running on port 7779 |
| Health Check | ✅ Pass | Returns {"status": "ok"} |
| widgets.json | ✅ Pass | {n} widgets configured |
| apps.json | ✅ Pass | {n} tabs configured |
| Backend Added | ✅ Pass | Successfully added to Workspace |
| Widgets Loading | ✅ Pass | All {n} widgets loaded |
| Console Errors | ✅ Pass | No JavaScript errors |
| Network Requests | ✅ Pass | All requests successful |

---

## Backend Tests

### Health Check
- **Endpoint**: GET /
- **Status**: ✅ Pass
- **Response**: {"status": "ok"}

### widgets.json
- **Endpoint**: GET /widgets.json
- **Status**: ✅ Pass
- **Widget Count**: {n}
- **Widgets**: {list widget names}

### apps.json
- **Endpoint**: GET /apps.json
- **Status**: ✅ Pass
- **Tab Count**: {n}

### Widget Endpoints
| Widget | Endpoint | Status | Response Time |
|--------|----------|--------|---------------|
| {name} | GET /{endpoint} | ✅ Pass | {ms}ms |

---

## Browser Tests

### Add Backend
- **Status**: ✅ Pass
- **URL**: http://localhost:7779
- **Screenshot**: [Dashboard Overview]

### Dashboard Load
- **Status**: ✅ Pass
- **Load Time**: ~{n}s
- **Screenshot**: [Widgets Loaded]

---

## Widget Tests

### {widget_name}
- **Type**: {widget_type}
- **Status**: ✅ Pass
- **Data Loaded**: Yes
- **Parameters**: {list if any}
- **Screenshot**: [Widget Screenshot]

---

## Console Errors

{none | list errors}

---

## Network Requests

| URL | Method | Status | Time |
|-----|--------|--------|------|
| /widgets.json | GET | 200 | {ms}ms |
| /{widget} | GET | 200 | {ms}ms |

---

## Recommendations

{any recommendations for improvements}

---

## Conclusion

**Overall Status**: ✅ Ready for Deployment

The app has passed all automated tests and is functioning correctly in OpenBB Workspace.

### Next Steps
1. Deploy to production (Fly.dev)
2. Share with users
3. Monitor for issues
```

---

## Error Handling

### Common Issues and Solutions

| Issue | Detection | Solution |
|-------|-----------|----------|
| Backend not starting | curl fails | Check port, dependencies |
| CORS error | Console error | Verify CORS origins |
| Widget not loading | Empty widget | Check endpoint response format |
| 404 errors | Network tab | Verify endpoint path |
| Auth error | 401 response | Configure API key |
| Timeout | Long loading | Increase timeout, check data source |

### If Testing Fails

1. **Take screenshots** of error states
2. **Log error messages** from console
3. **Check network requests** for failures
4. **Analyze the issue** and suggest fixes
5. **Report findings** to user

```markdown
## Testing Failed

❌ {n} issues found

### Issue 1: {description}
- **Type**: {CORS | Endpoint | Data | Auth}
- **Error**: {error message}
- **Screenshot**: [Error Screenshot]
- **Suggested Fix**: {how to fix}

### Recommended Actions
1. {action 1}
2. {action 2}

Would you like me to attempt to fix these issues and re-test?
```

---

## Cleanup

After testing:

1. **Stop the backend server** (if started by us)
2. **Note any warnings** for user
3. **Provide deployment instructions**

```bash
# Find and kill the uvicorn process
pkill -f "uvicorn main:app"
```

---

## GIF Recording (Optional)

For complex test runs, record a GIF:

### Start Recording
```
Use: mcp__claude-in-chrome__gif_creator
With: action: "start_recording", tabId: {tab_id}
```

### Take Screenshot (captures frame)
```
Use: mcp__claude-in-chrome__computer
With: action: "screenshot", tabId: {tab_id}
```

### Stop and Export
```
Use: mcp__claude-in-chrome__gif_creator
With: action: "stop_recording", tabId: {tab_id}
```

```
Use: mcp__claude-in-chrome__gif_creator
With: action: "export"
      tabId: {tab_id}
      download: true
      filename: "test-{app-name}.gif"
```

---

## Quick Test Checklist

For rapid testing, verify these essentials:

- [ ] `curl localhost:7779/` returns JSON
- [ ] `curl localhost:7779/widgets.json` returns array
- [ ] Backend added to OpenBB Workspace
- [ ] Dashboard loads without errors
- [ ] At least one widget shows data
- [ ] No console errors
- [ ] Screenshot captured

---

## Integration with Harness

### On Success

```markdown
## Testing Complete ✅

All {n} widgets passed testing.

The app is ready for deployment.

### Quick Deploy to Fly.dev
```bash
cd apps/{app-name}
flyctl launch
flyctl deploy
```

Would you like me to deploy the app?
```

### On Failure

```markdown
## Testing Failed ❌

{n} widgets failed testing.

### Issues Found:
1. {issue description}

### Fixes Applied:
- {fix 1}

Re-running tests...
```

This enables the harness to loop back and retry if needed.
