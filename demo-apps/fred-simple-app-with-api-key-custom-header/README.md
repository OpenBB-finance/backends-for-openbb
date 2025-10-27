# FRED Series with Custom Header Authentication

A simple OpenBB Workspace app that fetches FRED economic data using API key authentication via custom headers.

<img width="2804" height="1240" alt="CleanShot 2025-10-27 at 17 38 42@2x" src="https://github.com/user-attachments/assets/b9449263-3b3b-445c-8add-63754fc5d09e" />

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
    
<img width="1658" height="1264" alt="CleanShot 2025-10-27 at 17 16 43@2x" src="https://github.com/user-attachments/assets/1e0a838b-9dcf-468f-be2c-e7df5f9c3da3" />

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
