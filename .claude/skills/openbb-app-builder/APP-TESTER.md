# App Tester Reference

Guide for browser-based testing of OpenBB apps.

## Testing Process

### Step 1: Start Backend Server

```bash
cd {app-path}
uvicorn main:app --reload --port 7779
```

### Step 2: Verify Endpoints with curl

```bash
# Health check
curl http://localhost:7779/

# Widget configuration
curl http://localhost:7779/widgets.json

# Dashboard configuration
curl http://localhost:7779/apps.json

# Test individual widget endpoints
curl "http://localhost:7779/my_endpoint?param=value"
```

### Step 3: Test in OpenBB Workspace

1. Navigate to https://pro.openbb.co
2. Go to Settings > Data Connectors
3. Click "Add Custom Backend"
4. Enter URL: `http://localhost:7779`
5. Add any required API key headers
6. Click Save

### Step 4: Verify Widgets Load

1. Open the App Gallery
2. Find your app
3. Click to open the dashboard
4. Verify each widget loads correctly
5. Test parameter interactions
6. Test group synchronization

---

## Common Issues and Fixes

### Widget Not Loading

**Symptoms**: Widget shows loading spinner or error

**Checks**:
1. Is the backend running? Check terminal for errors
2. Is CORS configured correctly?
3. Does the endpoint return valid JSON?
4. Is the response format correct for widget type?

**Debug**:
```bash
# Check endpoint directly
curl -v "http://localhost:7779/endpoint_name"

# Check for CORS headers
curl -v -X OPTIONS "http://localhost:7779/endpoint_name" \
  -H "Origin: https://pro.openbb.co"
```

### CORS Error

**Symptoms**: Browser console shows CORS policy error

**Fix**: Ensure CORS middleware includes all required origins:
```python
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
```

### 404 on Endpoint

**Symptoms**: Widget shows 404 error

**Checks**:
1. Is endpoint path in widgets.json correct?
2. Does the @app.get decorator match?
3. Did you restart uvicorn after changes?

### Parameter Not Working

**Symptoms**: Changing parameter doesn't update widget

**Checks**:
1. Is parameter defined in both widget config AND endpoint?
2. Are parameter names spelled correctly?
3. For groups: Are both widgets in the same group?
4. For groups: Is group name "Group 1" pattern?

### Chart Not Rendering

**Symptoms**: Chart widget shows error or blank

**Checks**:
1. Is Plotly figure returned as JSON?
2. Did you use `JSONResponse(content=json.loads(fig.to_json()))`?
3. Is template correct for theme?

---

## Validation Scripts

Run validation before testing:

```bash
# Validate widget configurations
python scripts/validate_widgets.py {app-path}/

# Validate dashboard layout
python scripts/validate_apps.py {app-path}/

# Test live endpoints (requires running server)
python scripts/validate_endpoints.py {app-path}/ --base-url http://localhost:7779
```

---

## Test Checklist

### Backend Tests
- [ ] `GET /` returns status ok
- [ ] `GET /widgets.json` returns valid dict
- [ ] `GET /apps.json` returns valid config
- [ ] All widget endpoints return correct data format
- [ ] Error handling returns proper HTTP codes

### Widget Tests
For each widget:
- [ ] Widget loads without errors
- [ ] Data displays correctly
- [ ] Parameters change data as expected
- [ ] Theme changes apply (for charts)

### Integration Tests
- [ ] Dashboard loads all widgets
- [ ] Tab navigation works
- [ ] Parameter groups sync correctly
- [ ] Clicking table cells updates grouped widgets (if applicable)

### Edge Cases
- [ ] Empty data handled gracefully
- [ ] Invalid parameter values handled
- [ ] API errors show user-friendly messages

---

## Browser Console Debugging

Open browser DevTools (F12) and check:

1. **Console tab**: Look for JavaScript errors
2. **Network tab**:
   - Filter by XHR/Fetch
   - Check request URLs
   - Verify response status codes
   - Inspect response bodies
3. **Headers**: Verify CORS headers present

---

## Test Report Template

After testing, document:

```markdown
## Test Report: {App Name}

**Date**: {date}
**Backend URL**: http://localhost:7779

### Endpoints Tested
| Endpoint | Status | Notes |
|----------|--------|-------|
| / | PASS | Returns ok |
| /widgets.json | PASS | 5 widgets |
| /apps.json | PASS | 2 tabs |
| /widget_1 | PASS | Returns data |

### Widgets Tested
| Widget | Loads | Data | Params | Notes |
|--------|-------|------|--------|-------|
| widget_1 | PASS | PASS | PASS | |
| widget_2 | PASS | PASS | N/A | No params |

### Issues Found
1. {issue description} - {status}

### Screenshots
{attach if relevant}
```
