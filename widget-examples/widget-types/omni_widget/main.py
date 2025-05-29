import asyncio
from functools import wraps
from pydantic import BaseModel, Field
import json
from typing import Any, List, Literal
from uuid import UUID
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import List

app = FastAPI()

origins = [
    "https://pro.openbb.co"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Initialize empty dictionary for widgets
WIDGETS = {}

def register_widget(widget_config):
    """
    Decorator that registers a widget configuration in the WIDGETS dictionary.
    
    Args:
        widget_config (dict): The widget configuration to add to the WIDGETS 
            dictionary. This should follow the same structure as other entries 
            in WIDGETS.
    
    Returns:
        function: The decorated function.
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Call the original function
            return await func(*args, **kwargs)
            
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Call the original function
            return func(*args, **kwargs)
        
        # Extract the endpoint from the widget_config
        endpoint = widget_config.get("endpoint")
        if endpoint:
            # Add an id field to the widget_config if not already present
            if "id" not in widget_config:
                widget_config["id"] = endpoint
            
            WIDGETS[endpoint] = widget_config
        
        # Return the appropriate wrapper based on whether the function is async
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    return decorator

@app.get("/")
def read_root():
    return {"Info": "Omni Widget"}

@app.get("/widgets.json")
def get_widgets():
    """Widgets configuration file for the OpenBB Terminal Pro"""
    return WIDGETS

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


class OmniWidgetResponse(BaseModel):
    content: Any
    data_format: DataFormat
    extra_citations: list[ExtraCitation] | None = Field(default_factory=list)
    citable: bool = Field(
        default=True,
        description="Whether the source is citable.",
    )

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
            "description": "The prompt to send to the LLM to make queries or ask questions.",
            "label": "Prompt",
            "show": False
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
                {"value": "table", "label": "Table"}
            ]
        }
    ],
    "gridData": {"w": 30, "h": 12}
})
@app.post("/omni-widget")
async def get_omni_widget_post(
    data: str | dict = Body(...)
):
    if isinstance(data, str):
        data = json.loads(data)

    """Basic Omni Widget example showing different return types without citations"""

    if data.get("type") == "table":
        content = [
                {"col1": "value1", "col2": "value2", "col3": "value3", "col4": "value4"},
                {"col1": "value1", "col2": "value2", "col3": "value3", "col4": "value4"},
                {"col1": "value1", "col2": "value2", "col3": "value3", "col4": "value4"},
                {"col1": "value1", "col2": "value2", "col3": "value3", "col4": "value4"},
                {"col1": "value1", "col2": "value2", "col3": "value3", "col4": "value4"},
                {"col1": "value1", "col2": "value2", "col3": "value3", "col4": "value4"},
                {"col1": "value1", "col2": "value2", "col3": "value3", "col4": "value4"},
                {"col1": "value1", "col2": "value2", "col3": "value3", "col4": "value4"},
                {"col1": "value1", "col2": "value2", "col3": "value3", "col4": "value4"},
            ]

        return OmniWidgetResponse(
                content=content,
                data_format=DataFormat(data_type="object", parse_as="table"),
                citable=False
            )

    if data.get("type") == "chart":
        content = {
                "data": [
                    {"x": [1, 2, 3], "y": [4, 1, 2], "type": "bar"},
                    {"x": [1, 2, 3], "y": [2, 4, 5], "type": "bar"},
                    {"x": [1, 2, 3], "y": [2, 3, 6], "type": "bar"},
                ],
                "layout": {
                    "title": "Great Plot",
                    "template": "plotly_dark"
                },
            }

        return OmniWidgetResponse(
                content=content,
                data_format=DataFormat(data_type="object", parse_as="chart"),
                citable=False
            )

    # Default to markdown without citations
    content = f"""### Basic Omni Widget Response

**Input Parameters:**
- **Prompt:** `{data.get('prompt', 'No prompt provided')}`
- **Type:** `{data.get('type', 'markdown')}`

#### Raw Data:
```json
{json.dumps(data, indent=2)}
```

This is a basic omni widget response without citation tracking.
"""
    
    return OmniWidgetResponse(
        content=content,
        data_format=DataFormat(data_type="object", parse_as="text"),
        citable=False
    )



## This is an example of an omni widget that includes citation information for data tracking
## This is useful when you are interacting with an AI Agent and want to pass citations in the chat.
@register_widget({
    "name": "Omni Widget with Citations",
    "description": "An omni widget that includes citation information for data tracking",
    "category": "General",
    "type": "omni",
    "endpoint": "omni-widget-with-citations",
    "params": [
        {
            "paramName": "prompt",
            "type": "text",
            "description": "The prompt to send to the LLM to make queries or ask questions.",
            "label": "Prompt",
            "show": False
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
                {"value": "table", "label": "Table"}
            ]
        },
        {
            "paramName": "include_metadata",
            "type": "boolean",
            "description": "Include metadata in response",
            "label": "Include Metadata",
            "show": True,
            "value": True
        }
    ],
    "gridData": {"w": 30, "h": 15}
})
@app.post("/omni-widget-with-citations")
async def get_omni_widget_with_citations(
    data: str | dict = Body(...)
):
    if isinstance(data, str):
        data = json.loads(data)

    """Omni Widget example with citation support"""

    # Create citation information
    source_info = SourceInfo(
        type="widget",
        widget_id=data.get("widget_id", "omni_widget_citations"),
        origin=data.get("widget_origin", "omni_widget"),
        name="Omni Widget with Citations",
        description="Example widget demonstrating citation functionality",
        metadata={
            "filename": "omni_widget_response.md",
            "extension": "md",
            "input_args": data,
            "timestamp": data.get("timestamp", "")
        }
    )
    
    extra_citation = ExtraCitation(
        source_info=source_info,
        details=[
            {
                "Name": "Omni Widget with Citations",
                "Query": data.get("prompt"),
                "Type": data.get("type"),
                "Timestamp": data.get("timestamp", ""),
                "Data": json.dumps(data, indent=2)
            }
        ]
    )

    if data.get("type") == "table":
        content = [
            {"source": "Citation Example", "value": "123", "description": "Sample data with citation"},
            {"source": "Citation Example", "value": "456", "description": "More sample data"},
            {"source": "Citation Example", "value": "789", "description": "Additional sample data"},
        ]

        return OmniWidgetResponse(
            content=content,
            data_format=DataFormat(data_type="object", parse_as="table"),
            extra_citations=[extra_citation],
            citable=True
        )

    if data.get("type") == "chart":
        content = {
            "data": [
                {"x": [1, 2, 3], "y": [4, 1, 2], "type": "bar", "name": "Cited Data Series 1"},
                {"x": [1, 2, 3], "y": [2, 4, 5], "type": "bar", "name": "Cited Data Series 2"},
            ],
            "layout": {
                "title": "Chart with Citation Support",
                "template": "plotly_dark"
            },
        }

        return OmniWidgetResponse(
            content=content,
            data_format=DataFormat(data_type="object", parse_as="chart"),
            extra_citations=[extra_citation],
            citable=True
        )

    # Default to markdown with citations
    content = f"""### Omni Widget with Citation Support

**Input Parameters:**
- **Prompt:** `{data.get('prompt', 'No prompt provided')}`
- **Type:** `{data.get('type', 'markdown')}`

#### Data with Citation Tracking: 
This response includes citation information that will be automatically tracked and made available to agents and users.

**Citation Details:**
- **Name:** {source_info.name}
- **Origin:** {source_info.origin}
- **Timestamp:** {data.get('timestamp', 'Not provided')}
"""

    if data.get("include_metadata"):
        content += f"""

#### Additional Metadata:
- **Include Metadata:** {data.get('include_metadata')}
- **Full Input Data:**

```json
{json.dumps(data, indent=2)}
```
"""

    return OmniWidgetResponse(
        content=content,
        data_format=DataFormat(data_type="object", parse_as="text"),
        extra_citations=[extra_citation],
        citable=True
    )
