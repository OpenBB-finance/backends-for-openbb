import json
from pathlib import Path

from elasticsearch import Elasticsearch
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

client = Elasticsearch("", api_key="")

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
    return {"Info": "ElasticSearch backend template for OpenBB Pro"}


@app.get("/widgets.json")
def get_widgets():
    """Widgets configuration file for OpenBB Pro"""
    return JSONResponse(
        content=json.load((Path(__file__).parent.resolve() / "widgets.json").open())
    )


@app.get("/elastic_example")
def elastic_example():
    """Return snowflake data"""

    try:
        # Example of data ingestion
        documents = [
            {"index": {"_index": "search-spiderman", "_id": "9780553351927"}},
            {
                "name": "Snow Crash",
                "author": "Neal Stephenson",
                "release_date": "1992-06-01",
                "page_count": 470,
                "_extract_binary_content": True,
                "_reduce_whitespace": True,
                "_run_ml_inference": True,
            },
            {"index": {"_index": "search-spiderman", "_id": "9780441017225"}},
            {
                "name": "Revelation Space",
                "author": "Alastair Reynolds",
                "release_date": "2000-03-15",
                "page_count": 585,
                "_extract_binary_content": True,
                "_reduce_whitespace": True,
                "_run_ml_inference": True,
            },
            {"index": {"_index": "search-spiderman", "_id": "9780451524935"}},
            {
                "name": "1984",
                "author": "George Orwell",
                "release_date": "1985-06-01",
                "page_count": 328,
                "_extract_binary_content": True,
                "_reduce_whitespace": True,
                "_run_ml_inference": True,
            },
            {"index": {"_index": "search-spiderman", "_id": "9781451673319"}},
            {
                "name": "Fahrenheit 451",
                "author": "Ray Bradbury",
                "release_date": "1953-10-15",
                "page_count": 227,
                "_extract_binary_content": True,
                "_reduce_whitespace": True,
                "_run_ml_inference": True,
            },
            {"index": {"_index": "search-spiderman", "_id": "9780060850524"}},
            {
                "name": "Brave New World",
                "author": "Aldous Huxley",
                "release_date": "1932-06-01",
                "page_count": 268,
                "_extract_binary_content": True,
                "_reduce_whitespace": True,
                "_run_ml_inference": True,
            },
            {"index": {"_index": "search-spiderman", "_id": "9780385490818"}},
            {
                "name": "The Handmaid's Tale",
                "author": "Margaret Atwood",
                "release_date": "1985-06-01",
                "page_count": 311,
                "_extract_binary_content": True,
                "_reduce_whitespace": True,
                "_run_ml_inference": True,
            },
        ]
        client.bulk(operations=documents, pipeline="ent-search-generic-ingestion")

        res = client.search(index="search-spiderman", q="*")

        return [v["_source"] for v in res.body["hits"]["hits"]]
    except Exception as err:
        return JSONResponse(content={"error": err}, status_code=500)
