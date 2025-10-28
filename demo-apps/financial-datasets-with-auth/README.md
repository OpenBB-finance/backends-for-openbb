# OpenBB with Financial Datasets backend

## Setup

### 1. Install all the required libraries

```bash
poetry install
```

### 2. Configure your API Key

You can provide your Financial Datasets API key in two ways:

#### Option A: Environment Variable (default)
Update your .env file with the API key obtained from your [Financial Datasets API Key dashboard](https://www.financialdatasets.ai/):

```bash
FINANCIAL_DATASETS_API_KEY=your-api-key-here
```

#### Option B: Request Headers (override)
You can override the API key on a per-request basis by including it in the request headers. This is useful for client applications that manage their own API keys:

- `X-API-KEY: your-api-key`

If both header and environment variable are present, the header takes precedence.

### 3. Run the custom backend

```bash
poetry run uvicorn src.main:app --reload
```

### 4. Connect to OpenBB

Go into [OpenBB](https://pro.openbb.co), into the Data Connectors tab to be more specific.

### 5. Add a new custom backend

Add your backend at https://pro.openbb.co/app/data-connectors?modal=data-connectors&dcTab=backend as follows:

<img width="854" alt="Screenshot 2024-11-03 at 1 24 47 AM" src="https://github.com/user-attachments/assets/82ff3f7a-aaae-4449-a81e-546b576f67bd">

That's it, now you can access data from that widget.

## API Authentication

All endpoints that fetch data from Financial Datasets require authentication. The API key is resolved in this order:

1. **Request Header** (highest priority): `X-API-KEY`
2. **Environment Variable**: `FINANCIAL_DATASETS_API_KEY`

If no API key is found, most endpoints will return a 401 Unauthorized error. Some UI-critical endpoints (`/stock_tickers`, `/institutional_investors`) will return empty data to allow the interface to load.

## Example Usage with Header Override

```python
import requests

# Using header override
headers = {
    "X-API-KEY": "your-api-key"
}

response = requests.get(
    "http://localhost:8000/income?ticker=AAPL",
    headers=headers
)
```
