import json
from pathlib import Path

import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from openbb_core.api.rest_api import app
from openbb_platform_api.response_models import PdfResponseModel
from demo_earningsprep.app.depends import (
    PdfStore,
    PriceStore,
    TranscriptsStore,
)
from demo_earningsprep.app.models import (
    DeliveriesData,
    MarketsEqData,
    PriceActionData,
    PriceTargetsData,
    ProductionData,
    Symbols,
)


# Read the csv data and return it as a table to your widget
def read_csv_data(csv_file_path: str):
    """Read the csv data and return it as a table to your widget

    Args:
        csv_file_path (str): Path to the CSV file relative to ROOT_PATH
    """
    try:
        appfolder_path = Path(__file__).parent.parent.resolve()
        return pd.read_csv((appfolder_path / csv_file_path).open()).to_dict(
            orient="records"
        )
    except Exception as e:
        error_message = f"Error reading the CSV file: {str(e)}"
        return JSONResponse(content={"error": error_message}, status_code=500)


# Visible Alpha Production Data
@app.get(
    "/production",
    openapi_extra={
        "widget_config": {
            "name": "Quarterly Production Forecasts",
            "refetchInterval": False,
        }
    },
)
async def production() -> list[ProductionData]:
    """Visible Alpha quarterly production estimates."""
    try:
        return read_csv_data("data/production.csv")
    except Exception as e:
        error_message = f"Error reading the CSV file: {str(e)}"
        return JSONResponse(content={"error": error_message}, status_code=500)


# Visible Alpha Deliveries Data
@app.get(
    "/deliveries",
    openapi_extra={
        "widget_config": {
            "name": "Quarterly Deliveries Forecasts",
            "refetchInterval": False,
        }
    },
)
async def deliveries() -> list[DeliveriesData]:
    """Visible Alpha quarterly deliveries estimates."""
    try:
        return read_csv_data("data/deliveries.csv")
    except Exception as e:
        error_message = f"Error reading the CSV file: {str(e)}"
        return JSONResponse(content={"error": error_message}, status_code=500)


@app.get(
    "/markets_eq_audio_analysis",
    openapi_extra={
        "widget_config": {"name": "MarketsEQ Audio Analysis", "refetchInterval": False}
    },
)
async def markets_eq_audio_analysis() -> list[MarketsEqData]:
    """MarketsEQ audio analysis of the earnings transcript."""
    try:
        file_path = Path(__file__).parent.parent / "data" / "marketseq.csv"
        df = pd.read_csv(file_path)
        return JSONResponse(
            content=df.replace({np.nan: None}).to_dict(orient="records")
        )
    except FileNotFoundError as e:
        print(f"File not found error: {e}")
        raise HTTPException(
            status_code=404, detail=f"final_widget.csv not found at {file_path}"
        )
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/markets_eq_research_report",
    openapi_extra={
        "widget_config": {
            "name": "MarketsEQ Research Report",
            "refetchInterval": False,
        }
    },
)
async def markets_eq_research_report(store: PdfStore) -> PdfResponseModel:
    """MarketsEQ research report of the earnings transcript."""
    content = store.get_store("markets_eq").get("BA")
    if content is None:
        raise HTTPException(
            status_code=400, detail="No MarketsEQ research report found."
        )
    return {
        "content": content,
        "filename": "markets_eq_research_report.pdf",
    }


@app.get(
    "/eight_k",
    openapi_extra={"widget_config": {"name": "8-K", "refetchInterval": False}},
)
async def get_eight_k(
    store: PdfStore,
    symbol: Symbols = "BA",
) -> PdfResponseModel:
    """Display the earnings announcement release for the given company."""
    content = store.get_store("earnings").get(symbol)
    if content is None:
        raise HTTPException(status_code=400, detail="No earnings announcements found.")
    return {
        "content": content,
        "filename": f"{symbol}-earnings-announcement.pdf",
    }


