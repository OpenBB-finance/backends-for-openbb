import json
from pathlib import Path
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Literal, Union
from uuid import UUID
from fastapi import FastAPI, HTTPException, Body

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

@app.get("/")
def read_root():
    return {"Info": "Full example for OpenBB Custom Backend"}


@app.get("/widgets.json")
def get_widgets():
    """Widgets configuration file for the OpenBB Custom Backend"""
    return JSONResponse(
        content=json.load((Path(__file__).parent.resolve() / "widgets.json").open())
    )

class DataFormat(BaseModel):
    data_type: str
    parse_as: Literal["text", "table", "chart"]


class SourceInfo(BaseModel):
    type: Literal["widget"]
    uuid: UUID | None = Field(default=None)
    origin: str | None = Field(default=None)
    widget_id: str | None = Field(default=None)
    name: str
    description: str | None = Field(default=None)
    metadata: dict[str, Any] | None = Field(
        default=None,
        description="Additional metadata (eg. the selected ticker, endpoint used, etc.).",  # noqa: E501
    )


class ExtraCitation(BaseModel):
    source_info: SourceInfo | None = Field(default=None)
    details: List[dict] | None = Field(default=None)


class GreatWidgetResponse(BaseModel):
    content: Any
    data_format: DataFormat
    extra_citations: list[ExtraCitation] | None = Field(default_factory=list)
    citable: bool = Field(
        default=True,
        description="Whether the source is citable.",
    )


@app.post("/great-widget")
async def get_great_widget(data: Union[str, Dict] = Body(...)):
    """Get great widget using Gemini API"""

    if isinstance(data, str):
        data = json.loads(data)
    
    # Define the Gemini API endpoint and your API key
    gemini_api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    gemini_api_key = "key"

    # Safely extract the input text and content
    input_text = ""
    content = None
    print(data)
    if isinstance(data, dict):
        if "userInput" in data:
            input_text = data.get("userInput", "")
        if "content" in data:
            content = data.get("content", None)

    print("here")
    print(input_text)

    # Prepare the payload for the Gemini API request
    parts = [{"text": input_text}]
    
    # Add content to parts if it exists
    if content:
        if isinstance(content, str):
            parts.append({"text": content})
        else:
            parts.append({"text": json.dumps(content)})

    print(parts)
    
    payload = {
        "contents": [{
            "parts": parts
        }]
    }
    
    # Make the POST request to the Gemini API
    try:
        response = requests.post(
            f"{gemini_api_url}?key={gemini_api_key}",
            headers={"Content-Type": "application/json"},
            json=payload
        )
        response.raise_for_status()
        gemini_response = response.json()
    except requests.exceptions.RequestException as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Error communicating with Gemini API: {str(e)}")

    # Extract the text content from Gemini response
    gemini_text = gemini_response.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
    
    print(gemini_text)

    # Format response according to the simplified structure - ignore this for now
    formatted_response = {
        "data": [
            {
                "content": gemini_text,
                "extra_citations": [
                    {
                        "source_info": {
                            "type": "widget",
                            "widget_id": data.get("widget_id", "gemini_response"),
                            "origin": data.get("widget_origin", "gemini_widget"),
                            "name": "Gemini AI Response",
                            "description": f"Response from Gemini API for query: {data.get('input', 'Unknown query')}",
                            "metadata": {
                                "filename": "gemini_response.txt",
                                "extension": "txt",
                                "input_args": {
                                    "url": ""
                                }
                            }
                        },
                        "details": [
                            {
                                "Name": "Gemini AI Response",
                                "Query": data.get("input", "Unknown query"),
                                "Timestamp": data.get("timestamp", "")
                            }
                        ],
                        "quote_bounding_boxes": []
                    }
                ] if data.get("include_citations", True) else []  # Only include citations if requested
            }
        ]
    }


    return GreatWidgetResponse(
        content=gemini_text,
        data_format=DataFormat(data_type="object", parse_as="text"),
        extra_citations=formatted_response.get("data", [{}])[0].get("extra_citations", []),
        citable=True,
    )