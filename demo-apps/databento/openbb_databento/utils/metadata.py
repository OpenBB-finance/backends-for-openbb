"""CME Futures Metadata and Mappings"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pandas import DataFrame


def download_cme_assets() -> "DataFrame":  # pylint: disable=R0914
    """Download the CME asset directory mapping."""
    # pylint: disable=import-outside-toplevel
    from io import BytesIO  # noqa
    from openbb_core.provider.utils.helpers import make_request
    from pandas import ExcelFile, DataFrame, concat, read_excel

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

def check_asset_file_exists() -> str:
    """Check if the CME asset file exists."""
    # pylint: disable=import-outside-toplevel
    import os
    from pathlib import Path

    asset_file = (
        os.environ.get("CME_ASSETS_FILE")
        or Path(__file__).parent.parent / "assets" / "cme_asset_names.csv"
    )

    if not os.path.exists(asset_file):
        return ""
    return str(asset_file)

def load_cme_assets() -> "DataFrame":
    """Load the CME assets from the file."""
    # pylint: disable=import-outside-toplevel
    import logging
    import os
    from pathlib import Path
    from pandas import read_csv

    logger = logging.getLogger("uvicorn.error")

    asset_file = check_asset_file_exists()
    if not asset_file:
        logger.error("CME asset file not found, downloading it now.")
        assets = download_cme_assets()
        asset_file = (
            os.environ.get("CME_ASSETS_FILE")
            or Path(__file__).parent.parent / "assets" / "cme_asset_names.csv"
        )
        assets.to_csv(asset_file, index=False)

        return assets

    return read_csv(asset_file)
