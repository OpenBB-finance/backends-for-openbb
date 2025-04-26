"""Main application."""

import asyncio
import json
import os

from typing import Annotated, Literal, Optional

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from openbb_core.provider.abstract.data import Data
from pandas import DataFrame, DateOffset, DatetimeIndex, Timestamp, to_datetime
from pydantic import Field

from demo_risk.constants import DATASET_CHOICES, FACTOR_REGION_MAP, REGIONS_MAP
from demo_risk.depends import PortfolioData
from demo_risk.correlation_matrix import correlation_matrix, plot_factors
from demo_risk.utils import (
    FactorsDoc,
    get_portfolio_data,
    perform_ols,
)

app = FastAPI()

origins = [
    "https://pro.openbb.co",
    "https://pro.openbb.dev",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PriceHistory(Data):
    """Historical Price Performance."""

    date: str = Field(
        description="Closing date of the stock.",
        title="Date",
        json_schema_extra={
            "x-widget_config": {
                "cellDataType": "date",
                "chartDataType": "time",
            },
        },
        alias="Date",
    )
    close: float = Field(
        description="Closing value.",
        title="Close",
        json_schema_extra={
            "x-widget_config": {
                "chartDataType": "series",
            }
        },
    )


class HoldingsData(Data):
    """Portfolio Holdings Data."""

    symbol: str = Field(None, description="The ticker of the stock.", alias="Symbol")
    name: str = Field(None, description="The name of the stock.", alias="Name")
    country: str = Field(
        None,
        description="The country of the stock.",
        alias="Country",
    )
    sector: str = Field(
        None,
        description="The sector of the stock.",
        alias="Sector",
    )
    industry: str = Field(
        None,
        description="The industry of the stock.",
        alias="Industry",
    )
    weight: Optional[float] = Field(
        None,
        description="The weight of the stock in the portfolio.",
        json_schema_extra={"x-unit_measurement": "percent"},
        alias="Weight",
    )


@app.get("/templates.json", openapi_extra={"widget_config": {"exclude": True}})
async def get_templates():
    """Get templates."""
    return [
        {
            "name": "Fama French Factors and Research Portfolio",
            "img": "https://github.com/user-attachments/assets/8b2409d6-5ddc-4cbc-b20c-89a29b1bd923",
            "img_dark": "",
            "img_light": "",
            "description": "Examine sample portfolio holdings distribution across countries, sectors, and industries, while also understanding how different assets correlate with each other over various time periods. This app provides insights into how portfolios respond to different market factors using Fama-French analysis, helping investors understand their portfolio's underlying drivers of returns and risk exposures.",
            "allowCustomization": True,
            "tabs": {
                "reference-data": {
                    "id": "reference-data",
                    "name": "Reference Data",
                    "layout": [
                        {
                            "i": "fama_french_info_custom_obb",
                            "x": 0,
                            "y": 2,
                            "w": 12,
                            "h": 25,
                        },
                        {
                            "i": "load_factors_custom_obb",
                            "x": 12,
                            "y": 13,
                            "w": 28,
                            "h": 14,
                            "state": {
                                "params": {
                                    "frequency": "monthly",
                                    "start_date": "2021-01-01",
                                    "end_date": "2025-03-27",
                                },
                                "chartView": {"enabled": False, "chartType": "line"},
                            },
                        },
                        {
                            "i": "load_portfolios_custom_obb",
                            "x": 12,
                            "y": 2,
                            "w": 28,
                            "h": 11,
                            "state": {
                                "params": {
                                    "portfolio": "Portfolios_Formed_on_OP",
                                    "start_date": "2021-01-01",
                                    "end_date": "2025-03-27",
                                },
                                "chartView": {"enabled": False, "chartType": "line"},
                            },
                        },
                    ],
                },
                "portfolio-price--performance": {
                    "id": "portfolio-price--performance",
                    "name": "Portfolio Price & Performance",
                    "layout": [
                        {
                            "i": "portfolio_unit_price_custom_obb",
                            "x": 0,
                            "y": 2,
                            "w": 40,
                            "h": 24,
                            "state": {
                                "params": {"portfolio": "Client 2", "returns": "True"},
                                "chartView": {"enabled": True, "chartType": "line"},
                            },
                        }
                    ],
                },
                "portfolio-region-and-sector-exposure": {
                    "id": "portfolio-region-and-sector-exposure",
                    "name": "Portfolio Region and Sector Exposure",
                    "layout": [
                        {
                            "i": "portfolio_sectors_custom_obb",
                            "x": 0,
                            "y": 13,
                            "w": 19,
                            "h": 14,
                            "state": {
                                "chartView": {"enabled": True, "chartType": "pie"}
                            },
                        },
                        {
                            "i": "portfolio_countries_custom_obb",
                            "x": 0,
                            "y": 2,
                            "w": 19,
                            "h": 11,
                            "state": {
                                "chartView": {"enabled": True, "chartType": "pie"}
                            },
                        },
                        {
                            "i": "portfolio_industries_custom_obb",
                            "x": 19,
                            "y": 2,
                            "w": 21,
                            "h": 25,
                            "state": {
                                "params": {"portfolio": "Client 3"},
                                "chartView": {"enabled": True, "chartType": "pie"},
                            },
                        },
                    ],
                },
                "portfolio-holdings": {
                    "id": "portfolio-holdings",
                    "name": "Portfolio Holdings",
                    "layout": [
                        {
                            "i": "portfolio_holdings_custom_obb",
                            "x": 0,
                            "y": 2,
                            "w": 40,
                            "h": 25,
                            "state": {
                                "params": {"portfolio": "Client 2"},
                                "chartView": {"enabled": True, "chartType": "bar"},
                            },
                        }
                    ],
                },
                "portfolio-holdings-correlations": {
                    "id": "portfolio-holdings-correlations",
                    "name": "Portfolio Holdings Correlations",
                    "layout": [
                        {
                            "i": "holdings_correlation_custom_obb",
                            "x": 0,
                            "y": 2,
                            "w": 40,
                            "h": 26,
                            "state": {"params": {"portfolio": "Client 2"}},
                        }
                    ],
                },
                "portfolio-factor-correlations": {
                    "id": "portfolio-factor-correlations",
                    "name": "Portfolio Factor Attributions",
                    "layout": [
                        {
                            "i": "portfolio_factors_custom_obb",
                            "x": 0,
                            "y": 2,
                            "w": 30,
                            "h": 20,
                            "state": {"params": {"portfolio": "Client 2"}},
                        }
                    ],
                },
            },
            "groups": [
                {
                    "name": "Group 3",
                    "type": "param",
                    "paramName": "frequency",
                    "defaultValue": "monthly",
                    "widgetIds": [
                        "load_factors_custom_obb",
                        "load_portfolios_custom_obb",
                    ],
                },
                {
                    "name": "Group 2",
                    "type": "param",
                    "paramName": "start_date",
                    "defaultValue": "2021-01-01",
                    "widgetIds": [
                        "load_factors_custom_obb",
                        "load_portfolios_custom_obb",
                    ],
                },
                {
                    "name": "Group 4",
                    "type": "param",
                    "paramName": "end_date",
                    "defaultValue": "2025-03-27",
                    "widgetIds": [
                        "load_factors_custom_obb",
                        "load_portfolios_custom_obb",
                    ],
                },
                {
                    "name": "Group 5",
                    "type": "param",
                    "paramName": "region",
                    "defaultValue": "america",
                    "widgetIds": [
                        "load_factors_custom_obb",
                        "load_portfolios_custom_obb",
                    ],
                },
                {
                    "name": "Group 6",
                    "type": "endpointParam",
                    "paramName": "factor",
                    "defaultValue": "america",
                    "widgetIds": [
                        "load_factors_custom_obb",
                        "load_portfolios_custom_obb",
                    ],
                },
                {
                    "name": "Group 7",
                    "type": "param",
                    "paramName": "portfolio",
                    "defaultValue": "Client 1",
                    "widgetIds": [
                        "portfolio_sectors_custom_obb",
                        "portfolio_countries_custom_obb",
                        "portfolio_industries_custom_obb",
                        "portfolio_holdings_custom_obb",
                        "portfolio_unit_price_custom_obb",
                        "holdings_correlation_custom_obb",
                        "portfolio_factors_custom_obb",
                    ],
                },
            ],
        }
    ]

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}

