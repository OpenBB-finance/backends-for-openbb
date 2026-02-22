import random
from datetime import datetime
from fastapi import APIRouter, Query, HTTPException

from core import register_widget, WIDGETS

router = APIRouter()

MOCK_SYMBOLS = {
    "AAPL": {
        "name": "Apple Inc.",
        "description": "Apple Inc. Stock",
        "type": "stock",
        "exchange": "NASDAQ",
        "pricescale": 100,
        "minmov": 1,
        "volume_precision": 0,
    },
    "MSFT": {
        "name": "Microsoft Corporation",
        "description": "Microsoft Corporation Stock",
        "type": "stock",
        "exchange": "NASDAQ",
        "pricescale": 100,
        "minmov": 1,
        "volume_precision": 0,
    },
    "GOOGL": {
        "name": "Alphabet Inc.",
        "description": "Alphabet Inc. Stock",
        "type": "stock",
        "exchange": "NASDAQ",
        "pricescale": 100,
        "minmov": 1,
        "volume_precision": 0,
    },
}


def generate_mock_price_data(
    symbol: str, from_time: int, to_time: int, resolution: str
) -> dict:
    """
    Generate mock OHLCV data for a symbol.

    Creates realistic-looking price data for the TradingView chart.

    Args:
        symbol: The stock symbol to generate data for
        from_time: Start timestamp in seconds
        to_time: End timestamp in seconds
        resolution: Timeframe (1, 5, 15, 30, 60, D, W, M)

    Returns:
        Dictionary containing OHLCV data in TradingView's format
    """
    resolution_minutes = {
        "1": 1,
        "5": 5,
        "15": 15,
        "30": 30,
        "60": 60,
        "D": 1440,
        "W": 10080,
        "M": 43200,
    }.get(resolution, 60)

    current_time = from_time
    timestamps = []
    while current_time <= to_time:
        timestamps.append(current_time)
        current_time += resolution_minutes * 60

    base_price = 100.0 if symbol == "AAPL" else 200.0 if symbol == "MSFT" else 150.0
    prices = []
    current_price = base_price

    for _ in timestamps:
        change = random.uniform(-2, 2)
        current_price += change
        current_price = max(current_price, 1.0)
        prices.append(current_price)

    opens = []
    highs = []
    lows = []
    closes = []
    volumes = []

    for price in prices:
        is_bullish = random.random() > 0.5

        if is_bullish:
            open_price = price * 0.99
            close_price = price * 1.01
        else:
            open_price = price * 1.01
            close_price = price * 0.99

        high_price = max(open_price, close_price) * 1.02
        low_price = min(open_price, close_price) * 0.98

        opens.append(open_price)
        highs.append(high_price)
        lows.append(low_price)
        closes.append(close_price)

        price_change = abs(close_price - open_price)
        base_volume = 1000000
        volume_multiplier = 1 + (price_change / open_price) * 10
        volume = int(base_volume * volume_multiplier * random.uniform(0.8, 1.2))
        volumes.append(volume)

    return {
        "s": "ok",
        "t": timestamps,
        "o": opens,
        "h": highs,
        "l": lows,
        "c": closes,
        "v": volumes,
    }


@router.get("/udf/config")
async def get_config():
    """
    UDF configuration endpoint.

    Tells TradingView what features and data we support.
    """
    return {
        "supported_resolutions": ["1", "5", "15", "30", "60", "D", "W", "M"],
        "supports_group_request": False,
        "supports_marks": False,
        "supports_search": True,
        "supports_timescale_marks": False,
        "supports_time": True,
        "exchanges": [
            {"value": "", "name": "All Exchanges", "desc": ""},
            {"value": "NASDAQ", "name": "NASDAQ", "desc": "NASDAQ Stock Exchange"},
        ],
        "symbols_types": [
            {"name": "All types", "value": ""},
            {"name": "Stocks", "value": "stock"},
        ],
    }


@router.get("/udf/search")
async def search_symbols(
    query: str = Query("", description="Search query"),
    limit: int = Query(30, description="Limit of results"),
):
    """
    UDF symbol search endpoint.

    Allows users to search for symbols in the data feed.
    """
    results = []
    for symbol, info in MOCK_SYMBOLS.items():
        if query.lower() in symbol.lower() or query.lower() in info["name"].lower():
            results.append({
                "symbol": symbol,
                "full_name": f"NASDAQ:{symbol}",
                "description": info["description"],
                "exchange": "NASDAQ",
                "ticker": symbol,
                "type": "stock",
            })
            if len(results) >= limit:
                break
    return results


@router.get("/udf/symbols")
async def get_symbol_info(
    symbol: str = Query(..., description="Symbol to get info for")
):
    """
    UDF symbol info endpoint.

    Provides detailed information about a specific symbol.
    """
    clean_symbol = symbol.split(":")[-1]

    if clean_symbol not in MOCK_SYMBOLS:
        raise HTTPException(status_code=404, detail="Symbol not found")

    info = MOCK_SYMBOLS[clean_symbol]

    return {
        "name": clean_symbol,
        "description": info["name"],
        "type": info["type"],
        "exchange": info["exchange"],
        "pricescale": info["pricescale"],
        "minmov": info["minmov"],
        "volume_precision": info["volume_precision"],
        "has_volume": True,
        "has_intraday": True,
        "has_daily": True,
        "has_weekly_and_monthly": True,
        "supported_resolutions": ["1", "5", "15", "30", "60", "D", "W", "M"],
        "session-regular": "0930-1600",
        "timezone": "America/New_York",
    }


@router.get("/udf/history")
async def get_history(
    symbol: str = Query(..., description="Symbol"),
    resolution: str = Query(..., description="Resolution"),
    from_time: int = Query(..., alias="from", description="From timestamp"),
    to_time: int = Query(..., alias="to", description="To timestamp"),
):
    """
    UDF historical data endpoint.

    Provides actual price data for the chart.
    """
    clean_symbol = symbol.split(":")[-1] if ":" in symbol else symbol

    if clean_symbol not in MOCK_SYMBOLS:
        return {"s": "error", "errmsg": "Symbol not found"}

    return generate_mock_price_data(clean_symbol, from_time, to_time, resolution)


@router.get("/udf/time")
async def get_server_time():
    """
    UDF server time endpoint.

    Provides current server time for chart synchronization.
    """
    return int(datetime.now().timestamp())


@register_widget({
    "name": "TradingView Chart",
    "description": "Advanced charting with TradingView using mock data",
    "category": "Finance",
    "type": "advanced_charting",
    "endpoint": "/udf",
    "gridData": {"w": 20, "h": 20},
    "data": {
        "defaultSymbol": "AAPL",
        "updateFrequency": 60000,
        "chartConfig": {
            "upColor": "#26a69a",
            "downColor": "#ef5350",
            "borderUpColor": "#26a69a",
            "borderDownColor": "#ef5350",
            "wickUpColor": "#26a69a",
            "wickDownColor": "#ef5350",
            "volumeUpColor": "#26a69a",
            "volumeDownColor": "#ef5350",
            "showVolume": True,
        },
    },
})
def tradingview_chart():
    """Dummy function for TradingView chart widget registration"""
    pass
