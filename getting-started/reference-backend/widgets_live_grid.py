import asyncio
from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.websockets import WebSocketState
import numpy as np

from core import register_widget

router = APIRouter()

# Sample data store
WS_DATA = {
    "AAPL": {
        "price": 150.0,
        "prev_close": 145.54,
        "volume": 1000000,
        "change": 4.46,
        "change_percent": 0.03,
    },
    "GOOGL": {
        "price": 140.0,
        "prev_close": 138.20,
        "volume": 800000,
        "change": 1.80,
        "change_percent": 0.013,
    },
    "MSFT": {
        "price": 350.0,
        "prev_close": 345.00,
        "volume": 1200000,
        "change": 5.00,
        "change_percent": 0.014,
    },
    "AMZN": {
        "price": 178.0,
        "prev_close": 175.50,
        "volume": 900000,
        "change": 2.50,
        "change_percent": 0.014,
    },
    "TSLA": {
        "price": 245.0,
        "prev_close": 240.00,
        "volume": 1500000,
        "change": 5.00,
        "change_percent": 0.021,
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


@register_widget({
    "name": "Live Grid",
    "description": "Live Grid with real-time WebSocket updates",
    "type": "live_grid",
    "endpoint": "live_grid_data",
    "wsEndpoint": "live_grid_ws",
    "gridData": {"w": 20, "h": 9},
    "data": {
        "wsRowIdColumn": "symbol",
        "table": {
            "showAll": True,
            "columnsDefs": [
                {
                    "field": "symbol",
                    "headerName": "Symbol"
                },
                {
                    "field": "price",
                    "headerName": "Price",
                    "renderFn": "showCellChange",
                    "renderFnParams": {
                        "colorValueKey": "change"
                    }
                },
                {
                    "field": "change_percent",
                    "headerName": "Change %",
                    "renderFn": "greenRed"
                },
                {
                    "field": "volume",
                    "enableCellChangeWs": False,
                    "headerName": "Volume"
                }
            ]
        }
    },
    "params": [
        {
            "paramName": "symbol",
            "description": "The symbol to get details for",
            "value": "TSLA",
            "label": "Symbol",
            "type": "text",
            "multiSelect": True,
            "options": [
                {"label": "AAPL", "value": "AAPL"},
                {"label": "GOOGL", "value": "GOOGL"},
                {"label": "MSFT", "value": "MSFT"},
                {"label": "AMZN", "value": "AMZN"},
                {"label": "TSLA", "value": "TSLA"}
            ]
        }
    ]
})
@router.get("/live_grid_data")
def get_live_grid_data(symbol: str):
    """Initial data endpoint for live grid"""
    symbols = symbol.split(",")
    return [
        {
            "date": str(datetime.now().date()),
            **get_ws_data(sym),
            "market_cap": np.random.randint(1000000000, 2000000000),
        }
        for sym in symbols
    ]


@router.websocket("/live_grid_ws")
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


async def websocket_handler(websocket: WebSocket):
    """Handle WebSocket connections for live grid updates"""
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
