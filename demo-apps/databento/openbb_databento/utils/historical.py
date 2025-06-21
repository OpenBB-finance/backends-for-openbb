"""Historical data utilities."""
from typing import Literal, Optional
from datetime import datetime, timedelta

from databento.common.error import BentoError
from pandas import DataFrame
from pytz import timezone

# pylint: disable=R0913,R0914,R0915,R0917

def fetch_historical_continuous(
    cme_database,
    symbols: Optional[list[str]] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    interval: Optional[Literal["second", "minute", "hour", "day"]] = None,
    contract: Optional[int] = None,
    roll_rule: Optional[Literal["c", "n", "v"]] = None,
) -> DataFrame:
    """Get historical continuous futures data.
    
        This function will download data and write it to the database under the
        `ohlcv_1{interval[0]}_continuous` table.

        WARNING
        -------

        This function should not be run to serve just-in-time data.
        It will take a long time (several minutes +) to run,
        and is intended for building a database of historical continuous futures data.
    
        Parameters
        ----------
        symbols : Optional[list[str]]
            A list of asset symbols to download.
            If None, defaults to all assets in `openbb_databento.utils.constants.live grid_assets`.
            Assets should be an asset from the `futures_symbols` asset column.
        start_date : Optional[str]
            The start date for the data download in 'YYYY-MM-DD' format.
            If None, defaults to '2013-01-01'.
        end_date : Optional[str]
            The end date for the data download in 'YYYY-MM-DD' format.
            If None, defaults to yesterday's date.
        interval : Literal["second", "minute", "hour", "day"]
            The interval for the data download.
            Defaults to 'day'.
        contract : Optional[int]
            The contract position to download.
            If None, defaults to 0 (front month).
        roll_rule : Optional[Literal["c", "n", "v"]]
            The roll rule to apply when downloading the data.
            Set as one of "c", "n", or "v" - calendar, open interest, or volume.
            If None, defaults to "c".

        Returns
        -------
        DataFrame
            A DataFrame containing the historical continuous futures data.
        
        Raises
        ------
        BentoError
            If there is an error with the Databento API request.
    """
    # pylint: disable=import-outside-toplevel
    from openbb_databento.utils.database import CmeDatabase

    if not isinstance(cme_database, CmeDatabase):
        raise TypeError("cme_database must be an instance of CmeDatabase.")

    interval = interval or "day"
    start_date = start_date or "2013-01-01"
    end_date = end_date or None
    contract = int(contract) if contract is not None else 0
    roll_rule = roll_rule or "c"

    if roll_rule not in ["c", "n", "v"]:
        raise ValueError(
            "roll_rule must be one of 'c' (calendar), 'n' (nearest), or 'v' (volume)."
        )

    if interval not in ["second", "minute", "hour", "day"]:
        raise ValueError(
            "interval must be one of 'second', 'minute', 'hour', or 'day'."
        )

    client = cme_database.db_client()
    assets_df = cme_database.live_grid_assets.copy()
    names_map = assets_df.set_index("asset").name.to_dict()
    assets = symbols or assets_df.asset.unique().tolist()
    symbols = [f"{a}.{roll_rule}.{contract}" for a in assets]
    end_date = (
        (datetime.now(tz=timezone("UTC")) - timedelta(days=1))
        .replace(hour=23, minute=59, second=59, microsecond=0)
        .isoformat()
        if end_date is None else end_date
    )
    try:
        data = client.timeseries.get_range(
            dataset="GLBX.MDP3",
            schema=f"ohlcv-1{interval[0]}",
            stype_in="continuous",
            symbols=symbols,
            start=start_date,
            end=end_date,
        )
    except BentoError as e:
        raise e from e

    results = data.to_df().reset_index()
    results = results.rename(
        columns={
            "ts_event": "date",
        }
    )

    if interval == "day":
        results["date"] = results["date"].dt.date
    else:
        results["date"] = (
            results["date"].dt.tz_convert("America/Chicago")
        )

    contract_abbr = {
        0: "1st",
        1: "2nd",
        2: "3rd",
        3: "4th",
        4: "5th",
        5: "6th",
        6: "7th",
        7: "8th",
        8: "9th",
        9: "10th",
        10: "11th",
        11: "12th",
    }

    results.loc[:, "asset"] = results.symbol.apply(
        lambda x: x.split(".")[0]
    )
    results.loc[:, "asset_class"] = results.asset.map(
        assets_df.set_index("asset").asset_class
    )
    results.loc[:, "exchange"] = results.asset.map(
        assets_df.set_index("asset").exchange
    )
    results.loc[:, "exchange_name"] = results.asset.map(
        assets_df.set_index("asset").exchange_name
    )
    results.loc[:, "name"] = results.asset.apply(
        lambda x: (
            f"{names_map.get(x)} - "
            + f"{contract_abbr.get(contract, contract)} Contract"
        )
    )
    results.loc[:, "contract_unit"] = results.asset.map(
        assets_df.set_index("asset").unit_of_measure
    )
    results.loc[:, "contract_unit_multiplier"] = results.asset.map(
        assets_df.set_index("asset").unit_of_measure_qty
    )
    results.loc[:, "min_price_increment"] = results.asset.map(
        assets_df.set_index("asset").min_price_increment
    )
    results.loc[:, "currency"] = results.asset.map(
        assets_df.set_index("asset").currency
    )

    dtypes = {
        "date": "DATE",
        "instrument_id": "INTEGER",
        "asset": "TEXT",
        "asset_class": "TEXT",
        "exchange": "TEXT",
        "exchange_name": "TEXT",
        "contract_unit": "TEXT",
        "contract_unit_multiplier": "REAL",
        "min_price_increment": "REAL",
        "name": "TEXT",
        "currency": "TEXT",
        "symbol": "TEXT",
        "open": "REAL",
        "high": "REAL",
        "low": "REAL",
        "close": "REAL",
        "volume": "INTEGER"
    }

    results = DataFrame(results[list(dtypes)])
    table_name = f"ohlcv_1{interval[0]}_continuous"

    try:
        cme_database.safe_to_sql(
            results,
            table_name,
            if_exists="append",
            index=False,
            method=None,
            dtype=dtypes,
        )
    except Exception as e:  # pylint: disable=broad-except
        cme_database.logger.error(
            "Error writing to database: %s", e, exc_info=True
        )


    return results
