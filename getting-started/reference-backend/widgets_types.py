import base64
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Union
from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import JSONResponse, HTMLResponse

# Import from core module
from core import (
    register_widget, ROOT_PATH, WIDGETS,
    FileOption, FileDataFormat, DataContent, DataUrl, DataError
)

router = APIRouter()

@register_widget({
    "name": "Metric Widget",
    "description": "A metric widget",
    "endpoint": "metric_widget",
    "gridData": {"w": 5, "h": 5},
    "type": "metric",
})
@router.get("/metric_widget")
def metric_widget():
    """Returns metric data for KPI display"""
    data = [
        {"label": "Total Users", "value": "1,234,567", "delta": "12.5"},
        {"label": "Active Sessions", "value": "45,678", "delta": "-2.3"},
        {"label": "Revenue (USD)", "value": "$89,432", "delta": "8.9"},
        {"label": "Conversion Rate", "value": "3.2%", "delta": "0.0"},
        {"label": "Avg. Session Duration", "value": "4m 32s", "delta": "3.5"},
    ]
    return JSONResponse(content=data)


@register_widget({
    "name": "Markdown Widget",
    "description": "A markdown widget",
    "type": "markdown",
    "endpoint": "markdown_widget",
    "gridData": {"w": 12, "h": 4},
})
@router.get("/markdown_widget")
def markdown_widget():
    """Returns a markdown widget"""
    return "# Markdown Widget"


@register_widget({
    "name": "Markdown Widget with Category and Subcategory",
    "description": "A markdown widget with category and subcategory",
    "type": "markdown",
    "category": "Widgets",
    "subCategory": "Markdown Widgets",
    "endpoint": "markdown_widget_with_category_and_subcategory",
    "gridData": {"w": 12, "h": 4},
})
@router.get("/markdown_widget_with_category_and_subcategory")
def markdown_widget_with_category_and_subcategory():
    """Returns a markdown widget with category and subcategory"""
    return "Markdown Widget with Category and Subcategory"


@register_widget({
    "name": "Table Widget",
    "description": "A table widget",
    "type": "table",
    "endpoint": "table_widget",
    "gridData": {"w": 12, "h": 4},
})
@router.get("/table_widget")
def table_widget():
    """Returns a mock table data for demonstration"""
    mock_data = [
        {"name": "Ethereum", "tvl": 45000000000, "change_1d": 2.5, "change_7d": 5.2},
        {"name": "Bitcoin", "tvl": 35000000000, "change_1d": 1.2, "change_7d": 4.8},
        {"name": "Solana", "tvl": 8000000000, "change_1d": -0.5, "change_7d": 2.1},
    ]
    return mock_data


@register_widget({
    "name": "Table Widget from API Endpoint",
    "description": "A table widget from an API endpoint",
    "type": "table",
    "endpoint": "table_widget_from_api_endpoint",
    "gridData": {"w": 12, "h": 4},
})
@router.get("/table_widget_from_api_endpoint")
def table_widget_from_api_endpoint():
    """Get current TVL of all chains using Defi LLama"""
    response = requests.get("https://api.llama.fi/v2/chains")

    if response.status_code == 200:
        return response.json()

    print(f"Request error {response.status_code}: {response.text}")
    raise HTTPException(status_code=response.status_code, detail=response.text)


@register_widget({
    "name": "Markdown Widget with Error Handling",
    "description": "A markdown widget with error handling",
    "type": "markdown",
    "endpoint": "markdown_widget_with_error_handling",
    "gridData": {"w": 12, "h": 4},
})
@router.get("/markdown_widget_with_error_handling")
def markdown_widget_with_error_handling():
    """Returns a markdown widget with error handling"""
    raise HTTPException(status_code=500, detail="Error that just occurred")


