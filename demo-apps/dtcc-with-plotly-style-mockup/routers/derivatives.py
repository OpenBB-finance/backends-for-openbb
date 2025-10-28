from fastapi import APIRouter
from fastapi.responses import JSONResponse
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime
import sys
sys.path.append('..')

from shared.decorators import register_widget
from mockup_data.data_generator import (
    generate_swap_notionals,
    generate_cds_spreads,
    generate_counterparties
)
from plotly_config import get_theme_colors, base_layout, get_toolbar_config, get_dtcc_chart_colors

router = APIRouter(prefix="/derivatives", tags=["Derivatives"])

def generate_volatility_surface():
    """Generate mock volatility surface data."""
    import numpy as np
    
    strikes = np.arange(80, 121, 5)
    maturities = [7, 14, 30, 60, 90, 120, 180, 365]
    
    surface = []
    for maturity in maturities:
        row = []
        for strike in strikes:
            # Generate implied vol with smile
            moneyness = strike / 100
            base_vol = 0.15 + 0.005 * maturity / 30
            smile = 0.05 * (moneyness - 1) ** 2
            vol = base_vol + smile + np.random.normal(0, 0.01)
            row.append(max(0.05, min(0.5, vol)) * 100)
        surface.append(row)
    
    return {
        "strikes": strikes.tolist(),
        "maturities": maturities,
        "surface": surface
    }

def generate_net_positions():
    """Generate net open positions by asset class."""
    asset_classes = ["Interest Rate", "FX", "Equity", "Credit", "Commodity"]
    
    data = []
    for asset in asset_classes:
        data.append({
            "asset_class": asset,
            "long_notional": np.random.uniform(1000, 5000),
            "short_notional": np.random.uniform(1000, 5000),
            "net_notional": np.random.uniform(-2000, 2000),
            "contracts": np.random.randint(10000, 100000),
            "delta": np.random.uniform(-1000, 1000)
        })
    
    return data

# 1. Swap Notional Traded
@register_widget({
    "name": "Swap Notional by Tenor",
    "description": "Swap notional traded by tenor and currency",
    "category": "Derivatives",
    "subCategory": "Interest Rate Swaps",
    "type": "table",
    "endpoint": "derivatives/swap_notionals",
    "gridData": {"w": 20, "h": 10},
    "data": {
        "table": {
            "enableCharts": True,
            "chartView": {
                "enabled": True,
                "chartType": "heatmap"
            },
            "columnsDefs": [
                {
                    "field": "currency",
                    "headerName": "Currency",
                    "width": 100,
                    "pinned": "left",
                    "chartDataType": "category"
                },
                {
                    "field": "tenor",
                    "headerName": "Tenor",
                    "width": 80,
                    "chartDataType": "category"
                },
                {
                    "field": "notional",
                    "headerName": "Notional ($B)",
                    "width": 130,
                    "cellDataType": "number",
                    "formatterFn": "normalizedPercent",
                    "chartDataType": "series"
                },
                {
                    "field": "trades",
                    "headerName": "# Trades",
                    "width": 100,
                    "cellDataType": "number",
                    "formatterFn": "int"
                },
                {
                    "field": "avg_size",
                    "headerName": "Avg Size ($M)",
                    "width": 120,
                    "cellDataType": "number",
                    "formatterFn": "normalizedPercent"
                }
            ]
        }
    },
    "params": [
        {
            "paramName": "currency_pairs",
            "value": "Major",
            "label": "Currency Pairs",
            "description": "Filter foreign exchange derivatives by currency pair categories. Valid values: 'Major' (USD/EUR/GBP/JPY pairs), 'Minor' (cross-currency pairs), 'Exotic' (emerging market currencies), 'All' (all currency pairs). Determines which FX derivatives are included in the volume analysis.",
            "type": "text",
            "options": [
                {"label": "Major Pairs", "value": "Major"},
                {"label": "Minor Pairs", "value": "Minor"},
                {"label": "Exotic Pairs", "value": "Exotic"},
                {"label": "All Pairs", "value": "All"}
            ]
        },
        {
            "paramName": "notional_threshold",
            "value": 10,
            "label": "Min Notional ($M)",
            "description": "Minimum notional amount in millions of USD for derivative transactions to include. Only trades with notional values above this threshold will be displayed. Range: 1-10000. Example: 50 shows derivatives with >$50M notional.",
            "type": "number"
        },
        {
            "paramName": "include_compression",
            "value": True,
            "label": "Include Compression Events",
            "description": "Include portfolio compression events in the volume analysis. When enabled, shows volume reductions from trade compression cycles. When disabled, shows gross trading volumes only without compression adjustments.",
            "type": "boolean"
        }
    ]
})
@router.get("/swap_notionals")
def get_swap_notionals(
    currency_pairs: str = "Major",
    tenor_buckets: str = "All",
    notional_threshold: float = 10,
    counterparty_types: str = "All",
    clearing_status: str = "All",
    include_compression: bool = True
):
    """Get swap notional data with filtering parameters."""
    data = generate_swap_notionals(
        currency_pairs=currency_pairs,
        tenor_buckets=tenor_buckets,
        notional_threshold=notional_threshold,
        counterparty_types=counterparty_types,
        clearing_status=clearing_status,
        include_compression=include_compression
    )
    return data

