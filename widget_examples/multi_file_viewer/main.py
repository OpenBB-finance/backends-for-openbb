import json
from pathlib import Path
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
import base64

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
whitepapers = [
    {
        "name": "Bitcoin",
        "location": "bitcoin.pdf",
        "url": "https://openbb-assets.s3.us-east-1.amazonaws.com/testing/bitcoin.pdf",
        "category": "l1",
    },
    {
        "name": "Ethereum",
        "location": "ethereum.pdf",
        "url": "https://openbb-assets.s3.us-east-1.amazonaws.com/testing/ethereum.pdf",
        "category": "l1",
    },
    {
        "name": "ChainLink",
        "location": "chainlink.pdf",
        "url": "https://openbb-assets.s3.us-east-1.amazonaws.com/testing/chainlink.pdf",
        "category": "oracles",
    },
    {
        "name": "Solana",
        "location": "solana.pdf",
        "url": "https://openbb-assets.s3.us-east-1.amazonaws.com/testing/solana.pdf",
        "category": "l1",
    },
]


@app.get("/")
def read_root():
    return {"Info": "Full example for OpenBB Custom Backend"}


@app.get("/widgets.json")
def get_widgets():
    """Widgets configuration file for the OpenBB Custom Backend"""
    return JSONResponse(
        content=json.load((Path(__file__).parent.resolve() / "widgets.json").open())
    )


@app.get("/whitepapers")
async def get_whitepapers(category: str = Query("all")):
    if category == "all":
        return [{"label": wp["name"], "value": wp["name"]} for wp in whitepapers]
    return [
        {"label": wp["name"], "value": wp["name"]}
        for wp in whitepapers
        if wp["category"] == category
    ]


# This is a simple example of how to return a base64 encoded pdf.
@app.get("/whitepapers/view-base64")
async def view_whitepaper_base64(whitepaper: str):
    wp = next((wp for wp in whitepapers if wp["name"] == whitepaper), None)
    if not wp:
        raise HTTPException(status_code=404, detail="Whitepaper not found")

    file_path = Path.cwd() / wp["location"]
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Whitepaper file not found")

    with open(file_path, "rb") as file:
        base64_content = base64.b64encode(file.read()).decode("utf-8")

    return JSONResponse(
        headers={"Content-Type": "application/json"},
        content={
            "data_format": {"data_type": "pdf", "filename": f"{wp['name']}.pdf"},
            "content": base64_content,
        },
    )


# This is a simple example of how to return a url
# if you are using this endpoint you will need to change the widgets.json file to use this endpoint as well.
# You would want to return your own presigned url here for the file to load correctly or else the file will not load due to CORS policy.
@app.get("/whitepapers/view-url")
async def view_whitepaper_url(whitepaper: str):
    wp = next((wp for wp in whitepapers if wp["name"] == whitepaper), None)
    if not wp:
        raise HTTPException(status_code=404, detail="Whitepaper not found")

    # Fetch the presigned url and return it for the `file_reference`.
    # In the code below, we are simulating the presigned url by returning the url directly.
    presigned_url = wp["url"]

    file_path = Path.cwd() / wp["location"]
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Whitepaper file not found")

    return JSONResponse(
        headers={"Content-Type": "application/json"},
        content={
            "data_format": {"data_type": "pdf", "filename": f"{wp['name']}.pdf"},
            "file_reference": presigned_url,
        },
    )
