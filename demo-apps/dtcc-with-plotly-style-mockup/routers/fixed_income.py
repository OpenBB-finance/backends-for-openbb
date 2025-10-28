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
    generate_treasury_volumes,
    generate_repo_rates,
    generate_settlement_fails,
    generate_dealer_activity
)
from plotly_config import get_theme_colors, base_layout, get_toolbar_config, get_dtcc_chart_colors

router = APIRouter(prefix="/fixed_income", tags=["Fixed Income"])

# 1. Treasury Trade Volumes
@register_widget({
    "name": "Treasury Trade Volumes",
    "description": "Trade volumes over time by tenor (bills, notes, bonds)",
    "category": "Fixed Income",
    "subCategory": "Treasury Market",
    "type": "chart",
    "endpoint": "fixed_income/treasury_volumes",
    "gridData": {"w": 20, "h": 10},
    "raw": True,
    "params": [
        {
            "paramName": "time_period",
            "value": "1M",
            "label": "Time Period",
            "description": "Time window for treasury volume aggregation. 1D = daily volumes, 1W = weekly aggregation, 1M = monthly aggregation, 3M = quarterly, 1Y = annual. Determines the time series granularity and lookback period for volume analysis.",
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
            "paramName": "min_trade_size",
            "value": 1,
            "label": "Min Trade Size ($M)",
            "description": "Minimum trade size threshold in millions of USD. Only treasury transactions above this amount will be included in volume calculations. Range: 0.1-1000. Example: 5 filters trades below $5M.",
            "type": "number"
        },
        {
            "paramName": "trading_venue",
            "value": "All",
            "label": "Trading Venue",
            "description": "Filter by treasury trading venue type. D2C = dealer-to-customer transactions, D2D = interdealer market, Electronic = electronic trading platforms, Voice = voice-brokered trades, Primary = primary market auctions. Select 'All' to include all venue types.",
            "type": "text",
            "options": [
                {"label": "All Venues", "value": "All"},
                {"label": "Dealer-to-Customer", "value": "D2C"},
                {"label": "Dealer-to-Dealer", "value": "D2D"},
                {"label": "Electronic Trading", "value": "Electronic"},
                {"label": "Voice Trading", "value": "Voice"},
                {"label": "Primary Market", "value": "Primary"}
            ]
        }
    ]
})
@router.get("/treasury_volumes")
def get_treasury_volumes(time_period: str = "1M", treasury_types: List[str] = Query(default=["Bills (1-12M)", "Notes (2-10Y)"]), trading_venue: str = "All", min_trade_size: int = 1, maturity_bucket: str = "All", counterparty_segment: str = "All", raw: bool = False, theme: str = "dark"):
    """Get treasury trade volumes by tenor."""
    data = generate_treasury_volumes(time_period=time_period, 
                                   treasury_types=treasury_types,
                                   trading_venue=trading_venue,
                                   min_trade_size=min_trade_size,
                                   maturity_bucket=maturity_bucket,
                                   counterparty_segment=counterparty_segment)
    
    if raw:
        return data
    
    colors = get_theme_colors(theme)
    fig = go.Figure()
    
    dtcc_colors = get_dtcc_chart_colors()
    color_map = {
        "Bills (1-12M)": dtcc_colors['primary'],      # Core orange
        "Notes (2-10Y)": dtcc_colors['secondary'],    # Core green
        "Bonds (20-30Y)": dtcc_colors['tertiary'],    # Light orange
        "TIPS": dtcc_colors['quaternary'],             # Dark green
        "FRNs": dtcc_colors['fifth']                   # Even lighter orange
    }
    
    for tenor_data in data:
        fig.add_trace(go.Scatter(
            x=tenor_data["dates"],
            y=tenor_data["volumes"],
            name=tenor_data["tenor"],
            mode='lines',
            line=dict(width=2, color=color_map.get(tenor_data["tenor"], dtcc_colors['neutral']))
        ))
    
    layout_config = base_layout(theme=theme)
    layout_config.update({
        # 'title': 'Treasury Trade Volumes by Tenor',
        'xaxis_title': 'Date',
        'yaxis_title': 'Volume ($B)',
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

# 2. Repo Rate Spread Tracker
@register_widget({
    "name": "Repo Rate Spread Tracker",
    "description": "DTCC GCF Repo vs SOFR/ON RRP spreads",
    "category": "Fixed Income",
    "subCategory": "Repo Market",
    "type": "chart",
    "endpoint": "fixed_income/repo_spreads",
    "gridData": {"w": 20, "h": 10},
    "refetchInterval": 300000,
    "params": [
        {
            "paramName": "time_horizon_repo",
            "value": "1M",
            "label": "Time Horizon",
            "description": "Time period for repo rate spread analysis. 1D = intraday spreads, 1W = weekly patterns, 1M = monthly trends, 3M = quarterly analysis, 6M = longer-term spread relationships. Affects the granularity of spread calculations and trend analysis.",
            "type": "text",
            "options": [
                {"label": "1 Day", "value": "1D"},
                {"label": "1 Week", "value": "1W"},
                {"label": "1 Month", "value": "1M"},
                {"label": "3 Months", "value": "3M"},
                {"label": "6 Months", "value": "6M"}
            ]
        },
        {
            "paramName": "spread_analysis",
            "value": True,
            "label": "Show Spread Analysis",
            "description": "Enable detailed spread analysis between DTCC GCF Repo rates and benchmark rates. When enabled, displays spread calculations, volatility metrics, and basis point movements. When disabled, shows raw rates only.",
            "type": "boolean"
        },
        {
            "paramName": "benchmark_rate",
            "value": "SOFR",
            "label": "Benchmark Rate",
            "description": "Primary benchmark rate for spread calculations. SOFR = Secured Overnight Financing Rate, FedFunds = Federal Funds Rate, TBill = Treasury Bill rates, ONRRP = Overnight Reverse Repo Rate. Determines the baseline for spread analysis.",
            "type": "text",
            "options": [
                {"label": "SOFR", "value": "SOFR"},
                {"label": "Fed Funds", "value": "FedFunds"},
                {"label": "Treasury Bill", "value": "TBill"},
                {"label": "ON RRP", "value": "ONRRP"}
            ]
        }
    ]
})
@router.get("/repo_spreads")
def get_repo_spreads(benchmark_rates: List[str] = Query(default=["SOFR", "ON RRP"]), repo_types: List[str] = Query(default=["GCF Repo"]), collateral_grades: List[str] = Query(default=["Treasury", "Agency"]), time_horizon_repo: str = "1M", spread_analysis: bool = True, theme: str = "dark"):
    """Track repo rate spreads."""
    data = generate_repo_rates(time_period=time_horizon_repo,
                             currencies=["USD"],
                             region="US")
    colors = get_theme_colors(theme)
    
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        row_heights=[0.7, 0.3],
        subplot_titles=('Repo Rates', 'GCF-SOFR Spread')
    )
    
    dtcc_colors = get_dtcc_chart_colors()
    
    # Plot rates
    fig.add_trace(
        go.Scatter(x=data["dates"], y=data["GCF_Repo_USD"], 
                  name="GCF Repo", line=dict(color=dtcc_colors['primary'], width=2)),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=data["dates"], y=data["SOFR_USD"], 
                  name="SOFR", line=dict(color=dtcc_colors['secondary'], width=2)),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=data["dates"], y=data["ON_RRP_USD"], 
                  name="ON RRP", line=dict(color=dtcc_colors['tertiary'], width=2)),
        row=1, col=1
    )
    
    # Calculate and plot spread
    spread = [gcf - sofr for gcf, sofr in zip(data["GCF_Repo_USD"], data["SOFR_USD"])]
    fig.add_trace(
        go.Scatter(x=data["dates"], y=spread, 
                  name="GCF-SOFR Spread", 
                  fill='tozeroy',
                  line=dict(color=dtcc_colors['quaternary'], width=2)),
        row=2, col=1
    )
    
    layout_config = base_layout(theme=theme)
    layout_config.update({
        # 'title': 'Repo Rate Monitor',
        'xaxis2_title': 'Date',
        'yaxis_title': 'Rate (%)',
        'yaxis2_title': 'Spread (bps)',
        'hovermode': 'x unified',
        'showlegend': True,
        'height': 500
    })
    
    fig.update_layout(layout_config)
    
    figure_json = json.loads(fig.to_json())
    figure_json['config'] = get_toolbar_config()
    
    return figure_json