@register_widget({
    "name": "Sample News Feed",
    "description": "A simple newsfeed widget with example articles",
    "type": "newsfeed",
    "endpoint": "sample_newsfeed",
    "gridData": {"w": 40, "h": 20},
    "source": "example",
    "params": [
        {
            "paramName": "category",
            "label": "Category",
            "description": "Filter news by category",
            "type": "text",
            "value": "all",
            "options": [
                {"label": "All", "value": "all"},
                {"label": "Technology", "value": "tech"},
                {"label": "Business", "value": "business"},
                {"label": "Science", "value": "science"},
            ],
        },
        {
            "paramName": "limit",
            "label": "Number of Articles",
            "description": "Maximum number of articles to display",
            "type": "number",
            "value": "5",
        },
    ],
})
@router.get("/sample_newsfeed")
def get_sample_newsfeed(category: str = "all", limit: int = 5):
    """Returns sample news articles in the required newsfeed format"""
    sample_articles = {
        "tech": [
            {
                "title": "AI Breakthrough: New Model Achieves Human-Level Reasoning",
                "date": (datetime.now() - timedelta(hours=2)).isoformat(),
                "author": "Sarah Johnson",
                "excerpt": "Researchers at TechLab have unveiled a groundbreaking AI model...",
                "body": """# AI Breakthrough: New Model Achieves Human-Level Reasoning

Researchers at TechLab have unveiled a groundbreaking AI model that demonstrates unprecedented reasoning capabilities.

## Key Features
- **Advanced reasoning**: The model can solve complex logical problems
- **Multimodal understanding**: Processes text, images, and audio simultaneously
- **Energy efficient**: Uses 40% less computational resources than previous models""",
            },
            {
                "title": "Quantum Computing Startup Raises $500M in Series C Funding",
                "date": (datetime.now() - timedelta(hours=5)).isoformat(),
                "author": "Michael Chen",
                "excerpt": "QuantumLeap Technologies secures major funding round...",
                "body": """# Quantum Computing Startup Raises $500M in Series C Funding

QuantumLeap Technologies announced today that it has secured $500 million in Series C funding.

The company plans to use the funding to:
1. Scale manufacturing capabilities
2. Expand research team by 200 engineers
3. Develop partnerships with major cloud providers""",
            },
        ],
        "business": [
            {
                "title": "Global Markets Rally on Positive Economic Data",
                "date": (datetime.now() - timedelta(hours=1)).isoformat(),
                "author": "Robert Williams",
                "excerpt": "Stock markets across the globe surged today...",
                "body": """# Global Markets Rally on Positive Economic Data

Stock markets worldwide experienced significant gains today.

## Market Performance
- S&P 500: +2.3%
- NASDAQ: +2.8%
- FTSE 100: +1.9%
- Nikkei 225: +2.1%""",
            },
            {
                "title": "E-commerce Giant Announces Major Expansion into Southeast Asia",
                "date": (datetime.now() - timedelta(hours=4)).isoformat(),
                "author": "Lisa Anderson",
                "excerpt": "MegaShop reveals plans to invest $2 billion...",
                "body": """# E-commerce Giant Announces Major Expansion into Southeast Asia

MegaShop today unveiled ambitious plans to expand its presence across Southeast Asia with a $2 billion investment.

The expansion includes:
- New fulfillment centers in 5 countries
- Partnership with 10,000 local merchants
- Same-day delivery in major metropolitan areas""",
            },
        ],
        "science": [
            {
                "title": "Scientists Discover New Earth-like Exoplanet in Habitable Zone",
                "date": (datetime.now() - timedelta(hours=3)).isoformat(),
                "author": "Dr. Emily Rogers",
                "excerpt": "Astronomers using the James Webb Space Telescope have identified...",
                "body": """# Scientists Discover New Earth-like Exoplanet in Habitable Zone

A team of international astronomers has announced the discovery of an Earth-like exoplanet.

## Planet Characteristics
- **Size**: 1.2 times Earth's radius
- **Orbital period**: 385 days
- **Surface temperature**: Estimated 15°C average
- **Atmosphere**: Preliminary data suggests presence of water vapor""",
            },
            {
                "title": "Breakthrough in Cancer Treatment: New Immunotherapy Shows Promise",
                "date": (datetime.now() - timedelta(hours=6)).isoformat(),
                "author": "Dr. James Martinez",
                "excerpt": "Clinical trials reveal remarkable success rates...",
                "body": """# Breakthrough in Cancer Treatment: New Immunotherapy Shows Promise

Researchers at the National Cancer Institute have reported extraordinary results from Phase II clinical trials.

## Trial Results
- 78% response rate in patients with advanced melanoma
- 65% showed tumor reduction within 3 months
- Minimal side effects compared to traditional chemotherapy""",
            },
        ],
    }

    if category == "all":
        all_articles = []
        for cat_articles in sample_articles.values():
            all_articles.extend(cat_articles)
        articles = all_articles
    else:
        articles = sample_articles.get(category, [])

    articles.sort(key=lambda x: x["date"], reverse=True)
    articles = articles[:limit]

    return articles


