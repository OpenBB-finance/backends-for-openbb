import json
from datetime import datetime
from fastapi import APIRouter
import plotly.graph_objects as go

from core import register_widget, WIDGETS

router = APIRouter()

def get_theme_colors(theme: str = "dark") -> dict:
    """Get color palette based on theme."""
    if theme == "dark":
        return {
            "main_line": "#FF8000",
            "secondary_line": "#2D9BF0",
            "neutral": "#6B7280",
            "positive": "#22C55E",
            "negative": "#EF4444",
            "text": "#FFFFFF",
            "grid": "rgba(51, 51, 51, 0.3)",
            "background": "#151518",
            "heatmap": {"zmid": 0, "text_color": "#FFFFFF"},
        }
    return {
        "main_line": "#2E5090",
        "secondary_line": "#00AA44",
        "neutral": "#6B7280",
        "positive": "#22C55E",
        "negative": "#EF4444",
        "text": "#333333",
        "grid": "rgba(221, 221, 221, 0.3)",
        "background": "#FFFFFF",
        "heatmap": {"zmid": 0, "text_color": "#333333"},
    }


def base_layout(theme: str = "dark", **kwargs) -> dict:
    """Get base layout configuration for Plotly charts."""
    colors = get_theme_colors(theme)
    layout = {
        "paper_bgcolor": colors["background"],
        "plot_bgcolor": colors["background"],
        "font": {"color": colors["text"]},
        "xaxis": {
            "gridcolor": colors["grid"],
            "tickfont": {"color": colors["text"]},
        },
        "yaxis": {
            "gridcolor": colors["grid"],
            "tickfont": {"color": colors["text"]},
        },
        "legend": {
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "right",
            "x": 1,
            "font": {"color": colors["text"]},
        },
    }
    layout.update(kwargs)
    return layout


def get_toolbar_config() -> dict:
    """Get toolbar configuration for Plotly charts."""
    return {
        "displayModeBar": True,
        "responsive": True,
        "scrollZoom": True,
        "modeBarButtonsToRemove": [
            "lasso2d",
            "select2d",
            "autoScale2d",
            "toggleSpikelines",
            "hoverClosestCartesian",
            "hoverCompareCartesian",
        ],
        "modeBarButtonsToAdd": ["drawline", "drawcircle", "drawrect", "eraseshape"],
        "doubleClick": "reset+autosize",
        "showTips": True,
        "displaylogo": False,
    }


@register_widget({
    "name": "Plotly Chart",
    "description": "A basic Plotly chart widget",
    "type": "chart",
    "endpoint": "plotly_chart",
    "gridData": {"w": 40, "h": 15},
})
@router.get("/plotly_chart")
def get_plotly_chart():
    """Returns a basic Plotly chart"""
    mock_data = [
        {"date": "2023-01-01", "return": 2.5, "transactions": 1250},
        {"date": "2023-01-02", "return": -1.2, "transactions": 1580},
        {"date": "2023-01-03", "return": 3.1, "transactions": 1820},
        {"date": "2023-01-04", "return": 0.8, "transactions": 1450},
        {"date": "2023-01-05", "return": -2.3, "transactions": 1650},
        {"date": "2023-01-06", "return": 1.5, "transactions": 1550},
        {"date": "2023-01-07", "return": 2.8, "transactions": 1780},
        {"date": "2023-01-08", "return": -0.9, "transactions": 1620},
        {"date": "2023-01-09", "return": 1.2, "transactions": 1480},
        {"date": "2023-01-10", "return": 3.5, "transactions": 1920},
    ]

    dates = [datetime.strptime(d["date"], "%Y-%m-%d") for d in mock_data]
    returns = [d["return"] for d in mock_data]
    transactions = [d["transactions"] for d in mock_data]

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=dates,
            y=returns,
            mode="lines",
            name="Returns",
            line=dict(width=2, color="#FF8000"),
        )
    )

    fig.add_trace(
        go.Bar(
            x=dates,
            y=transactions,
            name="Transactions",
            opacity=0.5,
            marker_color="#2D9BF0",
        )
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Returns (%)",
        yaxis2=dict(
            title="Transactions",
            overlaying="y",
            side="right",
        ),
        paper_bgcolor="#151518",
        plot_bgcolor="#151518",
        font=dict(color="#FFFFFF"),
    )

    fig.data[1].update(yaxis="y2")

    return json.loads(fig.to_json())


