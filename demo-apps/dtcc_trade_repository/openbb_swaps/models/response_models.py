"""Swaps Data Response Models."""

from datetime import date as dateType
from typing import Optional
from openbb_core.provider.abstract.data import Data
from pydantic import ConfigDict, Field, model_serializer


SWAP_RATE_LEVELS_TENOR_MAP = {
    "1": "One Year",
    "2": "Two Year",
    "3": "Three Year",
    "4": "Four Year",
    "5": "Five Year",
    "7": "Seven Year",
    "10": "Ten Year",
    "15": "Fifteen Year",
    "20": "Twenty Year",
    "30": "Thirty Year",
    "40": "Forty Year",
    "50": "Fifty Year",
    "1s5s": "One Year - Five Year Spread",
    "2s10s": "Two Year - Ten Year Spread",
    "5s20s": "Five Year - Twenty Year Spread",
    "2s5s10s": "Two Year - Five Year - Ten Year Butterfly Spread",
    "2s10s30s": "Two Year - Ten Year - Thirty Year Butterfly Spread",
}


class SwapRateLevelsResponseModel(Data):
    """DTCC Swap Rate Levels Data."""

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$data": {
                    "table": {
                        "enableCharts": True,
                        "chartView": {
                            "chartType": "column",
                            "enabled": True,
                            "ignoreCellRange": True,
                        },
                    }
                }
            }
        }
    )

    __alias_dict__ = {
        "date": "curve_date",
        "ois_one_year": "ois_1",
        "ois_two_year": "ois_2",
        "ois_three_year": "ois_3",
        "ois_four_year": "ois_4",
        "ois_five_year": "ois_5",
        "ois_seven_year": "ois_7",
        "ois_ten_year": "ois_10",
        "ois_fifteen_year": "ois_15",
        "ois_twenty_year": "ois_20",
        "ois_thirty_year": "ois_30",
        "ois_forty_year": "ois_40",
        "ois_fifty_year": "ois_50",
        "ois_one_year_five_year_spread": "ois_1s5s",
        "ois_two_year_ten_year_spread": "ois_2s10s",
        "ois_five_year_twenty_year_spread": "ois_5s20s",
        "ois_two_year_five_year_ten_year_butterfly_spread": "ois_2s5s10s",
        "ois_two_year_ten_year_thirty_year_butterfly_spread": "ois_2s10s30s",
        "libor_one_year": "libor_1",
        "libor_two_year": "libor_2",
        "libor_three_year": "libor_3",
        "libor_four_year": "libor_4",
        "libor_five_year": "libor_5",
        "libor_seven_year": "libor_7",
        "libor_ten_year": "libor_10",
        "libor_fifteen_year": "libor_15",
        "libor_twenty_year": "libor_20",
        "libor_thirty_year": "libor_30",
        "libor_forty_year": "libor_40",
        "libor_fifty_year": "libor_50",
        "libor_one_year_five_year_spread": "libor_1s5s",
        "libor_two_year_ten_year_spread": "libor_2s10s",
        "libor_five_year_twenty_year_spread": "libor_5s20s",
        "libor_two_year_five_year_ten_year_butterfly_spread": "libor_2s5s10s",
        "libor_two_year_ten_year_thirty_year_butterfly_spread": "libor_2s10s30s",
    }

    date: dateType = Field(
        description="The date of the swap rate level.",
        json_schema_extra={
            "x-widget_config": {
                "chartDataType": "time",
            }
        },
    )
    ois_one_year: Optional[float] = Field(
        default=None,
        description="The one year OIS swap rate level.",
        json_schema_extra={
            "x-unit_measurement": "percent",
            "x-widget_config": {"headerName": "1Y OIS", "chartDataType": "series"},
        },
    )
    libor_one_year: Optional[float] = Field(
        default=None,
        description="The one year Libor swap rate level.",
        json_schema_extra={
            "x-unit_measurement": "percent",
            "x-widget_config": {"headerName": "1Y Libor", "chartDataType": "series"},
        },
    )
    ois_two_year: Optional[float] = Field(
        default=None,
        description="The two year OIS swap rate level.",
        json_schema_extra={
            "x-unit_measurement": "percent",
            "x-widget_config": {"headerName": "2Y OIS", "chartDataType": "series"},
        },
    )
    libor_two_year: Optional[float] = Field(
        default=None,
        description="The two year Libor swap rate level.",
        json_schema_extra={
            "x-unit_measurement": "percent",
            "x-widget_config": {"headerName": "2Y Libor", "chartDataType": "series"},
        },
    )
    ois_three_year: Optional[float] = Field(
        default=None,
        description="The three year OIS swap rate level.",
        json_schema_extra={
            "x-unit_measurement": "percent",
            "x-widget_config": {"headerName": "3Y OIS", "chartDataType": "series"},
        },
    )
    libor_three_year: Optional[float] = Field(
        default=None,
        description="The three year Libor swap rate level.",
        json_schema_extra={
            "x-unit_measurement": "percent",
            "x-widget_config": {"headerName": "3Y Libor", "chartDataType": "series"},
        },
    )
    ois_four_year: Optional[float] = Field(
        default=None,
        description="The four year OIS swap rate level.",
        json_schema_extra={
            "x-unit_measurement": "percent",
            "x-widget_config": {"headerName": "4Y OIS", "chartDataType": "series"},
        },
    )
    libor_four_year: Optional[float] = Field(
        default=None,
        description="The four year Libopr swap rate level.",
        json_schema_extra={
            "x-unit_measurement": "percent",
            "x-widget_config": {"headerName": "4Y Libor", "chartDataType": "series"},
        },
    )
    ois_five_year: Optional[float] = Field(
        default=None,
        description="The five year OIS swap rate level.",
        json_schema_extra={
            "x-unit_measurement": "percent",
            "x-widget_config": {"headerName": "5Y OIS", "chartDataType": "series"},
        },
    )
    libor_five_year: Optional[float] = Field(
        default=None,
        description="The five year Libor swap rate level.",
        json_schema_extra={
            "x-unit_measurement": "percent",
            "x-widget_config": {"headerName": "5Y Libor", "chartDataType": "series"},
        },
    )
    ois_seven_year: Optional[float] = Field(
        default=None,
        description="The seven year OIS swap rate level.",
        json_schema_extra={
            "x-unit_measurement": "percent",
            "x-widget_config": {"headerName": "7Y OIS", "chartDataType": "series"},
        },
    )
    libor_seven_year: Optional[float] = Field(
        default=None,
        description="The seven year Libor swap rate level.",
        json_schema_extra={
            "x-unit_measurement": "percent",
            "x-widget_config": {"headerName": "7Y Libor", "chartDataType": "series"},
        },
    )
    ois_ten_year: Optional[float] = Field(
        default=None,
        description="The ten year OIS swap rate level.",
        json_schema_extra={
            "x-unit_measurement": "percent",
            "x-widget_config": {"headerName": "10Y OIS", "chartDataType": "series"},
        },
    )
    libor_ten_year: Optional[float] = Field(
        default=None,
        description="The ten year Libor swap rate level.",
        json_schema_extra={
            "x-unit_measurement": "percent",
            "x-widget_config": {"headerName": "10Y Libor", "chartDataType": "series"},
        },
    )
    ois_fifteen_year: Optional[float] = Field(
        default=None,
        description="The fifteen year OIS swap rate level.",
        json_schema_extra={
            "x-unit_measurement": "percent",
            "x-widget_config": {"headerName": "15Y OIS", "chartDataType": "series"},
        },
    )
    libor_fifteen_year: Optional[float] = Field(
        default=None,
        description="The fifteen year Libor swap rate level.",
        json_schema_extra={
            "x-unit_measurement": "percent",
            "x-widget_config": {"headerName": "15Y Libor", "chartDataType": "series"},
        },
    )
    ois_twenty_year: Optional[float] = Field(
        default=None,
        description="The twenty year swap rate level.",
        json_schema_extra={
            "x-unit_measurement": "percent",
            "x-widget_config": {"headerName": "20Y OIS", "chartDataType": "series"},
        },
    )
    libor_twenty_year: Optional[float] = Field(
        default=None,
        description="The twenty year Libor swap rate level.",
        json_schema_extra={
            "x-unit_measurement": "percent",
            "x-widget_config": {"headerName": "20Y Libor", "chartDataType": "series"},
        },
    )
    ois_thirty_year: Optional[float] = Field(
        default=None,
        description="The thirty year OIS swap rate level.",
        json_schema_extra={
            "x-unit_measurement": "percent",
            "x-widget_config": {"headerName": "30Y OIS", "chartDataType": "series"},
        },
    )
    libor_thirty_year: Optional[float] = Field(
        default=None,
        description="The thirty year Libor swap rate level.",
        json_schema_extra={
            "x-unit_measurement": "percent",
            "x-widget_config": {"headerName": "30Y Libor", "chartDataType": "series"},
        },
    )
    ois_forty_year: Optional[float] = Field(
        default=None,
        description="The forty year swap rate level.",
        json_schema_extra={
            "x-unit_measurement": "percent",
            "x-widget_config": {"headerName": "40Y OIS", "chartDataType": "series"},
        },
    )
    libor_forty_year: Optional[float] = Field(
        default=None,
        description="The forty year swap rate level.",
        json_schema_extra={
            "x-unit_measurement": "percent",
            "x-widget_config": {"headerName": "40Y Libor", "chartDataType": "series"},
        },
    )
    ois_fifty_year: Optional[float] = Field(
        default=None,
        description="The fifty year OIS swap rate level.",
        json_schema_extra={
            "x-unit_measurement": "percent",
            "x-widget_config": {"headerName": "50Y OIS", "chartDataType": "series"},
        },
    )
    libor_fifty_year: Optional[float] = Field(
        default=None,
        description="The fifty year Libor swap rate level.",
        json_schema_extra={
            "x-unit_measurement": "percent",
            "x-widget_config": {"headerName": "50Y Libor", "chartDataType": "series"},
        },
    )
    ois_one_year_five_year_spread: Optional[float] = Field(
        default=None,
        description="The one year - five year OIS spread.",
        json_schema_extra={
            "x-unit_measurement": "percent",
            "x-widget_config": {
                "headerName": "1Y - 5Y OIS Spread",
                "chartDataType": "series",
            },
        },
    )
    libor_one_year_five_year_spread: Optional[float] = Field(
        default=None,
        description="The one year - five year Libor spread.",
        json_schema_extra={
            "x-unit_measurement": "percent",
            "x-widget_config": {
                "headerName": "1Y - 5Y Libor Spread",
                "chartDataType": "series",
            },
        },
    )
    ois_two_year_ten_year_spread: Optional[float] = Field(
        default=None,
        description="The two year - ten year OIS spread.",
        json_schema_extra={
            "x-unit_measurement": "percent",
            "x-widget_config": {
                "headerName": "2Y - 10Y OIS Spread",
                "chartDataType": "series",
            },
        },
    )
    libor_two_year_ten_year_spread: Optional[float] = Field(
        default=None,
        description="The two year - ten year Libor spread.",
        json_schema_extra={
            "x-unit_measurement": "percent",
            "x-widget_config": {
                "headerName": "2Y - 10Y Libor Spread",
                "chartDataType": "series",
            },
        },
    )
    ois_five_year_twenty_year_spread: Optional[float] = Field(
        default=None,
        description="The five year - twenty year OIS spread.",
        json_schema_extra={
            "x-unit_measurement": "percent",
            "x-widget_config": {
                "headerName": "5Y - 20Y OIS Spread",
                "chartDataType": "series",
            },
        },
    )
    libor_five_year_twenty_year_spread: Optional[float] = Field(
        default=None,
        description="The five year - twenty year Libor spread.",
        json_schema_extra={
            "x-unit_measurement": "percent",
            "x-widget_config": {
                "headerName": "5Y - 20Y Libor Spread",
                "chartDataType": "series",
            },
        },
    )
    ois_two_year_five_year_ten_year_butterfly_spread: Optional[float] = Field(
        default=None,
        description="The two year - five year - ten year OIS butterfly spread.",
        json_schema_extra={
            "x-unit_measurement": "percent",
            "x-widget_config": {
                "headerName": "2Y - 5Y - 10Y OIS Butterfly Spread",
                "chartDataType": "series",
            },
        },
    )
    libor_two_year_five_year_ten_year_butterfly_spread: Optional[float] = Field(
        default=None,
        description="The two year - five year - ten year Libor butterfly spread.",
        json_schema_extra={
            "x-unit_measurement": "percent",
            "x-widget_config": {
                "headerName": "2Y - 5Y - 10Y Libor Butterfly Spread",
                "chartDataType": "series",
            },
        },
    )
    ois_two_year_ten_year_thirty_year_butterfly_spread: Optional[float] = Field(
        default=None,
        description="The two year - ten year - thirty year OIS butterfly spread.",
        json_schema_extra={
            "x-unit_measurement": "percent",
            "x-widget_config": {
                "headerName": "2Y - 10Y - 30Y OIS Butterfly Spread",
                "chartDataType": "series",
            },
        },
    )
    libor_two_year_ten_year_thirty_year_butterfly_spread: Optional[float] = Field(
        default=None,
        description="The two year - ten year - thirty year Libor butterfly spread.",
        json_schema_extra={
            "x-unit_measurement": "percent",
            "x-widget_config": {
                "headerName": "2Y - 10Y - 30Y Libor Butterfly Spread",
                "chartDataType": "series",
            },
        },
    )

    @model_serializer()
    def serialize_model(self):
        """Serialize the model to a dictionary."""
        return {k: v for k, v in self.__dict__.items() if v is not None}


