# FRED Series with Custom Header Authentication

A simple OpenBB Workspace app that demonstrates custom header authentication for API keys. The FRED API key is passed as a custom header when connecting the backend to OpenBB Workspace, eliminating the need for API key management within the app itself.

## Features

### 🔒 **Custom Header Authentication**
- **Header-based API Key**: API key passed via custom headers when adding backend to workspace
- **No API Key UI**: Clean interface without exposed API key parameters
- **Secure Integration**: API key handled at the connection level, not within widgets

### 📊 **FRED Data Visualization**
- **Multi-Series Support**: Fetch multiple FRED series simultaneously (e.g., `RPI,PCE,UNRATE`)
- **Interactive Charts**: Built-in line chart visualization with table/chart toggle
- **Time Series Optimization**: Proper date handling and time-based charting
- **Single Widget Focus**: Clean, simple interface with just the data visualization

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**:
   ```bash
   uvicorn main:app --reload --port 8001
   ```

3. **Add to OpenBB Workspace with Custom Header**:
   - In OpenBB Workspace, add a new backend
   - URL: `http://localhost:8001`
   - **Add Custom Header**:
     - Header Name: `X-FRED-API-KEY` (or `fred-api-key`)
     - Header Value: `your_fred_api_key_here`
   - The API key will automatically be sent with all requests

## How Custom Headers Work

### Backend Connection
When adding this backend to OpenBB Workspace:
1. **URL**: Standard backend URL (`http://localhost:8001`)
2. **Custom Header**: Add header `X-FRED-API-KEY` with your FRED API key
3. **Automatic Authentication**: All requests include the API key header
4. **No Widget Configuration**: No need to enter API key in any widget

### Request Flow
```
OpenBB Workspace → Backend Request
Headers: {
  "X-FRED-API-KEY": "your_api_key_here",
  "Content-Type": "application/json",
  ...
}
```

### Code Implementation
```python
@app.get("/fred_series")
def fred_series(request: Request, series_id: str = "SP500", start_date: str = "2020-01-01"):
    # Extract API key from custom header
    api_key = request.headers.get('X-FRED-API-KEY') or request.headers.get('fred-api-key')
    
    if not api_key:
        raise HTTPException(status_code=401, detail="API key required in header")
    
    # Use API key with FRED API
    fred = Fred(api_key=api_key)
    # ... rest of implementation
```

## Widget Configuration

### Single FRED Series Widget
- **Multi-series input**: Comma-separated FRED series IDs
- **Date selection**: Start date picker
- **Chart/table toggle**: Built-in visualization options
- **Full-width layout**: 40-width widget for optimal viewing

### No API Key Parameters
- Clean parameter list with only data-related inputs
- No exposed API key fields
- Simplified user experience

## Example Series IDs

| Series ID | Description |
|-----------|-------------|
| `SP500` | S&P 500 Stock Price Index |
| `GDP` | Gross Domestic Product |
| `UNRATE` | Unemployment Rate |
| `FEDFUNDS` | Federal Funds Rate |
| `CPIAUCSL` | Consumer Price Index |
| `RPI` | Real Personal Income |
| `PCE` | Personal Consumption Expenditures |

## Multi-Series Examples

```
# Inflation Indicators
CPIAUCSL,CPILFESL,PCEPILFE

# Interest Rates  
FEDFUNDS,DGS10,DGS2

# Economic Activity
GDP,UNRATE,PAYEMS
```

## API Endpoints

- **`/`** - Root endpoint with app information
- **`/widgets.json`** - Single widget definition for FRED series
- **`/apps.json`** - Simple app configuration with one tab
- **`/fred_series`** - FRED data endpoint with header authentication

## Benefits of Custom Header Approach

### 🔒 **Security**
- API key never exposed in widget UI
- Centralized authentication at connection level
- No risk of API key being visible to end users

### 🎯 **Simplicity**
- Single widget with clean parameter list
- No API key management complexity
- Focus purely on data visualization

### 🔧 **Flexibility**
- Easy to change API key at connection level
- Same backend can be used with different API keys
- No need to modify widget parameters

## Getting Your FRED API Key

1. Visit: https://fred.stlouisfed.org/docs/api/api_key.html
2. Create a free account with the Federal Reserve Bank of St. Louis
3. Generate your API key
4. Add it as a custom header when connecting to OpenBB Workspace

---

**Note**: This demonstrates the custom header authentication pattern for OpenBB Workspace backends, providing a clean separation between authentication and data visualization.