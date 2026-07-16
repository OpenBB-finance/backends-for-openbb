import asyncio
import json
from pathlib import Path

from fastapi.responses import FileResponse, JSONResponse

from core import app, WIDGETS, warm_cache
from widgets_uk_housing import router as uk_router
from widgets_nyc_taxi import router as nyc_router

app.include_router(uk_router)
app.include_router(nyc_router)


@app.on_event("startup")
async def startup():
    asyncio.create_task(warm_cache())

THUMBNAILS_DIR = Path(__file__).parent / "thumbnails"


@app.get("/")
def root():
    return {"status": "ok", "app": "ClickHouse Explorer", "version": "1.0.0"}


@app.get("/widgets.json")
def get_widgets():
    return WIDGETS


@app.get("/apps.json")
def get_apps():
    with (Path(__file__).parent / "apps.json").open(encoding="utf-8") as file:
        return json.load(file)


@app.get("/thumbnails/{name}")
def get_thumbnail(name: str):
    path = THUMBNAILS_DIR / f"{Path(name).name}.svg"
    if not path.is_file():
        return JSONResponse(status_code=404, content={"error": "not found"})
    return FileResponse(path, media_type="image/svg+xml")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=7781)