# 3. Fails-to-Deliver Chart
@register_widget({
    "name": "Fails-to-Deliver Monitor",
    "description": "Track fails by CUSIP and tenor",
    "category": "Fixed Income",
    "subCategory": "Settlement",
    "type": "table",
    "endpoint": "fixed_income/fails_to_deliver",
    "gridData": {"w": 20, "h": 10},
    "data": {
        "table": {
            "enableCharts": True,
            "chartView": {
                "enabled": False,
                "chartType": "bar"
            },
            "columnsDefs": [
                {
                    "field": "cusip",
                    "headerName": "CUSIP",
                    "width": 120,
                    "pinned": "left"
                },
                {
                    "field": "tenor",
                    "headerName": "Tenor",
                    "width": 80
                },
                {
                    "field": "fails_amount",
                    "headerName": "Fails Amount ($)",
                    "width": 150,
                    "cellDataType": "number",
                    "formatterFn": "int",
                    "chartDataType": "series"
                },
                {
                    "field": "fail_rate",
                    "headerName": "Fail Rate (%)",
                    "width": 120,
                    "cellDataType": "number",
                    "formatterFn": "normalizedPercent",
                    "renderFn": "columnColor",
                    "renderFnParams": {
                        "colorRules": [
                            {"condition": "gt", "value": 3, "color": "#ED6D3C", "fill": True},
                            {"condition": "lte", "value": 3, "color": "#0E5447", "fill": False}
                        ]
                    }
                },
                {
                    "field": "days_failed",
                    "headerName": "Days Failed",
                    "width": 110,
                    "cellDataType": "number",
                    "renderFn": "greenRed"
                }
            ]
        }
    },
    "params": [
        {
            "paramName": "fail_threshold",
            "value": 1.0,
            "label": "Min Fail Rate (%)",
            "description": "Minimum failure rate threshold as a percentage. Only securities with failure rates above this level will be displayed. Range: 0-100. Example: 2.5 shows securities with >2.5% failure rate.",
            "type": "number"
        },
        {
            "paramName": "maturity_range",
            "value": "All",
            "label": "Maturity Range",
            "description": "Filter securities by time to maturity. 0-1Y = short-term (bills), 1-3Y = short-medium term, 3-7Y = medium term, 7-10Y = long term, 10Y+ = very long term. Select 'All' to include all maturity ranges.",
            "type": "text",
            "options": [
                {"label": "All Maturities", "value": "All"},
                {"label": "0-1 Year", "value": "0-1Y"},
                {"label": "1-3 Years", "value": "1-3Y"},
                {"label": "3-7 Years", "value": "3-7Y"},
                {"label": "7-10 Years", "value": "7-10Y"},
                {"label": "10+ Years", "value": "10Y+"}
            ]
        },
        {
            "paramName": "security_type",
            "value": "All",
            "label": "Security Type",
            "description": "Filter by fixed income security type. Treasury Bills = short-term government debt, Treasury Notes = medium-term government debt, Treasury Bonds = long-term government debt, Agency = government-sponsored enterprise securities, Corporate = corporate bonds. Select 'All' to include all security types.",
            "type": "text",
            "options": [
                {"label": "All Securities", "value": "All"},
                {"label": "Treasury Bills", "value": "Treasury Bills"},
                {"label": "Treasury Notes", "value": "Treasury Notes"},
                {"label": "Treasury Bonds", "value": "Treasury Bonds"},
                {"label": "Agency Securities", "value": "Agency"},
                {"label": "Corporate Bonds", "value": "Corporate"}
            ]
        }
    ]
})
@router.get("/fails_to_deliver")
def get_fails_to_deliver(fail_threshold: float = 1.0, security_types: List[str] = Query(default=["Treasury", "Agency"]), maturity_range: str = "All", aging_filter: str = "All", settlement_mode: str = "All"):
    """Get fails-to-deliver data."""
    return generate_settlement_fails(fail_threshold=fail_threshold,
                                   security_types=security_types,
                                   maturity_range=maturity_range,
                                   aging_filter=aging_filter,
                                   settlement_mode=settlement_mode)

