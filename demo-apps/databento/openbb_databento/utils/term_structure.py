
"""Download the term structure for a given asset by date, from CME."""
from typing import Optional
from datetime import datetime, timedelta

import databento as db
from databento.common.error import BentoError
from fastapi.exceptions import HTTPException
from pandas import DataFrame, concat

# pylint: disable=R0912, R0913, R0914, R0915, R0917

schema_dict: dict = {
    "asset": "TEXT",
    "date": "DATE",
    "symbol": "TEXT",
    "instrument_id": "INTEGER",
    "expiration": "DATE",
    "settlement_price": "REAL",
}


def download_term_structure(
    cme_database,
    asset: str,
    date: Optional[str] = None,
) -> DataFrame:
    """Download the term structure for a given asset.

    Parameters
    ----------
    cme_database : CmeDatabase
        An instance of the CmeDatabase singleton.
    asset : str
        The asset for which to download the term structure.
        Asset should be an asset from the `futures_symbols` asset column.

    Returns
    -------
    DataFrame
        A DataFrame containing the term structure data for the specified asset.
    """
    # pylint: disable=import-outside-toplevel
    from openbb_databento.utils.database import CmeDatabase

    if not isinstance(cme_database, CmeDatabase):
        raise TypeError("cme_database must be an instance of CmeDatabase.")

    client = cme_database.db_client()

    now = (
        (datetime.strptime(date, "%Y-%m-%d") + timedelta(days=1))
        if date is not None
        else datetime.now()
    )

    if now.weekday() in [5, 6]:
        # If today is Saturday or Sunday, set 'now' to the previous Friday
        now = now - timedelta(days=1 if now.weekday() == 5 else 2)
    now = now.replace(hour=0, minute=0, second=0, microsecond=0)
    start_date = (now - timedelta(days=3)).strftime("%Y-%m-%d")
    end_date = now.strftime("%Y-%m-%d")

    results = DataFrame()
    asset_symbols = cme_database.get_asset_symbols(asset, date)
    instrument_ids = asset_symbols.instrument_id.unique().tolist()

    try:
        data = client.timeseries.get_range(
            dataset="GLBX.MDP3",
            schema="statistics",
            symbols=instrument_ids,
            start=start_date,
            end=end_date,
            stype_in="instrument_id",
        )
        results = data.to_df().reset_index()
    except BentoError as e:
        end_date = None
        err = e.args[0]

        if err.get("case") == "data_end_after_available_end":
            msg = err.get("message", "")
            end_date = msg.split("'")[1].replace(" ", "T") if "'" in msg else None
        else:
            raise HTTPException(
                status_code=500,
                detail=(
                    f"Invalid request for asset {asset}: "
                    +f"{err.get('message', 'No additional error message provided')}"
                )
            ) from e

        try:
            data = client.timeseries.get_range(
                dataset="GLBX.MDP3",
                schema="statistics",
                symbols=instrument_ids,
                start=start_date,
                end=end_date,
                stype_in="instrument_id",
            )
            results = data.to_df().reset_index()
        except BentoError as exc:
            cme_database.logger.error(
                "Case: %s -> Message: %s",
                exc.args[0].get("case", "No case provided"),
                exc.args[0].get("message", "No additional error message provided")
            )
            return DataFrame()

    if results.empty:
        cme_database.logger.error(
            "Unable to retrieve settlement prices for %s",
            asset,
        )
        return DataFrame()

    asset_symbols.instrument_id = asset_symbols.instrument_id.astype(int)
    instrument_id_map = asset_symbols.set_index("instrument_id")["raw_symbol"].to_dict()
    term_structure_df = DataFrame(asset_symbols.copy())

    if term_structure_df.empty:
        raise BentoError(f"No data found for asset: {asset}")

    term_structure_df.instrument_id = term_structure_df.instrument_id.astype(int)
    results.loc[:, "raw_symbol"] = results.instrument_id.map(instrument_id_map)

    results.loc[:, "settlement_price"] = results[
        results["stat_type"] == db.StatType.SETTLEMENT_PRICE]["price"]
    results = results.dropna(subset=["settlement_price"])
    results.loc[:, "date"] = results["ts_ref"].dt.date
    results = results.groupby(["date", "instrument_id"]).agg("last").reset_index()
    results = results.drop_duplicates(subset=["instrument_id"], keep="last")
    results = results[
        [
            "date", "instrument_id", "settlement_price",
        ]
    ]
    results = results.query("instrument_id.isin(@term_structure_df.instrument_id)").copy()
    results.loc[:, "expiration"] = (
        results.instrument_id.map(
            term_structure_df.set_index('instrument_id').expiration
        )
    )
    results.loc[:, "symbol"] = (
        results.instrument_id.map(
            term_structure_df.set_index('instrument_id').raw_symbol
        )
    )
    results = results.sort_values(by="expiration").reset_index(drop=True)

    if results.empty:
        date = date or datetime.now().today().strftime("%Y-%m-%d")
        cme_database.logger.error(
            "No settlement prices found for asset %s on date %s",
            asset,
            date,
        )
        return DataFrame()

    results.loc[:, "asset"] = asset

    columns = [
        "asset",
        "date",
        "symbol",
        "instrument_id",
        "expiration",
        "settlement_price",
    ]
    results = results[columns]
    results = DataFrame(results).sort_values(by=["expiration"])
    tables = cme_database.table_names

    if "term_structures" not in tables:
        _ = cme_database.safe_to_sql(
            results,
            "term_structures",
            dtype=schema_dict,
            if_exists="append",
            index=False,
        )

        return results

    existing_data = cme_database.safe_read_sql(
    "SELECT * FROM term_structures"
    )

    if existing_data.empty or asset not in existing_data.asset.unique():
        _ = cme_database.safe_to_sql(
            results,
            "term_structures",
            dtype=schema_dict,
            if_exists="append",
            index=False,
        )
        return results

    new_data = DataFrame(concat(
        [
            existing_data,
            results,
        ],
        ignore_index=True
    )).drop_duplicates(subset=["asset", "date", "instrument_id"], keep="last")

    new_data.date = new_data.date.astype(str)
    new_data.instrument_id = new_data.instrument_id.astype(int)
    new_data.expiration = new_data.expiration.astype(str)

    _ = cme_database.safe_to_sql(
        new_data.reset_index(drop=True),
        "term_structures",
        index=False,
        dtype=schema_dict,
        if_exists="replace",
    )

    return results
