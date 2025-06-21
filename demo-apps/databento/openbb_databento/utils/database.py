"""Database utilities for OpenBB DataBento (async and sync versions)."""
# pylint: disable=import-outside-toplevel,C0413,R0902,R0904,R0913,R0917
# flake8: noqa: E402
import logging
import os
import random
import sqlite3
import time
import warnings
from io import BytesIO
from typing import Any, Callable, Optional, Literal
from datetime import datetime, timedelta
import atexit
import databento as db
from pytz import timezone

warnings.filterwarnings("ignore", category=DeprecationWarning)
from openbb_core.env import Env
from openbb_core.app.service.user_service import UserService
from openbb_core.provider.utils.helpers import make_request
from pandas import Categorical, ExcelFile, DataFrame, concat, read_excel

from openbb_databento.utils.constants import live_grid_assets

from openbb_databento.utils.definition import (
    download_asset_symbols,
    create_futures_symbols_db
)
from openbb_databento.utils.historical import (
    fetch_historical_continuous,
    update_historical_continuous_table
)
from openbb_databento.utils.term_structure import download_term_structure

db_logger = logging.getLogger("openbb_databento.utils.database")
db_logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(levelname)s:     %(message)s')
handler.setFormatter(formatter)
db_logger.addHandler(handler)

def get_logger():
    """Get the logger instance."""
    return db_logger

def dict_factory(cursor: sqlite3.Cursor, row: tuple) -> dict[str, Any]:
    """Convert sqlite3 Row to a dictionary."""
    return dict(sqlite3.Row(cursor, row))


