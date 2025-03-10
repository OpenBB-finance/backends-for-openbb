from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel
import httpx
import time
import logging
from enum import Enum
import json
from pathlib import Path
from fastapi.responses import JSONResponse

app = FastAPI(title="TradingView UDF Kraken API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Kraken API base URL
KRAKEN_API_BASE = "https://api.kraken.com"

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
        "1": "1",
        "3": "3",
        "5": "5",
        "15": "15",
        "30": "30",
        "60": "60",
        "120": "120",
        "240": "240",
        "360": "360",
        "480": "480",
        "720": "720",
        "D": "1440",
        "1D": "1440",
        "3D": "4320",
        "W": "10080",
        "1W": "10080",
        "M": "21600",
        "1M": "21600",
    }
    return resolution_map.get(resolution, "60")

async def fetch_kraken_data(endpoint: str, params: Dict[str, Any] = None) -> Any:
    url = f"{KRAKEN_API_BASE}{endpoint}"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            
            # Kraken API returns errors in a specific format
            if data.get("error") and len(data["error"]) > 0:
                logger.error(f"Kraken API error: {data['error']}")
                raise HTTPException(status_code=500, detail=f"Kraken API error: {data['error']}")
                
            return data
    except httpx.HTTPError as e:
        logger.error(f"Error fetching data from Kraken API: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching data from Kraken: {str(e)}")
    
@app.get("/")
async def root():
    return "OpenBB Workspace Backend example for bringing your own data to charting tradingview"

@app.get("/widgets.json")
def get_widgets():
    """Widgets configuration file for the OpenBB Custom Backend"""
    return JSONResponse(
        content=json.load((Path(__file__).parent.resolve() / "widgets.json").open())
    )

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
            {"value": "KRAKEN", "name": "Kraken", "desc": "Kraken Exchange"}
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
        # Get asset pairs from Kraken
        asset_pairs = await fetch_kraken_data("/0/public/AssetPairs")
        
        filtered_symbols = []
        for pair_name, pair_info in asset_pairs.get("result", {}).items():
            # Skip darkpool pairs
            if pair_name.startswith("."):
                continue
                
            base_asset = pair_info.get("base", "")
            quote_asset = pair_info.get("quote", "")
            wsname = pair_info.get("wsname", pair_name)
            
            if (query.lower() in pair_name.lower() or 
                query.lower() in base_asset.lower() or 
                query.lower() in quote_asset.lower()):
                filtered_symbols.append({
                    "symbol": pair_name,
                    "wsname": wsname,
                    "base": base_asset,
                    "quote": quote_asset,
                    "altname": pair_info.get("altname", pair_name)
                })
                
            if len(filtered_symbols) >= limit:
                break
        
        results = [
            UDFSearchResult(
                symbol=symbol["symbol"],
                full_name=f"KRAKEN:{symbol['symbol']}",
                description=f"{symbol['base']}/{symbol['quote']}",
                exchange="KRAKEN",
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
        # Get asset pairs from Kraken
        asset_pairs = await fetch_kraken_data("/0/public/AssetPairs")
        
        if clean_symbol not in asset_pairs.get("result", {}):
            return {"s": "error", "errmsg": "Symbol not found"}
            
        symbol_info = asset_pairs["result"][clean_symbol]
        
        # Determine price scale based on pair decimals
        pair_decimals = symbol_info.get("pair_decimals", 8)
        price_scale = 10 ** pair_decimals
        
        result = {
            "name": symbol_info.get("wsname", clean_symbol),
            "ticker": clean_symbol,
            "description": f"{symbol_info.get('base', '')}/{symbol_info.get('quote', '')}",
            "type": "crypto",
            "exchange": "KRAKEN",
            "listed_exchange": "KRAKEN",
            "timezone": "Etc/UTC",
            "session": "24x7",
            "minmov": 1,
            "pricescale": price_scale,
            "has_intraday": True,
            "has_daily": True,
            "has_weekly_and_monthly": True,
            "supported_resolutions": ["1", "3", "5", "15", "30", "60", "120", "240", "360", "480", "720", "D", "3D", "W", "M"],
            "currency_code": symbol_info.get("quote", ""),
            "original_currency_code": symbol_info.get("quote", ""),
            "volume_precision": symbol_info.get("lot_decimals", 8)
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
            "pair": clean_symbol,
            "interval": interval
        }
        
        # Kraken OHLC endpoint accepts 'since' parameter in seconds
        if from_time > 0:
            params["since"] = str(from_time)
            
        # Kraken doesn't have a direct 'to' parameter or 'countback'
        # We'll fetch data and filter it on our side
        
        ohlc_data = await fetch_kraken_data("/0/public/OHLC", params)
        
        if not ohlc_data or "result" not in ohlc_data:
            return {"s": "no_data"}
            
        # Kraken returns data in format {pair_name: [[time, open, high, low, close, vwap, volume, count], ...], last: timestamp}
        klines = ohlc_data["result"].get(clean_symbol, [])
        
        # Filter by time range
        filtered_klines = [
            kline for kline in klines 
            if from_time <= kline[0] <= to_time
        ]
        
        if not filtered_klines:
            return {"s": "no_data"}
            
        # Apply countback if specified
        if countback > 0 and len(filtered_klines) > countback:
            filtered_klines = filtered_klines[-countback:]
        
        result = {
            "s": "ok",
            "t": [int(kline[0]) for kline in filtered_klines],       # Time
            "o": [float(kline[1]) for kline in filtered_klines],     # Open
            "h": [float(kline[2]) for kline in filtered_klines],     # High
            "l": [float(kline[3]) for kline in filtered_klines],     # Low
            "c": [float(kline[4]) for kline in filtered_klines],     # Close
            "v": [float(kline[6]) for kline in filtered_klines]      # Volume
        }
        
        return result
    except Exception as e:
        logger.error(f"Error in history data: {e}")
        return {"s": "error", "errmsg": f"Failed to fetch history data: {str(e)}"}

@app.get("/udf/time")
async def get_server_time():
    try:
        time_data = await fetch_kraken_data("/0/public/Time")
        return int(time_data["result"]["unixtime"])  # Kraken returns time in seconds
    except Exception as e:
        logger.error(f"Error in server time: {e}")
        return int(time.time())  # Return current time as fallback

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)