@app.get(
    "/price_action",
    openapi_extra={
        "widget_config": {
            "name": "Earnings Call Price Action",
            "refetchInterval": False,
        }
    },
)
async def get_price_action(
    store: PriceStore,
    symbol: Symbols = "BA",
) -> list[PriceActionData]:
    """One-minute resolution market prices +/- one-day of the conference call."""
    content = store.get_store(symbol)

    if content is None:
        raise HTTPException(status_code=400, detail="No price action found.")
    content = content.reset_index()
    content.date = content.date.dt.strftime("%Y-%m-%d %H:%M:%S%z")
    records = json.loads(content.to_json(orient="records"))

    return records


@app.get(
    "/investor_presentations",
    openapi_extra={"widget_config": {"refetchInterval": False}},
)
async def get_investor_presentations(
    store: PdfStore,
    symbol: Symbols = "BA",
) -> PdfResponseModel:
    """Get the latest investors' presentation for the given company."""
    content = store.get_store("presentations").get(symbol)
    if content is None:
        raise HTTPException(status_code=400, detail="No investor presentations found.")
    return {
        "content": content,
        "filename": f"{symbol}-investor-presentation.pdf",
    }


@app.get(
    "/transcripts",
    openapi_extra={
        "widget_config": {"name": "Earnings Call Transcript", "refetchInterval": False}
    },
)
async def transcripts(
    store: TranscriptsStore,
    symbol: Symbols = "BA",
) -> str:
    """Open the earnings call transcript."""
    transcript = store.get_store(symbol)
    if not transcript:
        raise HTTPException(status_code=400, detail="No transcripts found.")

    output_lines = []
    for line in transcript.splitlines():
        section_title = line.split(":", 1)[0] if ":" in line else ""
        section_line = line.split(":", 1)[1] if ":" in line else ""
        if section_title and section_line:
            output_lines.append(f"### **{section_title.strip()}**:" + "\n\n")
            output_lines.append(section_line.strip() + "\n\n")
        else:
            output_lines.append(line)

    return "\n".join(output_lines)


@app.get(
    "/price_targets",
    openapi_extra={
        "widget_config": {
            "name": "Analysts' Price Targets",
            "refetchInterval": False,
        }
    },
)
async def get_price_targets(symbol: Symbols = "BA") -> list[PriceTargetsData]:
    """Get the analysts' price targets for the given company."""
    try:
        appfolder_path = Path(__file__).parent.parent.resolve()
        df = pd.read_csv(
            (appfolder_path / "data" / f"{symbol.lower()}_pt_by_analyst.csv").open()
        )
        return df.replace({np.nan: None}).to_dict(orient="records")
    except Exception as e:
        error_message = f"Error reading the CSV file: {str(e)}"
        return JSONResponse(content={"error": error_message}, status_code=500)


@app.get(
    "/widgets.json",
    include_in_schema=False,
)
async def get_widgets_json() -> JSONResponse:
    """Return the widgets.json file."""
    appfolder_path = Path(__file__).parent.resolve()
    widgets_file = appfolder_path / "widgets.json"

    if not widgets_file.exists():
        raise HTTPException(status_code=404, detail="widgets.json not found.")

    with open(widgets_file, encoding="utf-8") as file:
        widgets_data = json.load(file)

    return JSONResponse(content=widgets_data)


@app.get(
    "/apps.json",
    include_in_schema=False,
)
async def get_apps_json() -> JSONResponse:
    """Return the workspace_apps.json file."""
    appfolder_path = Path(__file__).parent.resolve()
    apps_file = appfolder_path / "workspace_apps.json"
    if not apps_file.exists():
        raise HTTPException(status_code=404, detail="workspace_apps.json not found.")

    with open(apps_file, encoding="utf-8") as file:
        apps_data = json.load(file)

    return JSONResponse(content=apps_data)


def main():
    """Run the application"""
    import uvicorn

    uvicorn.run(
        "demo_earningsprep.app.main:app",
        host="0.0.0.0",
        port=8055,
        reload=True,
    )


if __name__ == "__main__":
    main()