class SwapRateVolumeResponseModel(Data):
    """DTCC Swap Rate Volume Data."""

    __alias_dict__ = {
        "date": "spot_date",
        "libor_volume": "Libor Volume",
        "ois_volume": "OIS Volume",
        "total_5d_ma_volume": "Total 5-Day MA Volume",
    }

    date: dateType = Field(
        description="The reporting date.",
        json_schema_extra={
            "x-widget_config": {
                "chartDataType": "time",
                "headerName": "Spot Date",
            }
        },
    )
    libor_volume: int = Field(
        description="The total volume of Libor swaps on the reporting date.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Libor Volume", "chartDataType": "series"}
        },
    )
    ois_volume: int = Field(
        description="The total volume of OIS swaps on the reporting date.",
        json_schema_extra={
            "x-widget_config": {"headerName": "OIS Volume", "chartDataType": "series"}
        },
    )
    total_5d_ma_volume: int = Field(
        description="The total 5-day moving average volume of swaps on the reporting date.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Total 5-Day MA Volume",
                "chartDataType": "series",
            }
        },
    )


class TradeDistributionResponseModel(Data):
    """DTCC Trade Distribution Data."""

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$data": {
                    "table": {
                        "enableCharts": True,
                        "chartView": {"chartType": "column", "enabled": True},
                    }
                }
            }
        }
    )

    __alias_dict__ = {
        "date": "spot_date",
        "zero_to_one_year": "0-1",
        "one_to_three_year": "1-3",
        "three_to_four_year": "3-4",
        "four_to_five_year": "4-5",
        "five_to_seven_year": "5-7",
        "seven_to_ten_year": "7-10",
        "ten_to_fifteen_year": "10-15",
        "fifteen_to_twenty_year": "15-20",
        "twenty_to_twentyfive_year": "20-25",
        "twentyfive_to_thirty_year": "25-30",
        "thirty_to_forty_year": "30-40",
        "forty_to_fifty_year": "40-50",
    }

    zero_to_one_year: Optional[int] = Field(
        default=None,
        description="The total volume of swaps with a maturity of 0 to 1 year.",
        json_schema_extra={
            "x-widget_config": {"headerName": "0-1 Year", "chartDataType": "series"}
        },
    )
    one_to_three_year: Optional[int] = Field(
        default=None,
        description="The total volume of swaps with a maturity of 1 to 3 years.",
        json_schema_extra={
            "x-widget_config": {"headerName": "1-3 Year", "chartDataType": "series"}
        },
    )
    three_to_four_year: Optional[int] = Field(
        default=None,
        description="The total volume of swaps with a maturity of 3 to 4 years.",
        json_schema_extra={
            "x-widget_config": {"headerName": "3-4 Year", "chartDataType": "series"}
        },
    )
    four_to_five_year: Optional[int] = Field(
        default=None,
        description="The total volume of swaps with a maturity of 4 to 5 years.",
        json_schema_extra={
            "x-widget_config": {"headerName": "4-5 Year", "chartDataType": "series"}
        },
    )
    five_to_seven_year: Optional[int] = Field(
        default=None,
        description="The total volume of swaps with a maturity of 5 to 7 years.",
        json_schema_extra={
            "x-widget_config": {"headerName": "5-7 Year", "chartDataType": "series"}
        },
    )
    seven_to_ten_year: Optional[int] = Field(
        default=None,
        description="The total volume of swaps with a maturity of 7 to 10 years.",
        json_schema_extra={
            "x-widget_config": {"headerName": "7-10 Year", "chartDataType": "series"}
        },
    )
    ten_to_fifteen_year: Optional[int] = Field(
        default=None,
        description="The total volume of swaps with a maturity of 10 to 15 years.",
        json_schema_extra={
            "x-widget_config": {"headerName": "10-15 Year", "chartDataType": "series"}
        },
    )
    fifteen_to_twenty_year: Optional[int] = Field(
        default=None,
        description="The total volume of swaps with a maturity of 15 to 20 years.",
        json_schema_extra={
            "x-widget_config": {"headerName": "15-20 Year", "chartDataType": "series"}
        },
    )
    twenty_to_twentyfive_year: Optional[int] = Field(
        default=None,
        description="The total volume of swaps with a maturity of 20 to 25 years.",
        json_schema_extra={
            "x-widget_config": {"headerName": "20-25 Year", "chartDataType": "series"}
        },
    )
    twentyfive_to_thirty_year: Optional[int] = Field(
        default=None,
        description="The total volume of swaps with a maturity of 25 to 30 years.",
        json_schema_extra={
            "x-widget_config": {"headerName": "25-30 Year", "chartDataType": "series"}
        },
    )
    thirty_to_forty_year: Optional[int] = Field(
        default=None,
        description="The total volume of swaps with a maturity of 30 to 40 years.",
        json_schema_extra={
            "x-widget_config": {"headerName": "30-40 Year", "chartDataType": "series"}
        },
    )
    forty_to_fifty_year: Optional[int] = Field(
        default=None,
        description="The total volume of swaps with a maturity of 40 to 50 years.",
        json_schema_extra={
            "x-widget_config": {"headerName": "40-50 Year", "chartDataType": "series"}
        },
    )

    @model_serializer()
    def serialize_model(self):
        """Serialize the model to a dictionary."""
        return {k: v for k, v in self.__dict__.items() if v is not None}