@register_widget({
    "name": "Markdown Widget with Local Image",
    "description": "A markdown widget with a local image",
    "type": "markdown",
    "endpoint": "markdown_widget_with_local_image",
    "gridData": {"w": 20, "h": 20},
})
@router.get("/markdown_widget_with_local_image")
def markdown_widget_with_local_image():
    """Returns a markdown widget with a local image"""
    try:
        with open("img.png", "rb") as image_file:
            image_base64 = base64.b64encode(image_file.read()).decode("utf-8")
            return f"![Local Image](data:image/png;base64,{image_base64})"
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail="Image file not found") from e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error reading image: {str(e)}"
        ) from e


@register_widget({
    "name": "Markdown Widget with Image from URL",
    "description": "A markdown widget with an image from a URL",
    "type": "markdown",
    "endpoint": "markdown_widget_with_image_from_url",
    "gridData": {"w": 20, "h": 20},
})
@router.get("/markdown_widget_with_image_from_url")
def markdown_widget_with_image_from_url():
    """Returns a markdown widget with an image from a URL"""
    image_url = "https://api.star-history.com/svg?repos=openbb-finance/OpenBB&type=Date&theme=dark"

    try:
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()

        content_type = response.headers.get("content-type", "")
        if not content_type.startswith("image/"):
            raise HTTPException(
                status_code=500,
                detail=f"URL did not return an image. Content-Type: {content_type}",
            )

        image_base64 = base64.b64encode(response.content).decode("utf-8")
        return f"![OpenBB Logo](data:{content_type};base64,{image_base64})"

    except requests.RequestException as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch image: {str(e)}"
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing image: {str(e)}"
        ) from e


@register_widget({
    "name": "PDF Widget with Base64",
    "description": "Display a PDF file with base64 encoding",
    "endpoint": "pdf_widget_base64",
    "gridData": {"w": 20, "h": 20},
    "type": "pdf",
})
@router.get("/pdf_widget_base64")
def get_pdf_widget_base64():
    """Serve a file through base64 encoding."""
    try:
        name = "sample.pdf"
        with open(ROOT_PATH / name, "rb") as file:
            file_data = file.read()
            encoded_data = base64.b64encode(file_data)
            content = encoded_data.decode("utf-8")

    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="File not found") from exc

    return JSONResponse(
        headers={"Content-Type": "application/json"},
        content={
            "data_format": {"data_type": "pdf", "filename": name},
            "content": content,
        },
    )


@register_widget({
    "name": "PDF Widget with URL",
    "description": "Display a PDF file",
    "type": "pdf",
    "endpoint": "pdf_widget_url",
    "gridData": {"w": 20, "h": 20},
})
@router.get("/pdf_widget_url")
def get_pdf_widget_url():
    """Serve a file through URL."""
    file_reference = "https://openbb-assets.s3.us-east-1.amazonaws.com/testing/sample.pdf"
    if not file_reference:
        raise HTTPException(status_code=404, detail="File not found")
    return JSONResponse(
        headers={"Content-Type": "application/json"},
        content={
            "data_format": {"data_type": "pdf", "filename": "Sample.pdf"},
            "url": file_reference,
        },
    )


# Sample PDF files data
SAMPLE_PDFS = [
    {
        "name": "Sample",
        "location": "sample.pdf",
        "url": "https://openbb-assets.s3.us-east-1.amazonaws.com/testing/sample.pdf",
    },
    {
        "name": "Bitcoin Whitepaper",
        "location": "bitcoin.pdf",
        "url": "https://openbb-assets.s3.us-east-1.amazonaws.com/testing/bitcoin.pdf",
    },
]


