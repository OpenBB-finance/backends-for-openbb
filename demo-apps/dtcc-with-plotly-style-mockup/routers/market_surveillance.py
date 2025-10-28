from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from typing import List
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime
import sys
sys.path.append('..')

from shared.decorators import register_widget
from mockup_data.data_generator import (
    generate_trade_volumes,
    generate_anomalies,
    generate_counterparty_exposures,
    generate_compliance_alerts,
    generate_time_series
)
from plotly_config import get_theme_colors, base_layout, get_toolbar_config, get_dtcc_chart_colors

router = APIRouter(prefix="/market_surveillance", tags=["Market Surveillance"])

# 1. Trade Volume Heatmap
@register_widget({
    "name": "Trade Volume Heatmap",
    "description": "Monitor trade volumes by asset class across different hours",
    "category": "Market Surveillance",
    "subCategory": "Transparency",
    "type": "chart",
    "endpoint": "market_surveillance/trade_volume_heatmap",
    "gridData": {"w": 20, "h": 12},
    "params": [
        {
            "paramName": "time_period",
            "value": "1M",
            "label": "Time Period",
            "description": "Select the time window for aggregating trade volume data. Valid values: 1D (daily), 1W (weekly), 1M (monthly), 3M (quarterly), 1Y (yearly). This determines the granularity of the heatmap display.",
            "type": "text",
            "options": [
                {"label": "1 Day", "value": "1D"},
                {"label": "1 Week", "value": "1W"},
                {"label": "1 Month", "value": "1M"},
                {"label": "3 Months", "value": "3M"},
                {"label": "1 Year", "value": "1Y"}
            ]
        },
        {
            "paramName": "min_volume",
            "value": 1000,
            "label": "Min Volume (USD M)",
            "description": "Minimum trade volume threshold in millions of USD. Only trades above this value will be included in the heatmap. Range: 0-10000. Example: 500 filters trades below $500M.",
            "type": "number"
        },
        {
            "paramName": "region",
            "value": "US",
            "label": "Region",
            "description": "Geographic region filter for trade data. Valid options: US (United States), Europe (European markets), APAC (Asia Pacific), Americas (North/South America), Global (worldwide). Determines which markets are included in the analysis.",
            "type": "text",
            "options": [
                {"label": "United States", "value": "US"},
                {"label": "Europe", "value": "Europe"},
                {"label": "Asia Pacific", "value": "APAC"},
                {"label": "Americas", "value": "Americas"},
                {"label": "Global", "value": "Global"}
            ]
        }
    ]
})
@router.get("/trade_volume_heatmap")
def get_trade_volume_heatmap(time_period: str = "1M", asset_classes: List[str] = Query(default=["Equities", "Fixed Income"]), min_volume: int = 1000, region: str = "US", currency: str = "USD", theme: str = "dark"):
    """Generate trade volume heatmap by asset class."""
    # Apply parameter filtering logic
    data = generate_trade_volumes(time_period=time_period, asset_classes=asset_classes, 
                                min_volume=min_volume, region=region, currency=currency)
    
    # Transform data for heatmap
    df = pd.DataFrame(data)
    # Determine time column based on period
    time_column = 'hour' if time_period == "1D" else ('day' if time_period == "1W" else 'week')
    pivot = df.pivot_table(values='volume', index='asset_class', columns=time_column)
    
    colors = get_theme_colors(theme)
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=pivot.index,
        colorscale='RdYlGn',
        text=[[f'{val:.0f}' for val in row] for row in pivot.values],
        texttemplate='%{text}',
        textfont={"size": 10},
        hovertemplate=f'Asset: %{{y}}<br>{time_column.title()}: %{{x}}<br>Volume: %{{z:.2f}}M<extra></extra>'
    ))
    
    layout_config = base_layout(theme=theme)
    layout_config.update({
        # 'title': {
        #     'text': f"Trade Volume Heatmap - {date_range}",
        #     'x': 0.5,
        #     'xanchor': 'center'
        # },
        'xaxis_title': f"{time_column.title()} (UTC)",
        'yaxis_title': "Asset Class",
        'height': 500
    })
    
    fig.update_layout(layout_config)
    
    figure_json = json.loads(fig.to_json())
    figure_json['config'] = get_toolbar_config()
    
    return figure_json