@register_widget({
    "name": "Plotly Chart with Theme",
    "description": "Plotly chart with theme support",
    "type": "chart",
    "endpoint": "plotly_chart_with_theme",
    "gridData": {"w": 40, "h": 15},
})
@router.get("/plotly_chart_with_theme")
def get_plotly_chart_with_theme(theme: str = "dark"):
    """Returns a Plotly chart with theme support"""
    mock_data = [
        {"date": "2023-01-01", "return": 2.5, "transactions": 1250},
        {"date": "2023-01-02", "return": -1.2, "transactions": 1580},
        {"date": "2023-01-03", "return": 3.1, "transactions": 1820},
        {"date": "2023-01-04", "return": 0.8, "transactions": 1450},
        {"date": "2023-01-05", "return": -2.3, "transactions": 1650},
        {"date": "2023-01-06", "return": 1.5, "transactions": 1550},
        {"date": "2023-01-07", "return": 2.8, "transactions": 1780},
        {"date": "2023-01-08", "return": -0.9, "transactions": 1620},
        {"date": "2023-01-09", "return": 1.2, "transactions": 1480},
        {"date": "2023-01-10", "return": 3.5, "transactions": 1920},
    ]

    dates = [datetime.strptime(d["date"], "%Y-%m-%d") for d in mock_data]
    returns = [d["return"] for d in mock_data]
    transactions = [d["transactions"] for d in mock_data]

    fig = go.Figure()
    colors = get_theme_colors(theme)

    fig.add_trace(
        go.Scatter(
            x=dates,
            y=returns,
            mode="lines",
            name="Returns",
            line=dict(width=2, color=colors["main_line"]),
        )
    )

    fig.add_trace(
        go.Bar(
            x=dates,
            y=transactions,
            name="Transactions",
            opacity=0.5,
            marker_color=colors["secondary_line"],
        )
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Returns (%)",
        yaxis2=dict(
            title="Transactions",
            overlaying="y",
            side="right",
            gridcolor=colors["grid"],
            tickfont=dict(color=colors["text"]),
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color=colors["text"]),
        ),
        paper_bgcolor=colors["background"],
        plot_bgcolor=colors["background"],
        font=dict(color=colors["text"]),
        xaxis=dict(gridcolor=colors["grid"], tickfont=dict(color=colors["text"])),
        yaxis=dict(gridcolor=colors["grid"], tickfont=dict(color=colors["text"])),
    )

    fig.data[1].update(yaxis="y2")

    return json.loads(fig.to_json())


