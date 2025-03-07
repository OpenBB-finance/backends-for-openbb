from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel
import httpx
import time
import logging
from enum import Enum

app = FastAPI(title="TradingView UDF Binance API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Binance API base URL
BINANCE_API_BASE = "https://api.binance.com"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Models
class UDFSearchResult(BaseModel):
    symbol: str
    full_name: str
    description: str
    exchange: str
    ticker: str
    type: str

class UDFSymbolInfo(BaseModel):
    name: str
    ticker: str
    description: str
    type: str
    exchange: str
    listed_exchange: str
    timezone: str
    session: str
    minmov: int
    pricescale: int
    has_intraday: bool
    has_daily: bool
    has_weekly_and_monthly: bool
    supported_resolutions: List[str]
    currency_code: str
    original_currency_code: str
    volume_precision: int

class UDFBar(BaseModel):
    s: str
    errmsg: Optional[str] = None
    t: Optional[List[int]] = None
    c: Optional[List[float]] = None
    o: Optional[List[float]] = None
    h: Optional[List[float]] = None
    l: Optional[List[float]] = None
    v: Optional[List[float]] = None
    nextTime: Optional[int] = None

class ResolutionEnum(str, Enum):
    ONE_MINUTE = "1"
    THREE_MINUTES = "3"
    FIVE_MINUTES = "5"
    FIFTEEN_MINUTES = "15"
    THIRTY_MINUTES = "30"
    ONE_HOUR = "60"
    TWO_HOURS = "120"
    FOUR_HOURS = "240"
    SIX_HOURS = "360"
    EIGHT_HOURS = "480"
    TWELVE_HOURS = "720"
    ONE_DAY = "D"
    THREE_DAYS = "3D"
    ONE_WEEK = "W"
    ONE_MONTH = "M"

# Helper functions
def resolution_to_interval(resolution: str) -> str:
    resolution_map = {
        "1": "1m",
        "3": "3m",
        "5": "5m",
        "15": "15m",
        "30": "30m",
        "60": "1h",
        "120": "2h",
        "240": "4h",
        "360": "6h",
        "480": "8h",
        "720": "12h",
        "D": "1d",
        "1D": "1d",
        "3D": "3d",
        "W": "1w",
        "1W": "1w",
        "M": "1M",
        "1M": "1M",
    }
    return resolution_map.get(resolution, "1h")

async def fetch_binance_data(endpoint: str, params: Dict[str, Any] = None) -> Any:
    url = f"{BINANCE_API_BASE}{endpoint}"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        logger.error(f"Error fetching data from Binance API: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching data from Binance: {str(e)}")
    
@app.get("/")
async def root():
    return "OpenBB Workspace Backend example for bringing your own data to charting tradingview"

@app.get("/widgets.json")
async def get_widgets():
    return {
        "udf_binance": {
            "name": "Advanced Charting - Binance",
            "description":
                "Advanced charting for Binance, historical data from any binance asset",
            "type": "advanced_charting",
            "endpoint": "/udf",
            "data": {
                "defaultSymbol": "BTCUSDT",
            }
        }
    }

# UDF API endpoints
@app.get("/udf/config")
async def get_config():
    config = {
        "supported_resolutions": ["1", "3", "5", "15", "30", "60", "120", "240", "360", "480", "720", "D", "3D", "W", "M"],
        "supports_group_request": False,
        "supports_marks": False,
        "supports_search": True,
        "supports_timescale_marks": False,
        "supports_time": True,
        "exchanges": [
            {"value": "", "name": "All Exchanges", "desc": ""},
            {"value": "BINANCE", "name": "Binance", "desc": "Binance Exchange"}
        ],
        "symbols_types": [
            {"name": "All types", "value": ""},
            {"name": "Crypto", "value": "crypto"}
        ]
    }
    return config

@app.get("/udf/search", response_model=List[UDFSearchResult])
async def search_symbols(
    query: str = Query("", description="Search query"),
    limit: int = Query(30, description="Limit of results")
):
    try:
        exchange_info = await fetch_binance_data("/api/v3/exchangeInfo")
        
        filtered_symbols = [
            symbol for symbol in exchange_info["symbols"]
            if (query.lower() in symbol["symbol"].lower() or
                query.lower() in symbol["baseAsset"].lower() or
                query.lower() in symbol["quoteAsset"].lower())
        ][:limit]
        
        results = [
            UDFSearchResult(
                symbol=symbol["symbol"],
                full_name=f"BINANCE:{symbol['symbol']}",
                description=f"{symbol['baseAsset']}/{symbol['quoteAsset']}",
                exchange="BINANCE",
                ticker=symbol["symbol"],
                type="crypto"
            )
            for symbol in filtered_symbols
        ]
        
        return results
    except Exception as e:
        logger.error(f"Error in symbol search: {e}")
        return []

@app.get("/udf/symbols")
async def get_symbol_info(symbol: str = Query(..., description="Symbol to get info for")):
    clean_symbol = symbol.split(":")[-1] if ":" in symbol else symbol
    
    try:
        exchange_info = await fetch_binance_data("/api/v3/exchangeInfo")
        
        symbol_info = next((s for s in exchange_info["symbols"] if s["symbol"] == clean_symbol), None)
        
        if not symbol_info:
            return {"s": "error", "errmsg": "Symbol not found"}
        
        result = {
            "name": symbol_info["symbol"],
            "ticker": symbol_info["symbol"],
            "description": f"{symbol_info['baseAsset']}/{symbol_info['quoteAsset']}",
            "type": "crypto",
            "exchange": "BINANCE",
            "listed_exchange": "BINANCE",
            "timezone": "Etc/UTC",
            "session": "24x7",
            "minmov": 1,
            "pricescale": 100000000,  # Adjust based on the asset precision
            "has_intraday": True,
            "has_daily": True,
            "has_weekly_and_monthly": True,
            "supported_resolutions": ["1", "3", "5", "15", "30", "60", "120", "240", "360", "480", "720", "D", "3D", "W", "M"],
            "currency_code": symbol_info["quoteAsset"],
            "original_currency_code": symbol_info["quoteAsset"],
            "volume_precision": 8
        }
        
        return result
    except Exception as e:
        logger.error(f"Error in symbol info: {e}")
        return {"s": "error", "errmsg": "Failed to fetch symbol info"}

@app.get("/udf/history")
async def get_history(
    symbol: str = Query(..., description="Symbol"),
    resolution: str = Query(..., description="Resolution"),
    from_time: int = Query(..., alias="from", description="From timestamp"),
    to_time: int = Query(..., alias="to", description="To timestamp"),
    countback: Optional[int] = Query(0, description="Count back")
):
    clean_symbol = symbol.split(":")[-1] if ":" in symbol else symbol
    interval = resolution_to_interval(resolution)
    
    try:
        params = {
            "symbol": clean_symbol,
            "interval": interval
        }
        
        if countback > 0:
            params["limit"] = str(countback)
            params["endTime"] = str(to_time * 1000)  # Convert to milliseconds
        else:
            params["startTime"] = str(from_time * 1000)  # Convert to milliseconds
            params["endTime"] = str(to_time * 1000)  # Convert to milliseconds
            params["limit"] = "1000"  # Binance max limit
        
        klines = await fetch_binance_data("/api/v3/klines", params)
        
        if not klines:
            return {"s": "no_data"}
        
        result = {
            "s": "ok",
            "t": [int(kline[0] // 1000) for kline in klines],  # Open time (convert from ms to s)
            "o": [float(kline[1]) for kline in klines],  # Open price
            "h": [float(kline[2]) for kline in klines],  # High price
            "l": [float(kline[3]) for kline in klines],  # Low price
            "c": [float(kline[4]) for kline in klines],  # Close price
            "v": [float(kline[5]) for kline in klines]   # Volume
        }
        
        return result
    except Exception as e:
        logger.error(f"Error in history data: {e}")
        return {"s": "error", "errmsg": "Failed to fetch history data"}

@app.get("/udf/time")
async def get_server_time():
    try:
        time_data = await fetch_binance_data("/api/v3/time")
        return int(time_data["serverTime"] // 1000)  # Convert from ms to s
    except Exception as e:
        logger.error(f"Error in server time: {e}")
        return int(time.time())  # Return current time as fallback

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)