# 2. Anomaly Detector
@register_widget({
    "name": "Anomaly Detector",
    "description": "Track unusual settlement fails and trade cancellation spikes",
    "category": "Market Surveillance",
    "subCategory": "Risk Detection",
    "type": "table",
    "endpoint": "market_surveillance/anomaly_detector",
    "gridData": {"w": 20, "h": 10},
    "data": {
        "table": {
            "enableCharts": False,
            "columnsDefs": [
                {
                    "field": "id",
                    "headerName": "Anomaly ID",
                    "width": 120,
                    "pinned": "left"
                },
                {
                    "field": "timestamp",
                    "headerName": "Time",
                    "width": 180,
                    "cellDataType": "dateString"
                },
                {
                    "field": "type",
                    "headerName": "Type",
                    "width": 150
                },
                {
                    "field": "severity",
                    "headerName": "Severity",
                    "width": 100,
                    "renderFn": "columnColor",
                    "renderFnParams": {
                        "colorRules": [
                            {"condition": "eq", "value": "Critical", "color": "#ED6D3C", "fill": True},
                            {"condition": "eq", "value": "High", "color": "#F28352", "fill": True},
                            {"condition": "eq", "value": "Medium", "color": "#0E5447", "fill": False},
                            {"condition": "eq", "value": "Low", "color": "#0B413A", "fill": False}
                        ]
                    }
                },
                {
                    "field": "asset",
                    "headerName": "Asset Class",
                    "width": 120
                },
                {
                    "field": "counterparty",
                    "headerName": "Counterparty",
                    "width": 150
                },
                {
                    "field": "value",
                    "headerName": "Value (USD)",
                    "width": 150,
                    "cellDataType": "number",
                    "formatterFn": "int",
                    "prefix": "$"
                },
                {
                    "field": "status",
                    "headerName": "Status",
                    "width": 120,
                    "renderFn": "columnColor",
                    "renderFnParams": {
                        "colorRules": [
                            {"condition": "eq", "value": "Open", "color": "#ED6D3C", "fill": False},
                            {"condition": "eq", "value": "Investigating", "color": "#F28352", "fill": False},
                            {"condition": "eq", "value": "Resolved", "color": "#0E5447", "fill": False}
                        ]
                    }
                }
            ]
        }
    },
    "params": [
        {
            "paramName": "severity_filter",
            "value": "All",
            "label": "Severity Level",
            "description": "Filter anomalies by severity level. Critical = immediate action required, High = significant risk, Medium = moderate risk, Low = informational. Select 'All' to show all severity levels.",
            "type": "text",
            "options": [
                {"label": "All Severities", "value": "All"},
                {"label": "Critical", "value": "Critical"},
                {"label": "High", "value": "High"},
                {"label": "Medium", "value": "Medium"},
                {"label": "Low", "value": "Low"}
            ]
        },
        {
            "paramName": "min_value",
            "value": 0,
            "label": "Min Value (USD M)",
            "description": "Minimum transaction value threshold in millions of USD. Only anomalies involving transactions above this amount will be displayed. Range: 0-1000000. Example: 10 shows anomalies for transactions above $10M.",
            "type": "number"
        },
        {
            "paramName": "time_range",
            "value": "24H",
            "label": "Time Range",
            "description": "Time window for anomaly detection lookback. Valid formats: 1H (1 hour), 6H (6 hours), 24H (24 hours), 3D (3 days), 1W (1 week). Determines how far back to scan for anomalies.",
            "type": "text",
            "options": [
                {"label": "Last 1 Hour", "value": "1H"},
                {"label": "Last 6 Hours", "value": "6H"},
                {"label": "Last 24 Hours", "value": "24H"},
                {"label": "Last 3 Days", "value": "3D"},
                {"label": "Last Week", "value": "1W"}
            ]
        }
    ]
})
@router.get("/anomaly_detector")
def get_anomaly_detector(severity_filter: str = "All", asset_class_filter: str = "All", counterparty_type: str = "All", min_value: int = 0, time_range: str = "24H"):
    """Get anomaly detection data."""
    anomalies = generate_anomalies(time_range=time_range, asset_class_filter=asset_class_filter, 
                                  counterparty_type=counterparty_type)
    
    # Apply filters
    if severity_filter != "All":
        anomalies = [a for a in anomalies if a["severity"] == severity_filter]
    
    if asset_class_filter != "All":
        anomalies = [a for a in anomalies if a["asset"] == asset_class_filter]
    
    if counterparty_type != "All":
        anomalies = [a for a in anomalies if a.get("counterparty_type") == counterparty_type]
    
    if min_value > 0:
        anomalies = [a for a in anomalies if a["value"] >= min_value * 1000000]  # Convert to actual USD
    
    return anomalies