@router.get("/get_pdf_options")
async def get_pdf_options() -> List[FileOption]:
    """Get list of available PDFs"""
    return [FileOption(label=pdf["name"], value=pdf["name"]) for pdf in SAMPLE_PDFS]


@register_widget({
    "name": "Multi PDF Viewer - Base64",
    "description": "View multiple PDF files using base64 encoding",
    "type": "multi_file_viewer",
    "endpoint": "/multi_pdf_base64",
    "gridData": {"w": 20, "h": 10},
    "params": [{
        "paramName": "pdf_name",
        "description": "PDF file to display",
        "type": "endpoint",
        "label": "PDF File",
        "optionsEndpoint": "/get_pdf_options",
        "show": False,
        "value": ["Bitcoin Whitepaper"],
        "multiSelect": True,
        "roles": ["fileSelector"],
    }],
})
@router.post("/multi_pdf_base64")
async def get_multi_pdf_base64(
    pdf_name: List[str] = Body(..., embed=True)
) -> List[Union[DataContent, DataError]]:
    """Get multiple PDF files in base64 format"""
    files = []
    for name in pdf_name:
        pdf = next((p for p in SAMPLE_PDFS if p["name"] == name), None)
        if not pdf:
            files.append(DataError(error_type="not_found", content=f"PDF '{name}' not found").model_dump())
            continue

        file_path = ROOT_PATH / pdf["location"]
        if not file_path.exists():
            files.append(DataError(error_type="not_found", content=f"PDF file '{pdf['location']}' not found on disk").model_dump())
            continue

        with open(file_path, "rb") as file:
            base64_content = base64.b64encode(file.read()).decode("utf-8")
            files.append(DataContent(
                content=base64_content,
                data_format=FileDataFormat(data_type="pdf", filename=f"{pdf['name']}.pdf"),
            ).model_dump())

    return JSONResponse(headers={"Content-Type": "application/json"}, content=files)


@register_widget({
    "name": "Multi PDF Viewer - URL",
    "description": "View multiple PDF files using URLs",
    "type": "multi_file_viewer",
    "endpoint": "/multi_pdf_url",
    "gridData": {"w": 20, "h": 10},
    "params": [{
        "paramName": "pdf_name",
        "description": "PDF file to display",
        "type": "endpoint",
        "label": "PDF File",
        "optionsEndpoint": "/get_pdf_options",
        "value": ["Sample"],
        "show": False,
        "multiSelect": True,
        "roles": ["fileSelector"],
    }],
})
@router.post("/multi_pdf_url")
async def get_multi_pdf_url(
    pdf_name: List[str] = Body(..., embed=True)
) -> List[Union[DataUrl, DataError]]:
    """Get multiple PDF files via URLs"""
    files = []
    for name in pdf_name:
        pdf = next((p for p in SAMPLE_PDFS if p["name"] == name), None)
        if not pdf:
            files.append(DataError(error_type="not_found", content=f"PDF '{name}' not found").model_dump())
            continue

        if url := pdf.get("url"):
            files.append(DataUrl(
                url=url,
                data_format=FileDataFormat(data_type="pdf", filename=f"{pdf['name']}.pdf"),
            ).model_dump())
        else:
            files.append(DataError(error_type="not_found", content=f"URL not found for '{name}'").model_dump())

    return JSONResponse(headers={"Content-Type": "application/json"}, content=files)


