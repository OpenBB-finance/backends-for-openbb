# Validation Reference

Guide for validating OpenBB app files using the validation scripts.

## Validation Commands

### Validate widgets.json

```bash
python scripts/validate_widgets.py {app-path}/
```

**Checks:**
- Required fields (name, type, endpoint)
- Valid widget types (table, chart, metric, markdown, newsfeed, etc.)
- Parameter configurations and types
- Column definitions for tables
- Grid data ranges (w: 10-40, h: 4-100)
- Valid formatterFn and renderFn values

### Validate apps.json

```bash
python scripts/validate_apps.py {app-path}/
```

**Checks:**
- Tab structure and naming
- Layout positions (x, y, w, h)
- Widget references exist in widgets.json
- No overlapping widgets
- Group configurations use "Group N" pattern

### Validate Both

```bash
python scripts/validate_app.py {app-path}/
```

Runs both validators in sequence.

### Validate Live Endpoints

```bash
# Start server first
uvicorn {app-path}/main:app --port 7779 &

# Run endpoint validation
python scripts/validate_endpoints.py {app-path}/ --base-url http://localhost:7779
```

**Checks:**
- Server is running
- /widgets.json returns valid dict (not array)
- /apps.json returns valid config
- Each widget endpoint responds
- Response format matches widget type

---

## Common Errors and Fixes

### widgets.json Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `Missing required field: name` | Widget missing name | Add `"name": "Widget Name"` |
| `Invalid widget type: xxx` | Typo or unsupported type | Use: table, chart, metric, markdown, newsfeed |
| `Invalid formatterFn: currency` | "currency" not valid | Use `"none"` for currency display |
| `gridData.w must be 10-40` | Width out of range | Adjust w to valid range |
| `widgets.json must be object` | Array format used | Change `[{...}]` to `{"id": {...}}` |

### apps.json Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `Widget 'xxx' not found` | Widget ID mismatch | Ensure ID matches widgets.json key |
| `Widgets overlap at (x,y)` | Layout collision | Adjust x, y coordinates |
| `Invalid group name` | Custom group name | Use "Group 1", "Group 2", etc. |

### Endpoint Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `CORS error` | Missing origin | Add origin to CORS middleware |
| `404 Not Found` | Route not registered | Check @app.get decorator |
| `Invalid JSON response` | Wrong return format | Return list for tables, Plotly JSON for charts |

---

## Retry Logic

```
MAX_RETRIES = 3

for attempt in range(MAX_RETRIES):
    1. Run validation
    2. If success → continue to next phase
    3. If errors:
       a. Parse error messages
       b. Apply fixes to files
       c. Re-run validation
    4. If max retries exceeded → ask user for guidance
```

---

## Validation Output Examples

### Success

```
============================================================
OPENBB APP VALIDATION
============================================================
App Path: apps/my-app

Running widgets.json validation...
✅ widgets.json is valid (5 widgets)

Running apps.json validation...
✅ apps.json is valid (2 tabs, 1 group)

============================================================
FINAL RESULT
============================================================

✅ All validations passed!

Your app is ready. Next steps:
  1. cd apps/my-app
  2. pip install -r requirements.txt
  3. uvicorn main:app --reload --port 7779
  4. Add http://localhost:7779 to OpenBB Workspace
```

### Failure

```
============================================================
OPENBB APP VALIDATION
============================================================
App Path: apps/my-app

Running widgets.json validation...
❌ ERRORS in widgets.json:
  - Widget 'price_table': Invalid formatterFn 'currency' (use 'none')
  - Widget 'chart': Missing required field 'endpoint'

Running apps.json validation...
❌ ERRORS in apps.json:
  - Tab 'overview': Widget 'prices' not found in widgets.json
  - Group 'symbol-group' invalid (use 'Group 1', 'Group 2', etc.)

============================================================
FINAL RESULT
============================================================

❌ Validation failed. Please fix the errors above.
```

---

## Auto-Fix Patterns

When validation fails, apply these fixes automatically:

| Error Pattern | Auto-Fix |
|---------------|----------|
| `formatterFn: currency` | Replace with `formatterFn: none` |
| `widgets.json is array` | Convert to object with IDs as keys |
| `Missing endpoint field` | Add `"endpoint": "{widget_id}"` |
| `Group name invalid` | Replace with `"Group 1"`, `"Group 2"`, etc. |
| `Widget not found` | Check for typos, fix ID reference |