# 3. Counterparty Exposure Network
@register_widget({
    "name": "Counterparty Exposure Network",
    "description": "Visualize counterparty exposure relationships and systemic risk",
    "category": "Market Surveillance",
    "subCategory": "Network Analysis",
    "type": "chart",
    "endpoint": "market_surveillance/counterparty_network",
    "gridData": {"w": 20, "h": 15},
    "params": [
        {
            "paramName": "min_exposure",
            "value": 50,
            "label": "Min Exposure ($M)",
            "description": "Minimum exposure amount in millions of USD to include in the network visualization. Only counterparty relationships above this threshold will be displayed. Range: 1-10000. Example: 100 shows exposures above $100M.",
            "type": "number"
        },
        {
            "paramName": "risk_threshold",
            "value": "Medium",
            "label": "Risk Threshold",
            "description": "Risk level filter for counterparty exposures. Low = minimal risk, Medium = moderate risk requiring monitoring, High = significant risk requiring attention, Critical = immediate action required. Affects node colors and highlighting in the network.",
            "type": "text",
            "options": [
                {"label": "Low Risk", "value": "Low"},
                {"label": "Medium Risk", "value": "Medium"},
                {"label": "High Risk", "value": "High"},
                {"label": "Critical Risk", "value": "Critical"}
            ]
        },
        {
            "paramName": "network_depth",
            "value": 2,
            "label": "Network Depth (Hops)",
            "description": "Number of connection hops to include in the network graph. 1 = direct connections only, 2 = connections of connections, 3+ = extended network. Range: 1-5. Higher values show more complex relationships but may clutter the visualization.",
            "type": "number"
        },
        {
            "paramName": "geographic_region",
            "value": "Global",
            "label": "Geographic Region",
            "description": "Geographic scope for counterparty analysis. Global = worldwide entities, US = North American entities, Europe = European entities, APAC = Asia Pacific entities. Filters which counterparties are included based on their domicile.",
            "type": "text",
            "options": [
                {"label": "Global", "value": "Global"},
                {"label": "North America", "value": "US"},
                {"label": "Europe", "value": "Europe"},
                {"label": "Asia Pacific", "value": "APAC"}
            ]
        }
    ]
})
@router.get("/counterparty_network")
def get_counterparty_network(min_exposure: float = 50, counterparty_types: List[str] = Query(default=["Banks", "Asset Managers"]), risk_threshold: str = "Medium", geographic_region: str = "Global", network_depth: int = 2, theme: str = "dark"):
    """Generate counterparty exposure network visualization."""
    network_data = generate_counterparty_exposures(min_exposure=min_exposure, 
                                                  counterparty_types=counterparty_types,
                                                  risk_threshold=risk_threshold,
                                                  geographic_region=geographic_region,
                                                  network_depth=network_depth)
    colors = get_theme_colors(theme)
    
    # Create network graph using plotly
    edge_trace = []
    for link in network_data["links"]:
        if link["value"] >= min_exposure:
            # Find node positions (simplified circular layout)
            source_idx = next(i for i, n in enumerate(network_data["nodes"]) if n["id"] == link["source"])
            target_idx = next(i for i, n in enumerate(network_data["nodes"]) if n["id"] == link["target"])
            
            import math
            n_nodes = len(network_data["nodes"])
            source_x = math.cos(2 * math.pi * source_idx / n_nodes)
            source_y = math.sin(2 * math.pi * source_idx / n_nodes)
            target_x = math.cos(2 * math.pi * target_idx / n_nodes)
            target_y = math.sin(2 * math.pi * target_idx / n_nodes)
            
            edge_trace.append(
                go.Scatter(
                    x=[source_x, target_x, None],
                    y=[source_y, target_y, None],
                    mode='lines',
                    line=dict(width=link["value"]/100, color='rgba(125,125,125,0.5)'),
                    hoverinfo='none'
                )
            )
    
    # Node trace
    node_x = []
    node_y = []
    node_text = []
    node_color = []
    
    n_nodes = len(network_data["nodes"])
    for i, node in enumerate(network_data["nodes"]):
        x = math.cos(2 * math.pi * i / n_nodes)
        y = math.sin(2 * math.pi * i / n_nodes)
        node_x.append(x)
        node_y.append(y)
        node_text.append(f"{node['id']}<br>Exposure: ${node['exposure']}M<br>Risk Score: {node['risk_score']}")
        node_color.append(node['risk_score'])
    
    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        text=[n['id'] for n in network_data["nodes"]],
        textposition="top center",
        hovertext=node_text,
        hoverinfo='text',
        marker=dict(
            size=[n['exposure']/50 for n in network_data["nodes"]],
            color=node_color,
            colorscale='RdYlGn_r',
            showscale=True,
            colorbar=dict(
                thickness=15,
                title="Risk Score",
                xanchor="left"
            ),
            line=dict(width=2, color=colors["text"])
        )
    )
    
    fig = go.Figure(data=edge_trace + [node_trace])
    
    layout_config = base_layout(theme=theme)
    layout_config.update({
        # 'title': 'Counterparty Exposure Network',
        'showlegend': False,
        'xaxis': {'showgrid': False, 'zeroline': False, 'visible': False},
        'yaxis': {'showgrid': False, 'zeroline': False, 'visible': False},
        'height': 600
    })
    
    fig.update_layout(layout_config)
    
    figure_json = json.loads(fig.to_json())
    figure_json['config'] = get_toolbar_config()
    
    return figure_json