@app.get(
    "/fama_french_info",
    openapi_extra={
        "widget_config": {"refetchInterval": False},
        "name": "F-F Datasets Info",
    },
)
async def get_fama_french_info(store: PortfolioData) -> str:
    """Get Fama French info."""
    descriptions = ""
    LOADED_PORTFOLIO = (
        store.get_store("LOADED_PORTFOLIO")
        if "LOADED_PORTFOLIO" in store.list_stores
        else ""
    )
    LOADED_FACTORS = (
        store.get_store("LOADED_FACTORS")
        if "LOADED_FACTORS" in store.list_stores
        else ""
    )

    port_dataset = (
        store.get_store("loaded_ff_portfolio")
        if "loaded_ff_portfolio" in store.list_stores
        else {}
    )
    factor_dataset = (
        store.get_store("ff_factors") if "ff_factors" in store.list_stores else {}
    )

    if not port_dataset:
        await asyncio.sleep(2)
        port_dataset = (
            store.get_store("loaded_ff_portfolio")
            if "loaded_ff_portfolio" in store.list_stores
            else {}
        )

    if port_dataset:
        descrip = port_dataset.get("meta", {}).get("description", "")
        descriptions += (
            "\n\n"
            + f"### {LOADED_PORTFOLIO.replace('_', ' ')}"
            + "\n\n"
            + descrip
            + "\n\n"
            if descrip
            else ""
        )
    if factor_dataset:
        descrip = factor_dataset.get("meta", {}).get("description", "")
        descriptions += (
            "\n\n"
            + f"### {LOADED_FACTORS.replace('_', ' ')}"
            + "\n\n"
            + descrip
            + "\n\n"
            if descrip
            else ""
        )

    return descriptions + "\n\n" + FactorsDoc


