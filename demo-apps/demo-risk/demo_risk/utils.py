import re
from io import BytesIO
from functools import lru_cache
import zipfile

import statsmodels.api as sm
from openbb_core.provider.utils.helpers import get_requests_session
from demo_risk.constants import (
    BASE_URL,
    URL_MAP,
)
from pandas import DataFrame, to_datetime

FactorsDoc = """

Source
------

https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html

All returns are in U.S. dollars, include dividends and capital gains, and are not continuously compounded.

Market is the return on a region's value-weight market portfolio minus the U.S. one month T-bill rate.

The Fama/French 5 factors (2x3) are constructed using the 6 value-weight portfolios formed on size and book-to-market, the 6 value-weight portfolios formed on size and operating profitability, and the 6 value-weight portfolios formed on size and investment.

To construct the SMB, HML, RMW, and CMA factors, we sort stocks in a region into two market cap and three respective book-to-market equity (B/M), operating profitability (OP), and investment (INV) groups at the end of each June.

Big stocks are those in the top 90% of June market cap for the region, and small stocks are those in the bottom 10%. The B/M, OP, and INV breakpoints for a region are the 30th and 70th percentiles of respective ratios for the big stocks of the region.

Rm–Rf for July of year t to June of t+1 include all stocks for which we have market equity data for June of t. SMB, HML, RMW, and CMA for July of year t to June of t+1 include all stocks for which we have market equity data for December of t-1 and June of t, (positive) book equity data for t-1 (for SMB, HML, and RMW), non-missing revenues and at least one of the following: cost of goods sold, selling, general and administrative expenses, or interest expense for t-1 (for SMB and RMW), and total assets data for t-2 and t-1 (for SMB and CMA).

The momentum and short term reversal portfolios are reconstituted monthly and the other research portfolios are reconstituted annually. We reconstruct the full history of returns each month when we update the portfolios.

Size and Book-to-Market Portfolios
----------------------------------

- Small Value
- Small Neutral
- Small Growth
- Big Value
- Big Neutral
- Big Growth

BE < 0; bottom 30%, middle 40%, top 30%; quintiles; deciles.
Firms with negative book equity are in only the BE < 0 portfolio.

Size and Operating Profitability Portfolios
-------------------------------------------

- Small Robust
- Small Neutral
- Small Weak
- Big Robust
- Big Neutral
- Big Weak

Operating Profitability bottom 30%, middle 40%, top 30%; quintiles; deciles.

Size and Investment Portfolios
------------------------------

- Small Conservative
- Small Neutral
- Small Aggressive
- Big Conservative
- Big Neutral
- Big Aggressive

ME < 0 (not used); bottom 30%, middle 40%, top 30%; quintiles; deciles.
Investment bottom 30%, middle 40%, top 30%; quintiles; deciles.


Factors
-------

SMB: Small Minus Big

SMB (Small Minus Big) is the average return on the nine small stock portfolios minus the average return on the nine big stock portfolios

HML: High Minus Low

HML (High Minus Low) is the average return on the two value portfolios minus the average return on the two growth portfolios

RMW: Robust Minus Weak
RMW (Robust Minus Weak) is the average return on the two robust operating profitability portfolios minus the average return on the two weak operating profitability portfolio

CMA: Conservative Minus Aggressive

CMA (Conservative Minus Aggressive) is the average return on the two conservative investment portfolios minus the average return on the two aggressive investment portfolios

Definitions
-----------

ME : Market Equity

Market equity (size) is price times shares outstanding. Price and shares outstanding are from CRSP.

BE : Book Equity

Book equity is constructed from Compustat data or collected from the Moody’s Industrial, Financial, and Utilities manuals. BE is the book value of stockholders’ equity, plus balance sheet deferred taxes and investment tax credit (if available), minus the book value of preferred stock. Depending on availability, we use the redemption, liquidation, or par value (in that order) to estimate the book value of preferred stock. Stockholders’ equity is the value reported by Moody’s or Compustat, if it is available. If not, we measure stockholders’ equity as the book value of common equity plus the par value of preferred stock, or the book value of assets minus total liabilities (in that order). See Davis, Fama, and French, 2000, “Characteristics, Covariances, and Average Returns: 1929-1997,” Journal of Finance, for more details.

BE/ME : Book-to-Market

The book-to-market ratio used to form portfolios in June of year t is book equity for the fiscal year ending in calendar year t-1, divided by market equity at the end of December of t-1.

OP : Operating Profitability

The operating profitability ratio used to form portfolios in June of year t is annual revenues minus cost of goods sold, interest expense, and selling, general, and administrative expense divided by the sum of book equity and minority interest for the last fiscal year ending in t-1.

INV : Investment

The investment ratio used to form portfolios in June of year t is the change in total assets from the fiscal year ending in year t-2 to the fiscal year ending in t-1, divided by t-2 total assets.

E/P : Earnings/Price

Earnings is total earnings before extraordinary items, from Compustat. The earnings/price ratio used to form portfolios in June of year t is earnings for the fiscal year ending in calendar year t-1, divided by market equity at the end of December of t-1.

CF/P : Cashflow/Price

Cashflow is total earnings before extraordinary items, plus equity’s share of depreciation, plus deferred taxes (if available), from Compustat. Equity’s share is defined as market equity divided by assets minus book equity plus market equity. The cashflow/price ratio used to form portfolios in June of year t is the cashflow for the fiscal year ending in calendar year t-1, divided by market equity at the end of December of t-1.

D/P : Dividend Yield

The dividend yield used to form portfolios in June of year t is the total dividends paid from July of t-1 to June of t per dollar of equity in June of t. The dividend yield is computed using the with and without dividend returns from CRSP, as described in Fama and French, 1988, “Dividend yields and expected stock returns,” Journal of Financial Economics 25.
"""