# 2. CDS Spread Monitor
@register_widget({
    "name": "CDS Spread Monitor",
    "description": "Monitor CDS spreads for indices and single names",
    "category": "Derivatives",
    "subCategory": "Credit Derivatives",
    "type": "chart",
    "endpoint": "derivatives/cds_spreads",
    "gridData": {"w": 20, "h": 12},
    "raw": True,
    "params": [
        {
            "paramName": "view",
            "value": "indices",
            "label": "View",
            "description": "Type of CDS spread analysis to display. Valid values: 'indices' (CDS index spreads like CDX/iTraxx), 'single_names' (individual corporate CDS), 'sovereigns' (government CDS), 'sectors' (industry sector analysis). Determines the scope of credit risk analysis.",
            "type": "text",
            "options": [
                {"label": "CDS Indices", "value": "indices"},
                {"label": "Single Names", "value": "single_names"},
                {"label": "Sovereigns", "value": "sovereigns"},
                {"label": "Sectors", "value": "sectors"}
            ]
        },
        {
            "paramName": "spread_threshold_min",
            "value": 0,
            "label": "Min Spread (bps)",
            "description": "Minimum CDS spread in basis points to include in analysis. Only entities with spreads above this level will be displayed. Range: 0-5000. Example: 100 shows CDS with spreads >100bps (higher credit risk).",
            "type": "number"
        },
        {
            "paramName": "spread_threshold_max",
            "value": 1000,
            "label": "Max Spread (bps)",
            "description": "Maximum CDS spread in basis points to include in analysis. Only entities with spreads below this level will be displayed. Range: 1-5000. Example: 500 shows CDS with spreads <500bps (moderate credit risk).",
            "type": "number"
        }
    ]
})
@router.get("/cds_spreads")
def get_cds_spreads(
    view: str = "indices",
    credit_ratings: str = "All",
    sector_filters: str = "All",
    geographic_regions: str = "All",
    maturity_buckets: str = "All",
    spread_threshold_min: float = 0,
    spread_threshold_max: float = 1000,
    raw: bool = False,
    theme: str = "dark"
):
    """Get CDS spread data with filtering parameters."""
    data = generate_cds_spreads(
        credit_ratings=credit_ratings,
        sector_filters=sector_filters,
        geographic_regions=geographic_regions,
        maturity_buckets=maturity_buckets,
        spread_threshold_min=spread_threshold_min,
        spread_threshold_max=spread_threshold_max
    )
    
    if raw:
        return data
    
    colors = get_theme_colors(theme)
    fig = go.Figure()
    
    if view in ["indices", "both"]:
        for idx, index_data in enumerate(data["indices"]):
            fig.add_trace(go.Scatter(
                x=index_data["dates"],
                y=index_data["spreads"],
                name=index_data["name"],
                mode='lines',
                line=dict(width=2),
                visible=True if view != "both" else None
            ))
    
    if view in ["single_names", "both"]:
        for name_data in data["single_names"]:
            fig.add_trace(go.Scatter(
                x=name_data["dates"],
                y=name_data["spreads"],
                name=name_data["name"],
                mode='lines',
                line=dict(width=2, dash='dash' if view == "both" else None),
                visible=True if view != "both" else None
            ))
    
    layout_config = base_layout(theme=theme)
    layout_config.update({
        # 'title': 'CDS Spread Monitor',
        'xaxis_title': 'Date',
        'yaxis_title': 'Spread (bps)',
        'hovermode': 'x unified',
        'legend': dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        )
    })
    
    fig.update_layout(layout_config)
    
    figure_json = json.loads(fig.to_json())
    figure_json['config'] = get_toolbar_config()
    
    return figure_json