class CmeDatabase:
    """Synchronous SQLite database utility for managing read/write operations and connections.
    
    Initializes with a database path, allowing for read and write operations.

    This class is a singleton and all database connections will be closed on exit.

    A new instance of `databento.Historical` client is created with the `db_client` method.

    Set the `DATABENTO_API_KEY` environment variable to specify the API key,
    or provide it directly when initializing the class. The API key is passed
    to the `databento.Historical` client and is served by the db_client() method.

    Set the `CME_DB_FILE` environment variable to specify the database path,
    or provide it directly when initializing the class. If neither is provided,
    it defaults to a database file located in the `data` directory relative to this module.

    Properties
    ----------
    - asset_names: Returns a DataFrame containing CME asset names for mapping.
    - futures_symbols: Returns the contents of the `futures_symbols` table as a DataFrame.
    - live_grid_assets: Returns a DataFrame of live grid assets, subset `futures_symbols`.
    - read_connection: Returns the sqlite3 connection object for read operations.
    - write_connection: Returns the sqlite3 connection object for write operations.
    - table_names: Returns a list of all table names in the database.

    Methods
    -------
    - db_client: Returns a new instance of `databento.Historical` client.
    - download_cme_assets: Static method to download the CME asset directory mapping.
    - download_historical_continuous: Downloads OHLCV continuous futures data to database.
    - download_term_structure: Downloads term structure, open interest, and volume by asset.
    - check_for: Checks if a value exists in a specific column of a table, and optional condition.
    - close: Closes the database connections.
    - execute: Executes a write query in the write connection.
    - fetchall: Fetches all results from a read query.
    - fetchone: Fetches one result from a read query.
    - generate_futures_symbols_db: Generates or updates the `futures_symbols` table.
    - get_full_table: Returns the full table as a DataFrame.
    - get_table_schema: Returns the schema for a given table in the read connection.
    - safe_to_sql: Thread-safe wrapper for pandas to_sql operation.
    - safe_read_sql: Thread-safe wrapper for pandas read_sql operation.
    - set_live_grid_assets: Sets the live grid assets DataFrame from the 'futures_symbols' table.
    - update_historical_continuous: Updates the continuous futures table with latest data.

    Raises
    ------
    - ValueError: If the API key is not provided or set in the environment.
    - RuntimeError: If the database file cannot be found or created, wraps sqlite3 errors.
    """

    def __new__(cls, *args, **kwargs):
        """Ensure only one instance of CmeDatabase is created."""
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(  # pylint: disable=R0912,R0915
        self,
        db_file: Optional[str] = None,
        api_key: Optional[str] = None,
        row_factory: Optional[Callable[[sqlite3.Cursor, tuple], dict[str, Any]]] = None,
        logger: Optional[logging.Logger] = None
    ):
        """Initialize the CME database.
        
        Parameters
        ----------

        db_path : Optional[str]
            The path to the SQLite database file.
            Parameter overrides the `CME_DB_FILE` environment variable.
            If neither, defaults to a file in the OpenBBUserData folder.
        api_key : Optional[str]
            The API key for the Databento service.
            If not provided, it will look for the `DATABENTO_API_KEY` environment variable.
            If neither is provided, a ValueError is raised.
        row_factory : Optional[Callable[[sqlite3.Cursor, tuple], dict[str, Any]]]
            A callable to convert sqlite3 Row objects to dictionaries.
            Defaults to `dict_factory`, which converts rows to dictionaries.
        logger : Optional[logging.Logger]
            A custom logger instance to use for logging.
            If not provided, a default logger is created.
        """
        if hasattr(self, "_initialized") and self._initialized:
            return

        self.logger: logging.Logger = logger if logger is not None else get_logger()

        _ = Env()
        if api_key is None:
            credentials = UserService().read_from_file().credentials
            api_key = os.environ.get("DATABENTO_API_KEY") or getattr(
                credentials, "databento_api_key", None
            )

        if not api_key:
            raise ValueError(
                "Please set the DATABENTO_API_KEY environment variable"
                + " or provide it as an argument."
            )

        self._api_key = api_key

        if db_file is None:
            db_file = os.environ.get("CME_DB_FILE") or os.path.join(
                UserService().read_from_file().preferences.data_directory, "cme_database.db"
            )

        self.row_factory = row_factory or dict_factory
        self.db_path = "file://" + db_file if "://" not in db_file else db_file
        self._read_conn = sqlite3.connect(self.db_path, check_same_thread=False, uri=True)
        self._read_conn.row_factory = self.row_factory
        self._read_conn.execute("PRAGMA journal_mode=WAL;")
        self._read_conn.execute("PRAGMA busy_timeout=30000;")
        self._write_conn = sqlite3.connect(self.db_path, check_same_thread=False, uri=True)
        self._write_conn.row_factory = self.row_factory
        self._write_conn.execute("PRAGMA journal_mode=WAL;")
        self._write_conn.execute("PRAGMA synchronous=NORMAL;")
        self._write_conn.execute("PRAGMA busy_timeout=30000;")

        tables = self.table_names

        if "asset_names" in tables:
            try:
                query = "SELECT * FROM asset_names"
                assets = self.safe_read_sql(query)
            except sqlite3.OperationalError as exc:
                raise RuntimeError(
                    f"Failed to read the asset_names table from the database. -> {exc.args}"
                ) from exc
            except Exception as exc:
                raise RuntimeError(
                    f"Failed to read CME asset directory mapping -> {exc}"
                ) from exc
        else:
            try:
                assets = self.download_cme_assets()
                self.safe_to_sql(
                    assets,
                    "asset_names",
                    if_exists="replace",
                    index=False,
                    dtype={
                        "asset": "TEXT",
                        "asset_class": "TEXT",
                        "name": "TEXT",
                        "asset_category": "TEXT"
                    }
                )
            except sqlite3.OperationalError as exc:
                raise RuntimeError(
                    "Failed to create or update the asset_names table in the database."
                ) from exc
            except Exception as exc:
                raise RuntimeError(
                    "Failed to download CME asset directory mapping."
                ) from exc

        self._assets = assets
        self._live_grid_assets = DataFrame()
        self._futures_symbols = DataFrame()

        atexit.register(self.close)

        self._initialized = True

    def _retry_on_busy(self, func, max_retries=5) -> Any:
        """Retry database operations on busy/lock errors."""
        for attempt in range(max_retries):
            try:
                return func()
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e).lower() or "busy" in str(e).lower():
                    if attempt < max_retries - 1:
                        # Exponential backoff with jitter
                        delay = (2 ** attempt) + random.uniform(0, 1)
                        time.sleep(delay)
                        continue
                raise

    @staticmethod
    def download_cme_assets() -> DataFrame:  # pylint: disable=R0914
        """Download the CME asset directory mapping."""
        # pylint: disable=import-outside-toplevel
        assets = DataFrame()
        excel_file_url = "https://www.cmegroup.com/tools-information/files/quote-vendor-codes.xlsx"
        r = make_request(excel_file_url)
        r.raise_for_status()
        file = BytesIO(r.content)
        with ExcelFile(file) as excel_file:
            sheet_names = excel_file.sheet_names
            for sheet_name in sheet_names:
                sheet = read_excel(file, sheet_name=sheet_name)
                name, asset_type, symbol = (
                    sheet.iloc[1:, 0].str.strip(),
                    sheet.iloc[1:, 1].str.strip(),
                    sheet.iloc[1:, 2].str.strip()
                )
                df = DataFrame([symbol.values, asset_type.values, name.values]).T
                df.columns = ["asset", "asset_class", "name"]
                df.loc[:, "asset_category"] = sheet_name
                assets = concat([assets, df], axis=0)

        assets = (
            assets.reset_index(drop=True)
            .query("asset != '--' and asset_class.isin(['Futures', 'Options'])")
        )

        return assets

    @property
    def asset_names(self) -> DataFrame:
        """Return the CME asset names DataFrame."""
        return self._assets.copy()

    @property
    def live_grid_assets(self) -> DataFrame:
        """Return the CME live grid assets DataFrame."""
        if "futures_symbols" not in self.table_names:
            self.logger.info("'futures_symbols' table not found, generating it.")
            _ = self.generate_futures_symbols_db()

        if self._live_grid_assets.empty:
            _ = self.set_live_grid_assets()

        return self._live_grid_assets.copy()


    def set_live_grid_assets(
        self,
        symbols: Optional[list] = None,
        n_contracts: Optional[int] = None,
        roll_rule: Optional[Literal["c", "n", "v"]] = None
    ) -> bool:
        """Set the live grid assets DataFrame from the 'futures_symbols' table.
        
        Parameters
        ----------

        symbols : Optional[list]
            A list of asset symbols to filter the DataFrame.
            If None, defaults to the `live_grid_assets` constant.
        n_contracts : Optional[int]
            The number of contracts to keep for each asset.
            If None, defaults to 2 contracts per asset.
        roll_rule : Optional[str]
            The roll rule to apply when setting the live grid assets.
            Set as one of "c", "n", or "v" - calendar, open interest, or volume.
            If None, defaults to "c".

        Returns
        -------

        bool
            True if the DataFrame was successfully set, False otherwise.
        """
        if roll_rule is not None and roll_rule not in ["c", "n", "v"]:
            self.logger.error(
                "Invalid roll_rule '%s'. Must be one of 'c', 'n', or 'v'.", roll_rule
            )
            return False

        roll_rule = roll_rule or "c"

        try:
            symbols = symbols or live_grid_assets
            n_contracts = n_contracts or 2

            query = f"""
            SELECT * FROM futures_symbols
            WHERE asset IN ({",".join(f"'{asset}'" for asset in symbols)})
            """
            assets = self.safe_read_sql(query)
            now = datetime.now(timezone("America/Chicago"))
            assets = assets[assets["expiration"] > now.strftime("%Y-%m-%d %H:%M:%S%z")]
            assets = DataFrame(assets).sort_values(by=["asset", "expiration"])
            assets = assets.sort_values(by=["asset", "expiration"])
            assets.loc[:, "contract_position"] = assets.groupby("asset").cumcount()
            assets = assets[assets["contract_position"] < n_contracts]
            assets["continuous_symbol"] = (
                assets["asset"]
                + f".{roll_rule}."
                + assets["contract_position"].astype(str)
            )
            contract_names = {
                0: "1st Contract",
                1: "2nd Contract", 
                2: "3rd Contract",
                3: "4th Contract",
                4: "5th Contract",
                5: "6th Contract",
                6: "7th Contract",
                7: "8th Contract",
                8: "9th Contract",
                9: "10th Contract",
                10: "11th Contract",
                11: "12th Contract"
            }

            assets["name"] = assets.apply(
                lambda row: (
                    row["name"].split(" - ")[0] + " - "
                    + contract_names.get(
                        row["contract_position"],
                        f"{row['contract_position'] + 1}th Contract"
                    )
                ),
                axis=1
            )

            assets.asset_class = Categorical(
                assets.asset_class,
                categories=[
                    "Equity",
                    "Currency",
                    "Interest Rate",
                    "Energy",
                    "Metals",
                    "Commodity/Agriculture",
                    "Other"
                ],
                ordered=True,
            )

            self._live_grid_assets = (
                DataFrame(assets).sort_values(by=["asset_class", "asset", "contract_position"])
                .reset_index(drop=True)
            )
            return True
        except Exception as e:  # pylint: disable=W0718
            self.logger.error("Error setting live grid assets: %s", e)
            return False

    @property
    def futures_symbols(self) -> DataFrame:
        """Return the CME futures symbols DataFrame."""
        if "futures_symbols" not in self.table_names:
            self.logger.info("'futures_symbols' table not found, generating it.")
            df = self.generate_futures_symbols_db()
        if self._futures_symbols.empty:
            query = "SELECT * FROM futures_symbols"
            df = self.safe_read_sql(query)
            df.asset_class = Categorical(
                df.asset_class,
                categories=[
                    "Equity",
                    "Currency",
                    "Interest Rate",
                    "Energy",
                    "Metals",
                    "Commodity/Agriculture",
                    "Other"
                ],
                ordered=True,
            )
            df = df.sort_values(by=["asset_class", "name", "expiration"]).reset_index(drop=True)
        else:
            df = self._futures_symbols.copy()

        return df

    def close(self):
        """Close the database connections."""
        if self._read_conn:
            self._read_conn.close()
            self._read_conn = None
        if self._write_conn:
            self._write_conn.close()
            self._write_conn = None

    def fetchall(self, query: str, params: Optional[tuple] = None) -> list[dict[str, Any]]:
        """Fetch all results from a query in the read connection."""
        params_tuple = params or ()
        return self._read_conn.execute(query, params_tuple).fetchall() # type: ignore

    def fetchone(self, query: str, params: Optional[tuple] = None):
        """Fetch one result from a query in the read connection."""
        params_tuple = params or ()
        return self._read_conn.execute(query, params_tuple).fetchone() # type: ignore

    def execute(self, query: str, params: Optional[tuple] = None) -> dict[str, int]:
        """Execute a write query in the write connection."""
        def _execute():
            params_tuple = params or ()
            cur = self._write_conn.execute(query, params_tuple) # type: ignore
            self._write_conn.commit() # type: ignore
            return {
                "rowcount": cur.rowcount,
                "lastrowid": cur.lastrowid
            }
        return self._retry_on_busy(_execute)

    @property
    def table_names(self) -> list[str]:
        """Return a list of all table names in the database."""
        rows = self.fetchall("SELECT name FROM sqlite_master WHERE type='table';")
        return [row["name"] for row in rows]

    def get_table_schema(self, table_name: str) -> list[dict[str, Any]]:
        """Return a schema for the given table."""
        cur = self._read_conn.cursor()  # type: ignore
        cur.execute(f"PRAGMA table_info({table_name});")
        columns = cur.fetchall()
        return [
            {
            "cid": col[0],
            "name": col[1],
            "type": col[2],
            "nullable": not bool(col[3]),
            "default": col[4],
            "primary_key": bool(col[5]),
            }
            for col in columns
        ]

    def db_client(self) -> db.Historical:
        """Return the initialized databento.Historical client."""
        return db.Historical(self._api_key)

    @property
    def read_connection(self):
        """Return the read sqlite3 connection for use with pandas read_sql."""
        if self._read_conn is None:
            self._read_conn = sqlite3.connect(self.db_path, check_same_thread=False, uri=True)
            self._read_conn.row_factory = self.row_factory
            self._read_conn.execute("PRAGMA journal_mode=WAL;")
            self._read_conn.execute("PRAGMA busy_timeout=30000;")
        return self._read_conn

    @property
    def write_connection(self):
        """Return the write sqlite3 connection for use with pandas to_sql."""
        if self._write_conn is None:
            self._write_conn = sqlite3.connect(self.db_path, check_same_thread=False, uri=True)
            self._write_conn.row_factory = self.row_factory
            self._write_conn.execute("PRAGMA journal_mode=WAL;")
            self._write_conn.execute("PRAGMA synchronous=NORMAL;")
            self._write_conn.execute("PRAGMA busy_timeout=30000;")
        return self._write_conn

    def safe_to_sql(self, df, table_name, **kwargs):
        """Thread-safe pandas to_sql operation."""
        def _write():
            result = df.to_sql(table_name, self._write_conn, **kwargs)
            self._write_conn.commit()  # type: ignore
            return result

        return self._retry_on_busy(_write)

    def safe_read_sql(self, query, **kwargs) -> DataFrame:
        """Thread-safe pandas read_sql operation."""
        def _read():
            cursor = self._read_conn.execute(query, kwargs.get('params', ())) # type: ignore
            rows = cursor.fetchall()
            cursor.close()

            if not rows:
                return DataFrame()

            return DataFrame(rows)

        return self._retry_on_busy(_read)

    def check_for(
        self,
        table_name: str,
        column_name: str,
        value: Any,
    ) -> bool:
        """Check if a value exists in a specific column of a table.

        Parameters
        ----------
        table_name : str
            The name of the table to check.
        column_name : str
            The name of the column to check for the value.
        value : Any
            The value to check for in the specified column.
        Returns
        -------
        bool
        """
        query = f"SELECT EXISTS(SELECT 1 FROM {table_name} WHERE {column_name} = '{value}')"
        result = self.fetchone(query)

        return bool(list(result.values())[0]) if result else False

    def get_full_table(self, table_name: str) -> DataFrame:
        """Get the full table as a DataFrame."""
        table_names = self.table_names
        if table_name not in table_names:
            raise ValueError(
                f"Table '{table_name}' does not exist in the database."
                + f" Available tables: {table_names}"
            )
        query = f"SELECT * FROM {table_name}"

        return self.safe_read_sql(query)

    def generate_futures_symbols_db(
        self,
        date: Optional[str] = None,
        replace: bool = True,
    ) -> DataFrame:
        """Generate a database of symbols from the CME Globex MDP 3.0 feed.
        
        Parameters
        ----------
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
        return create_futures_symbols_db(
            cme_database=self,
            date=date,
            replace=replace,
        )

    def download_historical_continuous(
        self,
        symbols: Optional[list[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        interval: Optional[Literal["second", "minute", "hour", "day"]] = None,
        contract: Optional[int] = None,
        roll_rule: Optional[Literal["c", "n", "v"]] = None
    ) -> DataFrame:
        """Get historical continuous futures data.
        
        Use to bulk download many symbols by contract position - i.e, 0 is front month.

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
            If None, defaults to 'day'.
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
        return fetch_historical_continuous(
            cme_database=self,
            symbols=symbols,
            start_date=start_date,
            end_date=end_date,
            interval=interval,
            contract=contract,
            roll_rule=roll_rule
        )

    def update_historical_continuous(
        self,
        table_name: str,
    ) -> DataFrame:
        """Update the historical continuous futures data in the database.
        
        This function will update the `ohlcv_1{interval[0]}_continuous` table
        with the latest data from the Databento API.

        Parameters
        ----------
        table_name : str
            The name of the table to update.
            Should be in the format `ohlcv_1{interval[0]}_continuous`.

        Returns
        -------
        DataFrame
            A DataFrame containing the updated historical continuous futures data.
        
        Raises
        ------
        BentoError
            If there is an error with the Databento API request.
        """
        return update_historical_continuous_table(
            cme_database=self,
            table_name=table_name,
        )

    def get_asset_symbols(
        self,
        asset: str,
        date: Optional[str] = None,
        show_all: bool = False,
    ) -> DataFrame:
        """Download the asset symbols for a given asset.
        
        Works with the `asset_names` table to ensure the asset exists.
        
        Results are stored in the `asset_definitions` table, if they are not already present.

        The format of the table is suitable for mapping historical raw_symbol
        to the asset, instrument_id, and expiration date.

        Parameters
        ----------

        asset : str
            The asset for which to download the symbols.
            Asset should be an asset from the `futures_symbols` asset column.
        date : Optional[str]
            The date for which to download the symbols.
            Returns an empty DataFrame if the asset is not found for the specified date.
        show_all : bool
            If True, returns all symbols for the specified asset, regardless of date.

        Returns
        -------

        DataFrame
            A DataFrame containing the asset symbols for the specified asset.
        """
        if "asset_definitions" not in self.table_names or self.asset_names.empty:
            self.logger.error(
                "'asset_definitions' table not found. "
                + "Generate by running `generate_futures_symbols_db`."
            )
            return DataFrame()

        if asset not in self.asset_names.asset.tolist():
            self.logger.error(
                "Asset '%s' not found in the asset_names table. "
                + "Please check the asset_names property.",
                asset.upper()
            )
            return DataFrame()

        existing_assets = self.safe_read_sql(
            f"SELECT * FROM asset_definitions WHERE date = '{date}' OR asset = '{asset}'"
        )
        if date is None and not existing_assets.empty and show_all is True:
            existing_table = existing_assets.query("asset == @asset")
            if not existing_table.empty:
                return existing_table.sort_values(by=["date", "expiration"]).reset_index(drop=True)

        if date is None and existing_assets.empty:
            return download_asset_symbols(
                cme_database=self,
                asset=asset,
                date=date,
            )

        date = date or datetime.now(tz=timezone("America/Chicago")).strftime("%Y-%m-%d")

        asset_check = existing_assets.query("date == @date and asset == @asset")

        if not asset_check.empty:
            return asset_check.sort_values(by=["date", "expiration"]).reset_index(drop=True)

        return download_asset_symbols(
            cme_database=self,
            asset=asset,
            date=date,
        )

    def get_term_structure(
        self,
        asset: str,
        date: Optional[str] = None,
    ) -> DataFrame:
        """Download the term structure for a given asset.
        
        Parameters
        ----------

        asset : str
            The asset for which to download the term structure.
            Asset should be an asset from the `asset_names` asset column.
        date : Optional[str]
            The date for which to get the term structure.
            If None, defaults to today's date.

        Returns
        -------

        DataFrame
            A DataFrame containing the term structure data for the specified asset.
        """
        table_names = self.table_names
        if "asset_names" not in table_names:
            self.logger.error(
                "'asset_names' table not found. "
                + "Generate by running `download_cme_assets`."
            )
            return DataFrame()

        # Set default date to today if not provided
        target_date = datetime.strptime(date, "%Y-%m-%d") if date else datetime.now().today()
        target_date = (
            target_date
            if target_date.weekday() < 5
            else target_date - timedelta(days=target_date.weekday() - 4)
        ).strftime("%Y-%m-%d")


        # Check if term_structures table exists
        if "term_structures" not in table_names:
            return download_term_structure(
                cme_database=self,
                asset=asset,
                date=target_date,
            )

        # Check if data exists for this asset and date
        query = f"""
        SELECT * FROM term_structures
        WHERE asset = '{asset}' AND date = '{target_date}'
        """
        existing_ts = self.safe_read_sql(query)

        # If data exists for the target date, return it
        if not existing_ts.empty:
            return existing_ts.sort_values(by=["expiration"]).reset_index(drop=True)

        # Data doesn't exist for this date, download it
        results = download_term_structure(
            cme_database=self,
            asset=asset,
            date=target_date,
        )

        if not results.empty:
            return results.sort_values(by=["expiration"]).reset_index(drop=True)

        target_date = datetime.strptime(target_date, "%Y-%m-%d") - timedelta(days=1)
        target_date = target_date.strftime("%Y-%m-%d")

        self.logger.info(
            " Checking for the previous date for asset %s on date %s",
            asset,
            target_date
        )

        # Check if data exists for this asset and previous date
        query = f"""
        SELECT * FROM term_structures
        WHERE asset = '{asset}' AND date = '{target_date}'
        """
        existing_ts = self.safe_read_sql(query)

        if existing_ts.empty:
            return download_term_structure(
                cme_database=self,
                asset=asset,
                date=target_date,
            )

        return existing_ts