class SwapTradesResponseModel(Data):
    """DTCC Swap Trades Data."""

    __alias_dict__ = {
        "rate": "strike",
        "tenor": "time.to.mat",
        "pricing_rate": "Pricing Rate",
        "cleared_and_spot_starting": "Cleared and spot starting",
        "uncleared_and_forward_starting": "Non cleared and/or forward starting",
    }

    tenor: float = Field(
        description="Tenor of the swap, in years.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Tenor",
                "chartDataType": "category",
            }
        },
    )
    pricing_rate: Optional[float] = Field(
        default=None,
        description="The pricing rate of the swap trade.",
        json_schema_extra={
            "x-unit_measurement": "percent",
            "x-widget_config": {
                "headerName": "Pricing Rate",
                "chartDataType": "series",
            },
        },
    )
    cleared_and_spot_starting: Optional[float] = Field(
        default=None,
        description="Swap trades that are cleared and spot starting.",
        json_schema_extra={
            "x-unit_measurement": "percent",
            "x-widget_config": {
                "headerName": "Cleared & Spot Starting",
                "chartDataType": "series",
            },
        },
    )
    uncleared_and_forward_starting: Optional[float] = Field(
        default=None,
        description="Swap trades that are uncleared and/or forward starting.",
        json_schema_extra={
            "x-unit_measurement": "percent",
            "x-widget_config": {
                "headerName": "Uncleared and/or Forward Starting",
                "chartDataType": "series",
            },
        },
    )
