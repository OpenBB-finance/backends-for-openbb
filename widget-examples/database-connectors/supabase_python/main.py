import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from supabase import Client, create_client

supabase: Client = create_client("URL HERE", "KEY HERE")

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


@app.get("/")
def read_root():
    return {"Info": "Supabase backend template for OpenBB Pro"}


@app.get("/widgets.json")
def get_widgets():
    """Widgets configuration file for OpenBB Pro"""
    return JSONResponse(
        content=json.load((Path(__file__).parent.resolve() / "widgets.json").open())
    )


@app.get("/financial_data_from_supabase")
def get_financial_data():
    """Get financial data from supabase"""

    try:
        results = supabase.table("financial_data").select("*").execute()

        return results.data
    except Exception as err:
        print(f"Error {err}")
        return JSONResponse(content={"error": err}, status_code=500)