@app.get(
    "/load_portfolios",
    openapi_extra={
        "widget_config": {
            "refecthInterval": False,
            "name": "F-F Portfolio Data",
        }
    },
)
async def get_load_portfolios(
    store: PortfolioData,
    region: Annotated[
        str,
        Query(
            description="Region",
            json_schema_extra={
                "x-widget_config": {
                    "type": "endpoint",
                    "optionsEndpoint": "/get_factor_choices",
                    "optionsParams": {
                        "get_regions": True,
                        "is_portfolio": True,
                    },
                }
            },
        ),
    ] = "america",
    portfolio: Annotated[
        str,
        Query(
            description="Portfolio set to load.",
            json_schema_extra={
                "x-widget_config": {
                    "style": {"popupWidth": 300},
                    "type": "endpoint",
                    "optionsEndpoint": "/get_factor_choices",
                    "optionsParams": {
                        "region": "$region",
                        "is_portfolio": True,
                    },
                }
            },
        ),
    ] = "Portfolios_Formed_on_ME",
    measure: Annotated[
        Literal["Value", "Equal", "Number Of Firms", "Firm Size"],
        Query(description="Data measurement"),
    ] = "Value",
    frequency: Annotated[
        str,
        Query(
            description="Data frequency. Only valid when the dataset is not daily (in the name).",
            json_schema_extra={
                "x-widget_config": {
                    "style": {"popupWidth": 300},
                    "type": "endpoint",
                    "optionsEndpoint": "/get_factor_choices",
                    "optionsParams": {
                        "region": "$region",
                        "is_portfolio": True,
                        "portfolio": "$portfolio",
                    },
                }
            },
        ),
    ] = "monthly",
    start_date: Annotated[
        Optional[str],
        Query(
            description="Start date",
            json_schema_extra={"x-widget_config": {"value": "$currentDate-30y"}},
        ),
    ] = None,
    end_date: Annotated[
        Optional[str],
        Query(
            description="End date",
            json_schema_extra={"x-widget_config": {"value": "$currentDate"}},
        ),
    ] = None,
) -> list:
    """Get dataset."""
    if not portfolio:
        return "Please select a portfolio."
    measure = measure.replace(" ", "_").lower()

    parsed_portfolio = (
        [
            v.get("value")
            for v in DATASET_CHOICES
            if v.get("value", "").startswith(portfolio)
            and "daily" in v.get("value").lower()
        ]
        if frequency == "daily"
        else [
            v.get("value")
            for v in DATASET_CHOICES
            if v.get("value", "").startswith(portfolio)
        ]
    )

    if frequency == "daily":
        parsed_portfolio = [d for d in parsed_portfolio if "daily" in d.lower()]
        frequency = None

    try:
        data, meta = get_portfolio_data(parsed_portfolio[0], frequency, measure)
        df = data[0]

        if start_date:
            df = df[df.index >= start_date]
        if end_date:
            df = df[df.index <= end_date]
        df = df.astype(float)
        df = df.sort_index()
        if "loaded_ff_portfolio" not in store.list_stores:
            store.add_store("loaded_ff_portfolio", {"meta": meta[0], "data": df})
        elif "loaded_ff_portfolio" in store.list_stores:
            store.update_store("loaded_ff_portfolio", {"meta": meta[0], "data": df})
        if "LOADED_PORTFOLIO" not in store.list_stores:
            store.add_store("LOADED_PORTFOLIO", portfolio)
        elif "LOADED_PORTFOLIO" in store.list_stores:
            store.update_store("LOADED_PORTFOLIO", portfolio)

        return df.reset_index().to_dict(orient="records") if data else []
    except Exception:
        return []


