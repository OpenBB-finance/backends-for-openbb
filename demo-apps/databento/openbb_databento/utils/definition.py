"""Databento CME Definition Utilities."""
from typing import Optional
from datetime import datetime, timedelta
import databento as db
from databento.common.error import BentoError
from pandas import DataFrame, concat
from pytz import timezone

from openbb_databento.utils.constants import (
    exchange_map,
    underlying_product_map,
    security_type_map,
    unit_of_measure_map,
)

# pylint: disable=R0914,R0915,R0912
def download_asset_symbols(
    cme_database,
    asset: str,
    date: Optional[str] = None,
    include_spreads: bool = False,
) -> DataFrame:
    """Download the term structure for a given asset.

    Instrument ID mapping are saved to the database under the `asset_definitions` table.

    Parameters
    ----------

    cme_database : CmeDatabase
        An instance of the CmeDatabase singleton.
    asset : str
        The asset for which to download the term structure.
        Asset should be an asset from the `asset_names` asset column.
    date : Optional[str]
        The date for which to get asset definitions for.
    include_spreads : bool
        Whether to include spread definitions in the result.

    Returns
    -------

    DataFrame
        A DataFrame containing the asset definition data.
    """
    # pylint: disable=import-outside-toplevel
    from openbb_databento.utils.database import CmeDatabase

    if not isinstance(cme_database, CmeDatabase):
        raise TypeError("cme_database must be an instance of CmeDatabase.")

    client = cme_database.db_client()

    now = datetime.strptime(date, "%Y-%m-%d") if date is not None else datetime.now()
    if now.weekday() in [5, 6]:
        # If today is Saturday or Sunday, set 'now' to the previous Friday
        now = now - timedelta(days=1 if now.weekday() == 5 else 2)
    now = now.replace(hour=0, minute=0, second=0, microsecond=0)
    start_date = (
        (now - timedelta(days=1)).strftime("%Y-%m-%d")
        if date is None
        else now.strftime("%Y-%m-%d")
    )
    end_date = (
        now.strftime("%Y-%m-%d")
        if date is None
        else (now + timedelta(days=1)).strftime("%Y-%m-%d")
    )

    try:
        data = client.timeseries.get_range(
            dataset="GLBX.MDP3",
            schema="definition",
            symbols=[asset+ ".FUT"],
            start=start_date,
            end=end_date,
            stype_in="parent",
        )

    except BentoError as e:
        end_date = None
        err = e.args[0]

        if err.get("case") == "data_end_after_available_end":
            msg = err.get("message", "")
            end_date = msg.split("'")[1].replace(" ", "T") if "'" in msg else None
        else:
            err_msg = (
                f"Failed to download term structure data for asset {asset}"
                f" -> case: {err.get('case', 'No case provided')}"
                f" -> message: {err.get('message', 'No additional error message provided')}"
            )
            cme_database.logger.error(err_msg)

            return DataFrame()

        try:
            data = client.timeseries.get_range(
                dataset="GLBX.MDP3",
                schema="definition",
                symbols=[asset + ".FUT"],
                start=start_date,
                end=end_date,
                stype_in="parent",
            )
        except BentoError as exc:
            cme_database.logger.error(
                "Case: %s -> Message: %s",
                exc.args[0].get("case", "No case provided"),
                exc.args[0].get("message", "No additional error message provided")
            )
            return DataFrame()

    instrument_id_map: dict = {}
    for k, v in data.mappings.items():
        if include_spreads is True:
            instrument_id_map[v[-1]["symbol"]] = k
        elif ":" not in k and "-" not in k:
            instrument_id_map[v[-1]["symbol"]] = k

    results = data.to_df().reset_index()
    results = results.query("instrument_id.astype('string').isin(@instrument_id_map.keys())").copy()
    results.loc[:, "date"] = results["ts_recv"].dt.date

    results = results.groupby(
        ["date", "raw_symbol"]
    ).agg("last").reset_index().copy()
    results = DataFrame(
        results[["date", "instrument_id", "symbol", "activation", "expiration"]]
    ).sort_values(by="expiration").reset_index(drop=True)
    results = results.rename(
        columns={
            "activation": "first_trade_date",
            "symbol": "raw_symbol",
        }
    )
    results.first_trade_date = results.first_trade_date.dt.date
    date = results.date.max()
    results.loc[:, "asset"] = asset.upper()
    has_table = "asset_definitions" in cme_database.table_names
    asset_in_table = False
    date_in_table = False

    if has_table:
        existing = cme_database.safe_read_sql(
            f"SELECT * FROM asset_definitions WHERE date = '{date}' OR asset = '{asset}'"
        )

        if not existing.empty:
            if asset in existing.asset.tolist():
                asset_in_table = True
            if date in existing.date.tolist():
                date_in_table = True
    if (
        asset_in_table is False
        or date_in_table is False
        or (
            asset_in_table is True
            and date_in_table is False
        )
    ):
        try:
            cme_database.safe_to_sql(
                results,
                table_name="asset_definitions",
                if_exists="append",
                index=False,
                dtype={
                    "date": "DATE",
                    "asset": "TEXT",
                    "raw_symbol": "TEXT",
                    "instrument_id": "INTEGER",
                    "first_trade_date": "DATE",
                    "expiration": "DATETIME",
                },
            )
        except Exception as e:  # pylint: disable=broad-except
            cme_database.logger.error(
                f"Failed to save asset definitions to database: {e}"
            )

    return results