async def perform_ols(data, y: str, factors: list, **kwargs):
    """Perform Ordinary Least Squares regression."""
    data = DataFrame(data)

    if "Date" in data.columns:
        data = data.set_index("Date")

    X = sm.add_constant(data[factors])

    Y = data[y]

    model = sm.OLS(Y, X).fit()

    factors = model.params.index
    df = DataFrame(index=factors)
    df.loc[:, "coefficient"] = model.params.values
    confidence_intervals = model.conf_int().rename(
        columns={0: "lower_ci", 1: "upper_ci"}
    )
    pvalues = model.pvalues
    df.loc[:, "p_value"] = pvalues
    df = df.join(confidence_intervals)

    return df


@lru_cache
def download_file(dataset):
    if dataset not in list(URL_MAP):
        raise ValueError(
            f"Dataset {dataset} not found in available datasets: {list(URL_MAP)}"
        )
    url = BASE_URL + URL_MAP[dataset]
    with get_requests_session() as session:
        response = session.get(url)
        response.raise_for_status()

    data = ""
    with zipfile.ZipFile(BytesIO(response.content)) as f:
        data = f.open(f.namelist()[0]).read()
        try:
            data = data.decode("utf-8")
        except UnicodeDecodeError:
            data = data.decode("latin-1")

    return data


def apply_date(x):
    date = str(x).replace(" ", "")
    if len(date) == 6:
        date = date[:4] + "-" + date[4:]
        date = to_datetime(date, format="%Y-%m")
        date = date.date().strftime("%Y-%m-%d")
    elif len(date) == 8:
        date = date[:4] + "-" + date[4:6] + "-" + date[6:]
    elif len(date) == 4:
        date = date + "-12-31"
    return date


def read_csv_file(data: str):
    """Parse the raw data from a .csv file into a list of dictionaries representing tables."""
    lines = data.splitlines()
    tables = []
    general_description = []

    # Extract general description from the top of the file
    description_end_idx = 0
    for idx, line in enumerate(lines):
        if line.strip().startswith(",") or re.match(r"^\s*\d{4,6}", line):
            description_end_idx = idx
            break
        if line.strip():
            general_description.append(line.strip())

    # Extract initial table metadata from the last line of general description
    table_metadata = ""
    if general_description:
        if (
            "Monthly" in general_description[-1]
            or "Annual" in general_description[-1]
            or "Returns" in general_description[-1]
        ):
            table_metadata = general_description[-1]
            general_description = general_description[:-1]

    general_desc_text = "\n".join(general_description)

    # Process tables in the file
    i = description_end_idx

    while i < len(lines):
        # Skip empty lines
        while i < len(lines) and not lines[i].strip():
            i += 1

        if i >= len(lines):
            break

        # Check if this is a table header (starts with comma)
        if lines[i].strip().startswith(","):
            # Look for metadata line before this header
            metadata = table_metadata  # Default to initial metadata
            j = i - 1
            while j >= description_end_idx:
                if lines[j].strip():
                    metadata = lines[j].strip()
                    break
                j -= 1

            # Parse headers
            header_line = lines[i].strip()
            headers = ["Date"] + header_line.split(",")[1:]

            # Move past header row
            i += 1

            # Collect data rows
            data_rows = []

            # Look for data rows until we hit the next header or end of file
            while i < len(lines):
                line = lines[i].strip()
                if not line:
                    break
                values = line.split(",")
                if values:
                    data_rows.append([d.strip() for d in values])

                i += 1

            # Add table if it has data
            if data_rows:
                tables.append(
                    {
                        "meta": metadata,
                        "headers": headers,
                        "rows": data_rows,
                        "is_annual": "Annual" in metadata,
                    }
                )

        # Check for standalone metadata
        elif "--" in lines[i] and any(
            d in lines[i] for d in ["Daily", "Monthly", "Annual", "Weekly"]
        ):
            # Update metadata for next table
            table_metadata = lines[i].strip()
            i += 1
        else:
            # Skip other lines
            i += 1

    return tables, general_desc_text