@app.get(
    "/load_factors",
    openapi_extra={
        "widget_config": {
            "refetchInterval": False,
            "name": "F-F Factors Data",
        }
    },
)
async def get_load_factors(
    store: PortfolioData,
    region: Annotated[
        str,
        Query(
            description="Region",
            json_schema_extra={
                "x-widget_config": {
                    "type": "endpoint",
                    "optionsEndpoint": "/get_factor_choices",
                    "optionsParams": {
                        "get_regions": True,
                        "is_portfolio": True,
                    },
                }
            },
        ),
    ] = "america",
    factor: Annotated[
        str,
        Query(
            description="Factor",
            json_schema_extra={
                "x-widget_config": {
                    "type": "endpoint",
                    "optionsEndpoint": "/get_factor_choices",
                    "optionsParams": {"region": "$region", "is_portfolio": False},
                },
            },
        ),
    ] = "5_Factors",
    frequency: Annotated[
        str,
        Query(
            description="Data frequency. Only valid when the dataset is not daily or weekly (in the name).",
            json_schema_extra={
                "x-widget_config": {
                    "type": "endpoint",
                    "optionsEndpoint": "/get_factor_choices",
                    "optionsParams": {
                        "region": "$region",
                        "factor": "$factor",
                        "is_portfolio": False,
                    },
                },
            },
        ),
    ] = "Monthly",
    start_date: Annotated[
        Optional[str],
        Query(
            description="Start date",
            json_schema_extra={"x-widget_config": {"value": "$currentDate-5y"}},
        ),
    ] = None,
    end_date: Annotated[
        Optional[str],
        Query(
            description="End date",
            json_schema_extra={"x-widget_config": {"value": "$currentDate"}},
        ),
    ] = None,
) -> list:
    """Get dataset."""
    if not factor:
        return "Please select a factor."

    interval = (
        FACTOR_REGION_MAP.get(region, {})
        .get("intervals", {})
        .get(factor, {})
        .get(frequency)
    )

    factor = FACTOR_REGION_MAP.get(region, {}).get("factors", {}).get(factor, factor)

    factor = factor + interval if interval else factor
    frequency = (
        None if "daily" in factor.lower() or "weekly" in factor.lower() else frequency
    )

    try:
        dfs, meta = get_portfolio_data(factor, frequency)
        df = dfs[0]

        if start_date:
            df = df[df.index >= start_date]

        if end_date:
            df = df[df.index <= end_date]

        df = df.astype(float)
        df = df.sort_index()
        if "ff_factors" not in store.list_stores:
            store.add_store("ff_factors", {"meta": meta[0], "data": df})
        elif "ff_factors" in store.list_stores:
            store.update_store("ff_factors", {"meta": meta[0], "data": df})
        if "LOADED_FACTORS" not in store.list_stores:
            store.add_store("LOADED_FACTORS", factor)
        elif "LOADED_FACTORS" in store.list_stores:
            store.update_store("LOADED_FACTORS", factor)
        if "loaded_factors" not in store.list_stores:
            store.add_store("loaded_factors", df)
        elif "loaded_factors" in store.list_stores:
            store.update_store("loaded_factors", df)

        return df.reset_index().to_dict(orient="records")
    except Exception:
        return []


@app.get("/get_data_choices", openapi_extra={"widget_config": {"exclude": True}})
async def get_data_choices(
    store: PortfolioData,
    region: str = None,
    portfolio_set: str = None,
    measure: str = None,
):
    from pandas import DataFrame

    port_data = await get_load_portfolios(
        region, portfolio_set, measure, "daily", None, None
    )
    port_data = DataFrame(port_data)

    if port_data.empty:
        output = [{"label": "No portfolios found. Try a new parameter.", "value": None}]
    output = [{"label": c, "value": c} for c in port_data.columns if c != "Date"]

    if "loaded_portfolio" not in store.list_stores:
        store.add_store("loaded_portfolio", port_data)
    elif "loaded_portfolio" in store.list_stores:
        store.update_store("loaded_portfolio", port_data)

    return output


