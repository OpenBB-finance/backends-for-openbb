"""Swaps Data Query Parameter Types."""

from typing import Annotated, Literal, Union

from fastapi import Query

SWAP_TENOR_CHOICES = [
    {"value": "1", "label": "1Y"},
    {"value": "2", "label": "2Y"},
    {"value": "3", "label": "3Y"},
    {"value": "4", "label": "4Y"},
    {"value": "5", "label": "5Y"},
    {"value": "7", "label": "7Y"},
    {"value": "10", "label": "10Y"},
    {"value": "15", "label": "15Y"},
    {"value": "20", "label": "20Y"},
    {"value": "30", "label": "30Y"},
    {"value": "40", "label": "40Y"},
    {"value": "50", "label": "50Y"},
    {"value": "1s5s", "label": "1Y - 5Y Spread"},
    {"value": "2s10s", "label": "2Y - 10Y Spread"},
    {"value": "5s20s", "label": "5Y - 20Y Spread"},
    {"value": "2s5s10s", "label": "2Y - 5Y - 10Y Butterfly Spread"},
    {"value": "2s10s30s", "label": "2Y - 10Y - 30Y Butterfly Spread"},
]


SwapTypes = Annotated[
    Literal["Libor", "OIS", "Both"],
    Query(
        description="The type of swap rate level - Libor, OIS, Both. Default is OIS."
    ),
]


SwapRateTenors = Annotated[
    Union[
        str,
        Literal[
            "1",
            "2",
            "3",
            "4",
            "5",
            "7",
            "10",
            "15",
            "20",
            "30",
            "40",
            "50",
            "1s5s",
            "2s10s",
            "5s20s",
            "2s5s10s",
            "2s10s30s",
        ],
    ],
    Query(
        description="The tenor of swap to query. Can be a single tenor or a comma-separated list of tenors. Default is 2Y - 10Y Spread."
        + " Possible values are:\n"
        + "\n".join(
            [
                f"- {choice['value']} ({choice['label']})"
                for choice in SWAP_TENOR_CHOICES
            ]
        ),
        json_schema_extra={
            "x-widget_config": {
                "multiSelect": True,
                "type": "endpoint",
                "optionsEndpoint": "swap_rate_levels/tenors",
                "optionsParams": {"currency": "$currency", "swap_type": "$swap_type"},
            }
        },
    ),
]

SwapCurrency = Annotated[
    Literal["USD", "EUR", "GBP", "JPY"],
    Query(
        description="The underlying currency for the swap rate levels. Default is USD."
        + " Possible values are:\n"
        + "\n- USD\n- EUR\n- GBP\n- JPY",
    ),
]

SwapRatePeriod = Annotated[
    Literal["1m", "3m", "6m", "YTD", "1y"],
    Query(
        description="The historical window of levels. Default is 1y."
        + " Possible values are:\n"
        + "\n- 1m\n- 3m\n- 6m\n- YTD\n- 1y",
        json_schema_extra={
            "x-widget_config": {
                "type": "dropdown",
                "options": [
                    {"value": "1m", "label": "1 Month"},
                    {"value": "3m", "label": "3 Months"},
                    {"value": "6m", "label": "6 Months"},
                    {"value": "YTD", "label": "Year to Date"},
                    {"value": "1y", "label": "1 Year"},
                ],
            }
        },
    ),
]


SwapVolumeTypes = Annotated[
    Literal["Notional", "PV01"],
    Query(
        description="The type of volume to query. Default is Notional."
        + " Possible values are:\n"
        + "\n- Notional\n- PV01 (Dollar Value of 1 basis point change in the swap rate)"
    ),
]


SwapTenorBuckets = Annotated[
    Union[
        str,
        Literal[
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
        ],
    ],
    Query(
        description="The tenor bucket to query. Default is 7-10."
        + " Possible values are:\n"
        + "\n- 0-1\n- 1-3\n- 3-4\n- 4-5\n- 5-7\n- 7-10\n- 10-15\n- 15-20\n"
        + "- 20-25\n- 25-30\n- 30-40\n- 40-50\n\n",
        json_schema_extra={
            "x-widget_config": {
                "multiSelect": True,
                "label": "Tenor Buckets",
                "type": "endpoint",
                "optionsEndpoint": "swap_rate_volume/buckets",
                "optionsParams": {"currency": "$currency"},
            }
        },
    ),
]


SwapTradeDistributionDates = Annotated[
    str,
    Query(
        description="The date to query. Default is the last available date.",
        json_schema_extra={
            "x-widget_config": {
                "type": "endpoint",
                "optionsEndpoint": "trade_distribution/dates",
                "optionsParams": {"currency": "$currency", "swap_type": "$swap_type"},
                "label": "Trade Date",
            }
        },
    ),
]


SwapCurveDates = Annotated[
    str,
    Query(
        description="The date of the curve. Default is the last available date.",
        json_schema_extra={
            "x-widget_config": {
                "type": "endpoint",
                "multiSelect": True,
                "optionsEndpoint": "swap_curve/dates",
                "optionsParams": {"currency": "$currency", "swap_type": "$swap_type"},
                "label": "Curve Date",
            }
        },
    ),
]

SwapTradesDates = Annotated[
    str,
    Query(
        description="The date to query. This feature is not implemented for historical data.",
        json_schema_extra={
            "x-widget_config": {
                "options": [
                    {"value": "2025-04-15", "label": "2025-04-15"},
                    {
                        "value": "2025-04-15",
                        "label": "Integrate your database for this feature....",
                    },
                ],
                "label": "Trade Date",
            }
        },
    ),
]

SwapTradesClearedOnly = Annotated[
    bool,
    Query(
        description="Display only cleared trades. Default is False.",
        json_schema_extra={
            "x-widget_config": {
                "label": "Cleared Only",
            }
        },
    ),
]

SwapTradesIncludeStarting = Annotated[
    bool,
    Query(
        description="Include starting trades. Default is False.",
        json_schema_extra={
            "x-widget_config": {
                "label": "Include Forward Starting Swaps",
            }
        },
    ),
]