def process_csv_tables(tables, general_description=""):
    """Convert parsed table dictionaries from CSV files to pandas DataFrames."""
    dataframes = []
    metadata = []

    for table_idx, table in enumerate(tables):
        # Skip empty tables
        if not table["rows"]:
            continue

        # Create DataFrame from rows
        rows_data = table.get("rows", [])
        headers = table["headers"]

        # Check if we have enough headers
        max_cols = max(len(row) for row in rows_data)
        if len(headers) < max_cols:
            headers.extend([f"Column_{i}" for i in range(len(headers), max_cols)])

        # Create dataframe with proper dimensions and headers
        df = DataFrame(rows_data)

        if df.empty or df.shape[1] == 0:
            continue

        # Set column names
        df.columns = headers[: df.shape[1]]

        # Convert Date column to datetime
        try:
            # Convert YYYYMM format to datetime
            df["Date"] = df.Date.apply(apply_date)
        except Exception as e:
            print(f"Error parsing dates: {e}")
            df["Date"] = df["Date"].astype(str)

        # Set Date as index
        df = df.set_index("Date")
        df = df.sort_index()
        dataframes.append(df)

        # Get metadata from the table
        table_meta_desc = table["meta"].strip()

        # Determine frequency from the table's metadata
        frequency = "monthly"
        if "Annual" in table_meta_desc:
            frequency = "annual"

        # Create metadata entry
        table_meta = {
            "description": f"### {table_meta_desc}\n\n"
            + general_description.replace("\n", " ")
            + "\n\n",
            "frequency": frequency,
            "formations": headers[1:],
        }
        metadata.append(table_meta)

    return dataframes, metadata


def get_portfolio_data(
    dataset: str, frequency: str = None, measure: str = None
) -> tuple:
    """Get the portfolio data for a given dataset."""
    from demo_risk.depends import get_store

    store = get_store()

    if frequency and frequency.lower() not in ["monthly", "annual", "daily"]:
        raise ValueError(
            f"Frequency {frequency} not supported. Choose from 'monthly', 'annual', or 'daily'."
        )
    if measure and measure not in ["value", "equal", "number_of_firms", "firm_size"]:
        raise ValueError(
            f"Measure {measure} not supported. Choose from 'value', 'equal', 'number_of_firms', or 'firm_size'."
        )
    if measure in ["number_of_firms", "firm_size"] and frequency == "annual":
        raise ValueError(
            f"Measure '{measure}' is only available for monthly frequency."
        )
    if "Factor" in dataset:
        measure = None

    if dataset in store.list_stores:
        stored = store.get_store(dataset)
        dfs = stored["data"]
        metadata = stored["metadata"]
    else:
        file = download_file(dataset)
        table, desc = read_csv_file(file)
        dfs, metadata = process_csv_tables(table, desc)

        store.add_store(
            dataset,
            {"dataset": dataset, "data": dfs, "metadata": metadata},
        )

    if frequency:
        out_dfs = [
            df
            for df, meta in zip(dfs, metadata)
            if meta["frequency"].lower() == frequency.lower()
        ]
        out_metadata = [
            meta for meta in metadata if meta["frequency"].lower() == frequency.lower()
        ]
    else:
        out_dfs = dfs
        out_metadata = metadata

    if measure is not None:
        if measure in ["value", "equal"]:
            out_dfs = [
                df
                for df, meta in zip(out_dfs, out_metadata)
                if "--" in meta["description"]
                and measure.lower() in meta["description"].split(" -- ")[0].lower()
            ]
            out_metadata = [
                meta
                for meta in out_metadata
                if "--" in meta["description"]
                and measure.lower() in meta["description"].split(" -- ")[0].lower()
            ]
        elif measure == "number_of_firms":
            out_dfs = [
                df
                for df, meta in zip(out_dfs, out_metadata)
                if "Number of Firms" in meta["description"]
            ]
            out_metadata = [
                meta
                for meta in out_metadata
                if "Number of Firms" in meta["description"]
            ]
        elif measure == "firm_size":
            out_dfs = [
                df
                for df, meta in zip(out_dfs, out_metadata)
                if "Average Firm Size" in meta["description"]
            ]
            out_metadata = [
                meta
                for meta in out_metadata
                if "Average Firm Size" in meta["description"]
            ]

    return out_dfs, out_metadata