# 3. Volatility Surface
@register_widget({
    "name": "Volatility Surface",
    "description": "3D volatility surface from OTC trade activity",
    "category": "Derivatives",
    "subCategory": "Options",
    "type": "chart",
    "endpoint": "derivatives/volatility_surface",
    "gridData": {"w": 20, "h": 15},
    "params": [
        {
            "paramName": "underlying_assets",
            "value": "Equity Indices",
            "label": "Underlying Assets",
            "description": "Type of underlying assets for volatility surface analysis. Valid values: 'Equity Indices' (S&P 500, VIX, etc.), 'Individual Stocks' (single name equities), 'FX' (currency pairs), 'Commodities' (gold, oil, etc.), 'Interest Rates' (swaptions, caps/floors). Determines the asset class for implied volatility analysis.",
            "type": "text",
            "options": [
                {"label": "Equity Indices", "value": "Equity Indices"},
                {"label": "Individual Stocks", "value": "Individual Stocks"},
                {"label": "FX", "value": "FX"},
                {"label": "Commodities", "value": "Commodities"},
                {"label": "Interest Rates", "value": "Interest Rates"}
            ]
        },
        {
            "paramName": "strike_range_min",
            "value": 80,
            "label": "Min Strike (%)",
            "description": "Minimum strike price as percentage of spot price for volatility surface. Range: 50-100. Example: 80 shows options with strikes from 80% of current price (out-of-the-money puts). Lower values include more out-of-the-money options.",
            "type": "number"
        },
        {
            "paramName": "smoothing_enabled",
            "value": True,
            "label": "Enable Surface Smoothing",
            "description": "Apply mathematical smoothing to the volatility surface to remove noise and interpolate between data points. When enabled, creates smoother surface visualization. When disabled, shows raw market data which may appear more jagged.",
            "type": "boolean"
        }
    ]
})
@router.get("/volatility_surface")
def get_volatility_surface(
    underlying_assets: str = "Equity Indices",
    strike_range_min: float = 80,
    strike_range_max: float = 120,
    expiry_buckets: str = "All",
    volatility_types: str = "Implied",
    smoothing_enabled: bool = True,
    theme: str = "dark"
):
    """Generate volatility surface visualization with filtering parameters."""
    vol_data = generate_volatility_surface()
    colors = get_theme_colors(theme)
    
    fig = go.Figure(data=[go.Surface(
        x=vol_data["strikes"],
        y=vol_data["maturities"],
        z=vol_data["surface"],
        colorscale='Viridis',
        hovertemplate='Strike: %{x}<br>Maturity: %{y} days<br>IV: %{z:.1f}%<extra></extra>'
    )])
    
    layout_config = base_layout(theme=theme)
    layout_config.update({
        # 'title': 'Implied Volatility Surface',
        'scene': dict(
            xaxis_title='Strike',
            yaxis_title='Maturity (Days)',
            zaxis_title='Implied Vol (%)',
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.5)
            )
        ),
        'height': 600
    })
    
    fig.update_layout(layout_config)
    
    figure_json = json.loads(fig.to_json())
    figure_json['config'] = get_toolbar_config()
    
    return figure_json