# 4. Dealer Activity Leaderboard
@register_widget({
    "name": "Dealer Activity Leaderboard",
    "description": "Top repo lenders and borrowers",
    "category": "Fixed Income",
    "subCategory": "Dealer Activity",
    "type": "table",
    "endpoint": "fixed_income/dealer_activity",
    "gridData": {"w": 20, "h": 10},
    "data": {
        "table": {
            "enableCharts": True,
            "chartView": {
                "enabled": True,
                "chartType": "groupedColumn"
            },
            "columnsDefs": [
                {
                    "field": "dealer",
                    "headerName": "Dealer",
                    "width": 180,
                    "pinned": "left",
                    "chartDataType": "category"
                },
                {
                    "field": "lending_volume",
                    "headerName": "Lending ($B)",
                    "width": 130,
                    "cellDataType": "number",
                    "formatterFn": "normalizedPercent",
                    "chartDataType": "series"
                },
                {
                    "field": "borrowing_volume",
                    "headerName": "Borrowing ($B)",
                    "width": 130,
                    "cellDataType": "number",
                    "formatterFn": "normalizedPercent",
                    "chartDataType": "series"
                },
                {
                    "field": "net_position",
                    "headerName": "Net Position ($B)",
                    "width": 140,
                    "cellDataType": "number",
                    "formatterFn": "normalizedPercent",
                    "renderFn": "greenRed"
                },
                {
                    "field": "market_share",
                    "headerName": "Market Share (%)",
                    "width": 130,
                    "cellDataType": "number",
                    "formatterFn": "normalizedPercent"
                }
            ]
        }
    },
    "params": [
        {
            "paramName": "dealer_tier",
            "value": "All",
            "label": "Dealer Tier",
            "description": "Filter dealers by market tier classification. Tier 1 = primary dealers with direct Fed relationships, Tier 2 = regional dealers with significant market presence, Tier 3 = specialist dealers focusing on specific sectors. Select 'All' to include all dealer tiers.",
            "type": "text",
            "options": [
                {"label": "All Dealers", "value": "All"},
                {"label": "Tier 1 (Primary)", "value": "Tier1"},
                {"label": "Tier 2 (Regional)", "value": "Tier2"},
                {"label": "Tier 3 (Specialist)", "value": "Tier3"}
            ]
        },
        {
            "paramName": "min_volume_threshold",
            "value": 10,
            "label": "Min Volume ($B)",
            "description": "Minimum total trading volume threshold in billions of USD. Only dealers with combined lending/borrowing volume above this level will be displayed in the leaderboard. Range: 1-1000. Example: 50 shows dealers with >$50B volume.",
            "type": "number"
        },
        {
            "paramName": "activity_type",
            "value": "Both",
            "label": "Activity Type",
            "description": "Filter by type of repo market activity. Both = lending and borrowing activity combined, Lending = cash lending activity only, Borrowing = cash borrowing activity only. Affects which volumes are displayed and ranked.",
            "type": "text",
            "options": [
                {"label": "Both Lending & Borrowing", "value": "Both"},
                {"label": "Lending Only", "value": "Lending"},
                {"label": "Borrowing Only", "value": "Borrowing"}
            ]
        }
    ]
})
@router.get("/dealer_activity")
def get_dealer_activity(dealer_tier: str = "All", activity_type: str = "Both", repo_segment: str = "All", time_window: str = "1M", min_volume_threshold: int = 10):
    """Get dealer activity leaderboard."""
    return generate_dealer_activity()

