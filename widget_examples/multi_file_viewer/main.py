import json
from pathlib import Path
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
import base64

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


# We are assuming the url is a publicly accessible url (ex a presigned url from an s3 bucket)
whitepapers = [
    {
        "name": "Sample_1",
        "location": "sample.pdf",
        "url": "http://localhost:5011/random/whitepapers/Sample_1",
        "type": "l1",
    },
    {
        "name": "Sample_2",
        "location": "other-sample.pdf",
        "url": "http://localhost:5011/random/whitepapers/Sample_2",
        "type": "oracles",
    },
    {
        "name": "Sample_3",
        "location": "other-sample.pdf",
        "url": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
        "type": "defi",
    }
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

@app.get("/random/whitepapers")
async def get_whitepapers(type: str = Query("all")):
    if type == "all":
        return [{"label": wp["name"], "value": wp["name"]} for wp in whitepapers]
    return [{"label": wp["name"], "value": wp["name"]} for wp in whitepapers if wp["type"] == type]


# This is a simple example of how to return a base64 encoded pdf.
@app.get("/random/whitepapers/view-base64")
async def view_whitepaper_base64(whitepaper: str):
    wp = next((wp for wp in whitepapers if wp["name"] == whitepaper), None)
    if not wp:
        raise HTTPException(status_code=404, detail="Whitepaper not found")

    file_path = Path.cwd() / wp["location"]
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Whitepaper file not found")

    with open(file_path, "rb") as file:
        base64_content = base64.b64encode(file.read()).decode('utf-8')

    return JSONResponse(content={
        "headers": {"Content-Type": "application/json"},
        "data_format": {"data_type": "pdf", "filename": f"{wp['name']}.pdf"},
        "content": base64_content
    })

# This is a simple example of how to return a url
# You would want to return your own presigned url here for the file to load correctly or else the file will not load due to CORS policy.
@app.get("/random/whitepapers/view-url")
async def view_whitepaper_url(whitepaper: str):
    wp = next((wp for wp in whitepapers if wp["name"] == whitepaper), None)
    if not wp:
        raise HTTPException(status_code=404, detail="Whitepaper not found")
    
    # go get the presigned url and return it for the file_reference
    # code here to get the presigned url - we are simulating the presigned url by returning the url directly
    presigned_url = wp["url"]

    file_path = Path.cwd() / wp["location"]
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Whitepaper file not found")

    return JSONResponse(content={
        "headers": {"Content-Type": "application/json"},
        "data_format": {"data_type": "pdf", "filename": f"{wp['name']}.pdf"},
        "file_reference": presigned_url
    })