import json
from pathlib import Path

import clickhouse_connect
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

client = clickhouse_connect.get_client(
    host="",
    port=8443,
    username="default",
    password="",
)

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
    return {"Info": "ClickHouse backend template for OpenBB Pro"}


@app.get("/widgets.json")
def get_widgets():
    """Widgets configuration file for OpenBB Pro"""
    return JSONResponse(
        content=json.load((Path(__file__).parent.resolve() / "widgets.json").open())
    )


@app.get("/avg_price_per_year_london")
def avg_price_per_year_london():
    """Return clickhouse data"""

    results = client.query_df(
        """SELECT
   toYear(date) AS year,
   round(avg(price)) AS price
FROM uk_price_paid
WHERE town = 'LONDON'
GROUP BY year
ORDER BY year
"""
    )

    # convert df to json
    return json.loads(results.to_json(orient="records"))
