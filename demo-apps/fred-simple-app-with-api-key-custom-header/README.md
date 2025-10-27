# FRED Series with Custom Header Authentication

A simple OpenBB Workspace app that fetches FRED economic data using API key authentication via custom headers.

## Features

- **Custom Header Authentication**: API key passed via `X-FRED-API-KEY` header when connecting to OpenBB Workspace
- **Multi-Series Support**: Fetch multiple FRED series simultaneously (e.g., `GDP,UNRATE,CPIAUCSL`)
- **Interactive Visualization**: Line charts with table/chart toggle

## Setup

1. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**:

   ```bash
   uvicorn main:app --reload --port 8001
   ```

3. **Add to OpenBB Workspace**:
   - Add new backend with URL: `http://localhost:8001`
   - Add custom header:
     - Name: `X-FRED-API-KEY`
     - Value: `your_fred_api_key_here`

## Getting a FRED API Key

1. Visit [FRED API Key page](https://fred.stlouisfed.org/docs/api/api_key.html)
2. Create a free account
3. Generate your API key

## Example Series IDs

- `SP500` - S&P 500 Index
- `GDP` - Gross Domestic Product
- `UNRATE` - Unemployment Rate
- `FEDFUNDS` - Federal Funds Rate
- `CPIAUCSL` - Consumer Price Index