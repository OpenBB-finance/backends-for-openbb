"""Term Structures Router."""
# pylint: disable=R0911,W0612
# flake8: noqa: F841

from typing import Optional
from fastapi import APIRouter
from fastapi.exceptions import HTTPException

from openbb_databento.utils.udf import DatabaseDependency

router = APIRouter(prefix="/term_structures")


@router.get("/get_choices", openapi_extra={"widget_config": {"exclude": True}})
async def get_choices(udf_database: DatabaseDependency, asset_type: str = "") -> list:
    """Get the list of available term structures."""
    live_grid_assets = udf_database.database().live_grid_assets.asset.unique().tolist()
    assets = udf_database.database().asset_names.query(
        "asset in @live_grid_assets"
    )
    asset_map = assets.set_index("asset")["name"].to_dict()
    try:
        if asset_type == "equity":
            equity_assets = assets.query(
                "asset_category == 'Equities'"
            ).asset.unique().tolist()
            return [
                {
                    "label": asset_map.get(d, "").split(" - ")[0],
                    "value": d,
                    "extraInfo": {"description": d}
                }
                for d in equity_assets
            ]

        if asset_type == "currency":
            fx_assets = assets.query(
                "asset_category == 'FX'"
            ).asset.unique().tolist()
            return [
                {
                    "label": asset_map.get(d, "").split(" - ")[0],
                    "value": d,
                    "extraInfo": {"description": d}
                }
                for d in fx_assets
            ]


        if asset_type == "interest_rates":
            ir_assets = assets.query(
                "asset_category == 'Interest Rates'"
            ).asset.unique().tolist()
            return [
                {
                    "label": asset_map.get(d, "").split(" - ")[0],
                    "value": d,
                    "extraInfo": {"description": d}
                }
                for d in ir_assets
            ]


        if asset_type == "metals":
            metals_assets = assets.query(
                "asset_category == 'Metals' or asset == 'HR'"
            ).asset.unique().tolist()
            return [
                {
                    "label": asset_map.get(d, "").split(" - ")[0],
                    "value": d,
                    "extraInfo": {"description": d}
                }
                for d in metals_assets
            ]


        if asset_type == "agriculture-commodity":
            ag_assets = assets.query(
                "asset_category == 'Agriculture'"
            ).asset.unique().tolist()
            return [
                {
                    "label": asset_map.get(d, "").split(" - ")[0],
                    "value": d,
                    "extraInfo": {"description": d}
                }
                for d in ag_assets
            ]
        if asset_type == "energy":
            energy_assets = assets.query(
                "asset_category == 'Energy'"
            ).asset.unique().tolist()
            return [
                {
                    "label": asset_map.get(d, "").split(" - ")[0],
                    "value": d,
                    "extraInfo": {"description": d}
                }
                for d in energy_assets
            ]

        return [
            {
                "label": "Please select an asset type",
                "value": "",
            }
        ]

    except Exception as e:  # pylint: disable=broad-except
        udf_database.database().logger.error(
            "Error getting symbology map: %s",
            e,
            exc_info=True
        )
        return [{"label": f"Error: {e}", "value": ""}]




@router.get("/get_term_structure")
async def get_term_structure(
    udf_database: DatabaseDependency,
    asset: str,
    date: Optional[str] = None,
) -> list:
    """Get the term structure for a given symbol."""
    if asset not in udf_database.database().asset_names.asset.unique():
        raise ValueError(f"Invalid asset symbol: {asset}")

    data = udf_database.database().get_term_structure(asset, date)

    if data.empty:
        raise HTTPException(
            status_code=500,
            detail=(
                f"No term structure data found for symbol {asset} on date {date or 'latest'}"
                + " Try a different date or check the symbol spelling.",
            )
        )

    max_date = data.date.max()
    max_date = str(max_date)[:10]

    if date != max_date:
        udf_database.database().logger.warning(
            "Requested date %s does not match latest available date %s for asset %s",
            date if date is not None else "latest",
            max_date,
            asset,
        )

    return [
        {
            "as_of_date": str(row["date"]),
            "expiration": str(row["expiration"])[:10],
            "settlement_price": row["settlement_price"],
        }
        for _, row in data.iterrows()
    ]
