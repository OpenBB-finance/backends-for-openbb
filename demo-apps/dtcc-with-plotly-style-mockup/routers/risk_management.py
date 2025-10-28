from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from typing import List
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
import random
import sys
sys.path.append('..')

from shared.decorators import register_widget
from mockup_data.data_generator import (
    generate_counterparties,
    generate_time_series,
    generate_asset_classes
)
from plotly_config import get_theme_colors, base_layout, get_toolbar_config, get_dtcc_chart_colors

router = APIRouter(prefix="/risk_management", tags=["Risk Management"])

def generate_exposure_treemap(risk_levels=None, counterparty_sectors=None, min_exposure_threshold=100, currency_filter="USD", geographic_region="Global", **kwargs):
    """Generate counterparty exposure treemap data with parameter filtering."""
    if not risk_levels:
        risk_levels = ["Medium", "High"]
    if not counterparty_sectors:
        counterparty_sectors = ["Banks", "Asset Managers", "Hedge Funds", "Insurance", "Pension Funds"]
    
    firms = generate_counterparties()
    
    data = []
    for sector in counterparty_sectors:
        for i in range(3):
            firm = random.choice(firms)
            exposure = random.uniform(min_exposure_threshold, 5000)
            # Apply currency and region multipliers
            if currency_filter == "EUR":
                exposure *= 0.85
            elif currency_filter == "JPY":
                exposure *= 110
            if geographic_region != "Global":
                exposure *= random.uniform(0.8, 1.2)
            
            data.append({
                "firm": firm,
                "sector": sector,
                "exposure": round(exposure, 2),
                "collateral": round(exposure * random.uniform(0.7, 1.3), 2),
                "net_exposure": round(exposure * random.uniform(0.3, 0.8), 2),
                "currency": currency_filter,
                "region": geographic_region
            })
    
    return data

def generate_collateral_forecast():
    """Generate collateral requirement forecast data."""
    dates = []
    baseline = []
    stressed = []
    extreme = []
    
    for i in range(90):
        date = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
        dates.append(date)
        base_value = 1000 + i * 5
        baseline.append(round(base_value + random.uniform(-50, 50), 2))
        stressed.append(round(base_value * 1.3 + random.uniform(-100, 100), 2))
        extreme.append(round(base_value * 1.8 + random.uniform(-150, 150), 2))
    
    return {
        "dates": dates,
        "baseline": baseline,
        "stressed": stressed,
        "extreme": extreme
    }

def generate_settlement_fails():
    """Generate settlement fails tracking data."""
    data = []
    dates, _ = generate_time_series(30)
    
    for date in dates:
        data.append({
            "date": date,
            "treasury_fails": round(random.uniform(100, 1000), 2),
            "equity_fails": round(random.uniform(50, 500), 2),
            "mbs_fails": round(random.uniform(200, 800), 2),
            "corporate_fails": round(random.uniform(30, 300), 2)
        })
    
    return data

def generate_liquidity_heatmap():
    """Generate liquidity heatmap data."""
    maturities = ["O/N", "1W", "1M", "3M", "6M", "1Y", "2Y", "5Y"]
    collateral_types = ["Treasury", "Agency", "MBS", "Corporate IG", "Corporate HY", "Equity"]
    
    data = []
    for collateral in collateral_types:
        for maturity in maturities:
            availability = random.uniform(0, 100)
            if "Treasury" in collateral and maturity in ["O/N", "1W"]:
                availability *= 1.5
            data.append({
                "collateral": collateral,
                "maturity": maturity,
                "availability": round(min(availability, 100), 2),
                "demand": round(random.uniform(20, 80), 2)
            })
    
    return data

