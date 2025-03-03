import json
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()

origins = [
    "https://pro.openbb.co",
    "https://excel.openbb.co",
    "http://localhost:1420"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ROOT_PATH = Path(__file__).parent.resolve()

@app.get("/")
def read_root():
    return {"Info": "Full example for OpenBB Custom Backend"}


@app.get("/widgets.json")
def get_widgets():
    """Widgets configuration file for the OpenBB Custom Backend"""
    return JSONResponse(
        content=json.load((Path(__file__).parent.resolve() / "widgets.json").open())
    )

# example of how to get a simple metric widget
@app.get("/test_metric")
def test_metric():
        # Example data structure
    data = [{
        "label": "Example Label",
        "value": "12345",
        "delta": "0.01"
    },
    {
        "label": "Example Label 2",
        "value": "12345",
        "delta": "-0.01"
    },
    {
        "label": "Example Label 3",
        "value": "12345",
        "delta": "5.67"
    },
    {
        "label": "Example Label 4",
        "value": "12345",
        "delta": "0.00"
    },
        {
        "label": "Example Label 4",
        "value": "12345"
    }
    ]

    return JSONResponse(content=data)