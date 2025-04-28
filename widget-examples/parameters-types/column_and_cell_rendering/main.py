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

@app.get("/json-data")
def json_data():
    """Read mock csv data and return it as a table to your widget"""
    # Specify the path to your JSON file
    json_file_path = "mock_data.json"

    try:
        # Return the JSON data as is
        return json.load((ROOT_PATH / json_file_path).open()).get("stocks", [])
    except Exception as e:
        # Handle error cases here
        error_message = f"Error reading the JSON file: {str(e)}"
        return JSONResponse(content={"error": error_message}, status_code=500)