# 4. Compliance Ticker
@register_widget({
    "name": "Regulatory Compliance Ticker",
    "description": "Real-time regulatory compliance alerts and flags",
    "category": "Market Surveillance",
    "subCategory": "Compliance",
    "type": "table",
    "endpoint": "market_surveillance/compliance_ticker",
    "gridData": {"w": 20, "h": 8},
    "refetchInterval": 30000,
    "data": {
        "table": {
            "enableCharts": False,
            "columnsDefs": [
                {
                    "field": "timestamp",
                    "headerName": "Time",
                    "width": 180,
                    "cellDataType": "dateString"
                },
                {
                    "field": "id",
                    "headerName": "Alert ID",
                    "width": 100
                },
                {
                    "field": "type",
                    "headerName": "Type",
                    "width": 150
                },
                {
                    "field": "regulation",
                    "headerName": "Regulation",
                    "width": 120,
                    "renderFn": "columnColor",
                    "renderFnParams": {
                        "colorRules": [
                            {"condition": "eq", "value": "Dodd-Frank", "color": "#ED6D3C", "fill": False},
                            {"condition": "eq", "value": "MiFID II", "color": "#0E5447", "fill": False},
                            {"condition": "eq", "value": "EMIR", "color": "#F28352", "fill": False},
                            {"condition": "eq", "value": "Basel III", "color": "#0B413A", "fill": False}
                        ]
                    }
                },
                {
                    "field": "entity",
                    "headerName": "Entity",
                    "width": 150
                },
                {
                    "field": "severity",
                    "headerName": "Severity",
                    "width": 100,
                    "renderFn": "greenRed"
                },
                {
                    "field": "description",
                    "headerName": "Description",
                    "width": 300
                }
            ]
        }
    },
    "params": [
        {
            "paramName": "regulation_scope",
            "value": "All",
            "label": "Regulatory Scope",
            "description": "Filter compliance alerts by specific regulatory framework. Dodd-Frank = US financial reform, MiFID II = EU investment services directive, EMIR = EU derivatives regulation, Basel III = international banking regulation, CFTC = US commodities regulation. Select 'All' to view alerts from all regulatory frameworks.",
            "type": "text",
            "options": [
                {"label": "All Regulations", "value": "All"},
                {"label": "Dodd-Frank", "value": "Dodd-Frank"},
                {"label": "MiFID II", "value": "MiFID II"},
                {"label": "EMIR", "value": "EMIR"},
                {"label": "Basel III", "value": "Basel III"},
                {"label": "CFTC Rules", "value": "CFTC"}
            ]
        },
        {
            "paramName": "alert_severity",
            "value": "All",
            "label": "Alert Severity",
            "description": "Filter by compliance alert severity level. Critical = immediate regulatory action required, High = significant compliance risk, Medium = moderate risk requiring attention, Low = minor compliance issue, Info = informational notice. Select 'All' to view all severity levels.",
            "type": "text",
            "options": [
                {"label": "All Severities", "value": "All"},
                {"label": "Critical", "value": "Critical"},
                {"label": "High", "value": "High"},
                {"label": "Medium", "value": "Medium"},
                {"label": "Low", "value": "Low"},
                {"label": "Info", "value": "Info"}
            ]
        },
        {
            "paramName": "entity_type",
            "value": "All",
            "label": "Entity Type",
            "description": "Filter alerts by type of financial institution. Investment Bank = securities trading and underwriting, Commercial Bank = traditional banking services, Hedge Fund = alternative investment funds, Asset Manager = investment management companies, Insurance Company = insurance providers, Pension Fund = retirement plan managers. Select 'All' to view all entity types.",
            "type": "text",
            "options": [
                {"label": "All Entity Types", "value": "All"},
                {"label": "Investment Bank", "value": "Investment Bank"},
                {"label": "Commercial Bank", "value": "Commercial Bank"},
                {"label": "Hedge Fund", "value": "Hedge Fund"},
                {"label": "Asset Manager", "value": "Asset Manager"},
                {"label": "Insurance Company", "value": "Insurance Company"},
                {"label": "Pension Fund", "value": "Pension Fund"}
            ]
        }
    ]
})
@router.get("/compliance_ticker")
def get_compliance_ticker(regulation_scope: str = "All", alert_severity: str = "All", entity_type: str = "All", geographic_jurisdiction: str = "All"):
    """Get real-time compliance alerts."""
    alerts = generate_compliance_alerts(regulatory_scope=[regulation_scope] if regulation_scope != "All" else None, 
                                       severity=[alert_severity] if alert_severity != "All" else None,
                                       entity_type=[entity_type] if entity_type != "All" else None,
                                       time_period="1W")
    
    # Apply additional filtering if needed
    if regulation_scope != "All":
        alerts = [a for a in alerts if a.get("regulation") == regulation_scope]
    
    if alert_severity != "All":
        alerts = [a for a in alerts if a.get("severity") == alert_severity]
    
    return alerts

