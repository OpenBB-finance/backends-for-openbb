"""Main application and entry point."""

from dateutil.relativedelta import relativedelta
import json
from pathlib import Path

from fastapi import FastAPI
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_swaps.data.store import SwapsStore
from openbb_swaps.models.query_params import (
    SWAP_TENOR_CHOICES,
    SwapCurrency,
    SwapRateTenors,
    SwapTypes,
    SwapRatePeriod,
    SwapTenorBuckets,
    SwapTradeDistributionDates,
    SwapTradesClearedOnly,
    SwapTradesDates,
    SwapTradesIncludeStarting,
    SwapVolumeTypes,
)
from openbb_swaps.models.response_models import (
    SwapRateLevelsResponseModel,
    SwapRateVolumeResponseModel,
    SwapTradesResponseModel,
    TradeDistributionResponseModel,
)
from numpy import nan
from pandas import concat, to_datetime

app = FastAPI()


@app.get(
    "/swap_rate_levels/tenors",
    openapi_extra={"widget_config": {"exclude": True}},
)
def get_swap_rate_levels_tenors(
    store: SwapsStore, swap_type: SwapTypes, currency: SwapCurrency
) -> list:
    """Available tenors for a given currency and swap type."""
    store_key = currency.lower() + "_swaps"
    sheet_name = "Interest Rates"
    df = store.get_store(store_key, sheet_name=sheet_name)

    if swap_type != "Both":
        df = df[df["swap.type"] == swap_type]

    tenors = df["metric"].unique().tolist()

    return [d for d in SWAP_TENOR_CHOICES if d["value"] in tenors]


@app.get("/swap_rate_levels")
def swap_rate_levels(
    store: SwapsStore,
    currency: SwapCurrency = "USD",
    swap_type: SwapTypes = "OIS",
    tenor: SwapRateTenors = "2s10s",
    period: SwapRatePeriod = "1y",
) -> list[SwapRateLevelsResponseModel]:
    """Get swap rate levels as a time series, by term and currency."""
    store_key = currency.lower() + "_swaps"
    sheet_name = "Interest Rates"

    tenor = tenor.split(",") if "," in tenor else [tenor]
    lookback_period = (
        relativedelta(months=int(period[0])) if period in ["1m", "3m", "6m"] else None
    )

    try:
        df = store.get_store(store_key, sheet_name=sheet_name)
        df = df[df["metric"].isin(tenor)]

        df.curve_date = df["curve_date"].astype("datetime64[ns]")
        df = df.set_index("curve_date").sort_index()

        if lookback_period:
            df = df[df.index >= (df.index[-1] - lookback_period)]

        df.index = df.index.strftime("%Y-%m-%d")

        if period == "YTD":
            max_year = df.index[-1].split("-")[0]
            df = df[df.index >= f"{max_year}-01-01"]

        df = df.reset_index()
        df = df.sort_values(by=["curve_date", "metric", "swap.type"])
        df.rate = df["rate"].astype("float64").multiply(100).round(4)

        if swap_type != "Both":
            df = df[df["swap.type"] == swap_type]

        df = df.pivot(
            index="curve_date", columns=["swap.type", "metric"], values="rate"
        )

        df.columns = [f"{stype.lower()}_{metric}" for stype, metric in df.columns]
        df = df.reset_index().replace({nan: None})
        if df.empty:
            raise OpenBBError(f"No {currency} {swap_type} data found for {tenor}.")

        return df.to_dict(orient="records")

    except Exception as e:
        raise OpenBBError(e) from e


@app.get(
    "/swap_rate_volume/buckets",
    openapi_extra={"widget_config": {"exclude": True}},
)
def get_swap_rate_volume_buckets(store: SwapsStore, currency: SwapCurrency) -> list:
    """Available tenors for a given currency and swap type."""
    all_buckets = [
        "0-1",
        "1-3",
        "3-4",
        "4-5",
        "5-7",
        "7-10",
        "10-15",
        "15-20",
        "20-25",
        "25-30",
        "30-40",
        "40-50",
    ]
    store_key = currency.lower() + "_swaps"
    sheet_name = "Trading Data"
    df = store.get_store(store_key, sheet_name=sheet_name)

    tenors = df["Bucket"].unique().tolist()

    return [
        {"label": tenor, "value": tenor} for tenor in all_buckets if tenor in tenors
    ]


@app.get("/swap_rate_volume")
async def swap_rate_volume(
    store: SwapsStore,
    currency: SwapCurrency = "USD",
    stat: SwapVolumeTypes = "Notional",
    bucket: SwapTenorBuckets = "7-10",
    period: SwapRatePeriod = "1y",
) -> list[SwapRateVolumeResponseModel]:
    """Get swap rate volumes by underlying currency. Choose between total notional or the PV01 of the notional."""
    store_key = currency.lower() + "_swaps"
    sheet_name = "Trading Data"
    lookback_period = (
        relativedelta(months=int(period[0])) if period in ["1m", "3m", "6m"] else None
    )
    buckets = bucket.split(",") if "," in bucket else [bucket]

    try:
        df = store.get_store(store_key, sheet_name=sheet_name)

        df = df[df["Bucket"].isin(buckets)] if buckets else df
        df = df.reset_index()

        libor_volume = (
            df[df["swap.type"] == "Libor"]
            .copy()
            .groupby("spot_date")
            .agg({"notional": "sum", "pv01": "sum"})
        )
        ois_volume = (
            df[df["swap.type"] == "OIS"]
            .copy()
            .groupby("spot_date")
            .agg({"notional": "sum", "pv01": "sum"})
        )

        if stat == "Notional":
            _ = libor_volume.pop("pv01")
            _ = ois_volume.pop("pv01")
        else:
            _ = libor_volume.pop("notional")
            _ = ois_volume.pop("notional")

        libor_volume = libor_volume.rename(
            columns={"notional": "Libor Volume", "pv01": "Libor Volume"}
        )
        ois_volume = ois_volume.rename(
            columns={"notional": "OIS Volume", "pv01": "OIS Volume"}
        )
        output = libor_volume.join(ois_volume, how="outer")
        output = output.fillna(0)
        output.loc[:, "Total"] = output["Libor Volume"] + output["OIS Volume"]
        output.loc[:, "Total 5-Day MA Volume"] = output["Total"].rolling(5).mean()
        output = output.dropna(subset="Total 5-Day MA Volume").astype("int64")
        _ = output.pop("Total")
        output = output.reset_index()

        output.spot_date = output["spot_date"].astype("datetime64[ns]")
        output = output.set_index("spot_date").sort_index()

        if lookback_period:
            output = output[output.index >= (output.index[-1] - lookback_period)]

        output.index = output.index.strftime("%Y-%m-%d")

        if period == "YTD":
            max_year = output.index[-1].split("-")[0]
            output = output[output.index >= f"{max_year}-01-01"]

        return output.reset_index().to_dict(orient="records")

    except Exception as e:
        raise OpenBBError(e) from e