@register_widget({
    "name": "Plotly Chart with Theme and Toolbar",
    "description": "Plotly chart with Theme and toolbar",
    "type": "chart",
    "endpoint": "plotly_chart_with_theme_and_toolbar",
    "gridData": {"w": 40, "h": 15},
})
@router.get("/plotly_chart_with_theme_and_toolbar")
def get_plotly_chart_with_theme_and_toolbar(theme: str = "dark"):
    """Returns a Plotly chart with theme and toolbar"""
    mock_data = [
        {"date": "2023-01-01", "return": 2.5, "transactions": 1250},
        {"date": "2023-01-02", "return": -1.2, "transactions": 1580},
        {"date": "2023-01-03", "return": 3.1, "transactions": 1820},
        {"date": "2023-01-04", "return": 0.8, "transactions": 1450},
        {"date": "2023-01-05", "return": -2.3, "transactions": 1650},
        {"date": "2023-01-06", "return": 1.5, "transactions": 1550},
        {"date": "2023-01-07", "return": 2.8, "transactions": 1780},
        {"date": "2023-01-08", "return": -0.9, "transactions": 1620},
        {"date": "2023-01-09", "return": 1.2, "transactions": 1480},
        {"date": "2023-01-10", "return": 3.5, "transactions": 1920},
    ]

    dates = [datetime.strptime(d["date"], "%Y-%m-%d") for d in mock_data]
    returns = [d["return"] for d in mock_data]
    transactions = [d["transactions"] for d in mock_data]

    fig = go.Figure()
    colors = get_theme_colors(theme)

    fig.add_trace(
        go.Scatter(
            x=dates,
            y=returns,
            mode="lines",
            name="Returns",
            line=dict(width=2, color=colors["main_line"]),
        )
    )

    fig.add_trace(
        go.Bar(
            x=dates,
            y=transactions,
            name="Transactions",
            opacity=0.5,
            marker_color=colors["secondary_line"],
        )
    )

    fig.update_layout(**base_layout(theme=theme))
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Returns (%)",
        yaxis2=dict(
            title="Transactions",
            overlaying="y",
            side="right",
            gridcolor=colors["grid"],
            tickfont=dict(color=colors["text"]),
        ),
    )

    fig.data[1].update(yaxis="y2")

    figure_json = json.loads(fig.to_json())
    figure_json["config"] = get_toolbar_config()

    return figure_json


@register_widget({
    "name": "Plotly Chart with Theme and Toolbar using Config File",
    "description": "Plotly chart with theme and toolbar using config file",
    "type": "chart",
    "endpoint": "plotly_chart_with_theme_and_toolbar_using_config_file",
    "gridData": {"w": 40, "h": 15},
})
@router.get("/plotly_chart_with_theme_and_toolbar_using_config_file")
def get_plotly_chart_with_theme_and_toolbar_using_config_file(theme: str = "dark"):
    """Returns a Plotly chart using config helpers for cleaner code"""
    mock_data = [
        {"date": "2023-01-01", "return": 2.5, "transactions": 1250},
        {"date": "2023-01-02", "return": -1.2, "transactions": 1580},
        {"date": "2023-01-03", "return": 3.1, "transactions": 1820},
        {"date": "2023-01-04", "return": 0.8, "transactions": 1450},
        {"date": "2023-01-05", "return": -2.3, "transactions": 1650},
        {"date": "2023-01-06", "return": 1.5, "transactions": 1550},
        {"date": "2023-01-07", "return": 2.8, "transactions": 1780},
        {"date": "2023-01-08", "return": -0.9, "transactions": 1620},
        {"date": "2023-01-09", "return": 1.2, "transactions": 1480},
        {"date": "2023-01-10", "return": 3.5, "transactions": 1920},
    ]

    dates = [datetime.strptime(d["date"], "%Y-%m-%d") for d in mock_data]
    returns = [d["return"] for d in mock_data]
    transactions = [d["transactions"] for d in mock_data]

    colors = get_theme_colors(theme)
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=dates,
            y=returns,
            mode="lines",
            name="Returns",
            line=dict(width=2, color=colors["main_line"]),
        )
    )

    fig.add_trace(
        go.Bar(
            x=dates,
            y=transactions,
            name="Transactions",
            opacity=0.5,
            marker_color=colors["neutral"],
        )
    )

    fig.update_layout(**base_layout(theme=theme))
    fig.update_layout(
        yaxis2=dict(
            title="Transactions",
            overlaying="y",
            side="right",
            gridcolor=colors["grid"],
            tickfont=dict(color=colors["text"]),
        )
    )

    fig.data[1].update(yaxis="y2")

    figure_json = json.loads(fig.to_json())
    figure_json["config"] = get_toolbar_config()

    return figure_json


