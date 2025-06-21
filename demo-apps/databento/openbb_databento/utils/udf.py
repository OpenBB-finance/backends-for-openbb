
"""UDF Database Class for CME Data."""
# pylint: disable=too-many-instance-attributes,too-many-public-methods,no-member,too-many-nested-blocks,too-many-locals,too-many-arguments,too-many-branches,too-many-statements,import-outside-toplevel
# flake8: noqa: E402
from typing import Annotated, Optional
from decimal import Decimal, getcontext
from fastapi import Depends
from pandas import DataFrame, concat
from openbb_databento.utils.database import CmeDatabase
from openbb_databento.utils.constants import supported_units, unit_of_measure_map


class UdfDatabase:
    """A class to handle UDF database operations."""

    database = CmeDatabase
    _trading_session: Optional[dict] = None
    _udf_config: Optional[dict] = None
    _continuous_assets: DataFrame = DataFrame()
    _symbol_info_cache: dict = {}

    def get_udf_config(self) -> dict:
        """Get the UDF configuration."""
        if self._udf_config is not None:
            return self._udf_config
        supported_exchanges = self.get_supported_exchanges()

        self._udf_config = {
            "supported_resolutions": [],
            "supports_group_request": False,
            "supports_marks": False,
            "supports_search": True,
            "supports_timescale_marks": False,
            "supports_time": False,
            "exchanges": supported_exchanges,
            "symbols_types": [
                {"name": "All", "value": ""},
                {"name": "Equity", "value": "equity"},
                {"name": "Commodities", "value": "commodity"},
                {"name": "Energy", "value": "energy"},
                {"name": "FX", "value": "currency"},
                {"name": "Interest Rates", "value": "interest_rates"},
                {"name": "Metals", "value": "metals"},
                {"name": "Agriculture", "value": "agriculture"},
            ],
            "units": supported_units,
        }
        return self._udf_config

    def set_udf_config(self, value: dict) -> None:
        """Set the TradingView UDF configuration dictionary."""
        self._udf_config = value

    @property
    def has_intraday(self) -> bool:
        """Check if the database has intraday data."""
        return any(
            table.split("_")[1][0].isdigit() and table.split("_")[1][-1] in ["s", "m", "h"]
            for table in self.database().table_names  # pylint: disable=E1101
            if "_" in table
        )

    def get_supported_exchanges(self) -> list[dict]:
        """Get the list of supported exchanges."""
        exchanges_query = """
        SELECT DISTINCT exchange, exchange_name
        FROM futures_symbols
        WHERE exchange IS NOT NULL
        ORDER BY exchange;
        """
        exchanges = self.database().fetchall(exchanges_query)  # pylint: disable=E1101
        output = [{"name": "All Exchanges", "value": ""}]
        output.extend([
            {"name": row["exchange_name"], "value": row["exchange"]}
            for row in exchanges
        ])
        return output

    @property
    def trading_session(self) -> dict:
        """Get the trading session details."""
        if self._trading_session is not None:
            return self._trading_session
        self._trading_session = {
            "timezone": "America/Chicago",
            "session": "1700F1-1600:23456",
        }
        return self._trading_session

    @trading_session.setter
    def trading_session(self, value: dict) -> None:
        """Set the trading session details."""
        self._trading_session = value

    @property
    def continuous_assets(self) -> DataFrame:
        """Get all unique symbols."""
        if not hasattr(self, "_continuous_assets") or self._continuous_assets.empty:
            db = self.database()
            ohlcv_tables = [table for table in db.table_names if table.startswith("ohlcv_")]

            if not ohlcv_tables:
                return DataFrame()

            output = DataFrame()

            for table in ohlcv_tables:
                query = f"""
                SELECT DISTINCT symbol,
                    asset, name, exchange, exchange_name, asset_class,
                    currency, min_price_increment, contract_unit, contract_unit_multiplier
                FROM {table}
                ORDER BY date DESC;
                """
                df = db.safe_read_sql(query)

                if not df.empty:
                    output = concat([output, df])

                output = concat([output, db.safe_read_sql(query)]).drop_duplicates()

            self._continuous_assets = output.reset_index(drop=True)

        return self._continuous_assets

    def get_ohlcv_data(self, symbol: str, interval: str) -> DataFrame:
        """Get OHLCV data from the database for a given symbol and interval."""
        interval_str = (
            "1d" if interval[-1] in ["D", "W", "M"]
            else "1h" if interval in ("60", 60)
            else f"{interval}"
        )
        table_name = f"ohlcv_{interval_str.lower()}_continuous"

        if table_name not in self.database().table_names:
            self.database().logger.error("Table %s does not exist in the database.", table_name)
            return DataFrame()

        query = f"""
        SELECT *
        FROM {table_name}
        WHERE symbol = ?
        ORDER BY date;
        """
        return self.database().safe_read_sql(query, params=(symbol,))

    def get_symbol_info(self, symbol: str, interval: Optional[str] = None) -> dict:
        """Get symbol information from the database."""
        # Create cache key
        symbol = symbol.replace(".C.", ".c.")
        cache_key = f"{symbol}_{interval or '1d'}"

        if cache_key in self._symbol_info_cache:
            return self._symbol_info_cache[cache_key]

        interval_str = (
            "1d" if interval and interval[-1] in ["D", "W", "M"] else f"{interval or '1d'}"
        )
        table_name = f"ohlcv_{interval_str.lower()}_continuous"

        if table_name not in self.database().table_names:
            self.database().logger.error("Table %s does not exist in the database.", table_name)
            return {}

        query = f"""
        SELECT 
            symbol, asset, asset_class, exchange,
            exchange_name, contract_unit, contract_unit_multiplier,
            min_price_increment, name, currency
        FROM {table_name}
        WHERE symbol = ?
        ORDER BY date DESC
        LIMIT 1;
        """
        symbol_info = (self.database().fetchone(query, params=(symbol,)))

        if not symbol_info:
            return {"s": "no_data"}
        symbol = symbol.replace(".c.", ".C.")
        udf_symbol_info: dict = {
            "symbol": symbol,
            "ticker": symbol,
        }
        udf_symbol_info.update(self.trading_session)
        udf_symbol_info.update(self.compute_pricescacle(symbol_info["min_price_increment"]))

        asset_type = "commodity" if symbol_info["asset_class"] in [
            "Commodity/Agriculture",
            "Energy",
            "Metals",
        ] else "currency" if symbol_info["asset_class"] == "Currency" else "futures"

        udf_symbol_info["type"] = asset_type
        udf_symbol_info["exchange"] = symbol_info["exchange"]
        udf_symbol_info["listed_exchange"] = symbol_info["exchange"]

        udf_symbol_info["name"] = symbol
        multiplier = symbol_info.get("contract_unit_multiplier")
        unit = symbol_info["contract_unit"] + (
            f" x {multiplier}"  # Add multiplier if not 1
            if multiplier and multiplier != 1
            else ""
        )
        udf_symbol_info["description"] = symbol_info["name"] + " - " + unit
        map_of_measure = {v: k for k, v in unit_of_measure_map.items()}
        udf_symbol_info["unit_id"] = (
            map_of_measure.get(symbol_info["contract_unit"], symbol_info["contract_unit"])
        )
        symbol_has_intraday = False
        seconds_multipliers: list = []
        has_seconds = False
        supported_resolutions: list = []

        if self.has_intraday:
            table_names = self.database().table_names
            for table in table_names:
                if table.startswith("ohlcv_") and table.endswith("_continuous"):
                    # e.g., "1m", "30s", "1h"
                    interval_part = table.split("_")[1]
                    # Check if this symbol exists in this table
                    query = f"""
                    SELECT DISTINCT symbol
                    FROM {table}
                    WHERE symbol = ?
                    LIMIT 1;
                    """
                    if interval_part.endswith("s"):
                        has_seconds = True
                        multiplier = int(interval_part[:-1])
                        if multiplier not in seconds_multipliers:
                            seconds_multipliers.append(multiplier)
                        symbol_has_intraday = True
                    # Handle minute intervals - convert to string for supported_resolutions
                    elif interval_part.endswith("m"):
                        multiplier = int(interval_part[:-1])
                        resolution = str(multiplier)
                        if resolution not in supported_resolutions:
                            supported_resolutions.append(resolution)
                        symbol_has_intraday = True
                    # Handle hour intervals - convert to minutes for supported_resolutions
                    elif interval_part.endswith("h"):
                        multiplier = int(interval_part[:-1])
                        minutes = multiplier * 60
                        resolution = str(minutes)
                        if resolution not in supported_resolutions:
                            supported_resolutions.append(resolution)
                        symbol_has_intraday = True

            if has_seconds is True:
                udf_symbol_info["has_seconds"] = True
                udf_symbol_info["seconds_multipliers"] = sorted(
                    [str(m) for m in seconds_multipliers]
                )

            if symbol_has_intraday is True:
                udf_symbol_info["has_intraday"] = True

        # Add daily resolution if it exists
        if "ohlcv_1d_continuous" in table_names:
            query = """
            SELECT DISTINCT symbol
            FROM ohlcv_1d_continuous
            WHERE symbol = ?
            LIMIT 1;
            """
            supported_resolutions.extend(["D", "W", "M"])
            udf_symbol_info["has_daily"] = True
            udf_symbol_info["has_weekly_and_monthly"] =  True

        udf_symbol_info["has_intraday"] = symbol_has_intraday


        # Sort numeric resolutions and append 'D', 'W', 'M' at the end in order
        numeric_resolutions = sorted([r for r in supported_resolutions if r.isdigit()], key=int)
        period_resolutions = [r for r in ["D", "W", "M"] if r in supported_resolutions]
        udf_symbol_info["supported_resolutions"] = numeric_resolutions + period_resolutions
        udf_symbol_info["volume_precision"] = 1
        udf_symbol_info["currency_code"] = symbol_info["currency"]
        udf_symbol_info["original_currency_code"] = (
            udf_symbol_info["unit_id"]
            if asset_type == "currency"
            else symbol_info["currency"]
        )

        point_value = symbol_info.get("min_price_increment")
        contract_multiplier = symbol_info.get("contract_unit_multiplier")
        if point_value and contract_multiplier:
            udf_symbol_info["point_value"] = str(
                Decimal(str(point_value)) * Decimal(str(contract_multiplier))
            )
        # Add to cache
        self._symbol_info_cache[cache_key] = udf_symbol_info

        return udf_symbol_info

    @staticmethod
    def compute_pricescacle(min_price_increment: float) -> dict:
        """
        Calculate pricescale and minmov for TradingView pricescale.
        
        Parameters
        ----------
        min_price_increment : float
            The minimum price increment (tick size) for the security
            
        Returns
        -------
        dict
            Dictionary containing pricescale, minmov, minmove2, and fractional settings
        """
        # Set high precision for calculations
        getcontext().prec = 50

        # Convert to Decimal for precise arithmetic
        tick_decimal = Decimal(str(min_price_increment))

        # Find the number of decimal places needed
        decimal_places = abs(tick_decimal.as_tuple().exponent)  # type: ignore

        # Calculate pricescale as 10^decimal_places
        pricescale = 10 ** decimal_places

        # Calculate minmov as tick_size * pricescale
        minmov = int(tick_decimal * pricescale)

        return {
            "pricescale": str(pricescale),
            "minmov": str(minmov),
        }


DatabaseDependency = Annotated[UdfDatabase, Depends(UdfDatabase)]