@app.get(
    "/trade_distribution/dates",
    openapi_extra={"widget_config": {"exclude": True}},
)
def get_trade_distribution_dates(
    store: SwapsStore, currency: SwapCurrency, swap_type: SwapTypes
) -> list:
    """Available trade distribution dates for a given currency and swap type."""
    store_key = currency.lower() + "_swaps"
    sheet_name = "Trading Data"
    df = store.get_store(store_key, sheet_name=sheet_name)

    if swap_type != "Both":
        df = df[df["swap.type"] == swap_type]

    df.sort_values(by=["spot_date"], inplace=True, ascending=False)
    dates = df["spot_date"].astype(str).unique().tolist()

    return [{"label": date, "value": date} for date in dates]


@app.get("/trade_distribution")
async def trade_distribution(
    store: SwapsStore,
    currency: SwapCurrency = "USD",
    swap_type: SwapTypes = "Both",
    stat: SwapVolumeTypes = "Notional",
    date: SwapTradeDistributionDates = "2025-04-15",
) -> list[TradeDistributionResponseModel]:
    """Get swap rate volumes, by currency, as a time series. Choose between total notional or the PV01 of the notional."""
    store_key = currency.lower() + "_swaps"
    sheet_name = "Trading Data"

    try:
        df = store.get_store(store_key, sheet_name=sheet_name)

        if swap_type != "Both":
            df = df[df["swap.type"] == swap_type]

        df = df[df["spot_date"] == to_datetime(date)]

        if len(df) == 0:
            raise OpenBBError(f"No {swap_type} data found for {date}.")

        output = (
            df.copy()
            .groupby("Bucket")
            .agg(
                {
                    "notional": "sum",
                    "pv01": "sum",
                }
            )
        )

        output = output.fillna(0).round()

        output = (
            output[["notional"]].copy().T.reset_index()
            if stat == "Notional"
            else output[["pv01"]].copy().T.reset_index()
        )

        return output.to_dict(orient="records")
    except Exception as e:
        raise OpenBBError(e) from e


@app.get("/swap_trades")
async def swap_trades(
    store: SwapsStore,
    currency: SwapCurrency = "USD",
    date: SwapTradesDates = "2025-04-15",
    cleared_only: SwapTradesClearedOnly = False,
    include_starting: SwapTradesIncludeStarting = False,
) -> list[SwapTradesResponseModel]:
    """Get swap trades, by currency and swap type, for a given date."""
    store_key = currency.lower() + "_swaps"
    sheet_name = "Trades and Pricing Curve"
    target_cols = ["time.to.mat", "strike", "type"]

    try:
        df = store.get_store(store_key, sheet_name=sheet_name)
        df = df[df["spot_date"] == to_datetime(date)]
        df.strike = df.strike.astype("float64").multiply(100).round(4)
        output = df[df.type == "Pricing Rate"][target_cols]

        if cleared_only is True:
            if include_starting is True:
                cleared_and_forward_starting = df[df["cleared"].astype(str) == "1"][
                    target_cols
                ]
                output = concat([output, cleared_and_forward_starting], axis=0)
            else:
                cleared_only = df[
                    (df["cleared"].astype(str) == "1")
                    & (df.forward_starting.astype(str) == "0")
                ][target_cols]
                output = concat([output, cleared_only], axis=0)
        else:
            if include_starting is True:
                all_trades = df[df.type != "Pricing Rate"][target_cols]
                output = concat([output, all_trades], axis=0)
            else:
                not_forward_starting = df[df["forward_starting"].astype(str) == "0"][
                    target_cols
                ]
                output = concat([output, not_forward_starting], axis=0)

        output = output.pivot_table(
            columns="type",
            values="strike",
            index="time.to.mat",
        )

        for col in output.columns:
            output[col] = output[col].astype("float64").round(4)

        output = output.reset_index()
        output.loc[:, "time.to.mat"] = output["time.to.mat"].round(2)

        return output.replace({nan: None}).to_dict(orient="records")
    except Exception as e:
        raise OpenBBError(e) from e


@app.get("/apps.json")
def get_apps_json():
    """Return the apps.json configuration file."""
    try:
        apps_json_path = Path(__file__).parent / "apps.json"
        with open(apps_json_path, "r") as f:
            return json.load(f)
    except Exception as e:
        raise OpenBBError(f"Error reading apps.json: {str(e)}") from e
