"""UDF router for OpenBB Databento app."""
# pylint: disable=protected-access,too-many-arguments,too-many-locals,too-many-branches,too-many-statements,unused-argument
from typing import Any, Optional, Annotated
from datetime import datetime
from fastapi import APIRouter, Query
from pandas import DataFrame, to_datetime
from pytz import timezone

from openbb_databento.utils.udf import DatabaseDependency
from openbb_databento.utils.udf import UdfDatabase

router = APIRouter(prefix="/udf")

# This router has a dedicated startup event to initialize the symbols to use for the UDF search.
# This should happen after the database is initialized and before API requests are made.
# If the database singleton is not yet initialized, we initialize it here.


def startup_event():
    """Startup event to initialize the UDF database."""

    udf_database = UdfDatabase()
    udf_database.database().logger.info("Starting UDF database initialization...")
    UdfDatabase._continuous_assets = udf_database.continuous_assets

router.add_event_handler("startup", startup_event)

# The UDF config can be set in the UdfDatabase class.

@router.get("/config", response_model=Any)
async def udf_config(udf_database: DatabaseDependency):
    """Get UDF config."""
    return udf_database.get_udf_config()


@router.get("/symbols")
async def symbols(
    data: DatabaseDependency,
    symbol: str,
) -> dict:
    """Get symbol info."""
    symbol = symbol.replace(".C.", ".c.")
    return data.get_symbol_info(symbol)


@router.get("/search")
async def search_symbols(
    data: DatabaseDependency,
    query: str = "",
    symbol_type: Annotated[
        str,
        Query(
            description="Type of symbol to search for. Defaults to 'futures'.",
            alias="type",
        ),
    ] = "",
    exchange: str = "",
    limit: int = 20,
):
    """UDF search for symbols."""
    query = query if not query else query.strip()
    df = data.continuous_assets.copy()
    output: list = []
    if exchange and exchange != "":
        df = df.query("exchange == @exchange")

    if symbol_type != "":
        if symbol_type.lower() == "commodity":
            df = df.query("asset_class == 'Commodity/Agriculture'")
        elif symbol_type.lower() == "agriculture":
            df = df.query("asset_class == 'Commodity/Agriculture'")
        elif symbol_type.lower() == "metals":
            df = df.query("asset_class == 'Metals' or asset == 'HR'")
        elif symbol_type.lower() == "currency":
            df = df.query("asset_class.isin(['Currency'])")
        elif symbol_type.lower() == "energy":
            df = df.query("asset_class == 'Energy'")
        elif symbol_type.lower() == "interest_rates":
            df = df.query("asset_class == 'Interest Rate'")
        elif symbol_type.lower() == "equity":
            df = df.query("asset_class == 'Equity'")

    try:
        search_results = df[
            df.symbol.str.contains(query, case=False)
            | df.asset.str.contains(query, case=False)
            | df.asset_class.str.contains(query, case=False)
            | df.name.str.contains(query, case=False)
            | df.contract_unit.str.contains(query, case=False)
        ].head(limit) if query else df.head(limit) if query != "" else df

        for item in DataFrame(
            search_results
        ).sort_values(by=["asset_class", "asset", "name"]).to_dict("records"):
            item["symbol"] = item["symbol"].replace(".c.", ".C.")
            multiplier = item.get("contract_unit_multiplier", 1)
            if multiplier is None or multiplier == 0:
                multiplier = 1
            elif multiplier < 1:
                multiplier = float(multiplier)
            elif multiplier > 1:
                multiplier = int(multiplier)
            output.append(
                {
                    "symbol": item["symbol"],
                    "ticker": item["symbol"],
                    "exchange": item["exchange"],
                    "listed_exchange": item["exchange"],
                    "full_name": f"{item['exchange']}:{item['symbol']}",
                    "description": (
                        f"{item['name'].replace(' Futures', '')} "
                        + f"({multiplier} x {item['contract_unit']})",
                    ),
                    "type": "forex" if item["asset_class"] == "Currency" else "futures",
                }
            )

        return output
    except Exception as e:  # pylint: disable=broad-except
        data.database().logger.error(f"Error in symbol search: {e}")
        return []


@router.get("/history")
async def history(
    data: DatabaseDependency,
    symbol: str,
    resolution: Optional[str] = None,
    from_time: Annotated[
        Optional[int],
        Query(
            alias="from",
        ),
    ] = None,
    to_time: Annotated[
        Optional[int],
        Query(
            alias="to",
        ),
    ] = None,
    countback: Optional[int] = None,
) -> dict:
    """Get OHLC bars."""
    symbol = symbol.replace(".C.", ".c.")

    df = data.get_ohlcv_data(symbol=symbol, interval=resolution if resolution else "1d")
    if df.empty or len(df.index) == 0:
        return {"s": "no_data"}

    if resolution in ("1W", "1M"):
        df.date = to_datetime(df.date)
        if resolution == "1W":
            # 'W-SUN' makes weeks start on Sunday
            rule = "W-SUN"
        else:
            rule = "MS"
        df = df.reset_index(drop=True).set_index("date")
        df = (
            df.resample(rule)
            .agg(
                {
                    "open": "first",
                    "high": "max",
                    "low": "min",
                    "close": "last",
                    "volume": "sum",
                }
            )
            .dropna()
            .reset_index()
        )
        df.date = to_datetime(df.date)

    def apply_ts(x):
        """Apply timestamp with offset for intraday data."""
        d = (
            datetime.fromisoformat(x if isinstance(x, str) else x.isoformat())
            .astimezone(timezone("America/Chicago"))
            .timestamp()
        )
        return int(d)

    df.loc[:, "timestamp"] = df.date.apply(apply_ts)

    min_timestamp = df.timestamp.min()
    max_timestamp = df.timestamp.max()

    if from_time is not None and to_time is not None and to_time < min_timestamp:
        return {"s": "no_data"}

    if from_time is not None and from_time > max_timestamp:
        return {"s": "no_data"}

    if df.empty or len(df.index) == 0:
        return {"s": "no_data"}

    if df.empty or len(df.index) == 0:
        return {"s": "no_data"}

    return {
        "s": "ok",
        "t": df.timestamp.tolist(),
        "c": df.close.tolist(),
        "o": df.open.tolist(),
        "h": df.high.tolist(),
        "l": df.low.tolist(),
        "v": df.volume.tolist(),
    }