# 4. Net Open Positions
@register_widget({
    "name": "Net Open Positions",
    "description": "Net open positions by asset class",
    "category": "Derivatives",
    "subCategory": "Positions",
    "type": "table",
    "endpoint": "derivatives/net_positions",
    "gridData": {"w": 20, "h": 10},
    "data": {
        "table": {
            "enableCharts": True,
            "chartView": {
                "enabled": False,
                "chartType": "groupedColumn"
            },
            "columnsDefs": [
                {
                    "field": "asset_class",
                    "headerName": "Asset Class",
                    "width": 150,
                    "pinned": "left",
                    "chartDataType": "category"
                },
                {
                    "field": "long_notional",
                    "headerName": "Long ($B)",
                    "width": 120,
                    "cellDataType": "number",
                    "formatterFn": "normalizedPercent",
                    "chartDataType": "series"
                },
                {
                    "field": "short_notional",
                    "headerName": "Short ($B)",
                    "width": 120,
                    "cellDataType": "number",
                    "formatterFn": "normalizedPercent",
                    "chartDataType": "series"
                },
                {
                    "field": "net_notional",
                    "headerName": "Net ($B)",
                    "width": 120,
                    "cellDataType": "number",
                    "formatterFn": "normalizedPercent",
                    "renderFn": "greenRed"
                },
                {
                    "field": "contracts",
                    "headerName": "Contracts",
                    "width": 110,
                    "cellDataType": "number",
                    "formatterFn": "int"
                },
                {
                    "field": "delta",
                    "headerName": "Delta ($M)",
                    "width": 120,
                    "cellDataType": "number",
                    "formatterFn": "normalizedPercent",
                    "renderFn": "greenRed"
                }
            ]
        }
    },
    "params": [
        {
            "paramName": "position_threshold",
            "value": 100,
            "label": "Min Position Size ($M)",
            "description": "Minimum net position size in millions of USD to include in the analysis. Only firms with positions above this threshold will be displayed. Range: 1-10000. Example: 500 shows firms with >$500M net derivatives positions.",
            "type": "number"
        },
        {
            "paramName": "delta_exposure_min",
            "value": -5000,
            "label": "Min Delta Exposure ($M)",
            "description": "Minimum delta exposure in millions of USD (can be negative). Delta measures price sensitivity to underlying asset movements. Range: -10000 to 10000. Example: -1000 shows positions with delta exposure below -$1B (short exposure).",
            "type": "number"
        },
        {
            "paramName": "include_gamma",
            "value": False,
            "label": "Include Gamma Exposure",
            "description": "Include gamma exposure calculations in the position analysis. Gamma measures the rate of change of delta (second-order price sensitivity). When enabled, shows gamma risk alongside delta. When disabled, focuses on delta exposure only.",
            "type": "boolean"
        }
    ]
})
@router.get("/net_positions")
def get_net_positions(
    asset_classes: str = "All",
    position_threshold: float = 100,
    delta_exposure_min: float = -5000,
    delta_exposure_max: float = 5000,
    hedge_ratios: str = "All",
    include_gamma: bool = False
):
    """Get net open positions data with filtering parameters."""
    return generate_net_positions()

# 5. Counterparty Network - Derivatives
@register_widget({
    "name": "Derivatives Counterparty Network",
    "description": "Network of derivatives exposures between counterparties",
    "category": "Derivatives",
    "subCategory": "Network Analysis",
    "type": "chart",
    "endpoint": "derivatives/counterparty_network",
    "gridData": {"w": 20, "h": 15},
    "params": [
        {
            "paramName": "exposure_threshold",
            "value": 500,
            "label": "Min Exposure ($M)",
            "description": "Minimum counterparty exposure in millions of USD to include in the network visualization. Only relationships above this threshold will be displayed. Range: 10-50000. Example: 1000 shows exposures above $1B between counterparties.",
            "type": "number"
        },
        {
            "paramName": "risk_weighting",
            "value": "Notional",
            "label": "Risk Weighting",
            "description": "Method for calculating risk-weighted exposures in the network. Valid values: 'Notional' (gross notional amounts), 'Market Value' (current market value), 'Potential Future Exposure' (PFE-adjusted), 'CVA' (credit value adjustment weighted). Determines how connection thickness is calculated.",
            "type": "text",
            "options": [
                {"label": "Notional Amount", "value": "Notional"},
                {"label": "Market Value", "value": "Market Value"},
                {"label": "Potential Future Exposure", "value": "PFE"},
                {"label": "CVA Weighted", "value": "CVA"}
            ]
        },
        {
            "paramName": "show_cleared_only",
            "value": False,
            "label": "Show Cleared Trades Only",
            "description": "Filter to show only centrally cleared derivatives transactions. When enabled, excludes bilateral OTC trades and shows only CCP-cleared exposures. When disabled, includes both cleared and uncleared derivatives.",
            "type": "boolean"
        }
    ]
})
@router.get("/counterparty_network")
def get_derivatives_counterparty_network(
    counterparty_types: str = "All",
    exposure_threshold: float = 500,
    product_types: str = "All",
    risk_weighting: str = "Notional",
    show_cleared_only: bool = False,
    theme: str = "dark"
):
    """Generate derivatives counterparty network with filtering parameters."""
    import math
    import random
    
    firms = generate_counterparties()[:12]
    colors = get_theme_colors(theme)
    
    # Generate network data
    nodes = []
    links = []
    
    for i, firm in enumerate(firms):
        nodes.append({
            "id": firm,
            "derivatives_exposure": random.uniform(100, 3000),
            "collateral_posted": random.uniform(50, 1500)
        })
    
    # Create links
    for i in range(len(firms)):
        for j in range(i+1, len(firms)):
            if random.random() > 0.6:
                links.append({
                    "source": i,
                    "target": j,
                    "value": random.uniform(10, 500)
                })
    
    # Create Sankey diagram
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=[f"{firm}<br>${nodes[i]['derivatives_exposure']:.0f}M" 
                   for i, firm in enumerate(firms)],
            color=[f"rgba(59, 130, 246, {min(1, n['derivatives_exposure']/3000)})" 
                   for n in nodes]
        ),
        link=dict(
            source=[link["source"] for link in links],
            target=[link["target"] for link in links],
            value=[link["value"] for link in links],
            color="rgba(0, 0, 0, 0.2)"
        )
    )])
    
    layout_config = base_layout(theme=theme)
    layout_config.update({
        # 'title': 'Derivatives Exposure Flow Network',
        'height': 600
    })
    
    fig.update_layout(layout_config)
    
    figure_json = json.loads(fig.to_json())
    figure_json['config'] = get_toolbar_config()
    
    return figure_json

