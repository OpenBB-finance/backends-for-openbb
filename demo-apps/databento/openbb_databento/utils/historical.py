"""Historical data utilities."""
from typing import Literal, Optional
from datetime import datetime, timedelta

from databento.common.error import BentoError
from pandas import DataFrame, concat
from pytz import timezone

# pylint: disable=R0913,R0914,R0915,R0917

def clean_historical_continuous(
    cme_database,
    dataframe: DataFrame,
) -> DataFrame:
    """Clean historical continuous futures data.

    Parameters
    ----------
    cme_database : CmeDatabase
        The CME database instance.
    dataframe : DataFrame
        The DataFrame containing the historical continuous futures data.

    Returns
    -------
    DataFrame
        A cleaned DataFrame with the necessary columns and types.
    """
    # pylint: disable=import-outside-toplevel
    from openbb_databento.utils.database import CmeDatabase

    if not isinstance(cme_database, CmeDatabase):
        raise TypeError("cme_database must be an instance of CmeDatabase.")

    if dataframe.empty:
        return dataframe

    assets_df = cme_database.live_grid_assets.copy()
    names_map = assets_df.set_index("asset").name.to_dict()
    assets = assets_df.asset.unique().tolist()

    dataframe = dataframe.rename(
        columns={
            "ts_event": "date",
            "instrument_id": "symbol",
        }
    )

    dataframe["date"] = (
        dataframe["date"].dt.tz_convert("America/Chicago")
        if "date" in dataframe.columns else None
    )

    return dataframe

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