@app.get(
    "/get_factor_choices",
    openapi_extra={"widget_config": {"exclude": True}},
)
async def get_factor_choices(
    store: PortfolioData,
    region: str = None,
    factor: str = None,
    is_portfolio: bool = False,
    include_emerging: bool = True,
    get_regions: bool = False,
    portfolio: str = None,
    measure: str = None,
    frequency: str = None,
):

    if get_regions is True and is_portfolio is True and include_emerging is False:
        return [
            {"label": k.replace("_", " ").title(), "value": k}
            for k in list(REGIONS_MAP)
            if "emerging" not in k.lower()
        ]
    if get_regions is True and is_portfolio is True and include_emerging is True:
        return [
            {"label": k.replace("_", " ").title(), "value": k}
            for k in list(REGIONS_MAP)
        ]
    if region and not factor and not is_portfolio:
        factors = FACTOR_REGION_MAP.get(region, {}).get("factors", {})
        return [
            {
                "label": k.replace("_", " ")
                .title()
                .replace("Lt", "LT")
                .replace("St", "ST"),
                "value": k,
            }
            for k in list(factors)
        ]
    if region and factor and not is_portfolio:
        intervals = (
            FACTOR_REGION_MAP.get(region, {}).get("intervals", {}).get(factor, {})
        )
        intervals = [
            {"label": k.replace("_", " ").title(), "value": k} for k in list(intervals)
        ]
        return intervals

    if not is_portfolio:
        return [
            {"label": k.replace("_", " ").title(), "value": k}
            for k in list(FACTOR_REGION_MAP)
        ]

    mapped_region = REGIONS_MAP.get(region, "").replace("_", " ")
    if is_portfolio and region and not portfolio:

        portfolios = (
            [
                {
                    "label": (
                        d["label"].replace(mapped_region, "").strip()
                        if region != "america"
                        else d["label"]
                    ),
                    "value": d["value"],
                }
                for d in DATASET_CHOICES
                if "Portfolio" in d.get("value")
                and d["value"].startswith(REGIONS_MAP.get(region, region))
                and "daily" not in d.get("value", "").lower()
            ]
            if region != "america"
            else [
                d
                for d in DATASET_CHOICES
                if "Portfolio" in d.get("value")
                and all(
                    not d.get("value", "").startswith(reg)
                    for reg in REGIONS_MAP.values()
                    if reg
                )
                and "daily" not in d.get("value", "").lower()
            ]
        )

        if "ex_" not in region:
            portfolios = [d for d in portfolios if "ex_" not in d.get("value", "")]

        return portfolios

    if is_portfolio and region and portfolio:
        portfolios = (
            [
                d
                for d in DATASET_CHOICES
                if "Portfolio" in d.get("value")
                and d["value"].startswith(REGIONS_MAP.get(region, region))
                and portfolio in d.get("value", "")
            ]
            if region != "america"
            else [
                d
                for d in DATASET_CHOICES
                if "Portfolio" in d.get("value")
                and all(
                    not d.get("value", "").startswith(reg)
                    for reg in REGIONS_MAP.values()
                    if reg
                )
                and portfolio in d.get("value", "")
            ]
        )
        has_daily = False
        frequencies = ["monthly", "annual"]

        for d in portfolios:
            if "daily" in d.get("value", "").lower():
                has_daily = True
                break

        frequencies = ["daily"] + frequencies if has_daily else frequencies

        return [{"label": k.title(), "value": k} for k in frequencies]

    return [{"label": "No choices found. Try a new parameter.", "value": None}]


