import json
from pathlib import Path
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import requests

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

## Templates endpoint
@app.get("/templates.json")
def get_templates():
    """Templates configuration file for the OpenBB Custom Backend"""
    return JSONResponse(
        content=json.load((Path(__file__).parent.resolve() / "templates.json").open())
    )

@app.get("/chains_table")
def chains_table(chain: str = Query(None, description="Chain to filter by")):
    """Get current TVL of all chains using Defi LLama"""
    params = {}
    response = requests.get("https://api.llama.fi/v2/chains", params=params)

    if response.status_code == 200:
        data = response.json()
        # Filter by the chain parameter if provided
        if chain:
            data = [entry for entry in data if entry.get("name").lower() == chain.lower()]
        
        return data
    


    print(f"Request error {response.status_code}: {response.text}")
    return JSONResponse(
        content={"error": response.text}, status_code=response.status_code
    )

# example of how to get a dropdown list of chains
@app.get("/get_chains_list")
def get_chains_list():
    """Get list of chains using Defi LLama"""
    response = requests.get("https://api.llama.fi/v2/chains")

    if response.status_code == 200:
        data = response.json()
        # can pass as list of {label, value} for dropdown or list of strings
        #  [
        #   {"label": chain.get("name"), "value": chain.get("name")}
        #   for chain in data if chain.get("name")
        #  ]
        return [chain.get("name") for chain in data if chain.get("name")]

    print(f"Request error {response.status_code}: {response.text}")
    return JSONResponse(
        content={"error": response.text}, status_code=response.status_code
    )