# 1. Counterparty Exposure Treemap
@register_widget({
    "name": "Counterparty Exposure Treemap",
    "description": "Hierarchical view of counterparty exposures by firm and sector",
    "category": "Risk Management",
    "subCategory": "Exposure Analysis",
    "type": "chart",
    "endpoint": "risk_management/exposure_treemap",
    "gridData": {"w": 20, "h": 12},
    "params": [
        {
            "paramName": "exposure_type",
            "value": "gross",
            "label": "Exposure Type",
            "description": "Type of exposure calculation to display. Valid values: 'gross' (total exposure before netting), 'net' (exposure after netting agreements), 'collateral' (collateralized exposure only). Determines the basis for treemap sizing and risk assessment.",
            "type": "text",
            "options": [
                {"label": "Gross Exposure", "value": "gross"},
                {"label": "Net Exposure", "value": "net"},
                {"label": "Collateral Exposure", "value": "collateral"}
            ]
        },
        {
            "paramName": "min_exposure_threshold",
            "value": 100,
            "label": "Min Exposure ($M)",
            "description": "Minimum exposure amount in millions of USD to include in the treemap. Only counterparties with exposures above this threshold will be displayed. Range: 1-10000. Example: 500 shows exposures above $500M.",
            "type": "number"
        },
        {
            "paramName": "currency_filter",
            "value": "USD",
            "label": "Currency",
            "description": "Currency filter for exposure calculations. Valid ISO currency codes: USD, EUR, GBP, JPY, CHF, CAD, AUD. Only exposures denominated in the selected currency will be included in the analysis.",
            "type": "text",
            "options": [
                {"label": "US Dollar (USD)", "value": "USD"},
                {"label": "Euro (EUR)", "value": "EUR"},
                {"label": "British Pound (GBP)", "value": "GBP"},
                {"label": "Japanese Yen (JPY)", "value": "JPY"},
                {"label": "Swiss Franc (CHF)", "value": "CHF"}
            ]
        }
    ]
})
@router.get("/exposure_treemap")
def get_exposure_treemap(exposure_type: str = "gross", risk_levels: List[str] = Query(default=["Medium", "High"]), counterparty_sectors: List[str] = Query(default=["Banks", "Asset Managers"]), min_exposure_threshold: int = 100, currency_filter: str = "USD", geographic_region: str = "Global", theme: str = "dark"):
    """Generate counterparty exposure treemap."""
    data = generate_exposure_treemap(risk_levels=risk_levels, 
                                   counterparty_sectors=counterparty_sectors,
                                   min_exposure_threshold=min_exposure_threshold,
                                   currency_filter=currency_filter,
                                   geographic_region=geographic_region)
    colors = get_theme_colors(theme)
    
    # Prepare data for treemap
    labels = []
    parents = []
    values = []
    text = []
    
    # Add root
    labels.append("Total")
    parents.append("")
    values.append(0)
    text.append("Total Exposure")
    
    # Add sectors
    sectors = list(set(d["sector"] for d in data))
    for sector in sectors:
        labels.append(sector)
        parents.append("Total")
        sector_exposure = sum(d["exposure"] if exposure_type == "gross" 
                             else d["net_exposure"] if exposure_type == "net"
                             else d["collateral"] 
                             for d in data if d["sector"] == sector)
        values.append(sector_exposure)
        text.append(f"${sector_exposure:,.0f}M")
    
    # Add firms
    for d in data:
        labels.append(d["firm"])
        parents.append(d["sector"])
        value = d["exposure"] if exposure_type == "gross" else d["net_exposure"] if exposure_type == "net" else d["collateral"]
        values.append(value)
        text.append(f"${value:,.0f}M")
    
    fig = go.Figure(go.Treemap(
        labels=labels,
        parents=parents,
        values=values,
        text=text,
        textposition="middle center",
        marker=dict(
            colorscale='RdYlGn_r',
            cmid=50
        ),
        hovertemplate='<b>%{label}</b><br>Exposure: %{text}<br>%{percentRoot}<extra></extra>'
    ))
    
    layout_config = base_layout(theme=theme)
    layout_config.update({
        # 'title': f'Counterparty {exposure_type.title()} Exposure by Sector',
        'height': 500
    })
    
    fig.update_layout(layout_config)
    
    figure_json = json.loads(fig.to_json())
    figure_json['config'] = get_toolbar_config()
    
    return figure_json