@register_widget({
    "name": "HTML Widget",
    "description": "A HTML widget with interactive dashboard",
    "type": "html",
    "endpoint": "html_widget",
    "gridData": {"w": 40, "h": 20},
    "raw": True,
})
@router.get("/html_widget", response_class=HTMLResponse)
def html_widget(raw: bool = False):
    """Returns an HTML widget with mockup data"""
    dashboard_data = [
        {"metric": "Total Portfolio Value", "value": "$124,563", "change": "+5.4%", "period": "today"},
        {"metric": "Active Positions", "value": "42", "change": "+3", "period": "this week"},
        {"metric": "Daily P&L", "value": "$8,421", "change": "+12.3%", "period": "today"},
        {"metric": "Sharpe Ratio", "value": "0.87", "change": "-0.05", "period": "current"},
        {"metric": "Tech Stocks Allocation", "value": "68%", "change": "", "period": "current"},
        {"metric": "Fixed Income Allocation", "value": "32%", "change": "", "period": "current"},
        {"metric": "Recent Trade: AAPL", "value": "Bought 100 @ $182.50", "change": "", "period": "2 hours ago"},
        {"metric": "Recent Trade: GOOGL", "value": "Sold 50 @ $141.20", "change": "", "period": "5 hours ago"},
        {"metric": "Recent Trade: MSFT", "value": "Bought 75 @ $378.80", "change": "", "period": "Yesterday"},
    ]

    if raw:
        return JSONResponse(content=dashboard_data)

    return HTMLResponse(content="""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { text-align: center; color: white; margin-bottom: 30px; }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 12px rgba(0,0,0,0.15);
        }
        .stat-value { font-size: 2em; font-weight: bold; color: #333; }
        .stat-label { color: #666; margin-top: 5px; }
        .stat-change {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.85em;
            margin-top: 10px;
        }
        .positive { background: #d4edda; color: #155724; }
        .negative { background: #f8d7da; color: #721c24; }
        .chart-container {
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .progress-bar {
            width: 100%;
            height: 20px;
            background: #e0e0e0;
            border-radius: 10px;
            overflow: hidden;
            margin-top: 10px;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            transition: width 1s ease;
            animation: fillAnimation 2s ease-out;
        }
        @keyframes fillAnimation { from { width: 0%; } }
    </style>
</head>
<body>
    <div class="container">
        <div class="header"><h1>Portfolio Dashboard</h1></div>
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">$124,563</div>
                <div class="stat-label">Total Portfolio Value</div>
                <span class="stat-change positive">+5.4% today</span>
            </div>
            <div class="stat-card">
                <div class="stat-value">42</div>
                <div class="stat-label">Active Positions</div>
                <span class="stat-change positive">+3 this week</span>
            </div>
            <div class="stat-card">
                <div class="stat-value">$8,421</div>
                <div class="stat-label">Daily P&L</div>
                <span class="stat-change positive">+12.3%</span>
            </div>
            <div class="stat-card">
                <div class="stat-value">0.87</div>
                <div class="stat-label">Sharpe Ratio</div>
                <span class="stat-change negative">-0.05</span>
            </div>
        </div>
        <div class="chart-container">
            <h3>Performance Overview</h3>
            <div style="display: flex; justify-content: space-between; margin-top: 20px;">
                <div style="flex: 1; margin-right: 20px;">
                    <div>Tech Stocks (68%)</div>
                    <div class="progress-bar"><div class="progress-fill" style="width: 68%;"></div></div>
                </div>
                <div style="flex: 1;">
                    <div>Fixed Income (32%)</div>
                    <div class="progress-bar"><div class="progress-fill" style="width: 32%;"></div></div>
                </div>
            </div>
        </div>
        <div class="chart-container">
            <h3>Recent Activity</h3>
            <ul style="list-style: none; padding: 0;">
                <li style="padding: 10px 0; border-bottom: 1px solid #eee;">
                    <strong>AAPL</strong> - Bought 100 shares @ $182.50
                    <span style="float: right; color: #666;">2 hours ago</span>
                </li>
                <li style="padding: 10px 0; border-bottom: 1px solid #eee;">
                    <strong>GOOGL</strong> - Sold 50 shares @ $141.20
                    <span style="float: right; color: #666;">5 hours ago</span>
                </li>
                <li style="padding: 10px 0;">
                    <strong>MSFT</strong> - Bought 75 shares @ $378.80
                    <span style="float: right; color: #666;">Yesterday</span>
                </li>
            </ul>
        </div>
    </div>
    <script>
        document.querySelectorAll('.stat-card').forEach(card => {
            card.addEventListener('click', function() {
                this.style.transform = 'scale(1.05)';
                setTimeout(() => { this.style.transform = ''; }, 200);
            });
        });
    </script>
</body>
</html>
""")