# pylint: disable=R0912,W0612
# flake8: noqa: F841
def update_historical_continuous_table(
    cme_database,
    table_name: str,
) -> DataFrame:
    """Update historical continuous futures data."""
    last_date_query = f"SELECT MAX(date) as max_date FROM {table_name}"
    last_date_df = cme_database.safe_read_sql(last_date_query)

    if last_date_df.empty or "max_date" not in last_date_df.columns:
        raise ValueError(
            f"No time series data found in table {table_name}."
            + " Please ensure the table exists and has data."
        )

    last_date = last_date_df.max_date.iloc[0][:10]
    db_symbols_query = f"SELECT DISTINCT symbol FROM {table_name}"
    db_symbols_df = cme_database.safe_read_sql(db_symbols_query)

    if db_symbols_df.empty or "symbol" not in db_symbols_df.columns:
        raise ValueError(
            f"No symbols found in table {table_name}."
            + " Please ensure the table exists and has data."
        )

    db_symbols = db_symbols_df.symbol.unique().tolist()

    all_metadata = cme_database.safe_read_sql(
        "SELECT DISTINCT asset, asset_class, exchange, "
        + "exchange_name, contract_unit, contract_unit_multiplier, "
        + f" min_price_increment, name, currency FROM {table_name}"
    )

    metadata_cols = [
        "asset", "asset_class", "exchange", "exchange_name", 
        "contract_unit", "contract_unit_multiplier", "min_price_increment", 
        "name", "currency"
    ]

    # Create metadata mapping ONCE from existing table data
    metadata_map = (
        all_metadata[metadata_cols]
        .drop_duplicates("asset")
        .set_index("asset")
    )

    # Chunk symbols into groups of 2000
    chunk_size = 2000
    symbol_chunks = [db_symbols[i:i + chunk_size] for i in range(0, len(db_symbols), chunk_size)]

    msg = (
        f"Processing {len(db_symbols)} symbols in "
        + f"{len(symbol_chunks)} chunks of {chunk_size}"
    )
    cme_database.logger.info(msg)

    all_results = []
    client = cme_database.db_client()
    now = datetime.now(tz=timezone("UTC")).replace(microsecond=0)

    for chunk_idx, symbol_chunk in enumerate(symbol_chunks, 1):
        msg = (
            f"Processing chunk {chunk_idx}/{len(symbol_chunks)} "
            + f"with {len(symbol_chunk)} symbols"
        )
        cme_database.logger.info(msg)

        try:
            data = client.timeseries.get_range(
                dataset="GLBX.MDP3",
                schema=table_name.replace("_continuous", "").replace("_", "-"),
                stype_in="continuous",
                symbols=symbol_chunk,
                start=last_date,
                end=now.isoformat(),
            )
        except BentoError as e:
            end_date = None
            err = e.args[0]

            if err.get("case") == "data_end_after_available_end":
                msg = err.get("message", "")
                end_date = (
                    msg.split("'")[1].replace(" ", "T").split(".")[0] + "+00:00"
                    if "'" in msg
                    else None
                )
            else:
                err_msg = (
                    f"Failed to update OHLCV table: {table_name} (chunk {chunk_idx})."
                    f" -> case: {err.get('case', 'No case provided')}"
                    f" -> message: {err.get('message', 'No additional error message provided')}"
                )
                cme_database.logger.error(err_msg)
                continue

            try:
                data = client.timeseries.get_range(
                    dataset="GLBX.MDP3",
                    schema=table_name.replace("_continuous", "").replace("_", "-"),
                    symbols=symbol_chunk,
                    start=last_date,
                    end=end_date,
                    stype_in="continuous",
                )
            except BentoError as exc:
                cme_database.logger.error(
                    "Chunk %d - Case: %s -> Message: %s",
                    chunk_idx,
                    exc.args[0].get("case", "No case provided"),
                    exc.args[0].get("message", "No additional error message provided")
                )
                continue

        results = data.to_df().reset_index()
        results = results.rename(
            columns={
                "ts_event": "date",
            }
        )

        if table_name.split("_")[1] == "1d":
            results.date = results.date.dt.date
        else:
            results.date = results.date.dt.tz_convert("America/Chicago")

        results = DataFrame(
            results[
                [
                    "date",
                    "instrument_id",
                    "symbol",
                    "open",
                    "high",
                    "low",
                    "close",
                    "volume",
                ]
            ]
        )

        # Get existing data for this chunk's symbols only for duplicate filtering
        symbols_str = "', '".join(symbol_chunk)
        existing_data = cme_database.safe_read_sql(
            f"SELECT * FROM {table_name} "
            + f"WHERE date >= '{last_date}' AND symbol IN ('{symbols_str}')"
        )

        # First, extract asset from symbol for new results
        results["asset"] = results["symbol"].apply(lambda x: x.split(".")[0])

        # Map metadata to new results using asset
        for col in metadata_cols[1:]:  # Skip 'asset' since we already have it
            results[col] = results["asset"].map(metadata_map[col])

        # Get the column order from existing data if available, otherwise use a standard order
        if not existing_data.empty:
            column_order = existing_data.columns.tolist()
        else:
            column_order = [
                "date", "instrument_id", "asset", "asset_class", "exchange",
                "exchange_name", "contract_unit", "contract_unit_multiplier",
                "min_price_increment", "name", "currency", "symbol",
                "open", "high", "low", "close", "volume"
            ]

        # Reorder columns to match existing data structure
        results = DataFrame(results[column_order])

        # Filter out overlapping data to prevent duplicates
        if not existing_data.empty:
            existing_dates = existing_data.date.astype(str).unique()
            results = results.query("~`date`.astype('string').isin(@existing_dates)")

        if not results.empty:
            all_results.append(results)

    # Combine all chunks
    if all_results:
        final_results = concat(all_results, ignore_index=True)

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

        # Insert all new data
        try:
            cme_database.safe_to_sql(
                final_results,
                table_name,
                if_exists="append",
                index=False,
                method=None,
                dtype=dtypes,
            )
            cme_database.logger.info(f"Added {len(final_results)} new rows to {table_name}")
        except Exception as e:  # pylint: disable=broad-except
            cme_database.logger.error(f"Error writing to database: {e}", exc_info=True)

        return final_results

    cme_database.logger.info(f"No new data to add to {table_name}")

    return DataFrame()