# 2. Collateral Requirement Forecast
@register_widget({
    "name": "Collateral Requirement Forecast",
    "description": "Projected collateral requirements under different stress scenarios",
    "category": "Risk Management",
    "subCategory": "Collateral Management",
    "type": "chart",
    "endpoint": "risk_management/collateral_forecast",
    "gridData": {"w": 20, "h": 10},
    "params": [
        {
            "paramName": "forecast_horizon",
            "value": "30D",
            "label": "Forecast Horizon",
            "description": "Time period for collateral requirement projections. Valid formats: 7D (1 week), 14D (2 weeks), 30D (1 month), 60D (2 months), 90D (3 months). Determines the forecasting window for stress scenario analysis.",
            "type": "text",
            "options": [
                {"label": "1 Week", "value": "7D"},
                {"label": "2 Weeks", "value": "14D"},
                {"label": "1 Month", "value": "30D"},
                {"label": "2 Months", "value": "60D"},
                {"label": "3 Months", "value": "90D"}
            ]
        },
        {
            "paramName": "confidence_level",
            "value": 95,
            "label": "Confidence Level (%)",
            "description": "Statistical confidence level for collateral requirement estimates. Range: 90-99. Example: 95 means 95% confidence that actual requirements won't exceed the forecast. Higher values provide more conservative estimates.",
            "type": "number"
        },
        {
            "paramName": "portfolio_segment",
            "value": "All",
            "label": "Portfolio Segment",
            "description": "Filter by portfolio credit quality segment. IG = Investment Grade bonds (high credit quality), HY = High Yield bonds (lower credit quality), Govt = Government securities, Muni = Municipal bonds, Structured = Asset-backed securities. Select 'All' to include all segments.",
            "type": "text",
            "options": [
                {"label": "All Segments", "value": "All"},
                {"label": "Investment Grade", "value": "IG"},
                {"label": "High Yield", "value": "HY"},
                {"label": "Government", "value": "Govt"},
                {"label": "Municipal", "value": "Muni"},
                {"label": "Structured Products", "value": "Structured"}
            ]
        }
    ]
})
@router.get("/collateral_forecast")
def get_collateral_forecast(forecast_horizon: str = "30D", stress_scenarios: List[str] = Query(default=["Baseline", "Stressed"]), collateral_types: List[str] = Query(default=["Treasury", "Agency"]), confidence_level: int = 95, portfolio_segment: str = "All", theme: str = "dark"):
    """Generate collateral requirement forecast."""
    forecast_days = int(forecast_horizon.replace('D', ''))
    forecast_data = generate_collateral_forecast()
    colors = get_theme_colors(theme)
    
    # Limit to requested days
    dates = forecast_data["dates"][:forecast_days]
    baseline = forecast_data["baseline"][:forecast_days]
    stressed = forecast_data["stressed"][:forecast_days]
    extreme = forecast_data["extreme"][:forecast_days]
    
    fig = go.Figure()
    
    # Add baseline scenario
    fig.add_trace(go.Scatter(
        x=dates,
        y=baseline,
        name='Baseline',
        mode='lines',
        line=dict(color='#0E5447', width=2)  # DTCC Primary Green
    ))
    
    # Add stressed scenario
    fig.add_trace(go.Scatter(
        x=dates,
        y=stressed,
        name='Stressed (2008-like)',
        mode='lines',
        line=dict(color='#F28352', width=2, dash='dash')  # DTCC Light Orange
    ))
    
    # Add extreme scenario
    fig.add_trace(go.Scatter(
        x=dates,
        y=extreme,
        name='Extreme Stress',
        mode='lines',
        line=dict(color='#ED6D3C', width=2, dash='dot')  # DTCC Primary Orange
    ))
    
    # Add fill between baseline and extreme
    fig.add_trace(go.Scatter(
        x=dates + dates[::-1],
        y=baseline + extreme[::-1],
        fill='toself',
        fillcolor='rgba(239, 68, 68, 0.1)',
        line=dict(color='rgba(255,255,255,0)'),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    layout_config = base_layout(theme=theme)
    layout_config.update({
        # 'title': 'Collateral Requirement Forecast',
        'xaxis_title': 'Date',
        'yaxis_title': 'Collateral Required ($B)',
        'hovermode': 'x unified',
        'legend': dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    })
    
    fig.update_layout(layout_config)
    
    figure_json = json.loads(fig.to_json())
    figure_json['config'] = get_toolbar_config()
    
    return figure_json

# 3. Settlement Fails Tracker
@register_widget({
    "name": "Settlement Fails Tracker",
    "description": "Track settlement failures with stress scenario overlays",
    "category": "Risk Management",
    "subCategory": "Settlement Risk",
    "type": "chart",
    "endpoint": "risk_management/settlement_fails",
    "gridData": {"w": 20, "h": 10},
    "raw": True,
    "params": [
        {
            "paramName": "time_period",
            "value": "1M",
            "label": "Time Period",
            "description": "Time window for settlement fails analysis. 1W = weekly fails, 1M = monthly analysis, 3M = quarterly trends, 6M = semi-annual, 1Y = annual patterns. Determines the timeframe for fail tracking and trend analysis.",
            "type": "text",
            "options": [
                {"label": "1 Week", "value": "1W"},
                {"label": "1 Month", "value": "1M"},
                {"label": "3 Months", "value": "3M"},
                {"label": "6 Months", "value": "6M"},
                {"label": "1 Year", "value": "1Y"}
            ]
        },
        {
            "paramName": "min_fail_amount",
            "value": 10,
            "label": "Min Fail Amount ($M)",
            "description": "Minimum settlement fail amount in millions of USD to include in analysis. Only fails above this threshold will be displayed. Range: 1-1000. Example: 25 shows settlement fails above $25M.",
            "type": "number"
        },
        {
            "paramName": "settlement_type",
            "value": "All",
            "label": "Settlement Type",
            "type": "text",
            "options": [
                {"label": "All Types", "value": "All"},
                {"label": "T+0 (Same Day)", "value": "T+0"},
                {"label": "T+1 (Next Day)", "value": "T+1"},
                {"label": "T+2 (2 Days)", "value": "T+2"},
                {"label": "T+3+ (3+ Days)", "value": "T+3+"}
            ]
        }
    ]
})
@router.get("/settlement_fails")
def get_settlement_fails(time_period: str = "1M", asset_classes_filter: List[str] = Query(default=["Treasury", "Equity"]), settlement_type: str = "All", min_fail_amount: int = 10, counterparty_filter: str = "All", raw: bool = False, theme: str = "dark"):
    """Track settlement fails across asset classes."""
    data = generate_settlement_fails()
    
    if raw:
        return data
    
    df = pd.DataFrame(data)
    colors = get_theme_colors(theme)
    
    fig = go.Figure()
    
    # Create stacked area chart
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['treasury_fails'],
        name='Treasury',
        mode='lines',
        stackgroup='one',
        fillcolor='rgba(59, 130, 246, 0.5)',
        line=dict(color='#ED6D3C', width=0)  # DTCC Primary Orange
    ))
    
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['equity_fails'],
        name='Equity',
        mode='lines',
        stackgroup='one',
        fillcolor='rgba(139, 92, 246, 0.5)',
        line=dict(color='#0E5447', width=0)  # DTCC Primary Green
    ))
    
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['mbs_fails'],
        name='MBS',
        mode='lines',
        stackgroup='one',
        fillcolor='rgba(236, 72, 153, 0.5)',
        line=dict(color='#F28352', width=0)  # DTCC Light Orange
    ))
    
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['corporate_fails'],
        name='Corporate',
        mode='lines',
        stackgroup='one',
        fillcolor='rgba(245, 158, 11, 0.5)',
        line=dict(color='#0B413A', width=0)  # DTCC Dark Green
    ))
    
    layout_config = base_layout(theme=theme)
    layout_config.update({
        # 'title': 'Settlement Fails by Asset Class',
        'xaxis_title': 'Date',
        'yaxis_title': 'Fails Amount ($M)',
        'hovermode': 'x unified'
    })
    
    fig.update_layout(layout_config)
    
    figure_json = json.loads(fig.to_json())
    figure_json['config'] = get_toolbar_config()
    
    return figure_json

