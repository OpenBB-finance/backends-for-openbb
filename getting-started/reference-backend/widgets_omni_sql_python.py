import json
import sqlite3
import re
from fastapi import APIRouter, Body
import plotly.graph_objects as go

from core import (
    register_widget, WIDGETS,
    DataFormat, SourceInfo, ExtraCitation, OmniWidgetResponse
)
from widgets_plotly_chart import base_layout, get_toolbar_config

# Mock data for SQL widget
MOCK_DATA = [
    {"id": 1, "symbol": "AAPL", "name": "Apple Inc.", "price": 150.25, "volume": 45000000, "sector": "Technology"},
    {"id": 2, "symbol": "MSFT", "name": "Microsoft Corporation", "price": 350.50, "volume": 32000000, "sector": "Technology"},
    {"id": 3, "symbol": "GOOGL", "name": "Alphabet Inc.", "price": 140.75, "volume": 28000000, "sector": "Technology"},
    {"id": 4, "symbol": "AMZN", "name": "Amazon.com Inc.", "price": 178.25, "volume": 38000000, "sector": "Consumer Cyclical"},
    {"id": 5, "symbol": "TSLA", "name": "Tesla Inc.", "price": 245.80, "volume": 52000000, "sector": "Automotive"},
    {"id": 6, "symbol": "JPM", "name": "JPMorgan Chase", "price": 195.30, "volume": 12000000, "sector": "Financial"},
    {"id": 7, "symbol": "V", "name": "Visa Inc.", "price": 275.40, "volume": 8000000, "sector": "Financial"},
    {"id": 8, "symbol": "JNJ", "name": "Johnson & Johnson", "price": 155.60, "volume": 6500000, "sector": "Healthcare"},
    {"id": 9, "symbol": "WMT", "name": "Walmart Inc.", "price": 165.20, "volume": 7200000, "sector": "Consumer Defensive"},
    {"id": 10, "symbol": "PG", "name": "Procter & Gamble", "price": 158.90, "volume": 5800000, "sector": "Consumer Defensive"},
]

router = APIRouter()


@register_widget({
    "name": "Basic Omni Widget",
    "description": "A versatile omni widget that can display multiple types of content",
    "category": "General",
    "type": "omni",
    "endpoint": "omni-widget",
    "params": [
        {
            "paramName": "prompt",
            "type": "text",
            "description": "The prompt to send to the widget to make queries, ask questions or simply interact with it. This is required in order to get a response.",
            "label": "Prompt",
            "show": False,
        },
        {
            "paramName": "type",
            "type": "text",
            "description": "Type of content to return",
            "label": "Content Type",
            "show": True,
            "options": [
                {"value": "markdown", "label": "Markdown"},
                {"value": "chart", "label": "Chart"},
                {"value": "table", "label": "Table"},
            ],
        },
    ],
    "gridData": {"w": 30, "h": 12},
})
@router.post("/omni-widget")
async def get_omni_widget_post(data: str | dict = Body(...)):
    """Basic Omni Widget example showing different return types"""
    if isinstance(data, str):
        data = json.loads(data)

    prompt = data.get("prompt", "Hello World")

    if data.get("type") == "table":
        # 2x2 matrix with prompt value in all cells
        content = [
            {"col1": prompt, "col2": prompt},
            {"col1": prompt, "col2": prompt},
        ]
        return OmniWidgetResponse(
            content=content,
            data_format=DataFormat(data_type="object", parse_as="table"),
            citable=False,
        )

    if data.get("type") == "chart":
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(x=[1, 2, 3], y=[1, 3, 2], mode="lines", line=dict(color="#26a69a"))
        )

        base_layout_config = base_layout(theme="light")
        fig.update_layout(**base_layout_config)
        fig.update_layout(title=prompt, showlegend=False, margin=dict(b=10))

        content = json.loads(fig.to_json())
        content["config"] = get_toolbar_config()

        return OmniWidgetResponse(
            content=content,
            data_format=DataFormat(data_type="object", parse_as="chart"),
            citable=False,
        )

    # Default to markdown - just output the prompt
    return OmniWidgetResponse(
        content=prompt,
        data_format=DataFormat(data_type="object", parse_as="text"),
        citable=False,
    )


def execute_sql_on_mock_data(sql: str) -> list[dict]:
    """Execute SQL query against mock data using in-memory SQLite"""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Create table and insert mock data
    cursor.execute("""
        CREATE TABLE stocks (
            id INTEGER,
            symbol TEXT,
            name TEXT,
            price REAL,
            volume INTEGER,
            sector TEXT
        )
    """)

    for row in MOCK_DATA:
        cursor.execute(
            "INSERT INTO stocks VALUES (?, ?, ?, ?, ?, ?)",
            (row["id"], row["symbol"], row["name"], row["price"], row["volume"], row["sector"])
        )
    conn.commit()

    # Execute the user's query (replace DATA with stocks)
    normalized_sql = re.sub(r'\bDATA\b', 'stocks', sql, flags=re.IGNORECASE)
    cursor.execute(normalized_sql)
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


