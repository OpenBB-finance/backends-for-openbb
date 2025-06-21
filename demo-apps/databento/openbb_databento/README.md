![image](https://github.com/user-attachments/assets/0b460fda-2b12-44fd-a43b-b4b69db7ef1a)

## Databento Demonstration Application

This application is a demonstration integration of CME futures data, utilizing Databento's Python [client](https://github.com/databento/databento-python/tree/main).

The Workspace application consists of a TradingView Advanced Charting widget, asset term structures, and live trades. The instructions below demonstrate some basic usage patterns
to get started right away.


### Installation

Download the parent folder, `openbb-databento`, from the repository, then open a terminal shell and navigate into the folder.

Create a new Python environment between versions 3.10 and 3.12, inclusively.

Use your tool of choice to install - i.e, Poetry, pip, etc.

```sh
pip install -e .
```

### Authorization

A subscription to the CME Globex MDP 3.0 feed is required. Details of this dataset are found [here](https://databento.com/docs/venues-and-datasets/glbx-mdp3).

Add your Databento API key as an environment variable, `DATABENTO_API_KEY`, from the command line, or create/modify an `.env` file in `~/.openbb_platform/.env`.

The key can also be added to the "credentials" dictionary in, `~/.openbb_platform/user_settings.json`, with a key, `databento_api_key`.

### Database File

Set the location of this file with an environment variable, `CME_DB_FILE`.

If not set, the default location is: `$HOME/OpenBBUserdata/cme_database.db`

### Launching

**Note**: The database will need to be configured before launching for the application to have access to the data. See the Quickstart steps below.

The app is a FastAPI instance and is served via factory function, from:

```python
openbb_databento.app.main:get_app
```

You can also run using the shell command:

```sh
openbb-databento
```

### Quickstart

To get started with the least amount of thinking, follow these steps to setup.

Downloading a set of continuous futures symbols will take approximately thirty minutes to complete.

This process will capture a large amount of the offerings, around 275 assets, but will not represent the entirety of the collection.

Assuming the installation was already done, and the environment is active:

- Add your Databento API key, described above.
- Optionally, define the path and file to create for the SQLite3 database.
- Start a Python session

```python
from openbb_databento.utils.database import CmeDatabase

database = CmeDatabase()  # add `api_key=YOUR_KEY` if the environment variable is not set.

futures_symbols = database.generate_futures_symbols_db()

# WARNING: This will take several long minutes to complete.
ohlc = database.download_historical_continuous()

# Verify the tables are setup and exit the Python interpreter.
database.table_names
```

From the command line shell, launch the application:

```sh
openbb-databento
```

Open [Workspace](https://pro.openbb.co), and add the application with the URL of the running server.

The sections below expand on contents of this app, and how to use the code.


### Database File

After downloading from the Databento Historical client, data is stored in a SQLite database file.

Set the location of this file with an environment variable, `CME_DB_FILE`.

If not set, the default location is: `$HOME/OpenBBUserdata/cme_database.db`

Initialize and manage your database from a Python interpreter.

Follow the examples here to setup your database and get it ready for launch.


```python
from openbb_databento.utils.database import CmeDatabase  # The docstring for this class details available operations.

database = CmeDatabase() # Databento client will be authorized as described above, or pass your api_key and db_file here.
```

When it is initialized for the first time, it will download a mapping of Globex asset names from the CME quote vendor codes file.
This will be populated as the table, `asset_names`, and is used to map display names to metadata fetched from Databento.

```python
In [4]: database.table_names
Out[4]: ['asset_names']
```

You can interact directly with read/write sqlite3 connection objects by using the `database.read_connection` and `database.write_connection` properties.

Access any complete table by its name, using the function below. The response will be a pandas DataFrame.

```python
database.get_full_table("asset_names").iloc[-1]
```

| asset          | ZNC          |
|:---------------|:-------------|
| asset_class    | Futures      |
| name           | Zinc Futures |
| asset_category | Metals       |

### Metadata

To generate the full metadata table, run this command:

```python
symbols = database.generate_futures_symbols_db()
```

This will fetch all futures symbols from the Databento definitions schema and populate a table, `futures_symbols`.

This function can be run periodically to keep a current set of symbols. 

```python
Signature:
database.generate_futures_symbols_db(
    date: Optional[str] = None,
    replace: bool = True,
) -> pandas.core.frame.DataFrame
Docstring:
Generate a database of symbols from the CME Globex MDP 3.0 feed.

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
```

The output will look like this:

| raw_symbol          | ESH9                                    |
|:--------------------|:----------------------------------------|
| instrument_id       | 42002687                                |
| asset               | ES                                      |
| name                | E-mini S&P 500 Futures - 2029-03 Expiry |
| exchange            | XCME                                    |
| exchange_name       | Chicago Mercantile Exchange             |
| exchange_timezone   | America/Chicago                         |
| security_type       | Future                                  |
| asset_class         | Equity                                  |
| first_trade_date    | 2023-12-15                              |
| expiration          | 2029-03-16 08:30:00-0500                |
| currency            | USD                                     |
| min_price_increment | 0.25                                    |
| unit_of_measure     | Index Points                            |
| unit_of_measure_qty | 50.0                                    |
| source              | databento                               |
| as_of_date          | 2025-06-15 07:05:37-0500                |
| date                | 2025-06-15                              |

There will now be three tables:

- `asset_names`
- `futures_symbols`
- `asset_definitions`

The `assets_definitions` table is a reference lookup for symbols over time. Each parent asset will have an entry with child symbols grouped by date.

```python
database.get_full_table("asset_definitions").query("asset == 'RY'")
```

| date       | asset   |   instrument_id | raw_symbol   | first_trade_date   | expiration               |
|:-----------|:--------|----------------:|:-------------|:-------------------|:-------------------------|
| 2025-06-15 | RY      |        42001780 | RYM5         | 2023-12-18         | 2025-06-16 09:16:00-0500 |
| 2025-06-15 | RY      |        42011388 | RYU5         | 2024-03-18         | 2025-09-15 09:16:00-0500 |
| 2025-06-15 | RY      |        42445148 | RYZ5         | 2024-06-17         | 2025-12-15 09:16:00-0600 |
| 2025-06-15 | RY      |        42130915 | RYH6         | 2024-09-16         | 2026-03-16 09:16:00-0500 |
| 2025-06-15 | RY      |        42044970 | RYM6         | 2024-12-16         | 2026-06-15 09:16:00-0500 |
| 2025-06-15 | RY      |        42098670 | RYU6         | 2025-03-17         | 2026-09-14 09:16:00-0500 |
| 2025-06-15 | RY      |        42654390 | RYZ6         | 2025-06-16         | 2026-12-14 09:16:00-0600 |


This table is used and updated by the `database.get_term_structure` function.

### OHLCV Database and TradingView Charting

Historical candles are served from the database, which should be built ahead of time.

If no tables with OHLCV data can be found, the application will not load the UDF server and this feature will be disabled.

Populate a database from a Python interpreter:

```python
from openbb_databento.utils.database import CmeDatabase

database = CmeDatabase()

# Use the default settings to setup EOD data beginning 2013-01-01
data = database.download_historical_continuous()
```

The function accepts the following parameters:

```python
Signature:
database.download_historical_continuous(
    symbols: Optional[list[str]] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    interval: Optional[Literal['second', 'minute', 'hour', 'day']] = None,
    contract: Optional[int] = None,
    roll_rule: Optional[Literal['c', 'n', 'v']] = None,
) -> pandas.core.frame.DataFrame
Docstring:
Get historical continuous futures data.

Parameters
----------
symbols : Optional[list[str]]
    A list of asset symbols to download.
    If None, defaults to all assets in `openbb_databento.utils.constants.live grid_assets`.
    Assets should be an asset from the `futures_symbols` property's asset column.
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
```

The results are saved to a table, with each interval having its own. Table names will be assigned according to the interval, `ohlcv_1d_continuous`.

Data will look like this:

```python
query = "SELECT * from ohlcv_1d_continuous WHERE asset = 'ES'"
database.fetchone(query)

{
    'date': '2013-01-02',
    'instrument_id': 23970,
    'asset': 'ES',
    'asset_class': 'Equity',
    'exchange': 'XCME',
    'exchange_name': 'Chicago Mercantile Exchange',
    'contract_unit': 'Index Points',
    'contract_unit_multiplier': 50.0,
    'min_price_increment': 0.25,
    'name': 'E-mini S&P 500 Futures - 1st Contract',
    'currency': 'USD',
    'symbol': 'ES.c.0',
    'open': 1443.0,
    'high': 1458.0,
    'low': 1438.25,
    'close': 1454.25,
    'volume': 1945162
}
```

The UDF server will transform this data into the correct format and map metadata to the symbol search.

There is a wrapper class for handling database queries from the UDF server.

The symbol info fed to the UDF server will depend on the contents of the database.

If the symbol is found in tables, `ohlcv_1h_continuous` table, the supported resolutions will be added.


```python
from openbb_databento.utils.udf import UdfDatabase

udf_database = UdfDatabase()
udf_database.get_symbol_info("ES.c.0")

{
    'symbol': 'ES.C.0',
    'ticker': 'ES.C.0',
    'timezone': 'America/Chicago',
    'session': '1700F1-1600:23456',
    'pricescale': '100',
    'minmov': '25',
    'type': 'futures',
    'exchange': 'XCME',
    'listed_exchange': 'XCME',
    'name': 'ES.C.0',
    'description': 'E-mini S&P 500 Futures - 1st Contract - Index Points x 50.0',
    'unit_id': 'IPNT',
    'has_intraday': True,
    'has_daily': True,
    'has_weekly_and_monthly': True,
    'supported_resolutions': ['60', 'D', 'W', 'M'],
    'volume_precision': 1,
    'currency_code': 'USD',
    'original_currency_code': 'USD',
    'point_value': '12.500'
}
```


### Streaming Trades

Streaming tables in OpenBB Workspace require two endpoints, a GET request for populating the initial table and serving AI features,
and a WebSocket endpoint for feeding the updates.

The symbols available to the drop-down menus will vary based on how you use it.

The master connection subscribes to all symbols, and each widget has its own subscription list and connection to the application.

A startup event subscribes to all symbols in `live_grid_assets`.

You can work with it from a Python interpreter, as well as stream the master connection from an API endpoint.

```python
from openbb_databento.app.ws import ConnectionManager

connection_manager = ConnectionManager(
    cme_database = database,  # instance of the database from above
    connection_timeout=30.0,
    retry_delay=5.0,
    max_retries=3,
)
```

The symbols used can be configured using the `setter` function, `database.set_live_grid_assets`

This should be done before intializing the `ConnectionManager` above.

```python
Signature:
database.set_live_grid_assets(
    symbols: Optional[list] = None,
    n_contracts: Optional[int] = None,
    roll_rule: Optional[Literal['c', 'n', 'v']] = None,
) -> bool
Docstring:
Set the live grid assets DataFrame from the 'futures_symbols' table.

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
```

![image](https://github.com/user-attachments/assets/b5ad0f7e-1a89-42c2-821b-7ce809e81694)


