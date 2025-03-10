# Advanced Charting with TradingView UDF and Kraken API

This example demonstrates how to integrate Kraken cryptocurrency data with TradingView charts using the Universal Data Feed (UDF) protocol.

## Overview

This application serves as a backend adapter that connects TradingView charting widgets with Kraken's cryptocurrency market data. It implements the UDF protocol, which is TradingView's standardized API for external data providers.

## Key Components

### TradingView UDF Protocol

The UDF (Universal Data Feed) protocol is TradingView's standardized way of connecting to external data sources. It requires implementing several key endpoints:

1. **Configuration** (`/udf/config`): Provides information about supported features, resolutions, and exchanges
2. **Symbol Search** (`/udf/search`): Allows searching for available trading pairs
3. **Symbol Info** (`/udf/symbols`): Returns detailed information about a specific symbol
4. **Historical Data** (`/udf/history`): Retrieves OHLCV (Open, High, Low, Close, Volume) data for charting
5. **Server Time** (`/udf/time`): Provides the current server time for synchronization

### Resolution Mapping

TradingView uses specific resolution codes that need to be mapped to Kraken's interval parameters:

"1" → 1 minute
"60" → 1 hour
"D" → 1 day
"W" → 1 week


The `resolution_to_interval()` function handles this conversion.

### Data Formatting

TradingView expects data in a specific format:
- Historical data must include arrays for time, open, high, low, close, and volume
- Symbol information must specify details like price scale, minimum movement, and supported resolutions

## How It Works

1. The frontend TradingView widget connects to this backend
2. The widget requests available symbols and their details
3. When a user selects a symbol and timeframe, the widget requests historical data
4. This backend fetches the data from Kraken and transforms it to the format TradingView expects
5. The widget renders the chart with the provided data

## Implementation Details

### Required UDF Response Models

- `UDFSearchResult`: Format for symbol search results
- `UDFSymbolInfo`: Detailed information about a trading pair
- `UDFBar`: OHLCV data format for historical prices

### Key Endpoints

- `/widgets.json`: Defines the widget configuration for OpenBB Workspace
- `/udf/config`: Provides UDF configuration details
- `/udf/search`: Searches available trading pairs
- `/udf/symbols`: Returns detailed symbol information
- `/udf/history`: Retrieves historical price data
- `/udf/time`: Returns current server time

## Getting Started

### Running the Application

```python
Run `uvicorn main:app --port 5050`
```

The server will start on http://localhost:5050

Now you can add the backend to the [data connectors page](https://pro.openbb.co/app/data-connectors) with the base url of your API. In this case it is `http://localhost:5050`

The widget will be available when searching for `Advanced Charting`.

### Testing

You can test the API endpoints directly:

- Configuration: http://localhost:5050/udf/config
- Symbol Search: http://localhost:5050/udf/search?query=BTC
- Symbol Info: http://localhost:5050/udf/symbols?symbol=XBTUSDC
- Historical Data: http://localhost:5050/udf/history?symbol=XBTUSDC&resolution=D&from=1609459200&to=1640995200

## Extending for Other Data Sources

To adapt this for other data sources:
1. Modify the `fetch_kraken_data()` function to connect to your data source
2. Update the data transformation logic in each endpoint
3. Adjust the resolution mapping to match your data source's intervals

## Resources

- [TradingView UDF Documentation](https://www.tradingview.com/charting-library-docs/latest/connecting_data/UDF/)
- [Kraken API Documentation](https://docs.kraken.com/rest/)