@register_widget({
    "name": "SQL Query Widget",
    "description": "Execute SQL queries against mock stock data. Use 'DATA' as the table name.",
    "category": "General",
    "type": "omni",
    "endpoint": "omni-sql-widget",
    "params": [
        {
            "paramName": "prompt",
            "type": "text",
            "description": "Enter a SQL query to execute against the mock data. Use 'DATA' as the table name. Available columns: id, symbol, name, price, volume, sector",
            "label": "SQL Query",
            "value": "SELECT * FROM DATA LIMIT 5",
            "show": False,
            "language": "sql"
        }
    ],
    "gridData": {"w": 30, "h": 12},
})
@router.post("/omni-sql-widget")
async def get_omni_sql_widget(data: str | dict = Body(...)):
    """SQL Query Widget - executes SQL against mock stock data"""
    if isinstance(data, str):
        data = json.loads(data)

    sql_query = data.get("prompt", "SELECT * FROM DATA LIMIT 5")

    try:
        results = execute_sql_on_mock_data(sql_query)

        if not results:
            return OmniWidgetResponse(
                content="No results found for the query.",
                data_format=DataFormat(data_type="object", parse_as="text"),
                citable=False,
            )

        return OmniWidgetResponse(
            content=results,
            data_format=DataFormat(data_type="object", parse_as="table"),
            citable=False,
        )

    except Exception as e:
        error_content = f"""### SQL Query Error

**Query:** `{sql_query}`

**Error:** {str(e)}

**Available columns:** id, symbol, name, price, volume, sector

**Example queries:**
- `SELECT * FROM DATA LIMIT 5`
- `SELECT symbol, price FROM DATA WHERE sector = 'Technology'`
- `SELECT sector, AVG(price) as avg_price FROM DATA GROUP BY sector`
"""
        return OmniWidgetResponse(
            content=error_content,
            data_format=DataFormat(data_type="object", parse_as="text"),
            citable=False,
        )


DEFAULT_PYTHON_CODE = '''# Create a simple bar chart
fig = go.Figure()

fig.add_trace(go.Bar(
    x=["Q1", "Q2", "Q3", "Q4"],
    y=[100, 150, 130, 180],
    name="Revenue",
    marker_color="#26a69a"
))

fig.add_trace(go.Bar(
    x=["Q1", "Q2", "Q3", "Q4"],
    y=[80, 120, 110, 150],
    name="Profit",
    marker_color="#ef5350"
))

fig.update_layout(
    title="Quarterly Performance",
    barmode="group",
    xaxis_title="Quarter",
    yaxis_title="Amount ($M)"
)'''


@register_widget({
    "name": "Python Chart Widget",
    "description": "Write Python code to create Plotly charts. Use 'fig' as the figure variable.",
    "category": "General",
    "type": "omni",
    "endpoint": "omni-python-widget",
    "params": [
        {
            "paramName": "prompt",
            "type": "text",
            "description": "Enter Python code to create a Plotly chart. Use 'go' for plotly.graph_objects and assign your figure to 'fig'.",
            "label": "Python Code",
            "value": DEFAULT_PYTHON_CODE,
            "show": False,
            "language": "python"
        }
    ],
    "gridData": {"w": 30, "h": 12},
})
@router.post("/omni-python-widget")
async def get_omni_python_widget(data: str | dict = Body(...)):
    """Python Chart Widget - executes Python code to create Plotly charts"""
    if isinstance(data, str):
        data = json.loads(data)

    python_code = data.get("prompt", DEFAULT_PYTHON_CODE)

    try:
        # Create a restricted namespace for execution
        namespace = {"go": go}
        exec(python_code, namespace)

        fig = namespace.get("fig")
        if fig is None:
            return OmniWidgetResponse(
                content="Error: No 'fig' variable found. Please assign your Plotly figure to 'fig'.",
                data_format=DataFormat(data_type="object", parse_as="text"),
                citable=False,
            )

        # Apply base layout with light theme
        base_layout_config = base_layout(theme="light")
        fig.update_layout(**base_layout_config)

        content = json.loads(fig.to_json())
        content["config"] = get_toolbar_config()

        return OmniWidgetResponse(
            content=content,
            data_format=DataFormat(data_type="object", parse_as="chart"),
            citable=False,
        )

    except Exception as e:
        error_content = f"""### Python Execution Error

**Error:** {str(e)}

**Your code:**
```python
{python_code}
```

**Example code:**
```python
fig = go.Figure()
fig.add_trace(go.Bar(x=["A", "B", "C"], y=[1, 2, 3]))
fig.update_layout(title="My Chart")
```
"""
        return OmniWidgetResponse(
            content=error_content,
            data_format=DataFormat(data_type="object", parse_as="text"),
            citable=False,
        )