# 5. Market Activity Summary Metrics
@register_widget({
    "name": "Market Activity Metrics",
    "description": "Key market surveillance metrics at a glance",
    "category": "Market Surveillance",
    "subCategory": "Summary",
    "type": "metric",
    "endpoint": "market_surveillance/activity_metrics",
    "gridData": {"w": 20, "h": 4},
    "params": [
        {
            "paramName": "time_horizon",
            "value": "1D",
            "label": "Time Horizon",
            "description": "Time period for calculating market activity metrics. 1D = daily metrics, 1W = weekly aggregation, 1M = monthly aggregation, YTD = year-to-date cumulative metrics. Affects volume scaling and trend calculations.",
            "type": "text",
            "options": [
                {"label": "1 Day", "value": "1D"},
                {"label": "1 Week", "value": "1W"},
                {"label": "1 Month", "value": "1M"},
                {"label": "Year to Date", "value": "YTD"}
            ]
        },
        {
            "paramName": "benchmark_comparison",
            "value": True,
            "label": "Show Benchmark Comparison",
            "description": "Enable comparison of current metrics against historical benchmarks and market averages. When enabled, delta values show percentage change versus benchmark. When disabled, shows absolute values only.",
            "type": "boolean"
        }
    ]
})
@router.get("/activity_metrics")
def get_activity_metrics(time_horizon: str = "1D", metric_category: str = "All", benchmark_comparison: bool = True):
    """Get market activity summary metrics."""
    import random
    
    # Base metrics adjusted for time horizon
    time_multiplier = {"1D": 1, "1W": 7, "1M": 30, "YTD": 365}[time_horizon]
    
    all_metrics = [
        {
            "label": "Total Trade Volume",
            "value": f"${4.7 * time_multiplier:.1f}T" if time_multiplier > 1 else "$4.7T",
            "delta": str(round(random.uniform(8, 16), 1)),
            "category": "Volume"
        },
        {
            "label": "Active Anomalies", 
            "value": str(int(23 * time_multiplier**0.5)),
            "delta": str(round(random.uniform(-12, -4), 1)),
            "category": "Risk"
        },
        {
            "label": "Settlement Fails",
            "value": f"${int(892 * time_multiplier**0.7)}M",
            "delta": str(round(random.uniform(10, 20), 1)),
            "category": "Risk"
        },
        {
            "label": "Compliance Alerts",
            "value": str(int(47 * time_multiplier**0.6)),
            "delta": str(round(random.uniform(2, 8), 1)),
            "category": "Compliance"
        },
        {
            "label": "System Health",
            "value": "98.7%",
            "delta": str(round(random.uniform(-0.5, 0.5), 1)),
            "category": "System"
        },
        {
            "label": "Market Concentration",
            "value": "72.3%",
            "delta": str(round(random.uniform(-2, 2), 1)),
            "category": "Risk"
        },
        {
            "label": "Cross-Border Volume",
            "value": f"${1.2 * time_multiplier:.1f}T" if time_multiplier > 1 else "$1.2T",
            "delta": str(round(random.uniform(5, 15), 1)),
            "category": "Volume"
        }
    ]
    
    # Filter by category if specified
    if metric_category != "All":
        all_metrics = [m for m in all_metrics if m["category"] == metric_category]
    
    # Remove category field from output
    for metric in all_metrics:
        del metric["category"]
    
    return all_metrics[:5]  # Return top 5 metrics