@register_widget({
    "name": "Plotly Heatmap",
    "description": "Plotly heatmap",
    "type": "chart",
    "endpoint": "plotly_heatmap",
    "gridData": {"w": 40, "h": 15},
    "params": [{
        "paramName": "color_scale",
        "description": "Select the color scale for the heatmap",
        "value": "RdBu_r",
        "label": "Color Scale",
        "type": "text",
        "show": True,
        "options": [
            {"label": "Red-Blue (RdBu_r)", "value": "RdBu_r"},
            {"label": "Viridis", "value": "Viridis"},
            {"label": "Plasma", "value": "Plasma"},
            {"label": "Inferno", "value": "Inferno"},
            {"label": "Magma", "value": "Magma"},
            {"label": "Greens", "value": "Greens"},
            {"label": "Blues", "value": "Blues"},
            {"label": "Reds", "value": "Reds"},
        ],
    }],
})
@router.get("/plotly_heatmap")
def get_plotly_heatmap(color_scale: str = "RdBu_r", theme: str = "dark"):
    """Returns a Plotly heatmap correlation matrix"""
    symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
    corr_matrix = [
        [1.00, 0.65, 0.45, 0.30, 0.20],
        [0.65, 1.00, 0.55, 0.40, 0.25],
        [0.45, 0.55, 1.00, 0.35, 0.15],
        [0.30, 0.40, 0.35, 1.00, 0.10],
        [0.20, 0.25, 0.15, 0.10, 1.00],
    ]

    colors = get_theme_colors(theme)
    fig = go.Figure()

    layout_config = base_layout(theme=theme)
    layout_config["title"] = {
        "text": "Correlation Matrix",
        "x": 0.5,
        "y": 0.95,
        "xanchor": "center",
        "yanchor": "top",
        "font": {"size": 20},
    }
    layout_config["margin"] = {"t": 50, "b": 50, "l": 50, "r": 50}
    fig.update_layout(layout_config)

    fig.add_trace(
        go.Heatmap(
            z=corr_matrix,
            x=symbols,
            y=symbols,
            colorscale=color_scale,
            zmid=colors["heatmap"]["zmid"],
            text=[[f"{val:.2f}" for val in row] for row in corr_matrix],
            texttemplate="%{text}",
            textfont={"color": colors["heatmap"]["text_color"]},
            hoverongaps=False,
            hovertemplate="%{x} - %{y}<br>Correlation: %{z:.2f}<extra></extra>",
        )
    )

    figure_json = json.loads(fig.to_json())
    figure_json["config"] = {**get_toolbar_config(), "scrollZoom": False}

    return figure_json


@register_widget({
    "name": "Plotly Heatmap with Raw Data",
    "description": "Plotly heatmap with raw data",
    "type": "chart",
    "endpoint": "plotly_heatmap_with_raw_data",
    "gridData": {"w": 40, "h": 15},
    "raw": True,
    "params": [{
        "paramName": "color_scale",
        "description": "Select the color scale for the heatmap",
        "value": "RdBu_r",
        "label": "Color Scale",
        "type": "text",
        "show": True,
        "options": [
            {"label": "Red-Blue (RdBu_r)", "value": "RdBu_r"},
            {"label": "Viridis", "value": "Viridis"},
            {"label": "Plasma", "value": "Plasma"},
            {"label": "Inferno", "value": "Inferno"},
            {"label": "Magma", "value": "Magma"},
            {"label": "Greens", "value": "Greens"},
            {"label": "Blues", "value": "Blues"},
            {"label": "Reds", "value": "Reds"},
        ],
    }],
})
@router.get("/plotly_heatmap_with_raw_data")
def get_plotly_heatmap_with_raw_data(
    color_scale: str = "RdBu_r", raw: bool = False, theme: str = "dark"
):
    """Returns a Plotly heatmap with raw data option for AI analysis"""
    symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
    corr_matrix = [
        [1.00, 0.65, 0.45, 0.30, 0.20],
        [0.65, 1.00, 0.55, 0.40, 0.25],
        [0.45, 0.55, 1.00, 0.35, 0.15],
        [0.30, 0.40, 0.35, 1.00, 0.10],
        [0.20, 0.25, 0.15, 0.10, 1.00],
    ]

    if raw:
        data = []
        for i, symbol1 in enumerate(symbols):
            for j, symbol2 in enumerate(symbols):
                data.append({
                    "symbol1": symbol1,
                    "symbol2": symbol2,
                    "correlation": corr_matrix[i][j],
                })
        return data

    colors = get_theme_colors(theme)
    fig = go.Figure()

    layout_config = base_layout(theme=theme)
    layout_config["title"] = {
        "text": "Correlation Matrix",
        "x": 0.5,
        "y": 0.95,
        "xanchor": "center",
        "yanchor": "top",
        "font": {"size": 20},
    }
    layout_config["margin"] = {"t": 50, "b": 50, "l": 50, "r": 50}
    fig.update_layout(layout_config)

    fig.add_trace(
        go.Heatmap(
            z=corr_matrix,
            x=symbols,
            y=symbols,
            colorscale=color_scale,
            zmid=colors["heatmap"]["zmid"],
            text=[[f"{val:.2f}" for val in row] for row in corr_matrix],
            texttemplate="%{text}",
            textfont={"color": colors["heatmap"]["text_color"]},
            hoverongaps=False,
            hovertemplate="%{x} - %{y}<br>Correlation: %{z:.2f}<extra></extra>",
        )
    )

    figure_json = json.loads(fig.to_json())
    figure_json["config"] = {**get_toolbar_config(), "scrollZoom": False}

    return figure_json


