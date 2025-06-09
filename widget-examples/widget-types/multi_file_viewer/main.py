import json
from pathlib import Path
from typing import List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import base64
from models import FileOption, FileRequest, DataContent, DataUrl, DataError, DataFormat

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
WHITEPAPERS = {
    "bitcoin.pdf": {
        "label": "Bitcoin",
        "filename": "bitcoin.pdf",
        "url": "https://openbb-assets.s3.us-east-1.amazonaws.com/testing/bitcoin.pdf",
        "category": "l1",
    },
    "ethereum.pdf": {
        "label": "Ethereum",
        "filename": "ethereum.pdf",
        "url": "https://openbb-assets.s3.us-east-1.amazonaws.com/testing/ethereum.pdf",
        "category": "l1",
    },
    "chainlink.pdf": {
        "label": "Chainlink",
        "filename": "chainlink.pdf",
        "url": "https://openbb-assets.s3.us-east-1.amazonaws.com/testing/chainlink.pdf",
        "category": "oracles",
    },
    "solana.pdf": {
        "label": "Solana",
        "filename": "solana.pdf",
        "url": "https://openbb-assets.s3.us-east-1.amazonaws.com/testing/solana.pdf",
        "category": "l1",
    },
}


@app.get("/")
def read_root():
    return {"Info": "Multi File Viewer Example"}


@app.get("/widgets.json")
def get_widgets():
    """Widgets configuration file for the OpenBB Custom Backend"""
    return JSONResponse(
        content=json.load((Path(__file__).parent.resolve() / "widgets.json").open())
    )


@app.get("/options")
async def get_options(category: str = "all") -> List[FileOption]:
    if category == "all":
        return [
            FileOption(label=whitepaper["label"], value=whitepaper["filename"])
            for whitepaper in WHITEPAPERS.values()
        ]
    return [
        FileOption(label=whitepaper["label"], value=whitepaper["filename"])
        for whitepaper in WHITEPAPERS.values()
        if whitepaper["category"] == category
    ]


# For multi file viewer we need accept a list of filenames and return a list of results.
# The number of files returned must match the number of filenames requested.


# This is an example of how to return a list of base64 encoded files.
@app.post("/whitepapers/base64")
async def get_whitepapers_base64(
    request: FileRequest,
) -> List[DataContent | DataUrl | DataError]:
    files = []
    for name in request.filenames:
        if whitepaper := WHITEPAPERS.get(name):
            file_name_with_extension = whitepaper["filename"]
            file_path = Path.cwd() / "whitepapers" / file_name_with_extension
            if file_path.exists():
                with open(file_path, "rb") as file:
                    base64_content = base64.b64encode(file.read()).decode("utf-8")
                    files.append(
                        DataContent(
                            content=base64_content,
                            data_format=DataFormat(
                                data_type="pdf",
                                filename=file_name_with_extension,
                            ),
                        ).model_dump()
                    )
            else:
                files.append(
                    DataError(
                        error_type="not_found", content="File not found"
                    ).model_dump()
                )
        else:
            files.append(
                DataError(
                    error_type="not_found", content=f"Whitepaper '{name}' not found"
                ).model_dump()
            )
    return JSONResponse(headers={"Content-Type": "application/json"}, content=files)


# This is an example of how to return a list of urls.
# if you are using this endpoint you will need to change the widgets.json file to use this endpoint as well.
# You would want to return your own presigned url here for the file to load correctly or else the file will not load due to CORS policy.
@app.post("/whitepapers/url")
async def get_whitepapers_url(
    request: FileRequest,
) -> List[DataContent | DataUrl | DataError]:
    files = []
    for name in request.filenames:
        if whitepaper := WHITEPAPERS.get(name):
            file_name_with_extension = whitepaper["filename"]
            if url := whitepaper.get("url"):
                files.append(
                    DataUrl(
                        url=url,
                        data_format=DataFormat(
                            data_type="pdf", filename=file_name_with_extension
                        ),
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
    return JSONResponse(headers={"Content-Type": "application/json"}, content=files)
