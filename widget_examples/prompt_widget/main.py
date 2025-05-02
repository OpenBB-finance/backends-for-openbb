import json
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import requests
from dotenv import load_dotenv

from models import Citation, PromptRequest, PromptResponse, DataFormat, SourceInfo

load_dotenv(".env")

ROOT_PATH = Path(__file__).parent.resolve()
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

app = FastAPI()

origins = ["https://pro.openbb.co", "https://excel.openbb.co", "http://localhost:1420"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Info": "Full example for OpenBB Custom Backend"}


@app.get("/widgets.json")
def get_widgets():
    """Widgets configuration file for the OpenBB Custom Backend"""
    return JSONResponse(content=json.load((ROOT_PATH / "widgets.json").open()))


@app.post("/query")
async def query(request: PromptRequest):
    """Process a prompt request and return a response."""

    try:
        response = requests.post(
            url=f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
            headers={"Content-Type": "application/json"},
            json={"contents": [{"parts": [{"text": request.prompt}]}]},
        )
        response.raise_for_status()
        result = response.json()
        content = (
            result.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "Failed to get response.")
        )
    except requests.exceptions.RequestException as e:
        print(e)
        raise HTTPException(
            status_code=500, detail=f"Error communicating with Gemini API: {str(e)}"
        )
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Unexpected error.")

    citation = Citation(
        source_info=SourceInfo(
            type="widget",
            widget_id="llm_widget",
            origin="LLM Widget Backend",
            name="Gemini",
            description="Response from Gemini API",
            metadata={},
        ),
        details=[
            {
                "Name": "Gemini",
                "Prompt": request.prompt,
            }
        ],
    )

    return PromptResponse(
        content=content,
        data_format=DataFormat(data_type="object", parse_as="text"),
        extra_citations=[citation],
        citable=False,
    )
