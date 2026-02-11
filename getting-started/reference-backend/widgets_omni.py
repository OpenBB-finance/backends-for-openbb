"""
Omni Widgets for OpenBB Workspace

This module demonstrates Omni widgets that can return multiple content types:
- Markdown: Rich text content
- Table: Tabular data
- Chart: Plotly charts
- Citations: Source tracking for AI context

Omni widgets are versatile and can dynamically return different content
types based on parameters or user interaction.
"""

import json
from fastapi import APIRouter, Body
import plotly.graph_objects as go

from core import (
    register_widget, WIDGETS,
    DataFormat, SourceInfo, ExtraCitation, OmniWidgetResponse
)
from widgets_plotly_chart import base_layout, get_toolbar_config

router = APIRouter()


# ============================================================================
# BASIC OMNI WIDGET
# ============================================================================

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
    """Basic Omni Widget example showing different return types without citations"""
    if isinstance(data, str):
        data = json.loads(data)

    if data.get("type") == "table":
        content = [
            {"col1": "value1", "col2": "value2", "col3": "value3", "col4": "value4"},
            {"col1": "value1", "col2": "value2", "col3": "value3", "col4": "value4"},
            {"col1": "value1", "col2": "value2", "col3": "value3", "col4": "value4"},
            {"col1": "value1", "col2": "value2", "col3": "value3", "col4": "value4"},
        ]

        return OmniWidgetResponse(
            content=content,
            data_format=DataFormat(data_type="object", parse_as="table"),
            citable=False,
        )

    if data.get("type") == "chart":
        fig = go.Figure()

        fig.add_trace(
            go.Bar(x=["A", "B", "C"], y=[4, 1, 2], name="Series 1", marker_color="#26a69a")
        )
        fig.add_trace(
            go.Bar(x=["A", "B", "C"], y=[2, 4, 5], name="Series 2", marker_color="#ef5350")
        )
        fig.add_trace(
            go.Bar(x=["A", "B", "C"], y=[2, 3, 6], name="Series 3", marker_color="#f0a500")
        )

        base_layout_config = base_layout(theme="dark")
        base_layout_config.update({
            "font": {"color": "#216df1"},
            "title": {"font": {"color": "#216df1"}},
        })
        fig.update_layout(**base_layout_config)
        fig.update_layout(
            title="Plotly Chart example",
            bargap=0.15,
            bargroupgap=0.1,
            margin=dict(t=50),
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.2,
                xanchor="center",
                x=0.5,
                font=dict(color="#216df1"),
                bgcolor="rgba(0,0,0,0)",
            ),
        )

        content = json.loads(fig.to_json())
        content["config"] = get_toolbar_config()

        return OmniWidgetResponse(
            content=content,
            data_format=DataFormat(data_type="object", parse_as="chart"),
            citable=False,
        )

    # Default to markdown
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
        citable=False,
    )


# ============================================================================
# OMNI WIDGET WITH CITATIONS
# ============================================================================

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
        {
            "paramName": "include_metadata",
            "type": "boolean",
            "description": "Include metadata in response",
            "label": "Include Metadata",
            "show": True,
            "value": True,
        },
    ],
    "gridData": {"w": 30, "h": 15},
})
@router.post("/omni-widget-with-citations")
async def get_omni_widget_with_citations(data: str | dict = Body(...)):
    """Omni Widget example with citation support"""
    if isinstance(data, str):
        data = json.loads(data)

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
            "timestamp": data.get("timestamp", ""),
        },
    )

    extra_citation = ExtraCitation(
        source_info=source_info,
        details=[{
            "Name": "Omni Widget with Citations",
            "Query": data.get("prompt"),
            "Type": data.get("type"),
            "Timestamp": data.get("timestamp", ""),
            "Data": json.dumps(data, indent=2),
        }],
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
            citable=True,
        )

    if data.get("type") == "chart":
        fig = go.Figure()

        fig.add_trace(
            go.Bar(x=["A", "B", "C"], y=[4, 1, 2], name="Cited Data Series 1", marker_color="#26a69a")
        )
        fig.add_trace(
            go.Bar(x=["A", "B", "C"], y=[2, 4, 5], name="Cited Data Series 2", marker_color="#ef5350")
        )
        fig.add_trace(
            go.Bar(x=["A", "B", "C"], y=[2, 3, 6], name="Cited Data Series 3", marker_color="#f0a500")
        )

        base_layout_config = base_layout(theme="dark")
        base_layout_config.update({
            "font": {"color": "#216df1"},
            "title": {"font": {"color": "#216df1"}},
        })
        fig.update_layout(**base_layout_config)
        fig.update_layout(
            title="Chart with Citation Support",
            bargap=0.15,
            bargroupgap=0.1,
            margin=dict(t=50),
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.2,
                xanchor="center",
                x=0.5,
                font=dict(color="#216df1"),
                bgcolor="rgba(0,0,0,0)",
            ),
        )

        content = json.loads(fig.to_json())
        content["config"] = get_toolbar_config()

        return OmniWidgetResponse(
            content=content,
            data_format=DataFormat(data_type="object", parse_as="chart"),
            extra_citations=[extra_citation],
            citable=True,
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
        citable=True,
    )
