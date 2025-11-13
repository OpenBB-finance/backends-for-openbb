# HTML Widget WebSocket Refactor: Raw Data Support

## Overview

Refactored the HTML widget example (`widget-examples/widget-types/html_widget/`) to align with the Plotly chart widget pattern, enabling raw data support for better AI integration. The widget now uses a Python WebSocket server as an intermediary between Binance and the frontend, rather than connecting directly from the browser.

## Problem Statement

The previous implementation had the following limitations:

1. **Direct browser-to-Binance connection**: The HTML connected directly to Binance's WebSocket, which:
   - Made it impossible to support the `raw` parameter for AI data
   - Couldn't be monitored or cached server-side
   - Limited server-side data processing capabilities

2. **No raw data support**: Without the `raw` flag, the AI would receive HTML markup instead of structured JSON data, making it difficult for the AI to understand and work with the data.

3. **No theme support**: The widget didn't respect the user's light/dark theme preference.

4. **No server-side caching**: Historical data was fetched on every page load from the browser.

## Architecture Changes

### Before (Direct Connection)
```
Browser HTML → Binance WebSocket API
Browser HTML → Binance REST API (historical data)
```

### After (Python Intermediary)
```
Browser HTML → Python WebSocket Server → Binance WebSocket API
                     ↓
              Cache & Broadcast
                     ↓
              Multiple Clients
```

## Implementation Details

### 1. Python Backend (`main.py`)

#### Added Dependencies
- `websockets`: For connecting to Binance WebSocket
- `FastAPI WebSocket`: For serving WebSocket connections to clients
- `asyncio`: For managing concurrent connections

#### Key Components

**WebSocket Connection Management** (Lines 30-31)
```python
active_connections: Dict[str, Set[WebSocket]] = {}
historical_data_cache: Dict[str, list] = {}
```
- Maintains active client connections grouped by `symbol_interval` key
- Caches historical data to avoid repeated API calls

**Historical Data Fetching** (Lines 46-71)
```python
async def fetch_binance_historical_data(symbol: str, interval: str) -> list
```
- Fetches 1000 candles from Binance REST API
- Transforms data to lightweight-charts format
- Returns structured JSON with OHLCV data

**Binance WebSocket Bridge** (Lines 74-111)
```python
async def connect_to_binance_websocket(symbol: str, interval: str, stream_key: str)
```
- Connects to Binance WebSocket stream
- Transforms real-time kline data
- Broadcasts to all connected clients for that stream
- Handles reconnection with 5-second backoff
- Automatically cleans up disconnected clients

**Client WebSocket Endpoint** (Lines 114-145)
```python
@app.websocket("/ws/binance")
async def websocket_endpoint(websocket: WebSocket, symbol: str, interval: str)
```
- Accepts client WebSocket connections
- Sends cached historical data immediately on connect
- Adds client to broadcast list for real-time updates
- Starts Binance connection if not already running
- Handles disconnection cleanup

**HTTP Endpoint with Raw Support** (Lines 148-168)
```python
@app.get("/html_binance_ohlc")
async def html_binance_ohlc(symbol: str, interval: str, raw: bool, theme: str)
```
- When `raw=true`: Returns JSON array of OHLCV data for AI
- When `raw=false`: Returns themed HTML
- Supports `theme` parameter (light/dark)
- Uses same data cache as WebSocket endpoint

### 2. Frontend (`index.html`)

#### Theme Support (Lines 70-94)
```javascript
const themes = {
    dark: { background: '#131722', textColor: '#d1d4dc', ... },
    light: { background: '#ffffff', textColor: '#191919', ... }
};
```
- Parses `theme` parameter from URL
- Applies theme colors to chart and body
- Defaults to dark theme

#### WebSocket Connection (Lines 133-188)
```javascript
function connectWebSocket()
```
- Constructs WebSocket URL based on current page origin
- Handles two message types:
  1. `{ type: 'historical', data: [...] }` - Initial data load
  2. `{ time, open, high, low, close, volume }` - Real-time updates
- Sends data to parent window via `postMessage` for AI integration
- Implements automatic reconnection with 5-second delay

**Key Changes:**
- Removed direct Binance API calls
- Removed `transformKline` function (transformation now happens server-side)
- Changed from `fetchHistoricalData()` to `connectWebSocket()` for initialization

### 3. Widget Configuration (`widgets.json`)

Added raw data support and parameters:

```json
{
  "raw": true,
  "params": {
    "symbol": {
      "label": "Symbol",
      "type": "text",
      "value": "BTCUSDT"
    },
    "interval": {
      "label": "Interval",
      "type": "text",
      "value": "1h"
    }
  }
}
```

## Benefits

### 1. AI Integration
- **Before**: AI received HTML markup, difficult to parse and understand
- **After**: AI receives structured JSON array with clean OHLCV data
- Matches the pattern established by `Chart.tsx` component

### 2. Performance Optimization
- Historical data cached server-side (per symbol/interval)
- Multiple clients share same Binance WebSocket connection
- Reduced Binance API calls
- Faster initial load for subsequent clients

### 3. Server-Side Control
- Can implement rate limiting
- Can add data transformations
- Can log/monitor all data flowing through
- Can implement custom business logic