# 5. Liquidity Curve Heatmap
@register_widget({
    "name": "Liquidity Curve Heatmap",
    "description": "Repo availability vs collateral type",
    "category": "Fixed Income",
    "subCategory": "Liquidity",
    "type": "chart",
    "endpoint": "fixed_income/liquidity_curve",
    "gridData": {"w": 20, "h": 10}
})
@router.get("/liquidity_curve")
def get_liquidity_curve(theme: str = "dark"):
    """Generate liquidity curve heatmap."""
    import random
    
    # Generate mock data
    collateral_types = ["Treasury", "Agency", "MBS", "Corp IG", "Corp HY"]
    terms = ["O/N", "1W", "2W", "1M", "3M", "6M", "9M", "1Y"]
    
    z_data = []
    for collateral in collateral_types:
        row = []
        for term in terms:
            # Treasury has highest availability, Corp HY lowest
            base = 80 if collateral == "Treasury" else 60 if collateral == "Agency" else 40
            availability = base + random.uniform(-20, 20)
            row.append(max(0, min(100, availability)))
        z_data.append(row)
    
    colors = get_theme_colors(theme)
    
    fig = go.Figure(data=go.Heatmap(
        z=z_data,
        x=terms,
        y=collateral_types,
        colorscale='RdYlGn',
        zmid=50,
        text=[[f'{val:.0f}%' for val in row] for row in z_data],
        texttemplate='%{text}',
        hovertemplate='Collateral: %{y}<br>Term: %{x}<br>Availability: %{z:.1f}%<extra></extra>'
    ))
    
    layout_config = base_layout(theme=theme)
    layout_config.update({
        # 'title': 'Repo Liquidity Availability',
        'xaxis_title': 'Term',
        'yaxis_title': 'Collateral Type',
        'height': 400
    })
    
    fig.update_layout(layout_config)
    
    figure_json = json.loads(fig.to_json())
    figure_json['config'] = get_toolbar_config()
    
    return figure_json