# ============================================================================
# PLOTLY CHART WITH RAW DATA
# ============================================================================

@register_widget({
    "name": "Plotly Chart with Raw Data",
    "description": "Plotly chart with raw data support for AI analysis",
    "type": "chart",
    "endpoint": "plotly_chart_with_raw_data",
    "gridData": {"w": 40, "h": 15},
    "raw": True,
})
@router.get("/plotly_chart_with_raw_data")
def get_plotly_chart_with_raw_data(raw: bool = False, theme: str = "dark"):
    """Returns a Plotly chart with raw data option for AI analysis"""
    mock_data = [
        {"date": "2023-01-01", "return": 2.5, "transactions": 1250},
        {"date": "2023-01-02", "return": -1.2, "transactions": 1580},
        {"date": "2023-01-03", "return": 3.1, "transactions": 1820},
        {"date": "2023-01-04", "return": 0.8, "transactions": 1450},
        {"date": "2023-01-05", "return": -2.3, "transactions": 1650},
        {"date": "2023-01-06", "return": 1.5, "transactions": 1550},
        {"date": "2023-01-07", "return": 2.8, "transactions": 1780},
        {"date": "2023-01-08", "return": -0.9, "transactions": 1620},
        {"date": "2023-01-09", "return": 1.2, "transactions": 1480},
        {"date": "2023-01-10", "return": 3.5, "transactions": 1920},
    ]

    if raw:
        return mock_data

    dates = [datetime.strptime(d["date"], "%Y-%m-%d") for d in mock_data]
    returns = [d["return"] for d in mock_data]
    transactions = [d["transactions"] for d in mock_data]

    fig = go.Figure()
    colors = get_theme_colors(theme)

    fig.add_trace(
        go.Scatter(
            x=dates,
            y=returns,
            mode="lines",
            name="Returns",
            line=dict(width=2, color=colors["main_line"]),
        )
    )

    fig.add_trace(
        go.Bar(
            x=dates,
            y=transactions,
            name="Transactions",
            opacity=0.5,
            marker_color=colors["secondary_line"],
        )
    )

    fig.update_layout(**base_layout(theme=theme))
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Returns (%)",
        yaxis2=dict(
            title="Transactions",
            overlaying="y",
            side="right",
            gridcolor=colors["grid"],
            tickfont=dict(color=colors["text"]),
        ),
    )

    fig.data[1].update(yaxis="y2")

    figure_json = json.loads(fig.to_json())
    figure_json["config"] = get_toolbar_config()

    return figure_json