@app.get(
    "/portfolio_factors",
    openapi_extra={
        "widget_config": {
            "name": "Portfolio Factor Attributions",
            "type": "chart",
            "gridData": {"w": 40, "h": 20},
            "params": [{"paramName": "theme", "show": False}],
        }
    },
)
async def portfolio_factors(
    store: PortfolioData,
    region: Annotated[
        str,
        Query(
            description="Region for the factor data.",
            json_schema_extra={
                "x-widget_config": {
                    "type": "endpoint",
                    "optionsEndpoint": "/get_factor_choices",
                    "optionsParams": {
                        "get_regions": True,
                        "is_portfolio": True,
                        "include_emerging": False,
                    },
                }
            },
        ),
    ] = "america",
    factor: Annotated[
        str,
        Query(
            description="Factor set to use for analysis.",
            json_schema_extra={
                "x-widget_config": {
                    "type": "endpoint",
                    "optionsEndpoint": "/get_factor_choices",
                    "optionsParams": {"region": "$region", "is_portfolio": False},
                },
            },
        ),
    ] = "5_Factors",
    portfolio: Literal["Client 1", "Client 2", "Client 3"] = "Client 1",
    theme: str = "dark",
) -> dict:
    """Get dataset."""
    frequency = "daily"
    if not factor:
        return "Please select a factor."

    try:
        # Get client portfolio data
        portfolio_data = store.get_store(f"portfolio_{portfolio[-1]}")
        returns_data = portfolio_data.get("portfolio_returns")

        # Make sure we have portfolio data
        if returns_data is None or returns_data.empty:
            return [{"Error": f"No data found for portfolio {portfolio}"}]

        # Load factor data first to understand its date range
        interval = (
            FACTOR_REGION_MAP.get(region, {})
            .get("intervals", {})
            .get(factor, {})
            .get(frequency)
        )
        factor_name = (
            FACTOR_REGION_MAP.get(region, {}).get("factors", {}).get(factor, factor)
        )
        factor_name = factor_name + interval if interval else factor_name
        factor_freq = (
            None
            if "daily" in factor_name.lower() or "weekly" in factor_name.lower()
            else frequency
        )

        if "LOADED_FACTORS" in store.list_stores:
            store.update_store("LOADED_FACTORS", factor_name)
        else:
            store.add_store("LOADED_FACTORS", factor_name)

        dfs, meta = get_portfolio_data(factor_name, factor_freq)
        factor_df = dfs[0]
        # Apply date filtering if specified

        # Convert to float and sort
        factor_df = factor_df.astype(float)
        factor_df = factor_df.sort_index()

        # Get the factor date range to match our portfolio resampling
        factor_min_date = factor_df.index.min()
        factor_max_date = factor_df.index.max()

        portfolio_df = returns_data.to_frame().rename(columns={"close": portfolio})
        portfolio_df.index = portfolio_df.index.astype(str)

        # Filter portfolio data to factor date range
        portfolio_df = portfolio_df[
            (portfolio_df.index >= factor_min_date)
            & (portfolio_df.index <= factor_max_date)
        ]

        portfolio_df = portfolio_df.sort_index()

        # Find the intersection of dates between the two dataframes
        common_dates = portfolio_df.index.intersection(factor_df.index)

        if len(common_dates) == 0:
            return [
                {"Error": "No matching dates found between portfolio and factor data."}
            ]

        # Use only the common dates
        portfolio_df = portfolio_df.loc[common_dates]
        factor_df = factor_df.loc[common_dates]

        factor_df.loc[:, portfolio] = portfolio_df[portfolio].values

        if "ff_factors" in store.list_stores:
            store.update_store("ff_factors", {"meta": meta[0], "data": factor_df})
        else:
            store.add_store("ff_factors", {"meta": meta[0], "data": factor_df})

        coefficients = []
        added_portfolios = portfolio.split(",") if "," in portfolio else [portfolio]
        timeframes = ["1 Month", "3 Month", "YTD", "1 Year", "3 Year", "Max"]
        if not added_portfolios:
            return [
                {"Error": "Please select target data from the loaded portfolio set."}
            ]
        # Return as records for API response
        factor_cols = [
            k
            for k in factor_df.columns
            if k not in ["Date", "RF"] and k not in added_portfolios
        ]

        # Get current date
        factor_df.index = factor_df.index.astype("datetime64[s]")
        max_date = factor_df.index.max()
        current_year = max_date.year

        for timeframe in timeframes:
            added_port = factor_df.copy()
            if portfolio in added_port.columns and "RF" in factor_df.columns:
                added_port.loc[:, f"{portfolio}"] = (
                    added_port[portfolio].values - added_port["RF"].values
                )

            # Apply period filtering
            if timeframe == "1 Month":
                start_date = max_date - DateOffset(months=1)
                added_port = added_port[added_port.index >= start_date]
            elif timeframe == "3 Month":
                start_date = max_date - DateOffset(months=3)
                added_port = added_port[added_port.index >= start_date]
            elif timeframe == "YTD":
                start_date = Timestamp(f"{current_year}-01-01")
                added_port = added_port[added_port.index >= start_date]
            elif timeframe == "1 Year":
                start_date = max_date - DateOffset(years=1)
                added_port = added_port[added_port.index >= start_date]
            elif timeframe == "3 Year":
                start_date = max_date - DateOffset(years=3)
                added_port = added_port[added_port.index >= start_date]

            model = await perform_ols(
                added_port,
                portfolio,
                factor_cols,
            )
            model = model
            model.reset_index(inplace=True)
            model.rename(columns={"index": "factor"}, inplace=True)

            model.loc[:, "period"] = timeframe
            model = model[
                [
                    "period",
                    "factor",
                    "coefficient",
                    "p_value",
                    "lower_ci",
                    "upper_ci",
                ]
            ]
            records = model.convert_dtypes().to_dict(orient="records")
            coefficients.extend(records)

        pivoted = DataFrame(coefficients).pivot_table(
            columns="factor",
            index="period",
            values=["coefficient", "p_value", "lower_ci", "upper_ci"],
            sort=False,
        )
        coeffs = pivoted["coefficient"].reset_index()
        p_value = pivoted["p_value"].reset_index()

        X = [d.replace("const", "Constant") for d in coeffs.columns.tolist()[1:]]
        Y = coeffs.period.tolist()
        colors_df = p_value.iloc[:, 1:].copy()
        text_df = coeffs.iloc[:, 1:].copy()

        fig = plot_factors(text_df, colors_df, X, Y)

        fig_json = json.loads(fig.to_json())

        return fig_json

    except Exception as e:
        print(f"Error loading factor data: {e}")
        return [{"Error": f"Failed to load factor data: {str(e)}"}]


