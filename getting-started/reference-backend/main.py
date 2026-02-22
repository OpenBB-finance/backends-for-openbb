"""
Main FastAPI Application for OpenBB Workspace Reference Backend

This file imports the core app and includes all widget routers.
Widget endpoints are organized into separate modules by category.

To run the server:
    uvicorn main:app --reload --port 5050
"""

import json
from fastapi.responses import JSONResponse

# Import core components
from core import app, ROOT_PATH, WIDGETS

# Import widget routers
from widgets_types import router as types_router
from widgets_settings import router as settings_router
from widgets_input_params import router as input_params_router
from widgets_grouping import router as widgets_grouping_router
from widgets_aggrid_table import router as aggrid_router
from widgets_plotly_chart import router as plotly_router
from widgets_input_form import router as form_router
from widgets_tradingview import router as tradingview_router
from widgets_omni_sql_python import router as omni_sql_python_router
from widgets_sparkline import router as sparkline_router
from widgets_youtube import router as youtube_router
from widgets_highchart import router as highchart_router
from widgets_live_grid import router as live_grid_router


# ============================================================================
# CORE ENDPOINTS
# ============================================================================

@app.get("/")
def read_root():
    """Root endpoint that returns basic information about the API"""
    return {"Info": "Hello World"}


@app.get("/widgets.json")
def get_widgets():
    """Returns the configuration of all registered widgets"""
    return WIDGETS


@app.get("/apps.json")
def get_apps():
    """Apps configuration file for the OpenBB Workspace"""
    return JSONResponse(
        content=json.load((ROOT_PATH / "apps.json").open())
    )


# ============================================================================
# INCLUDE WIDGET ROUTERS
# ============================================================================

app.include_router(types_router)
app.include_router(settings_router)
app.include_router(input_params_router)
app.include_router(widgets_grouping_router)
app.include_router(aggrid_router)
app.include_router(plotly_router)
app.include_router(form_router)
app.include_router(tradingview_router)
app.include_router(omni_sql_python_router)
app.include_router(sparkline_router)
app.include_router(youtube_router)
app.include_router(highchart_router)
app.include_router(live_grid_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5050)
