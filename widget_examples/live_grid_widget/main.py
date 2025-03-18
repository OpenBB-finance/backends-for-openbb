import json
from pathlib import Path
from textwrap import dedent
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.websockets import WebSocketState
import numpy as np
import asyncio
from typing import List
from datetime import datetime

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

@app.get("/")
def read_root():
    return {"Info": "Full example for OpenBB Custom Backend"}


@app.get("/widgets.json")
def get_widgets():
    """Widgets configuration file for the OpenBB Custom Backend"""
    return JSONResponse(
        content=json.load((Path(__file__).parent.resolve() / "widgets.json").open())
    )

# Sample data store
WS_DATA = {
    "AAPL": {
        "price": 150.0,
        "prev_close": 145.54,
        "volume": 1000000,
        "change": 4.46,
        "change_percent": 0.03,
    },
    "AMZN": {
        "price": 3400.0,
        "prev_close": 3450.0,
        "volume": 1000000,
        "change": -50.0,
        "change_percent": -0.01,
    },
    "GOOGL": {
        "price": 2900.0,
        "prev_close": 2850.0,
        "volume": 1000000,
        "change": 50.0,
        "change_percent": 0.01,
    },
    "MSFT": {
        "price": 300.0,
        "prev_close": 305.0,
        "volume": 1000000,
        "change": -95.0,
        "change_percent": -0.12,
    },
    "TSLA": {
        "price": 700.0,
        "prev_close": 795.0,
        "volume": 1000000,
        "change": 100.0,
        "change_percent": 0.12,
    },
}

def get_ws_data(symbol: str):
    """Generate real-time data for a symbol"""
    data = WS_DATA.get(symbol, {"price": 100.0, "prev_close": 100.0, "volume": 1000000})
    
    price = data["price"] + np.random.uniform(-10, 10)
    volume = data["volume"] + np.random.randint(100, 1000)
    change = price - data["prev_close"]
    change_percent = change / data["prev_close"]
    
    WS_DATA[symbol].update(dict(price=price, volume=volume))
    
    return {
        "symbol": symbol,
        "price": price,
        "change": change,
        "change_percent": change_percent,
        "volume": volume,
    }

# Live Feed Initial Data Endpoint (This sets the initial data for the widget + allows Copilot to grab the data)
@app.get("/test_websocket")
def test_websocket(symbol: str):
    """Initial data endpoint"""
    symbols = symbol.split(",")
    return [
        {
            "date": datetime.now().date(),
            **get_ws_data(symbol),
            "market_cap": np.random.randint(1000000000, 2000000000),
        }
        for symbol in symbols
    ]

# Live Feed WebSocket Endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for live updates"""
    await websocket.accept()
    try:
        await websocket_handler(websocket)
    except WebSocketDisconnect:
        return
    except Exception as e:
        await websocket.close(code=1011)
        raise HTTPException(status_code=500, detail=str(e))

# Sample WebSocket Handler
async def websocket_handler(websocket: WebSocket):
    subbed_symbols: set[str] = set()

    async def consumer_handler(ws: WebSocket):
        try:
            async for data in ws.iter_json():
                if symbols := data.get("params", {}).get("symbol"):
                    if isinstance(symbols, str):
                        symbols = symbols.split(",")

                    subbed_symbols.clear()
                    subbed_symbols.update(set(symbols))

        except WebSocketDisconnect:
            pass
        except RuntimeError:
            await ws.close()

    async def producer_handler(ws: WebSocket):
        try:
            while websocket.client_state != WebSocketState.DISCONNECTED:
                current_symbols = list(subbed_symbols)
                np.random.shuffle(current_symbols)

                for symbol in current_symbols:
                    await ws.send_json(get_ws_data(symbol))
                    await asyncio.sleep(np.random.uniform(0.5, 0.8))

                await asyncio.sleep(np.random.uniform(0.1, 0.3))

        except WebSocketDisconnect:
            pass
        except RuntimeError:
            await ws.close()

    consumer_task = asyncio.create_task(consumer_handler(websocket))
    producer_task = asyncio.create_task(producer_handler(websocket))

    done, pending = await asyncio.wait(
        [consumer_task, producer_task], return_when=asyncio.FIRST_COMPLETED
    )

    for task in pending:
        task.cancel()