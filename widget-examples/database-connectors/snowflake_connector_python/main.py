import json
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from utils import get_snowflake_connection
from snowflake.connector import SnowflakeConnection

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
    return {"Info": "Snowflake example for OpenBB Custom Backend"}


@app.get("/widgets.json")
def get_widgets():
    """Widgets configuration file for the OpenBB Custom Backend"""
    return JSONResponse(
        content=json.load((Path(__file__).parent.resolve() / "widgets.json").open())
    )


# This endpoint will serve to get all available schemas
# We will use this to populate the dropdown in the view widget
@app.get("/schema")
def get_schema(
    connection: Annotated[SnowflakeConnection, Depends(get_snowflake_connection)]
):
    with connection.cursor() as cursor:
        cursor.execute("SHOW SCHEMAS")
        return JSONResponse(content=[r[1] for r in cursor.fetchall()])


# This endpoint returns all the views in a given schema
@app.get("/views/{schema}")
def get_views(schema: str, connection=Depends(get_snowflake_connection)):
    cursor = connection.cursor()
    cursor.execute(f"SHOW VIEWS IN SCHEMA {schema}")
    return JSONResponse(content=[{"view": r[1]} for r in cursor.fetchall()])


# This endpoint returns the close price of a given stock
@app.get("/stock/{ticker}")
def get_stock_ticker(ticker: str, connection=Depends(get_snowflake_connection)):
    cursor = connection.cursor()
    cursor.execute(
        f"SELECT date,value FROM CYBERSYN.STOCK_PRICE_TIMESERIES WHERE TICKER = '{ticker.upper()}' and VARIABLE = 'post-market_close' order by date desc"
    )
    res = cursor.fetchall()
    serialized_res = [{"date": date.isoformat(), "close": value} for date, value in res]

    return JSONResponse(content=serialized_res)