### 4. User Experience
- Theme support (light/dark)
- Customizable parameters (symbol, interval)
- Toggle button in UI to switch between HTML and raw data views
- Consistent behavior with Chart widgets

### 5. Scalability
- One Binance connection serves multiple clients
- Connection pooling by stream key (`symbol_interval`)
- Automatic cleanup of unused connections
- Graceful handling of disconnections

## Data Flow

### Initial Connection
1. Client loads HTML page with parameters (symbol, interval, theme)
2. HTML connects to `/ws/binance?symbol=BTCUSDT&interval=1h`
3. Python accepts connection and checks cache
4. If cache miss: Python fetches historical data from Binance REST API
5. Python sends `{ type: 'historical', data: [...] }` to client
6. If Binance WebSocket not running: Python starts background task
7. Python adds client to broadcast list
8. Client receives historical data and renders chart

### Real-Time Updates
1. Binance sends kline update to Python WebSocket
2. Python transforms data to lightweight-charts format
3. Python broadcasts to all clients subscribed to that stream
4. Client receives update and updates chart

### Raw Data Request (for AI)
1. Frontend requests `/html_binance_ohlc?symbol=BTCUSDT&interval=1h&raw=true`
2. Python checks cache for `BTCUSDT_1h`
3. If cache miss: Python fetches from Binance
4. Python returns JSON array directly
5. Frontend displays data in AgGrid table
6. AI can parse and understand the structured data

## Comparison with Chart Widget Pattern

This implementation mirrors the Plotly chart widget (`chart_widget/main.py`):

| Feature | Chart Widget | HTML Widget (New) |
|---------|-------------|-------------------|
| Raw parameter | ✅ Returns DataFrame as JSON | ✅ Returns OHLCV array as JSON |
| Theme parameter | ✅ Template selection | ✅ Color scheme selection |
| Server-side data | ✅ Fetches from API | ✅ Fetches and caches |
| Real-time updates | ❌ Static data | ✅ WebSocket streaming |
| Raw flag in widgets.json | ✅ `"raw": true` | ✅ `"raw": true` |
| Parameters | ✅ Configurable | ✅ Configurable (symbol, interval) |

## Technical Considerations

### Connection Management
- Uses `Set[WebSocket]` for O(1) add/remove operations
- Groups connections by stream key to minimize Binance connections
- Lazy initialization: Binance connection only starts when first client connects

### Error Handling
- Graceful degradation on Binance connection failure
- Automatic reconnection with exponential backoff
- Client-side reconnection logic
- Disconnected client cleanup to prevent memory leaks

### Data Consistency
- Cache shared between HTTP endpoint and WebSocket
- Single source of truth for historical data
- Real-time updates maintain consistency with initial data

### Security Considerations
- CORS configured for specific origins
- No authentication required (public market data)
- WebSocket sandboxing on client side
- No user input validation needed (controlled parameters)

## Usage

### As HTML View
Access via frontend with toggle off (default):
- User sees interactive candlestick chart
- Real-time updates as they happen
- Theme matches user preference

### As Raw Data View
Access via frontend with toggle on:
- User sees AgGrid table with OHLCV data
- Can inspect exact values
- Better for data analysis

### For AI Integration
When AI queries the widget:
- Frontend automatically requests `raw=true`
- Backend returns JSON array
- AI receives structured data: `[{ time, open, high, low, close, volume }, ...]`
- AI can analyze trends, patterns, calculate indicators, etc.

## Dependencies

### Python
```
fastapi
websockets
requests
```

### JavaScript (CDN)
```
lightweight-charts
```

## Future Enhancements

Potential improvements:
1. **Multiple exchanges**: Support Coinbase, Kraken, etc.
2. **Technical indicators**: Add server-side calculation (RSI, MACD, etc.)
3. **Authentication**: Add API key support for private data
4. **Data persistence**: Store historical data in database
5. **Rate limiting**: Implement per-client limits
6. **Compression**: Use WebSocket compression for large datasets
7. **Replay mode**: Allow historical data replay for backtesting

## Testing Recommendations

1. **Single client**: Connect and verify real-time updates
2. **Multiple clients**: Open multiple browsers, verify shared connection
3. **Reconnection**: Kill Python server, verify client reconnects
4. **Theme switching**: Test light/dark themes
5. **Raw mode**: Toggle raw view, verify AgGrid displays correctly
6. **AI integration**: Query with `raw=true`, verify JSON response
7. **Symbol changes**: Change symbol parameter, verify new stream
8. **Cache behavior**: Restart server, verify cache rebuilds correctly

## Summary

This refactor brings the HTML widget example to feature parity with the Plotly chart widget, enabling:
- ✅ Raw data support for AI integration
- ✅ Theme support for better UX
- ✅ Server-side WebSocket management
- ✅ Performance optimization via caching
- ✅ Real-time data streaming
- ✅ Scalable architecture

The implementation follows the established patterns from `Chart.tsx` and `chart_widget/main.py`, ensuring consistency across the codebase while adding unique capabilities (real-time streaming) that showcase the power of HTML widgets.