# 6. Derivatives Metrics
@register_widget({
    "name": "Derivatives Metrics",
    "description": "Key derivatives market metrics",
    "category": "Derivatives",
    "subCategory": "Summary",
    "type": "metric",
    "endpoint": "derivatives/metrics",
    "gridData": {"w": 20, "h": 4},
    "params": [
        {
            "paramName": "calculation_methods",
            "value": "Market Value",
            "label": "Calculation Method",
            "description": "Method for calculating derivatives metrics. Valid values: 'Market Value' (current market valuation), 'Notional' (face value amounts), 'Risk-Adjusted' (risk-weighted values), 'Credit Adjusted' (CVA/DVA adjusted). Determines the basis for metric calculations.",
            "type": "text",
            "options": [
                {"label": "Market Value", "value": "Market Value"},
                {"label": "Notional Amount", "value": "Notional"},
                {"label": "Risk-Adjusted", "value": "Risk-Adjusted"},
                {"label": "Credit Adjusted", "value": "Credit Adjusted"}
            ]
        },
        {
            "paramName": "time_horizons",
            "value": "1D",
            "label": "Time Horizon",
            "description": "Time period for derivatives metrics calculation. Valid formats: 1D (daily), 1W (weekly), 1M (monthly), 3M (quarterly), 1Y (annual). Affects the timeframe for volume, risk, and performance metrics.",
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
            "paramName": "include_compression",
            "value": True,
            "label": "Include Compression Metrics",
            "description": "Include portfolio compression cycle metrics in the summary. When enabled, shows compression ratios, notional reductions, and operational savings. When disabled, focuses on gross trading metrics without compression adjustments.",
            "type": "boolean"
        }
    ]
})
@router.get("/metrics")
def get_derivatives_metrics(
    calculation_methods: str = "Market Value",
    risk_categories: str = "All",
    time_horizons: str = "1D",
    include_compression: bool = True
):
    """Get derivatives market metrics with calculation parameters."""
    # Apply filtering logic based on parameters
    base_metrics = [
        {
            "label": "Total Notional",
            "value": "$487T",
            "delta": "6.8"
        },
        {
            "label": "Daily Volume",
            "value": "$2.3T",
            "delta": "-3.2"
        },
        {
            "label": "Compression Rate" if include_compression else "Active Contracts",
            "value": "42%" if include_compression else "1.2M",
            "delta": "2.1" if include_compression else "8.5"
        },
        {
            "label": "CDS Spread (IG)",
            "value": "68bps",
            "delta": "5.0"
        },
        {
            "label": "Active Contracts",
            "value": "1.2M",
            "delta": "8.5"
        }
    ]
    
    return base_metrics

