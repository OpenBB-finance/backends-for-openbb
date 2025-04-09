from datetime import datetime, timezone
import json
from pathlib import Path
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx

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


# Define a function to transform the article data
# endpoint needs to return an array of so we transform the article to a dict and return an array of dicts
# {
# 	title: string;
# 	date: string;
# 	author: string;
# 	excerpt: string;
# 	body: string;
# }

def transform_article(article: dict) -> dict:
    """Transforms a single article from Coindesk API format to the desired format."""
    # ... (transform_article function remains the same) ...
    # Convert UNIX timestamp to ISO 8601 string in UTC
    published_on_ts = article.get("PUBLISHED_ON", 0)
    try:
        # Ensure the timestamp is treated as an integer or float
        dt_object = datetime.fromtimestamp(int(published_on_ts), tz=timezone.utc)
        date_str = dt_object.isoformat()
    except (ValueError, TypeError):
        date_str = "Invalid Date" # Handle cases where timestamp is missing or invalid

    body = article.get("BODY", "")
    # Create excerpt from body (first 150 characters)
    excerpt = f"{body[:150]}..." if len(body) > 150 else body

    return {
        "title": article.get("TITLE", "No Title"),
        "date": date_str,
        "author": article.get("AUTHORS", "Unknown Author"),
        "excerpt": excerpt,
        "body": body, # Assuming the body is already markdown
        "url": article.get("URL", ""),
        "image_url": article.get("IMAGE_URL", "")
    }


# Define an asynchronous function to fetch news from Coindesk using httpx
async def fetch_news(limit: int = 10, lang: str = "EN") -> list[dict]:
    """Fetches and transforms news articles from the Coindesk API using httpx."""
    url = f"https://data-api.coindesk.com/news/v1/article/list?lang={lang}&limit={limit}"
    # Use an async client for non-blocking I/O
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url) # <-- Use await with httpx
            response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
            data = response.json()

            articles = data.get("Data", [])
            if not isinstance(articles, list):
                 print(f"Warning: Expected 'Data' to be a list, but got {type(articles)}")
                 return [] # Return empty list if data format is unexpected

            # Call the synchronous transform_article without await
            return [transform_article(article) for article in articles if isinstance(article, dict)]

        except httpx.RequestError as exc: # <-- Catch httpx specific request errors
            print(f"An error occurred while requesting {url}: {exc}")
            # Distinguish between connection errors and HTTP errors if possible
            status_code = 503
            detail = f"Error connecting to Coindesk API: {exc}"
            # Check if the exception has a response attribute (for HTTP errors)
            if hasattr(exc, 'response') and exc.response is not None:
                status_code = exc.response.status_code
                # Use response.text for the error detail from the API
                detail = f"Error from Coindesk API ({status_code}): {exc.response.text}"
            raise HTTPException(status_code=status_code, detail=detail)
        except json.JSONDecodeError:
            print(f"Failed to decode JSON response from {url}")
            raise HTTPException(status_code=500, detail="Failed to decode response from Coindesk API")
        except Exception as exc:
             print(f"An unexpected error occurred: {exc}")
             raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {exc}")


@app.get("/coindesk/news")
async def get_coindesk_news(
    limit: int = Query(10, description="The number of news articles to fetch", ge=1, le=100),
    lang: str = Query("EN", description="The language of the news articles (e.g., EN, ES, PT)")
):
    """Endpoint to fetch news from Coindesk."""
    try:
        # Call the asynchronous fetch_news function
        news_data = await fetch_news(limit=limit, lang=lang)
        return JSONResponse(content=news_data)
    except HTTPException as http_exc:
        # Re-raise HTTPException to let FastAPI handle it
        raise http_exc
    except Exception as e:
        # Catch any other unexpected errors
        print(f"Unexpected error in /coindesk/news endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")