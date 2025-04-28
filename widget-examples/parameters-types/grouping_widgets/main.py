import json
from pathlib import Path
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:1420",
    "http://localhost:5050",
    "https://pro.openbb.dev",
    "https://pro.openbb.co",
    "https://excel.openbb.co",
    "https://excel.openbb.dev",
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

# Example of how to get historical TVL of a chain using Defi LLama
@app.get("/historical_chains")
def get_historical_chains(chain: str = None):
    """Get historical TVL of a chain using Defi LLama"""

    if chain is None:
        chain = "Ethereum"
    response = requests.get(f'https://api.llama.fi/v2/historicalChainTvl/{chain}')

    if response.status_code == 200:
        return response.json()

    print(f"Request error {response.status_code}: {response.text}")
    return JSONResponse(
        content={"error": response.text}, status_code=response.status_code
    )


# Fetching list of chains for a parameter in the widget

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

# example of how get advanced dropdown labels - can change out the get_chains_list endpoint to this one to show advanced dropdown
@app.get("/get_chains_list_advanced")
def get_chains_list_advanced():
    """Get list of chains using Defi LLama"""
    response = requests.get("https://api.llama.fi/v2/chains")

    if response.status_code == 200:
        data = response.json()
        # can pass as list of {label, value} for dropdown or list of strings
        return [
            {"label": chain.get("name"), "value": chain.get("name"), "extraInfo":{
                "description": chain.get("tokenSymbol", "N/A"),
                "rightOfDescription": chain.get("chainId", "N/A")
            }}
            for chain in data if chain.get("name")
        ]


    print(f"Request error {response.status_code}: {response.text}")
    return JSONResponse(
        content={"error": response.text}, status_code=response.status_code
    )