# 6. Fixed Income Metrics
@register_widget({
    "name": "Fixed Income Metrics",
    "description": "Key fixed income market metrics",
    "category": "Fixed Income",
    "subCategory": "Summary",
    "type": "metric",
    "endpoint": "fixed_income/metrics",
    "gridData": {"w": 20, "h": 4}
})
@router.get("/metrics")
def get_fixed_income_metrics():
    """Get fixed income market metrics."""
    return [
        {
            "label": "Treasury Volume",
            "value": "$892B",
            "delta": "8.3"
        },
        {
            "label": "GCF Repo Rate",
            "value": "2.48%",
            "delta": "0.05"
        },
        {
            "label": "Fails Rate",
            "value": "1.2%",
            "delta": "-0.3"
        },
        {
            "label": "Top Dealer Share",
            "value": "14.7%",
            "delta": "1.2"
        },
        {
            "label": "Liquidity Score",
            "value": "82/100",
            "delta": "-2.0"
        }
    ]

# 7. Dashboard Notes
@register_widget({
    "name": "Fixed Income Dashboard Notes",
    "description": "Comprehensive overview and documentation for the Fixed Income Markets dashboard",
    "category": "Documentation",
    "type": "markdown",
    "endpoint": "fixed_income/notes",
    "gridData": {"w": 40, "h": 30}
})
@router.get("/notes")
def get_notes():
    """Get Fixed Income dashboard documentation."""
    markdown_content = """# DTCC Fixed Income Markets Dashboard

## Overview
The DTCC Fixed Income Markets Dashboard provides comprehensive treasury and repo market monitoring capabilities, tracking trade volumes by tenor, repo rate spreads, settlement failures, dealer activity, and liquidity conditions across fixed income securities. This dashboard serves as the central hub for monitoring the health and efficiency of fixed income markets.

## Purpose
• **Treasury Market Analysis**: Monitor trading volumes, price trends, and liquidity conditions across bills, notes, bonds, TIPS, and FRNs

• **Repo Market Surveillance**: Track repo rates, spreads vs benchmarks, and monitor GCF repo activity and pricing dynamics

• **Settlement Monitoring**: Identify and track fails-to-deliver events, aging analysis, and settlement efficiency metrics

• **Dealer Activity Analysis**: Monitor primary dealer participation, market share analysis, and competitive dynamics in fixed income markets

---

## Tab 1: Treasury Market
**Purpose**: Comprehensive monitoring of U.S. Treasury market activity and performance

### Widgets:
• **Fixed Income Metrics**: Key market indicators including treasury volume ($892B), GCF repo rate (2.48%), fails rate (1.2%), top dealer share (14.7%), and liquidity score (82/100)

• **Treasury Trade Volumes**: Time series visualization of trading volumes by tenor (Bills 1-12M, Notes 2-10Y, Bonds 20-30Y, TIPS, FRNs) with selectable time periods

• **Repo Rate Spread Tracker**: Dual-panel chart showing repo rates vs SOFR/ON RRP with spread analysis and real-time updates every 5 minutes

---

## Tab 2: Repo Market
**Purpose**: In-depth analysis of repo market dynamics and participant activity

### Widgets:
• **Dealer Activity Leaderboard**: Ranking of primary dealers by lending/borrowing volume, net positions, and market share with chart visualization capabilities

• **Liquidity Curve Heatmap**: Matrix showing repo availability by collateral type (Treasury, Agency, MBS, Corp IG/HY) across term structure

• **Fails-to-Deliver Monitor**: Detailed table of settlement fails by CUSIP and tenor with fail rates, aging analysis, and severity indicators

---

## Data Sources
• **DTCC Trade Repositories**: Real-time feeds from DTCC's Fixed Income Clearing Corporation (FICC) for comprehensive trade capture

• **Federal Reserve Systems**: Integration with SOFR, ON RRP, and other Federal Reserve benchmark rates and operations data

• **Primary Dealer Reports**: Direct feeds from primary dealer reporting systems for accurate market share and activity analysis

• **Settlement Systems**: Real-time connection to DTCC settlement infrastructure for immediate fail detection and tracking

• **Market Data Vendors**: Bloomberg, Refinitiv, and other providers for benchmark rates, yield curves, and market reference data

## Key Metrics Tracked
• **Volume Analytics**: Daily, weekly, and monthly trading volumes across all treasury tenors with historical trend analysis

• **Rate Monitoring**: GCF repo rates, general collateral rates, SOFR spreads, and ON RRP facility usage

• **Settlement Performance**: Fail-to-deliver rates, aging analysis, resolution times, and counterparty-specific settlement statistics

• **Liquidity Indicators**: Bid-ask spreads, market depth, dealer inventory levels, and collateral availability metrics

• **Market Structure**: Dealer market share, client flow analysis, electronic vs voice trading ratios, and trading venue analysis

• **Risk Metrics**: Duration risk, yield curve positioning, basis risks, and interest rate exposure across the fixed income complex

• **Operational Efficiency**: Settlement rates, exception handling, STP rates, and processing time analytics

## Use Cases
• **Fixed Income Traders**: Monitor market conditions, identify trading opportunities, and track competitor activity and market share

• **Risk Managers**: Assess interest rate risk, monitor settlement exposure, and track counterparty concentration in repo markets

• **Compliance Teams**: Ensure adherence to repo market regulations and monitor for suspicious trading patterns or market manipulation

• **Treasury Operations**: Optimize repo funding strategies, monitor collateral availability, and manage settlement risk exposure

• **Market Regulators**: Oversee market integrity, monitor systemic risk in repo markets, and assess market structure evolution"""

    return markdown_content