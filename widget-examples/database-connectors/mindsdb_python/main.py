import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from mindsdb_sdk import connect

server = connect(
    login="",
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
    return {"Info": "MindsDB backend template for OpenBB Pro"}


@app.get("/widgets.json")
def get_widgets():
    """Widgets configuration file for OpenBB Pro"""
    return JSONResponse(
        content=json.load((Path(__file__).parent.resolve() / "widgets.json").open())
    )


@app.get("/home_rentals_prediction")
def get_home_rentals_prediction():
    """Return MindsDB data"""

    try:
        database = server.get_database("example_db")
        table = database.get_table("demo_data.home_rentals")
        project = server.get_project("mindsdb")
        model = project.get_model("home_rentals_model")
        predictions = model.predict(table)

        predictions = predictions.drop("rental_price_explain", axis=1)

        data_dict = predictions.to_dict(orient="records")

        for i, data in enumerate(data_dict, start=1):
            data["id"] = i

        return data_dict
    except Exception as err:
        print(f"Programming Error: {err}")
        return JSONResponse(content={"error": err}, status_code=500)
