import json
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import requests
from dotenv import load_dotenv
import logging
from google.genai import Client, types

from models import Citation, PromptRequest, PromptResponse, DataFormat, SourceInfo

load_dotenv(".env")

ROOT_PATH = Path(__file__).parent.resolve()
GEMINI_MODEL = "gemini-2.0-flash"
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


@app.post("/ask")
async def ask(request: PromptRequest):
    """Process a prompt request and return a response."""

    client = Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=request.prompt,
    )
    content = response.text
    if not content:
        raise HTTPException(status_code=500, detail="Empty response from Gemini API.")
    return PromptResponse(
        content=content,
        data_format=DataFormat(data_type="object", parse_as="text"),
    )
