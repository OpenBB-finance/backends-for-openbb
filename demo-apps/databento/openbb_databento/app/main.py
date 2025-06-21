"""Main entry point for the OpenBB Databento FastAPI application and factory."""
import json
from pathlib import Path
import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from openbb_core.api.rest_api import app
from openbb_databento.app.term_structures import router as term_structures_router
from openbb_databento.app.udf import router as udf_router
from openbb_databento.app.ws import create_databento_manager

def get_app() -> FastAPI:
    """Main function to run the FastAPI app."""
    manager = create_databento_manager()
    table_names = manager.database.table_names
    start_udf = True

    if not any(
        table.startswith("ohlcv_") for table in table_names
    ):
        start_udf = False
        manager.database.logger.warning(
            "\n\nNo OHLCV tables found in the database. UDF server will not be started.\n\n"
        )
        _ = manager.database.set_live_grid_assets()

    app.include_router(manager.router, tags=["Live"])

    if start_udf:
        app.include_router(udf_router, tags=["UDF"])

    app.include_router(term_structures_router, tags=["Term Structures"])

    @app.get("/about")
    async def about():
        """About endpoint."""
        about_text = ""
        about_path = Path(__file__).parent.parent / "README.md"

        with open(about_path, encoding="utf-8") as f:
            about_text = f.read()

        return about_text

    @app.get("/widgets.json", include_in_schema=False)
    async def get_widgets_json():
        """Endpoint to serve the widgets configuration."""
        widgets: dict = {}
        config_path = Path(__file__).parent.parent / "widgets.json"

        if not config_path.exists():
            raise HTTPException(status_code=404, detail="widgets.json file could not be found.")

        with open(config_path, encoding="utf-8") as f:
            widgets = json.load(f)

        return widgets

    @app.get("/apps.json", include_in_schema=False)
    async def get_apps_json():
        """Endpoint to serve the apps configuration."""
        apps: list = []
        config_path = Path(__file__).parent.parent / "apps.json"

        if not config_path.exists():
            raise HTTPException(status_code=404, detail="apps.json file could not be found.")

        with open(config_path, encoding="utf-8") as f:
            apps = json.load(f)

        return apps

    return app


def main():
    """Main function to run the FastAPI app."""
    uvicorn.run(
        "openbb_databento.app.main:get_app",
        host="0.0.0.0",
        port=6940,
        factory=True,
    )

if __name__ == "__main__":
    main()
