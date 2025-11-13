import json
import asyncio
from pathlib import Path
from typing import Dict, Set
import requests
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
import websockets

app = FastAPI()

origins = [
    "https://pro.openbb.co",
    "https://excel.openbb.co",
    "http://localhost:1420"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ROOT_PATH = Path(__file__).parent.resolve()

# Store active WebSocket connections and data cache
active_connections: Dict[str, Set[WebSocket]] = {}
historical_data_cache: Dict[str, list] = {}

@app.get("/")
def read_root():
    return {"Info": "Full example for OpenBB Custom Backend"}


@app.get("/widgets.json")
def get_widgets():
    """Widgets configuration file for the OpenBB Custom Backend"""
    return JSONResponse(
        content=json.load((Path(__file__).parent.resolve() / "widgets.json").open())
    )


async def fetch_binance_historical_data(symbol: str, interval: str) -> list:
    """Fetch historical OHLC data from Binance"""
    try:
        response = requests.get(
            f"https://api.binance.us/api/v3/klines",
            params={"symbol": symbol, "interval": interval, "limit": 1000}
        )

        if response.status_code == 200:
            data = response.json()
            # Transform to lightweight-charts format
            transformed = []
            for kline in data:
                transformed.append({
                    "time": kline[0] / 1000,  # Convert ms to seconds
                    "open": float(kline[1]),
                    "high": float(kline[2]),
                    "low": float(kline[3]),
                    "close": float(kline[4]),
                    "volume": float(kline[5])
                })
            return transformed
        return []
    except Exception as e:
        print(f"Error fetching historical data: {e}")
        return []


async def connect_to_binance_websocket(symbol: str, interval: str, stream_key: str):
    """Connect to Binance WebSocket and broadcast to connected clients"""
    ws_url = f"wss://stream.binance.us:9443/ws/{symbol.lower()}@kline_{interval}"

    while True:
        try:
            async with websockets.connect(ws_url) as binance_ws:
                print(f"Connected to Binance WebSocket: {stream_key}")

                async for message in binance_ws:
                    data = json.loads(message)

                    if data.get('e') == 'kline':
                        kline = data['k']
                        candle = {
                            "time": kline['t'] / 1000,
                            "open": float(kline['o']),
                            "high": float(kline['h']),
                            "low": float(kline['l']),
                            "close": float(kline['c']),
                            "volume": float(kline['v'])
                        }

                        # Broadcast to all connected clients for this stream
                        if stream_key in active_connections:
                            disconnected = set()
                            for connection in active_connections[stream_key]:
                                try:
                                    await connection.send_json(candle)
                                except Exception:
                                    disconnected.add(connection)

                            # Remove disconnected clients
                            active_connections[stream_key] -= disconnected

        except Exception as e:
            print(f"WebSocket error for {stream_key}: {e}")
            await asyncio.sleep(5)  # Wait before reconnecting


@app.websocket("/ws/binance")
async def websocket_endpoint(websocket: WebSocket, symbol: str = "BTCUSDT", interval: str = "1h"):
    """WebSocket endpoint for clients to receive real-time data"""
    await websocket.accept()

    stream_key = f"{symbol}_{interval}"

    # Add connection to active connections
    if stream_key not in active_connections:
        active_connections[stream_key] = set()
        # Start background task to connect to Binance if not already running
        asyncio.create_task(connect_to_binance_websocket(symbol, interval, stream_key))

    active_connections[stream_key].add(websocket)

    try:
        # Send historical data first
        if stream_key not in historical_data_cache:
            historical_data_cache[stream_key] = await fetch_binance_historical_data(symbol, interval)

        await websocket.send_json({
            "type": "historical",
            "data": historical_data_cache[stream_key]
        })

        # Keep connection alive and handle any messages from client
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections[stream_key].discard(websocket)
        if not active_connections[stream_key]:
            del active_connections[stream_key]


@app.get("/html_binance_ohlc")
async def html_binance_ohlc(
    symbol: str = "BTCUSDT",
    interval: str = "1h",
    raw: bool = False,
    theme: str = "dark"
):
    """Display Binance OHLC data using lightweight-charts or return raw data"""

    # If raw=true, return the historical data as JSON for AI
    if raw:
        stream_key = f"{symbol}_{interval}"
        if stream_key not in historical_data_cache:
            historical_data_cache[stream_key] = await fetch_binance_historical_data(symbol, interval)
        return historical_data_cache[stream_key]

    # Otherwise, return themed HTML
    html_content = (ROOT_PATH / "index.html").read_text()

    # Replace theme placeholder if needed (will be handled in HTML)
    return HTMLResponse(content=html_content)