import base64
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, TypedDict
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

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


@app.get("/")
def read_root():
    return {"Info": "Newsfeed Widget Example"}


@app.get("/widgets.json")
def get_widgets():
    """Widgets configuration file for the OpenBB Custom Backend."""
    return JSONResponse(content=json.load((ROOT_PATH / "widgets.json").open()))


class CoindeskArticle(TypedDict):
    TYPE: str
    ID: int
    TITLE: str
    SUBTITLE: Optional[str]
    AUTHORS: str
    URL: str
    BODY: str
    PUBLISHED_ON: int
    IMAGE_URL: str
    KEYWORDS: str
    LANG: str
    SENTIMENT: str


class TransformedArticle(TypedDict):
    title: str
    date: str
    author: str
    excerpt: str
    body: str


def transform_article(article: CoindeskArticle) -> TransformedArticle:
    """Transform a CoinDesk article to a standardized format."""
    # Convert UNIX timestamp to ISO format
    date = datetime.fromtimestamp(article["PUBLISHED_ON"]).isoformat()
    
    # Create excerpt from body (first 150 characters)
    body = article["BODY"]
    excerpt = f"{body[:150]}..." if len(body) > 150 else body
    
    return {
        "title": article["TITLE"],
        "date": date,
        "author": article["AUTHORS"],
        "excerpt": excerpt,
        "body": body,
    }


def fetch_news(limit: str, lang: str, categories: Optional[str] = None) -> List[TransformedArticle]:
    """Fetch news from the CoinDesk API."""
    url = f"https://data-api.coindesk.com/news/v1/article/list?lang={lang}&limit={limit}"
    
    if categories:
        url += f"&categories={categories}"
    
    response = requests.get(url)
    
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=f"Failed to fetch news: {response.reason}")
    
    data = response.json()
    return [transform_article(article) for article in data.get("Data", [])]


@app.get("/news")
def get_coindesk_news(limit: str = "10", lang: str = "EN", categories: Optional[str] = None):
    """Get news from CoinDesk."""
    try:
        news = fetch_news(limit, lang, categories)
        return news
    except Exception as e:
        return JSONResponse(content={"error": f"Failed to fetch news: {str(e)}"}, status_code=500)