@app.get(
    "/portfolio_holdings",
    openapi_extra={
        "widget_config": {"refetchInterval": False, "name": "Portfolio Holdings"}
    },
)
async def portfolio_holdings(
    store: PortfolioData,
    portfolio: Annotated[
        Literal["Client 1", "Client 2", "Client 3"],
        Query(
            description="Select the portfolio.",
        ),
    ] = "Client 1",
) -> list[HoldingsData]:
    """Get portfolio holdings."""
    port_data = store.get_store(f"portfolio_{portfolio[-1]}")
    if not port_data:
        return []

    holdings = port_data.get("holdings")
    holdings.Weight = holdings.Weight * 100
    if holdings is not None:
        return holdings.to_dict(orient="records")
    return []


@app.get(
    "/portfolio_countries",
    openapi_extra={
        "widget_config": {
            "refetchInterval": False,
            "name": "Portfolio Exposure by Country",
        },
    },
)
async def portfolio_countries(
    store: PortfolioData,
    portfolio: Annotated[
        Literal["Client 1", "Client 2", "Client 3"],
        Query(
            description="Select the portfolio.",
        ),
    ] = "Client 1",
) -> list:
    """Get portfolio's exposure by country."""
    port_data = store.get_store(f"portfolio_{portfolio[-1]}")
    if not port_data:
        return []

    holdings = port_data.get("country_exposure")
    if holdings is not None:
        return holdings.to_dict(orient="records")
    return []


@app.get(
    "/portfolio_sectors",
    openapi_extra={
        "widget_config": {
            "refetchInterval": False,
            "name": "Portfolio Exposure by Sector",
        },
    },
)
async def portfolio_sectors(
    store: PortfolioData,
    portfolio: Annotated[
        Literal["Client 1", "Client 2", "Client 3"],
        Query(
            description="Select the portfolio.",
        ),
    ] = "Client 1",
) -> list:
    """Get portfolio's exposure by sector."""
    port_data = store.get_store(f"portfolio_{portfolio[-1]}")
    if not port_data:
        return []

    holdings = port_data.get("sector_exposure")
    if holdings is not None:
        return holdings.to_dict(orient="records")
    return []


@app.get(
    "/portfolio_industries",
    openapi_extra={
        "widget_config": {
            "refetchInterval": False,
            "name": "Portfolio Exposure by Industry",
        },
    },
)
async def portfolio_industries(
    store: PortfolioData,
    portfolio: Annotated[
        Literal["Client 1", "Client 2", "Client 3"],
        Query(
            description="Select the portfolio.",
        ),
    ] = "Client 1",
) -> list:
    """Get portfolio's exposure by industry."""
    port_data = store.get_store(f"portfolio_{portfolio[-1]}")
    if not port_data:
        return []

    holdings = port_data.get("industry_exposure")
    if holdings is not None:
        return holdings.to_dict(orient="records")
    return []


@app.get(
    "/portfolio_unit_price",
    openapi_extra={
        "widget_config": {
            "refetchInterval": False,
            "name": "Portfolio Price Performance",
        },
    },
)
async def portfolio_unit_price(
    store: PortfolioData,
    portfolio: Annotated[
        Literal["Client 1", "Client 2", "Client 3"],
        Query(
            description="Select the portfolio.",
        ),
    ] = "Client 1",
    asset: Annotated[
        str,
        Query(
            description="Select the asset.",
            json_schema_extra={
                "x-widget_config": {
                    "type": "endpoint",
                    "optionsEndpoint": "/get_asset_choices",
                    "optionsParams": {"portfolio": "$portfolio"},
                    "style": {"popupWidth": 400},
                },
            },
        ),
    ] = "Portfolio Units",
    period: Annotated[
        Literal["1 Month", "3 Month", "YTD", "1 Year", "3 Year", "Max"],
        Query(
            description="Select the period.",
        ),
    ] = "1 Year",
    returns: Annotated[
        bool, Query(description="Show returns instead of unit price.")
    ] = False,
) -> list[PriceHistory]:
    """Get portfolio's unit price history."""
    port_data = store.get_store(f"portfolio_{portfolio[-1]}")
    if not port_data:
        return []

    holdings = (
        (
            port_data.get("portfolio_returns").to_frame()
            if returns is True
            else port_data.get("portfolio_price_data")
        )
        if asset == "Portfolio Units"
        else (
            port_data.get("underlying_returns").get(asset)
            if returns is True
            else port_data.get("underlying_price_data").get(asset)
        )
    )

    if holdings is None or holdings.empty:
        return []

    if asset != "Portfolio Units":
        holdings = holdings.to_frame().rename(columns={asset: "close"})

    # Ensure index is datetime type
    if not isinstance(holdings.index, DatetimeIndex):
        holdings.index = to_datetime(holdings.index)

    # Sort by date
    holdings = holdings.sort_index()

    # Get current date
    max_date = holdings.index.max()
    current_year = max_date.year

    # Apply period filtering
    if period == "1 Month":
        start_date = max_date - DateOffset(months=1)
        holdings = holdings[holdings.index >= start_date]
    elif period == "3 Month":
        start_date = max_date - DateOffset(months=3)
        holdings = holdings[holdings.index >= start_date]
    elif period == "YTD":
        start_date = Timestamp(f"{current_year}-01-01")
        holdings = holdings[holdings.index >= start_date]
    elif period == "1 Year":
        start_date = max_date - DateOffset(years=1)
        holdings = holdings[holdings.index >= start_date]
    elif period == "3 Year":
        start_date = max_date - DateOffset(years=3)
        holdings = holdings[holdings.index >= start_date]
    # For "Max", we use all data

    # If showing returns, calculate cumulative returns
    if returns is True:
        holdings.close = holdings.close.cumsum()

    holdings = holdings.dropna(subset=["close"])

    # Convert index to string for serialization
    holdings.index = holdings.index.astype(str)

    return holdings.reset_index().to_dict(orient="records")