def create_futures_symbols_db(  # pylint: disable=R0914, R0915, W0212
    cme_database,
    date: Optional[str] = None,
    replace: bool = True,
) -> DataFrame:
    """Generate a database of symbols from the CME Globex MDP 3.0 feed.
    
    Parameters
    ----------

    cme_database : CmeDatabase
        An instance of the CmeDatabase singleton.
    date : Optional[str]
        The date for which to generate the symbols.
        If not provided, defaults to yesterday's date.
    replace : bool
        Whether to replace the existing `futures_symbols` table.
        Set to False to add a new date to the `asset_definitions` table.

    Returns
    -------

    DataFrame
        The dataframe containing the resulting futures symbols.
    """
    output = DataFrame()
    client = cme_database.db_client()
    cme_assets = cme_database.asset_names
    cme_futures_name_map = (
        cme_assets.query("asset_class == 'Futures'")
        .set_index("asset")[["name"]]
        .to_dict()["name"]
    )
    now = datetime.now(tz=timezone("America/Chicago")).replace(hour=0, minute=0, second=0, microsecond=0)
    # If today is Saturday or Sunday, set 'now' to the previous Friday
    if now.weekday() in [5, 6]:  # Saturday
        now = now - timedelta(days=1 if now.weekday() == 5 else 2)

    now = now.replace(hour=0, minute=0, second=0, microsecond=0)
    start_date = now - timedelta(days=3 if now.weekday() == 0 else 1)

    try:
        # Get all symbols from the database.
        data = client.timeseries.get_range(
            dataset="GLBX.MDP3",
            schema="definition",
            symbols="ALL_SYMBOLS",
            stype_in="parent",
            start=date or start_date.strftime("%Y-%m-%d"),
        )
    except BentoError as e:
        raise e from e

    df = data.to_df().reset_index()

    if df.empty:
        raise BentoError(
            "No data found for the specified date range."
        )

    df = df[df["instrument_class"] == db.InstrumentClass.FUTURE]
    df = df.query("`asset` in @cme_futures_name_map.keys()")
    df = df.sort_values(by="ts_event")
    df = df.groupby("raw_symbol").agg("last").reset_index()
    output.loc[:, "raw_symbol"] = df.raw_symbol
    output.loc[:, "instrument_id"] = df.instrument_id
    output.loc[:, "asset"] = df.asset

    def format_future_name(row):
        """Format the future name based on asset and maturity."""
        name = cme_futures_name_map.get(row.asset, "")
        maturity = f"{row.maturity_year}-{str(row.maturity_month).zfill(2)}"
        if row.maturity_day != 255:
            maturity += f"-{str(row.maturity_day).zfill(2)}"
        return f"{name} - {maturity} Expiry"

    output.loc[:, "name"] = df.apply(format_future_name, axis=1)
    output.loc[:, "exchange"] = df.exchange
    output.loc[:, "exchange_name"] = df.exchange.map(exchange_map)
    output.loc[:, "exchange_timezone"] = "America/Chicago"
    output.loc[:, "security_type"] = df.security_type.map(security_type_map)
    output.loc[:, "asset_class"] = df.underlying_product.map(underlying_product_map)
    output.loc[:, "first_trade_date"] = (
        df.activation.dt.tz_convert("America/Chicago").dt.strftime("%Y-%m-%d")
    )
    output.loc[:, "expiration"] = (
        df.expiration.dt.tz_convert("America/Chicago").dt.strftime("%Y-%m-%d %H:%M:%S%z")
    )
    output.loc[:, "currency"] = df.currency
    output.loc[:, "min_price_increment"] = df.min_price_increment
    output.loc[:, "unit_of_measure"] = df.unit_of_measure.map(unit_of_measure_map)
    output.loc[:, "unit_of_measure_qty"] = df.unit_of_measure_qty
    output.loc[:, "source"] = "databento"
    output.loc[:, "as_of_date"] = (
        df.ts_event.dt.tz_convert("America/Chicago").dt.strftime("%Y-%m-%d %H:%M:%S%z")
    )

    try:
        if replace is True:
            cme_database.safe_to_sql(
                output,
                "futures_symbols",
                if_exists="replace",
                index=False,
                dtype={
                    "instrument_id": "TEXT PRIMARY KEY",
                    "raw_symbol": "TEXT",
                    "asset": "TEXT",
                    "name": "TEXT",
                    "exchange": "TEXT",
                    "exchange_name": "TEXT",
                    "security_type": "TEXT",
                    "asset_class": "TEXT",
                    "first_trade_date": "DATE",
                    "expiration": "DATETIME",
                    "currency": "TEXT",
                    "min_price_increment": "REAL",
                    "unit_of_measure": "TEXT",
                    "unit_of_measure_qty": "REAL",
                    "source": "TEXT",
                    "as_of_date": "DATETIME"
                },
            )

            cme_database._futures_symbols = output

        if cme_database._futures_symbols.empty:
            cme_database._futures_symbols = output

        output.loc[:, "date"] = output["as_of_date"].str[:10]

        symbols_mapping = DataFrame(
            output.copy()[
                ["date", "asset", "instrument_id", "raw_symbol", "first_trade_date", "expiration"]
            ]
        ).sort_values(by=["asset", "expiration"]).reset_index(drop=True)

        has_table = "asset_definitions" in cme_database.table_names
        date_in_table = False

        if has_table:
            check_dates = cme_database.safe_read_sql(
                "SELECT DISTINCT date FROM asset_definitions"
            )
            if not check_dates.empty:
                date_in_table = check_dates.date.isin([output.date.max()]).any()

                if date_in_table:
                    old_defs = cme_database.safe_read_sql(
                        f"SELECT * FROM asset_definitions WHERE date = '{output.date.max()}'"
                    )
                    if not old_defs.empty:
                        merged_defs = (
                            concat([old_defs, symbols_mapping], ignore_index=True)
                            .drop_duplicates(keep='last')
                        )
                        _ = cme_database.safe_to_sql(
                            merged_defs,
                            "asset_definitions",
                            if_exists="replace",
                            index=False,
                            dtype={
                                "date": "DATE",
                                "instrument_id": "INTEGER",
                                "raw_symbol": "TEXT",
                                "first_trade_date": "DATE",
                                "expiration": "DATETIME",
                            },
                        )

        if not has_table or not date_in_table or (has_table and not date_in_table):
            cme_database.logger.info(
                "Writing asset definitions to database for date %s", output.date.max()
            )
            _ = cme_database.safe_to_sql(
                symbols_mapping,
                "asset_definitions",
                if_exists="append",
                index=False,
                dtype={
                    "date": "DATE",
                    "instrument_id": "INTEGER",
                    "raw_symbol": "TEXT",
                    "first_trade_date": "DATE",
                    "expiration": "DATETIME",
                },
            )

        return output

    except Exception as e:
        cme_database.logger.error("Error writing to database: %s", e)
        raise e from e