# 4. Liquidity Heatmap
@register_widget({
    "name": "Liquidity Heatmap",
    "description": "Repo availability vs collateral type across maturity buckets",
    "category": "Risk Management",
    "subCategory": "Liquidity Risk",
    "type": "chart",
    "endpoint": "risk_management/liquidity_heatmap",
    "gridData": {"w": 20, "h": 10},
    "params": [
        {
            "paramName": "liquidity_metric",
            "value": "availability",
            "label": "Liquidity Metric",
            "description": "Type of liquidity measurement to display. Valid values: 'availability' (liquidity available), 'utilization' (liquidity being used), 'concentration' (liquidity concentration risk), 'velocity' (liquidity turnover rate). Determines the heatmap color scale and values.",
            "type": "text",
            "options": [
                {"label": "Availability", "value": "availability"},
                {"label": "Utilization", "value": "utilization"},
                {"label": "Concentration", "value": "concentration"},
                {"label": "Velocity", "value": "velocity"}
            ]
        },
        {
            "paramName": "currency_denomination",
            "value": "USD",
            "label": "Currency",
            "description": "Currency denomination for liquidity analysis. Valid ISO codes: USD, EUR, GBP, JPY, CHF. Only liquidity in the selected currency will be included in the heatmap calculations.",
            "type": "text",
            "options": [
                {"label": "US Dollar (USD)", "value": "USD"},
                {"label": "Euro (EUR)", "value": "EUR"},
                {"label": "British Pound (GBP)", "value": "GBP"},
                {"label": "Japanese Yen (JPY)", "value": "JPY"},
                {"label": "Swiss Franc (CHF)", "value": "CHF"}
            ]
        },
        {
            "paramName": "stress_overlay",
            "value": False,
            "label": "Show Stress Overlay",
            "description": "Enable stress scenario overlay on the liquidity heatmap. When enabled, displays projected liquidity conditions under stress scenarios. When disabled, shows current liquidity conditions only.",
            "type": "boolean"
        }
    ]
})
@router.get("/liquidity_heatmap")
def get_liquidity_heatmap(collateral_types_filter: List[str] = Query(default=["Treasury", "Agency"]), maturity_buckets: List[str] = Query(default=["O/N", "1W", "1M"]), liquidity_metric: str = "availability", currency_denomination: str = "USD", stress_overlay: bool = False, theme: str = "dark"):
    """Generate liquidity heatmap."""
    data = generate_liquidity_heatmap()
    df = pd.DataFrame(data)
    
    # Create pivot table
    pivot = df.pivot_table(values='availability', index='collateral', columns='maturity')
    
    colors = get_theme_colors(theme)
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=pivot.index,
        colorscale='RdYlGn',
        zmid=50,
        text=[[f'{val:.0f}%' for val in row] for row in pivot.values],
        texttemplate='%{text}',
        textfont={"size": 10},
        hovertemplate='Collateral: %{y}<br>Maturity: %{x}<br>Availability: %{z:.1f}%<extra></extra>'
    ))
    
    layout_config = base_layout(theme=theme)
    layout_config.update({
        # 'title': 'Liquidity Availability Heatmap',
        'xaxis_title': 'Maturity',
        'yaxis_title': 'Collateral Type',
        'height': 400
    })
    
    fig.update_layout(layout_config)
    
    figure_json = json.loads(fig.to_json())
    figure_json['config'] = get_toolbar_config()
    
    return figure_json