@app.get(
    "/get_asset_choices",
    openapi_extra={
        "widget_config": {
            "exclude": True,
        },
    },
)
async def get_asset_choices(
    store: PortfolioData,
    portfolio: str = "Client 1",
) -> list:
    """Get asset choices for the portfolio."""
    port_data = store.get_store(f"portfolio_{portfolio[-1]}")
    if not port_data:
        return [{"label": "No assets found", "value": None}]

    holdings = port_data.get("holdings")

    symbols = holdings.Symbol.tolist()
    names = holdings.Name.tolist()

    choices = []
    choices.append({"label": "Portfolio Units", "value": "Portfolio Units"})
    for sym, name in zip(symbols, names):
        choices.append({"label": name, "value": sym})

    return choices


@app.get(
    "/portfolio_underlying_returns",
    openapi_extra={
        "widget_config": {
            "refetchInterval": False,
            "name": "Returns of the portfolio's underlying assets",
        },
    },
)
async def portfolio_underlying_returns(
    store: PortfolioData,
    portfolio: Annotated[
        Literal["Client 1", "Client 2", "Client 3"],
        Query(
            description="Select the portfolio.",
        ),
    ] = "Client 1",
) -> list:
    """Get portfolio's returns by underlying asset."""
    port_data = store.get_store(f"portfolio_{portfolio[-1]}")
    if not port_data:
        return []

    holdings = port_data.get("underlying_performance")
    if holdings is not None:
        return holdings.to_dict(orient="records")
    return []


@app.get(
    "/holdings_correlation",
    openapi_extra={
        "widget_config": {
            "refetchInterval": False,
            "name": "Portfolio Holdings Correlations",
            "type": "chart",
            "gridData": {"w": 40, "h": 20},
            "params": [{"paramName": "theme", "show": False}],
        },
    },
)
async def holdings_correlation(
    store: PortfolioData,
    portfolio: Annotated[
        Literal["Client 1", "Client 2", "Client 3"],
        Query(
            description="Select the portfolio.",
        ),
    ] = "Client 1",
    timeframe: Annotated[
        Literal["1 Month", "3 Month", "1 Year", "3 Year", "5 Year"],
        Query(
            description="Select the timeframe.",
        ),
    ] = "3 Month",
    theme: str = "dark",
) -> dict:
    """Get portfolio holdings."""
    import json

    port_data = store.get_store(f"portfolio_{portfolio[-1]}")
    if not port_data:
        return []

    data = port_data.get("underlying_returns")

    timedelta = (
        21
        if timeframe == "1 Month"
        else (
            63
            if timeframe == "3 Month"
            else (
                252
                if timeframe == "1 Year"
                else 252 * 3 if timeframe == "3 Year" else 252 * 5
            )
        )
    )
    data = data.iloc[-timedelta:]

    if data is not None:
        fig = correlation_matrix(
            data,
            chart=True,
            theme=theme,
        )
        fig_json = json.loads(fig.to_json())

    return fig_json


# def main():
#     """Run the app."""
#     import subprocess

#     subprocess.run(
#         [
#             "openbb-api",
#             "--app",
#             __file__,
#             "--port",
#             "6020",
#         ]
#     )


# if __name__ == "__main__":
#     main()