# 7. Dashboard Notes
@register_widget({
    "name": "Market Surveillance Dashboard Notes",
    "description": "Comprehensive overview and documentation for the Market Surveillance dashboard",
    "category": "Documentation",
    "type": "markdown",
    "endpoint": "market_surveillance/notes",
    "gridData": {"w": 40, "h": 30}
})
@router.get("/notes")
def get_notes():
    """Get Market Surveillance dashboard documentation."""
    markdown_content = """# DTCC Market Surveillance Dashboard

## Overview
The DTCC Market Surveillance Dashboard provides comprehensive market transparency and surveillance capabilities, offering real-time monitoring of trade volumes, anomaly detection, counterparty exposure analysis, and regulatory compliance tracking across all asset classes. This dashboard serves as the primary tool for identifying market irregularities and ensuring market integrity.

## Purpose
• **Real-time Market Monitoring**: Track trading activity, volumes, and patterns across all major asset classes with sub-second latency

• **Anomaly Detection**: Identify unusual settlement fails, trade cancellation spikes, and suspicious trading patterns using advanced algorithms

• **Counterparty Risk Assessment**: Analyze exposure relationships and systemic risk through network visualization and concentration metrics

• **Regulatory Compliance Oversight**: Monitor compliance with market regulations and generate alerts for potential violations

---

## Tab 1: Market Overview
**Purpose**: Provide a high-level view of current market activity and key surveillance metrics

### Widgets:
• **Market Activity Metrics**: Key performance indicators including total trade volume ($4.7T), active anomalies (23), settlement fails ($892M), compliance alerts (47), and system health (98.7%)

• **Trade Volume Heatmap**: Interactive visualization showing trade volumes by asset class across different hours, filterable by date range (24 hours, 7 days, 30 days)

• **Counterparty Exposure Network**: Network graph displaying counterparty relationships with exposure amounts, risk scores, and minimum exposure filtering

---

## Tab 2: Anomaly Detection
**Purpose**: Focus on identifying and investigating unusual market behavior and potential risks

### Widgets:
• **Anomaly Detector**: Comprehensive table of detected anomalies with severity levels, asset classes, counterparties, and status tracking

• **Regulatory Compliance Ticker**: Real-time feed of compliance alerts across regulations (Dodd-Frank, MiFID II, EMIR, Basel III) with severity indicators and entity details

---

## Data Sources
• **Real-time Trade Feeds**: Direct connections to major exchanges and trading venues for immediate trade capture

• **Settlement Systems**: Integration with DTCC settlement infrastructure for fails and obligation tracking

• **Regulatory Repositories**: Links to trade repositories for compliance monitoring and reporting validation

• **Counterparty Databases**: Master data for entity identification, LEI validation, and relationship mapping

• **Historical Archives**: Multi-year trading history for trend analysis and anomaly baseline establishment

## Key Metrics Tracked
• **Trade Volume Metrics**: Daily, weekly, and monthly volumes across equities, fixed income, derivatives, and repo markets

• **Settlement Performance**: Fail rates, settlement times, and obligation tracking by asset class and counterparty

• **Anomaly Indicators**: Statistical deviations, unusual volume spikes, and pattern recognition alerts

• **Compliance Scores**: Adherence rates to regulatory requirements with drill-down capabilities

• **Network Risk Metrics**: Counterparty concentration, systemic risk indicators, and exposure clustering

• **System Health**: Platform uptime, data latency, and processing performance metrics

• **Alert Response Times**: Time to detection, investigation duration, and resolution tracking

## Use Cases
• **Market Supervisors**: Monitor overall market health, identify emerging risks, and coordinate regulatory responses

• **Risk Managers**: Track counterparty exposures, assess concentration risks, and monitor settlement obligations

• **Compliance Officers**: Ensure adherence to regulatory requirements and investigate potential violations

• **Operations Teams**: Monitor system performance, track settlement processes, and manage operational risks

• **Regulatory Bodies**: Access aggregated market data for policy development and oversight activities"""

    return markdown_content