# 5. Risk Metrics Summary
@register_widget({
    "name": "Risk Metrics Summary",
    "description": "Key risk management metrics",
    "category": "Risk Management",
    "subCategory": "Summary",
    "type": "metric",
    "endpoint": "risk_management/risk_metrics",
    "gridData": {"w": 20, "h": 4},
    "refetchInterval": 60000,
    "params": [
        {
            "paramName": "risk_category",
            "value": "All",
            "label": "Risk Category",
            "description": "Filter risk metrics by category. Valid values: 'All' (all risk types), 'Credit' (counterparty credit risk), 'Market' (market price risk), 'Liquidity' (liquidity risk), 'Operational' (operational risk). Determines which risk metrics are displayed.",
            "type": "text",
            "options": [
                {"label": "All Categories", "value": "All"},
                {"label": "Credit Risk", "value": "Credit"},
                {"label": "Market Risk", "value": "Market"},
                {"label": "Liquidity Risk", "value": "Liquidity"},
                {"label": "Operational Risk", "value": "Operational"}
            ]
        },
        {
            "paramName": "confidence_interval",
            "value": 99,
            "label": "Confidence Level (%)",
            "description": "Statistical confidence level for risk calculations (VaR, CVaR). Range: 90-99.9. Example: 99 means 99% confidence that losses won't exceed the calculated value. Higher values provide more conservative risk estimates.",
            "type": "number"
        }
    ]
})
@router.get("/risk_metrics")
def get_risk_metrics(risk_category: str = "All", calculation_method: str = "VaR", confidence_interval: float = 99, time_horizon_metrics: str = "1D", portfolio_level: str = "Firm"):
    """Get risk management summary metrics."""
    import random
    
    # Generate metrics based on parameters
    base_metrics = {
        "All": [
            {"label": f"Total Exposure ({portfolio_level})", "value": "$28.4B", "delta": "5.2"},
            {"label": "Collateral Coverage", "value": "87.3%", "delta": "-2.1"},
            {"label": "Settlement Fail Rate", "value": "0.42%", "delta": "0.08"},
            {"label": "Liquidity Score", "value": "78/100", "delta": "-3.0"},
            {"label": f"{calculation_method} ({confidence_interval}%)", "value": "$142M", "delta": "12.5"}
        ],
        "Credit": [
            {"label": "Credit Exposure", "value": "$18.2B", "delta": "3.8"},
            {"label": "Default Probability", "value": "1.2%", "delta": "0.3"},
            {"label": "Credit VaR", "value": "$89M", "delta": "8.1"},
            {"label": "Recovery Rate", "value": "65%", "delta": "-1.5"}
        ],
        "Market": [
            {"label": "Market VaR", "value": "$95M", "delta": "15.2"},
            {"label": "Duration Risk", "value": "4.2", "delta": "0.3"},
            {"label": "Equity Beta", "value": "1.15", "delta": "0.05"},
            {"label": "FX Exposure", "value": "$2.1B", "delta": "12.0"}
        ],
        "Liquidity": [
            {"label": "Cash Position", "value": "$3.2B", "delta": "8.5"},
            {"label": "Liquidity Coverage", "value": "125%", "delta": "2.3"},
            {"label": "Funding Gap", "value": "$850M", "delta": "-5.1"},
            {"label": "Asset Liquidity", "value": "82%", "delta": "-1.8"}
        ],
        "Operational": [
            {"label": "Op Risk Capital", "value": "$450M", "delta": "2.1"},
            {"label": "System Uptime", "value": "99.8%", "delta": "0.1"},
            {"label": "Trade Errors", "value": "23", "delta": "-15.0"},
            {"label": "Audit Score", "value": "92/100", "delta": "1.0"}
        ]
    }
    
    return base_metrics.get(risk_category, base_metrics["All"])[:5]