# 7. Dashboard Notes
@register_widget({
    "name": "Derivatives Dashboard Notes",
    "description": "Comprehensive overview and documentation for the Derivatives Analytics dashboard",
    "category": "Documentation",
    "type": "markdown",
    "endpoint": "derivatives/notes",
    "gridData": {"w": 40, "h": 30}
})
@router.get("/notes")
def get_notes():
    """Get Derivatives dashboard documentation."""
    markdown_content = """# DTCC Derivatives Analytics Dashboard

## Overview
The DTCC Derivatives Analytics Dashboard provides advanced derivatives market analysis featuring insights into swap notionals, CDS spreads, volatility surfaces, net positions, and counterparty networks across OTC derivatives markets. This platform serves as the primary tool for monitoring derivatives market activity, risk exposure, and systemic connections.

## Purpose
• **Swap Market Analysis**: Monitor interest rate, credit, and cross-currency swap activity with notional tracking and tenor analysis

• **Credit Risk Monitoring**: Track CDS spreads across indices and single names with historical analysis and trend identification

• **Options Market Intelligence**: Analyze implied volatility surfaces and options activity for risk management and trading insights

• **Position Risk Assessment**: Monitor net open positions across asset classes and analyze concentration risks and exposure networks

---

## Tab 1: Swaps & Credit
**Purpose**: Comprehensive analysis of swap markets and credit derivatives activity

### Widgets:
• **Derivatives Metrics**: Key market indicators including total notional ($487T), daily volume ($2.3T), compression rate (42%), CDS spread IG (68bps), and active contracts (1.2M)

• **Swap Notional by Tenor**: Interactive table showing notional amounts by currency and tenor with heatmap visualization and trade count analysis

• **CDS Spread Monitor**: Multi-series chart tracking CDS spreads for major indices and single names with configurable views (indices, single names, both)

---

## Tab 2: Risk & Positions
**Purpose**: Risk analysis and position monitoring across derivatives portfolios

### Widgets:
• **Volatility Surface**: 3D visualization of implied volatility surface from OTC options activity showing strike/maturity relationships

• **Net Open Positions**: Comprehensive breakdown of long/short positions by asset class (Interest Rate, FX, Equity, Credit, Commodity) with delta analysis

• **Derivatives Counterparty Network**: Sankey diagram showing exposure flows between major dealers with derivatives-specific risk metrics

---

## Data Sources
• **DTCC Trade Repositories**: Complete OTC derivatives transaction reporting including swaps, forwards, and options across all asset classes

• **CDS Market Data**: Real-time and historical CDS spread data from major index providers and single-name credit markets

• **Options Clearing Corporations**: Cleared options data for volatility surface construction and options flow analysis

• **Counterparty Master Data**: Global Legal Entity Identifier (LEI) database and counterparty relationship mapping

• **Market Data Vendors**: Bloomberg, Refinitiv, and MarkitSERV for pricing, valuation, and reference data integration

## Key Metrics Tracked
• **Notional Exposures**: Gross and net notional amounts by asset class, currency, tenor, and counterparty with trend analysis

• **CDS Analytics**: Spread levels, basis relationships, curve analysis, and credit event monitoring across sovereign and corporate names

• **Volatility Metrics**: Implied volatility levels, volatility smile dynamics, term structure analysis, and volatility risk premiums

• **Position Analytics**: Net open interest, position concentration, delta exposure, and gamma risk across derivatives portfolios

• **Network Analysis**: Counterparty interconnectedness, systemic risk indicators, and exposure concentration metrics

• **Compression Efficiency**: Portfolio compression rates, notional reduction achieved, and operational risk mitigation

• **Regulatory Compliance**: Trade reporting completeness, regulatory capital metrics, and margin requirement tracking

## Use Cases
• **Derivatives Traders**: Monitor market conditions, identify trading opportunities, and analyze competitive positioning in OTC markets

• **Risk Managers**: Assess portfolio risk, monitor counterparty exposures, and manage derivatives-specific risks including CVA and DVA

• **Quantitative Analysts**: Analyze volatility surfaces, model validation, and derivatives pricing model calibration and validation

• **Compliance Officers**: Ensure derivatives trade reporting compliance and monitor for market abuse in OTC derivatives markets

• **Central Banks**: Monitor systemic risk in derivatives markets and assess the effectiveness of central clearing mandates"""

    return markdown_content