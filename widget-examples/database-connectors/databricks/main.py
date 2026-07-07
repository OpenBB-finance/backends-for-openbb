import json
from pathlib import Path

from fastapi.responses import FileResponse, JSONResponse

from core import app, WIDGETS
from widgets_nyctaxi import router as nyctaxi_router
from widgets_bakehouse import router as bakehouse_router
from widgets_wanderbricks import router as wanderbricks_router
from widgets_tpch import router as tpch_router
from widgets_sql import router as sql_router

app.include_router(nyctaxi_router)
app.include_router(bakehouse_router)
app.include_router(wanderbricks_router)
app.include_router(tpch_router)
app.include_router(sql_router)

ROOT_PATH = Path(__file__).parent.resolve()


@app.get("/")
def read_root():
    return {"Info": "Databricks example for OpenBB Custom Backend"}


@app.get("/widgets.json")
def get_widgets():
    """Widgets configuration file for the OpenBB Custom Backend"""
    return WIDGETS


@app.get("/apps.json")
def get_apps():
    """App templates grouping the widgets into dashboards"""
    return JSONResponse(content=json.load((ROOT_PATH / "apps.json").open()))


@app.get("/thumbnails/{name}")
def get_thumbnail(name: str):
    """Thumbnails for the app cards"""
    path = (ROOT_PATH / "thumbnails" / f"{Path(name).name}.svg").resolve()
    if not path.is_file():
        return JSONResponse(status_code=404, content={"error": "not found"})
    return FileResponse(path, media_type="image/svg+xml")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5402)