# 6. Stress Test Results Table
@register_widget({
    "name": "Stress Test Results",
    "description": "Detailed stress test results by scenario",
    "category": "Risk Management",
    "subCategory": "Stress Testing",
    "type": "table",
    "endpoint": "risk_management/stress_test_results",
    "gridData": {"w": 20, "h": 10},
    "data": {
        "table": {
            "enableCharts": True,
            "chartView": {
                "enabled": False,
                "chartType": "column"
            },
            "columnsDefs": [
                {
                    "field": "scenario",
                    "headerName": "Scenario",
                    "width": 200,
                    "pinned": "left"
                },
                {
                    "field": "probability",
                    "headerName": "Probability",
                    "width": 100,
                    "cellDataType": "number",
                    "formatterFn": "percent"
                },
                {
                    "field": "impact",
                    "headerName": "P&L Impact ($M)",
                    "width": 150,
                    "cellDataType": "number",
                    "formatterFn": "int",
                    "renderFn": "greenRed"
                },
                {
                    "field": "collateral_call",
                    "headerName": "Collateral Call ($M)",
                    "width": 150,
                    "cellDataType": "number",
                    "formatterFn": "int"
                },
                {
                    "field": "liquidity_need",
                    "headerName": "Liquidity Need ($M)",
                    "width": 150,
                    "cellDataType": "number",
                    "formatterFn": "int"
                },
                {
                    "field": "risk_score",
                    "headerName": "Risk Score",
                    "width": 120,
                    "renderFn": "columnColor",
                    "renderFnParams": {
                        "colorRules": [
                            {"condition": "gt", "value": 80, "color": "#ED6D3C", "fill": True},
                            {"condition": "gt", "value": 60, "color": "#F28352", "fill": True},
                            {"condition": "gt", "value": 40, "color": "#0E5447", "fill": False},
                            {"condition": "lte", "value": 40, "color": "#0B413A", "fill": False}
                        ]
                    }
                }
            ]
        }
    },
    "params": [
        {
            "paramName": "scenario_type",
            "value": "All",
            "label": "Scenario Type",
            "description": "Type of stress test scenarios to display. Valid values: 'All' (all scenarios), 'Historical' (based on past crises), 'Hypothetical' (designed stress scenarios), 'Regulatory' (supervisory stress tests). Determines which stress test results are shown.",
            "type": "text",
            "options": [
                {"label": "All Scenarios", "value": "All"},
                {"label": "Historical", "value": "Historical"},
                {"label": "Hypothetical", "value": "Hypothetical"},
                {"label": "Regulatory", "value": "Regulatory"}
            ]
        },
        {
            "paramName": "time_horizon_stress",
            "value": "1Y",
            "label": "Time Horizon",
            "description": "Time horizon for stress test projections. Valid formats: 1M (1 month), 3M (quarterly), 6M (semi-annual), 1Y (annual), 2Y (bi-annual). Determines the projection period for stress scenario analysis.",
            "type": "text",
            "options": [
                {"label": "1 Month", "value": "1M"},
                {"label": "3 Months", "value": "3M"},
                {"label": "6 Months", "value": "6M"},
                {"label": "1 Year", "value": "1Y"},
                {"label": "2 Years", "value": "2Y"}
            ]
        },
        {
            "paramName": "include_tail_risk",
            "value": True,
            "label": "Include Tail Risk Events",
            "description": "Include extreme tail risk events in stress testing analysis. When enabled, considers low-probability, high-impact scenarios. When disabled, focuses on more likely stress scenarios only.",
            "type": "boolean"
        }
    ]
})
@router.get("/stress_test_results")
def get_stress_test_results(scenario_type: str = "All", severity_threshold: str = "Medium", time_horizon_stress: str = "1Y", regulatory_framework: str = "All", include_tail_risk: bool = True):
    """Get stress test scenario results."""
    import random
    
    # Define scenarios by type
    scenario_groups = {
        "Market": [
            {"name": "Market Crash (2008-like)", "prob": 5, "impact": -2500, "type": "Market"},
            {"name": "Flash Crash", "prob": 10, "impact": -800, "type": "Market"},
            {"name": "Interest Rate Shock (+300bp)", "prob": 15, "impact": -1200, "type": "Market"}
        ],
        "Credit": [
            {"name": "Credit Spread Widening", "prob": 20, "impact": -600, "type": "Credit"},
            {"name": "Counterparty Default", "prob": 3, "impact": -3000, "type": "Credit"},
            {"name": "Sovereign Default", "prob": 2, "impact": -4500, "type": "Credit"}
        ],
        "Liquidity": [
            {"name": "Liquidity Crisis", "prob": 8, "impact": -1800, "type": "Liquidity"},
            {"name": "Funding Squeeze", "prob": 15, "impact": -900, "type": "Liquidity"}
        ],
        "Operational": [
            {"name": "Operational Failure", "prob": 12, "impact": -400, "type": "Operational"},
            {"name": "Cyber Attack", "prob": 7, "impact": -1000, "type": "Operational"}
        ]
    }
    
    # Select scenarios based on type filter
    all_scenarios = []
    if scenario_type == "All":
        for group in scenario_groups.values():
            all_scenarios.extend(group)
    else:
        all_scenarios = scenario_groups.get(scenario_type, [])
    
    # Add tail risk events if requested
    if include_tail_risk:
        tail_events = [
            {"name": "Pandemic-like Event", "prob": 1, "impact": -5000, "type": "Operational"},
            {"name": "Global Currency Crisis", "prob": 2, "impact": -3500, "type": "Market"}
        ]
        all_scenarios.extend(tail_events)
    
    # Filter by severity
    severity_thresholds = {"Low": 500, "Medium": 1000, "High": 2000, "Extreme": 3000}
    if severity_threshold != "All":
        threshold = severity_thresholds.get(severity_threshold, 0)
        all_scenarios = [s for s in all_scenarios if abs(s["impact"]) >= threshold]
    
    # Generate results
    results = []
    for scenario in all_scenarios:
        # Adjust impact based on time horizon
        time_multiplier = {"1M": 0.3, "3M": 0.6, "6M": 0.8, "1Y": 1.0, "2Y": 1.3}[time_horizon_stress]
        adjusted_impact = scenario["impact"] * time_multiplier
        
        results.append({
            "scenario": scenario["name"],
            "probability": scenario["prob"],
            "impact": round(adjusted_impact),
            "collateral_call": round(abs(adjusted_impact) * random.uniform(0.3, 0.6)),
            "liquidity_need": round(abs(adjusted_impact) * random.uniform(0.4, 0.8)),
            "risk_score": min(100, abs(adjusted_impact) / 30)
        })
    
    return sorted(results, key=lambda x: abs(x["impact"]), reverse=True)

