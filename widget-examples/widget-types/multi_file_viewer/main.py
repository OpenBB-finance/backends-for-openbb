import json
from pathlib import Path
from typing import List
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import base64

from pydantic import BaseModel

app = FastAPI()

origins = ["https://pro.openbb.co", "https://excel.openbb.co", "http://localhost:1420"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ROOT_PATH = Path(__file__).parent.resolve()


# We are assuming the url is a publicly accessible url (ex a presigned url from an s3 bucket)
whitepapers = {
    "Bitcoin": {
        "location": "bitcoin.pdf",
        "url": "https://openbb-assets.s3.us-east-1.amazonaws.com/testing/bitcoin.pdf",
        "category": "l1",
    },
    "Ethereum": {
        "location": "ethereum.pdf",
        "url": "https://openbb-assets.s3.us-east-1.amazonaws.com/testing/ethereum.pdf",
        "category": "l1",
    },
    "ChainLink": {
        "location": "chainlink.pdf",
        "url": "https://openbb-assets.s3.us-east-1.amazonaws.com/testing/chainlink.pdf",
        "category": "oracles",
    },
    "Solana": {
        "location": "solana.pdf",
        "url": "https://openbb-assets.s3.us-east-1.amazonaws.com/testing/solana.pdf",
        "category": "l1",
    },
}


@app.get("/")
def read_root():
    return {"Info": "Full example for OpenBB Custom Backend"}


@app.get("/widgets.json")
def get_widgets():
    """Widgets configuration file for the OpenBB Custom Backend"""
    return JSONResponse(
        content=json.load((Path(__file__).parent.resolve() / "widgets.json").open())
    )


@app.get("/options")
async def get_options(category: str = Query("all")):
    if category == "all":
        return [{"label": name, "value": name} for name in whitepapers]
    return [
        {"label": name, "value": name}
        for name, wp in whitepapers.items()
        if wp["category"] == category
    ]


class DataContent(BaseModel):
    content: str
    data_format: dict


class DataError(BaseModel):
    error_type: str
    content: str


# This is a simple example of how to return a base64 encoded pdf.
@app.get("/whitepapers/base64")
async def get_whitepapers_base64(filename: List[str] = Query(...)):
    files: List[dict] = []
    for name in filename:
        if whitepaper := whitepapers.get(name):
            file_path = Path.cwd() / whitepaper["location"]
            if file_path.exists():
                with open(file_path, "rb") as file:
                    base64_content = base64.b64encode(file.read()).decode("utf-8")
                    files.append(
                        DataContent(
                            content=base64_content,
                            data_format={"data_type": "pdf", "filename": f"{name}.pdf"},
                        ).model_dump()
                    )
            else:
                files.append(
                    DataError(
                        error_type="not_found", content=f"File not found"
                    ).model_dump()
                )
        else:
            files.append(
                DataError(
                    error_type="not_found", content=f"Whitepaper '{name}' not found"
                ).model_dump()
            )

    return JSONResponse(
        headers={"Content-Type": "application/json"},
        content=files,
    )


# This is a simple example of how to return a url
# if you are using this endpoint you will need to change the widgets.json file to use this endpoint as well.
# You would want to return your own presigned url here for the file to load correctly or else the file will not load due to CORS policy.
@app.get("/whitepapers/url")
async def get_whitepapers_url(filename: List[str] = Query(...)):
    files: List[dict] = []
    for name in filename:
        if whitepaper := whitepapers.get(name):
            if url := whitepaper.get("url"):
                files.append(
                    DataContent(
                        content=url,
                        data_format={"data_type": "pdf", "filename": f"{name}.pdf"},
                    ).model_dump()
                )
            else:
                files.append(
                    DataError(
                        error_type="not_found", content="URL not found"
                    ).model_dump()
                )
        else:
            files.append(
                DataError(
                    error_type="not_found", content=f"Whitepaper '{name}' not found"
                ).model_dump()
            )

    return JSONResponse(
        headers={"Content-Type": "application/json"},
        content=files,
    )