# 7. Dashboard Notes
@register_widget({
    "name": "Risk Management Dashboard Notes",
    "description": "Comprehensive overview and documentation for the Risk Management dashboard",
    "category": "Documentation",
    "type": "markdown",
    "endpoint": "risk_management/notes",
    "gridData": {"w": 40, "h": 30}
})
@router.get("/notes")
def get_notes():
    """Get Risk Management dashboard documentation."""
    markdown_content = """# DTCC Risk Management Dashboard

## Overview
The DTCC Risk Management Dashboard provides advanced risk management and stress testing capabilities featuring counterparty exposure analysis, collateral requirement forecasting, settlement risk monitoring, and comprehensive stress scenario modeling. This dashboard enables proactive risk assessment and mitigation across all trading activities.

## Purpose
• **Counterparty Risk Monitoring**: Track and analyze exposures across all counterparties with real-time risk scoring and concentration analysis

• **Collateral Management**: Forecast collateral requirements under various scenarios including baseline, stressed, and extreme market conditions

• **Settlement Risk Assessment**: Monitor settlement failures, track obligations, and identify potential disruptions across asset classes

• **Stress Testing**: Run comprehensive stress tests using historical and hypothetical scenarios to assess portfolio resilience

---

## Tab 1: Exposure Analysis
**Purpose**: Comprehensive view of counterparty exposures and concentration risks

### Widgets:
• **Risk Metrics Summary**: Key risk indicators including total exposure ($28.4B), collateral coverage (87.3%), settlement fail rate (0.42%), liquidity score (78/100), and VaR 99% ($142M)

• **Counterparty Exposure Treemap**: Hierarchical visualization of exposures by firm and sector, switchable between gross exposure, net exposure, and collateralized views

• **Liquidity Heatmap**: Repo availability matrix across collateral types (Treasury, Agency, MBS, Corporate IG/HY, Equity) and maturity buckets

---

## Tab 2: Stress Testing
**Purpose**: Scenario analysis and stress testing for risk assessment and planning

### Widgets:
• **Collateral Requirement Forecast**: 90-day projection of collateral needs under baseline, stressed (2008-like), and extreme stress scenarios

• **Settlement Fails Tracker**: Stacked area chart showing fails by asset class (Treasury, Equity, MBS, Corporate) with trend analysis

• **Stress Test Results**: Comprehensive scenario analysis table showing probability, P&L impact, collateral calls, liquidity needs, and risk scores for various stress events

---

## Data Sources
• **Exposure Management Systems**: Real-time feeds from counterparty exposure databases and netting systems
• **Collateral Management Platforms**: Integration with collateral optimization and forecasting systems
• **Settlement Infrastructure**: Direct connections to DTCC settlement platforms for real-time fail tracking
• **Market Data Providers**: Historical and real-time market data for stress testing and scenario modeling
• **Risk Management Systems**: Portfolio risk metrics, VaR calculations, and concentration monitoring tools

## Key Metrics Tracked
• **Exposure Metrics**: Gross exposure, net exposure, collateral coverage ratios, and concentration indices by counterparty and sector
• **Liquidity Indicators**: Available collateral, funding costs, repo availability, and liquidity transformation ratios
• **Settlement Performance**: Fail rates, settlement times, obligation aging, and counterparty-specific settlement statistics
• **Stress Test Results**: Scenario-based P&L impacts, capital adequacy, liquidity survival periods, and recovery metrics
• **Risk Appetite Metrics**: Limit utilization, risk budget consumption, and early warning indicator thresholds
• **Collateral Optimization**: Cheapest-to-deliver analysis, substitution costs, and inventory management metrics
• **Operational Risk**: Processing errors, system availability, and exception rates across risk management processes

## Use Cases
• **Chief Risk Officers**: Oversee enterprise-wide risk management, set risk appetite, and ensure regulatory compliance
• **Portfolio Managers**: Monitor position-level risks, optimize collateral usage, and assess concentration limits
• **Collateral Managers**: Forecast funding needs, optimize collateral allocation, and manage margin requirements
• **Stress Testing Teams**: Design and execute stress scenarios, validate model assumptions, and report regulatory stress tests
• **Treasury Teams**: Manage liquidity risks, optimize funding strategies, and coordinate with collateral management"""

    return markdown_content