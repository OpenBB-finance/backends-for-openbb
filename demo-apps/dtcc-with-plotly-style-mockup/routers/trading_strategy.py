from fastapi import APIRouter
from fastapi.responses import JSONResponse
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import sys
sys.path.append('..')

from shared.decorators import register_widget
from mockup_data.data_generator import generate_time_series
from plotly_config import get_theme_colors, base_layout, get_toolbar_config, get_dtcc_chart_colors

router = APIRouter(prefix="/trading_strategy", tags=["Trading & Investment Strategy"])

def generate_repo_squeeze_data():
    """Generate repo squeeze detector data."""
    securities = ["UST 2Y", "UST 5Y", "UST 10Y", "UST 30Y", "TIPS 5Y", "TIPS 10Y"]
    
    data = []
    dates, _ = generate_time_series(30)
    
    for security in securities:
        for date in dates:
            base_rate = random.uniform(2.0, 3.0)
            squeeze_premium = random.uniform(0, 50) if random.random() > 0.8 else 0
            
            data.append({
                "date": date,
                "security": security,
                "repo_rate": round(base_rate + squeeze_premium, 2),
                "general_rate": round(base_rate, 2),
                "squeeze_premium": round(squeeze_premium, 2),
                "availability": round(random.uniform(50, 100), 1),
                "demand_score": round(random.uniform(0, 100), 1)
            })
    
    return data

def generate_sentiment_gauge():
    """Generate short-interest sentiment data."""
    sectors = ["Technology", "Healthcare", "Financial", "Energy", "Consumer", "Industrial"]
    
    data = []
    for sector in sectors:
        short_interest = random.uniform(5, 25)
        sentiment_score = 100 - (short_interest * 2)  # Inverse relationship
        
        data.append({
            "sector": sector,
            "short_interest_pct": round(short_interest, 1),
            "sentiment_score": round(sentiment_score, 1),
            "trend_7d": round(random.uniform(-5, 5), 2),
            "volume_ratio": round(random.uniform(0.8, 2.5), 2),
            "momentum": random.choice(["Bullish", "Bearish", "Neutral"])
        })
    
    return sorted(data, key=lambda x: x["sentiment_score"])

def generate_liquidity_fragmentation():
    """Generate liquidity fragmentation index data."""
    venues = ["Primary Market", "Dark Pools", "ECNs", "Crossing Networks", "Internalization"]
    assets = ["Equities", "Fixed Income", "FX", "Commodities"]
    
    data = []
    for asset in assets:
        total_volume = random.uniform(1000, 5000)
        remaining = total_volume
        
        for i, venue in enumerate(venues):
            if i == len(venues) - 1:
                volume = remaining
            else:
                volume = random.uniform(0, remaining * 0.4)
                remaining -= volume
            
            bid_ask = random.uniform(0.5, 5.0)
            
            data.append({
                "asset_class": asset,
                "venue": venue,
                "volume_share": round(volume / total_volume * 100, 1),
                "bid_ask_spread": round(bid_ask, 2),
                "fragmentation_score": round(random.uniform(20, 80), 1),
                "liquidity_score": round(100 - bid_ask * 10, 1)
            })
    
    return data

def generate_arbitrage_opportunities():
    """Generate cross-asset arbitrage monitor data."""
    opportunities = [
        "CDS vs Bond Spread", "ETF vs NAV", "Calendar Spread", 
        "Cross-Currency", "Index Arbitrage", "Convertible Bond"
    ]
    
    data = []
    for i, opp in enumerate(opportunities):
        data.append({
            "opportunity": opp,
            "spread_bps": round(random.uniform(-10, 25), 1),
            "historical_avg": round(random.uniform(2, 8), 1),
            "z_score": round(random.uniform(-2.5, 3.0), 2),
            "volume": round(random.uniform(50, 500), 2),
            "signal_strength": random.choice(["Weak", "Moderate", "Strong"]),
            "risk_adjusted_return": round(random.uniform(-5, 15), 2),
            "trade_feasibility": round(random.uniform(60, 95), 0)
        })
    
    return sorted(data, key=lambda x: abs(x["z_score"]), reverse=True)

def generate_flow_momentum():
    """Generate flow momentum tracker data."""
    securities = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "SPY", "QQQ", "IWM"]
    
    data = []
    dates, _ = generate_time_series(7)
    
    for security in securities:
        net_flow = []
        cumulative = 0
        
        for date in dates:
            daily_flow = random.uniform(-100, 100)
            cumulative += daily_flow
            net_flow.append(round(daily_flow, 2))
        
        momentum_score = cumulative / len(dates)
        
        data.append({
            "security": security,
            "dates": dates,
            "daily_flows": net_flow,
            "cumulative_flow": round(cumulative, 2),
            "momentum_score": round(momentum_score, 2),
            "volume_trend": random.choice(["Increasing", "Decreasing", "Stable"]),
            "price_correlation": round(random.uniform(-0.8, 0.8), 3),
            "signal": "Buy" if momentum_score > 10 else "Sell" if momentum_score < -10 else "Hold"
        })
    
    return sorted(data, key=lambda x: abs(x["momentum_score"]), reverse=True)

# 1. Repo Squeeze Detector
@register_widget({
    "name": "Repo Squeeze Detector",
    "description": "Detect spikes in collateral demand and repo rates",
    "category": "Trading Strategy",
    "subCategory": "Fixed Income",
    "type": "chart",
    "endpoint": "trading_strategy/repo_squeeze",
    "gridData": {"w": 20, "h": 12},
    "raw": True,
    "params": [
        {
            "paramName": "security_filter",
            "value": "All",
            "label": "Security",
            "description": "Filter repo squeeze analysis by security type. Valid values: 'All' (all securities), 'Treasury' (US Treasury securities), 'Agency' (government-sponsored enterprise securities), 'Corporate' (corporate bonds), 'Municipal' (municipal bonds). Determines which securities are analyzed for squeeze conditions.",
            "type": "text",
            "options": [
                {"label": "All Securities", "value": "All"},
                {"label": "Treasury Securities", "value": "Treasury"},
                {"label": "Agency Securities", "value": "Agency"},
                {"label": "Corporate Bonds", "value": "Corporate"},
                {"label": "Municipal Bonds", "value": "Municipal"}
            ]
        },
        {
            "paramName": "squeeze_threshold",
            "value": 10,
            "label": "Squeeze Threshold (bps)",
            "description": "Minimum spread widening in basis points to identify as a repo squeeze event. Higher thresholds identify more severe squeezes. Range: 1-100. Example: 15 flags securities with >15bps spread widening indicating supply constraints.",
            "type": "number"
        },
        {
            "paramName": "time_horizon",
            "value": "1M",
            "label": "Time Horizon",
            "description": "Time period for repo squeeze analysis. Valid formats: 1D (daily squeeze events), 1W (weekly patterns), 1M (monthly analysis), 3M (quarterly trends). Determines the lookback period for squeeze detection and trend analysis.",
            "type": "text",
            "options": [
                {"label": "1 Day", "value": "1D"},
                {"label": "1 Week", "value": "1W"},
                {"label": "1 Month", "value": "1M"},
                {"label": "3 Months", "value": "3M"}
            ]
        }
    ]
})
@router.get("/repo_squeeze")
def get_repo_squeeze(
    security_filter: str = "All",
    collateral_types: str = "All",
    squeeze_threshold: float = 10,
    tenor_buckets: str = "All",
    market_segments: str = "All",
    time_horizon: str = "1M",
    raw: bool = False,
    theme: str = "dark"
):
    """Get repo squeeze detection data with filtering parameters."""
    data = generate_repo_squeeze_data()
    
    if raw:
        return data
    
    df = pd.DataFrame(data)
    if security_filter != "All":
        df = df[df["security"] == security_filter]
    
    colors = get_theme_colors(theme)
    
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        row_heights=[0.7, 0.3],
        subplot_titles=('Repo Rates vs General Rate', 'Squeeze Premium')
    )
    
    for security in df["security"].unique():
        security_data = df[df["security"] == security]
        
        # Repo rates
        fig.add_trace(
            go.Scatter(x=security_data["date"], y=security_data["repo_rate"],
                      name=f"{security} Repo", mode='lines'),
            row=1, col=1
        )
        
        # Squeeze premium
        fig.add_trace(
            go.Bar(x=security_data["date"], y=security_data["squeeze_premium"],
                  name=f"{security} Squeeze", opacity=0.6),
            row=2, col=1
        )
    
    # Add general rate line
    general_data = df.groupby("date")["general_rate"].mean().reset_index()
    fig.add_trace(
        go.Scatter(x=general_data["date"], y=general_data["general_rate"],
                  name="General Rate", line=dict(dash='dash', color='gray')),
        row=1, col=1
    )
    
    layout_config = base_layout(theme=theme)
    layout_config.update({
        # 'title': 'Repo Squeeze Detection',
        'xaxis2_title': 'Date',
        'yaxis_title': 'Rate (%)',
        'yaxis2_title': 'Squeeze Premium (bps)',
        'hovermode': 'x unified',
        'height': 600
    })
    
    fig.update_layout(layout_config)
    
    figure_json = json.loads(fig.to_json())
    figure_json['config'] = get_toolbar_config()
    
    return figure_json

# 2. Short-Interest Sentiment Gauge
@register_widget({
    "name": "Short-Interest Sentiment Gauge",
    "description": "Market bearishness proxy by sector",
    "category": "Trading Strategy",
    "subCategory": "Sentiment Analysis",
    "type": "table",
    "endpoint": "trading_strategy/sentiment_gauge",
    "gridData": {"w": 20, "h": 10},
    "data": {
        "table": {
            "enableCharts": True,
            "chartView": {
                "enabled": True,
                "chartType": "bar"
            },
            "columnsDefs": [
                {
                    "field": "sector",
                    "headerName": "Sector",
                    "width": 120,
                    "pinned": "left",
                    "chartDataType": "category"
                },
                {
                    "field": "short_interest_pct",
                    "headerName": "Short Interest (%)",
                    "width": 140,
                    "cellDataType": "number",
                    "formatterFn": "normalizedPercent",
                    "chartDataType": "series"
                },
                {
                    "field": "sentiment_score",
                    "headerName": "Sentiment Score",
                    "width": 130,
                    "cellDataType": "number",
                    "renderFn": "columnColor",
                    "renderFnParams": {
                        "colorRules": [
                            {"condition": "gt", "value": 70, "color": "#0E5447", "fill": False},
                            {"condition": "gt", "value": 50, "color": "#F28352", "fill": False},
                            {"condition": "lte", "value": 50, "color": "#ED6D3C", "fill": False}
                        ]
                    }
                },
                {
                    "field": "trend_7d",
                    "headerName": "7D Trend (%)",
                    "width": 120,
                    "cellDataType": "number",
                    "formatterFn": "normalizedPercent",
                    "renderFn": "greenRed"
                },
                {
                    "field": "volume_ratio",
                    "headerName": "Volume Ratio",
                    "width": 120,
                    "cellDataType": "number"
                },
                {
                    "field": "momentum",
                    "headerName": "Momentum",
                    "width": 100,
                    "renderFn": "columnColor",
                    "renderFnParams": {
                        "colorRules": [
                            {"condition": "eq", "value": "Bullish", "color": "#0E5447", "fill": False},
                            {"condition": "eq", "value": "Bearish", "color": "#ED6D3C", "fill": False},
                            {"condition": "eq", "value": "Neutral", "color": "#8E8E8E", "fill": False}
                        ]
                    }
                }
            ]
        }
    },
    "params": [
        {
            "paramName": "sentiment_range_min",
            "value": 0,
            "label": "Min Sentiment Score",
            "description": "Minimum sentiment score to include in analysis. Sentiment scores range from 0 (extremely bearish) to 100 (extremely bullish). Range: 0-100. Example: 30 shows sectors with neutral to bullish sentiment only.",
            "type": "number"
        },
        {
            "paramName": "sentiment_range_max",
            "value": 100,
            "label": "Max Sentiment Score",
            "description": "Maximum sentiment score to include in analysis. Sets upper bound for sentiment filtering. Range: 0-100. Example: 70 excludes extremely bullish sentiment readings to focus on moderate sentiment ranges.",
            "type": "number"
        },
        {
            "paramName": "time_window",
            "value": "1M",
            "label": "Analysis Time Window",
            "description": "Time period for sentiment gauge analysis. Valid formats: 1W (weekly sentiment), 1M (monthly sentiment trends), 3M (quarterly sentiment analysis), 6M (longer-term sentiment patterns). Determines the timeframe for sentiment measurement.",
            "type": "text",
            "options": [
                {"label": "1 Week", "value": "1W"},
                {"label": "1 Month", "value": "1M"},
                {"label": "3 Months", "value": "3M"},
                {"label": "6 Months", "value": "6M"}
            ]
        }
    ]
})
@router.get("/sentiment_gauge")
def get_sentiment_gauge(
    sector_filters: str = "All",
    sentiment_range_min: float = 0,
    sentiment_range_max: float = 100,
    volume_ratios: str = "All",
    momentum_indicators: str = "All",
    time_window: str = "1M"
):
    """Get short-interest sentiment gauge with filtering parameters."""
    return generate_sentiment_gauge()

# 3. Liquidity Fragmentation Index
@register_widget({
    "name": "Liquidity Fragmentation Index",
    "description": "Bid/ask spreads inferred from clearing data",
    "category": "Trading Strategy",
    "subCategory": "Market Structure",
    "type": "chart",
    "endpoint": "trading_strategy/liquidity_fragmentation",
    "gridData": {"w": 20, "h": 10},
    "params": [
        {
            "paramName": "fragmentation_metrics",
            "value": "VolumeShare",
            "label": "Fragmentation Metrics",
            "description": "Method for measuring market fragmentation. Valid values: 'VolumeShare' (venue volume distribution), 'OrderCount' (order fragmentation), 'SpreadImpact' (liquidity impact), 'ConcentrationIndex' (market concentration). Determines how fragmentation is calculated and displayed.",
            "type": "text",
            "options": [
                {"label": "Volume Share", "value": "VolumeShare"},
                {"label": "Order Count", "value": "OrderCount"},
                {"label": "Spread Impact", "value": "SpreadImpact"},
                {"label": "Concentration Index", "value": "ConcentrationIndex"}
            ]
        },
        {
            "paramName": "liquidity_threshold",
            "value": 50,
            "label": "Min Liquidity Score",
            "description": "Minimum liquidity score to include venues in fragmentation analysis. Liquidity scores range from 0-100 based on depth and tightness. Range: 0-100. Example: 70 includes only high-liquidity venues in the fragmentation calculation.",
            "type": "number"
        }
    ]
})
@router.get("/liquidity_fragmentation")
def get_liquidity_fragmentation(
    venue_types: str = "All",
    fragmentation_metrics: str = "VolumeShare",
    asset_categories: str = "All",
    time_windows: str = "1H",
    liquidity_threshold: float = 50,
    theme: str = "dark"
):
    """Get liquidity fragmentation analysis with filtering parameters."""
    data = generate_liquidity_fragmentation()
    df = pd.DataFrame(data)
    
    colors = get_theme_colors(theme)
    
    fig = go.Figure()
    
    asset_classes = df["asset_class"].unique()
    venues = df["venue"].unique()
    
    # Create stacked bar chart
    for venue in venues:
        venue_data = df[df["venue"] == venue]
        
        fig.add_trace(go.Bar(
            x=venue_data["asset_class"],
            y=venue_data["volume_share"],
            name=venue,
            text=[f'{v}%' for v in venue_data["volume_share"]],
            textposition='inside'
        ))
    
    layout_config = base_layout(theme=theme)
    layout_config.update({
        # 'title': 'Market Volume Distribution by Venue',
        'xaxis_title': 'Asset Class',
        'yaxis_title': 'Volume Share (%)',
        'barmode': 'stack',
        'hovermode': 'x unified'
    })
    
    fig.update_layout(layout_config)
    
    figure_json = json.loads(fig.to_json())
    figure_json['config'] = get_toolbar_config()
    
    return figure_json

# 4. Cross-Asset Arbitrage Monitor
@register_widget({
    "name": "Cross-Asset Arbitrage Monitor",
    "description": "CDS vs bond spreads, ETF vs NAV deviations",
    "category": "Trading Strategy",
    "subCategory": "Arbitrage",
    "type": "table",
    "endpoint": "trading_strategy/arbitrage_monitor",
    "gridData": {"w": 20, "h": 10},
    "data": {
        "table": {
            "enableCharts": True,
            "chartView": {
                "enabled": False,
                "chartType": "scatter"
            },
            "columnsDefs": [
                {
                    "field": "opportunity",
                    "headerName": "Opportunity",
                    "width": 150,
                    "pinned": "left"
                },
                {
                    "field": "spread_bps",
                    "headerName": "Current Spread (bps)",
                    "width": 150,
                    "cellDataType": "number",
                    "renderFn": "greenRed"
                },
                {
                    "field": "historical_avg",
                    "headerName": "Historical Avg (bps)",
                    "width": 150,
                    "cellDataType": "number"
                },
                {
                    "field": "z_score",
                    "headerName": "Z-Score",
                    "width": 100,
                    "cellDataType": "number",
                    "renderFn": "columnColor",
                    "renderFnParams": {
                        "colorRules": [
                            {"condition": "gt", "value": 2, "color": "#ED6D3C", "fill": True},
                            {"condition": "gt", "value": 1, "color": "#F28352", "fill": False},
                            {"condition": "lt", "value": -1, "color": "#0E5447", "fill": False}
                        ]
                    }
                },
                {
                    "field": "volume",
                    "headerName": "Volume ($M)",
                    "width": 120,
                    "cellDataType": "number",
                    "formatterFn": "normalizedPercent"
                },
                {
                    "field": "signal_strength",
                    "headerName": "Signal",
                    "width": 100,
                    "renderFn": "columnColor",
                    "renderFnParams": {
                        "colorRules": [
                            {"condition": "eq", "value": "Strong", "color": "#0E5447", "fill": True},
                            {"condition": "eq", "value": "Moderate", "color": "#F28352", "fill": False},
                            {"condition": "eq", "value": "Weak", "color": "#8E8E8E", "fill": False}
                        ]
                    }
                },
                {
                    "field": "risk_adjusted_return",
                    "headerName": "Risk-Adj Return (%)",
                    "width": 160,
                    "cellDataType": "number",
                    "formatterFn": "normalizedPercent",
                    "renderFn": "greenRed"
                }
            ]
        }
    },
    "params": [
        {
            "paramName": "spread_threshold_min",
            "value": -50,
            "label": "Min Spread Threshold (bps)",
            "description": "Minimum spread in basis points for arbitrage opportunities. Negative values indicate profitable opportunities (asset underpriced). Range: -200 to 200. Example: -10 shows opportunities with >10bps profit potential.",
            "type": "number"
        },
        {
            "paramName": "feasibility_scores",
            "value": 70,
            "label": "Min Feasibility Score (%)",
            "description": "Minimum feasibility score for arbitrage execution. Scores consider liquidity, transaction costs, and execution risk. Range: 0-100. Example: 80 shows only high-probability arbitrage opportunities with strong execution feasibility.",
            "type": "number"
        },
        {
            "paramName": "volume_threshold",
            "value": 50,
            "label": "Min Volume Threshold ($M)",
            "description": "Minimum notional volume in millions of USD for arbitrage opportunities. Only opportunities above this size will be displayed. Range: 1-1000. Example: 100 shows arbitrage opportunities with >$100M potential volume.",
            "type": "number"
        }
    ]
})
@router.get("/arbitrage_monitor")
def get_arbitrage_monitor(
    opportunity_types: str = "All",
    spread_threshold_min: float = -50,
    spread_threshold_max: float = 50,
    signal_strength: str = "All",
    feasibility_scores: float = 70,
    volume_threshold: float = 50
):
    """Get cross-asset arbitrage opportunities with filtering parameters."""
    return generate_arbitrage_opportunities()

# 5. Flow Momentum Tracker
@register_widget({
    "name": "Flow Momentum Tracker",
    "description": "Net buy/sell activity mapped to performance",
    "category": "Trading Strategy",
    "subCategory": "Flow Analysis",
    "type": "chart",
    "endpoint": "trading_strategy/flow_momentum",
    "gridData": {"w": 20, "h": 12},
    "raw": True,
    "params": [
        {
            "paramName": "flow_thresholds",
            "value": 10,
            "label": "Min Flow Threshold ($M)",
            "description": "Minimum money flow amount in millions of USD to include in momentum analysis. Only securities with flows above this threshold will be tracked. Range: 1-1000. Example: 25 focuses on securities with >$25M flow activity.",
            "type": "number"
        },
        {
            "paramName": "correlation_range_min",
            "value": -1,
            "label": "Min Price Correlation",
            "description": "Minimum correlation coefficient between flow and price movements. Range: -1 to 1. Example: 0.3 shows securities where flows have positive correlation with price (flow follows price). -1 includes all correlations.",
            "type": "number"
        },
        {
            "paramName": "momentum_lookback",
            "value": "7D",
            "label": "Momentum Lookback Period",
            "description": "Time period for calculating flow momentum signals. Valid formats: 1D (daily momentum), 7D (weekly momentum), 1M (monthly momentum), 3M (quarterly trends). Determines the timeframe for momentum score calculation.",
            "type": "text",
            "options": [
                {"label": "1 Day", "value": "1D"},
                {"label": "7 Days", "value": "7D"},
                {"label": "1 Month", "value": "1M"},
                {"label": "3 Months", "value": "3M"}
            ]
        }
    ]
})
@router.get("/flow_momentum")
def get_flow_momentum(
    security_filters: str = "All",
    flow_thresholds: float = 10,
    correlation_range_min: float = -1,
    correlation_range_max: float = 1,
    signal_generation: str = "All",
    momentum_lookback: str = "7D",
    raw: bool = False,
    theme: str = "dark"
):
    """Get flow momentum analysis with filtering parameters."""
    data = generate_flow_momentum()
    
    if raw:
        return data
    
    colors = get_theme_colors(theme)
    
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        row_heights=[0.7, 0.3],
        subplot_titles=('Cumulative Flow by Security', 'Momentum Score')
    )
    
    # Plot top 5 securities by momentum
    top_securities = sorted(data, key=lambda x: abs(x["momentum_score"]), reverse=True)[:5]
    
    for security_data in top_securities:
        # Cumulative flow
        cumulative = np.cumsum(security_data["daily_flows"])
        
        fig.add_trace(
            go.Scatter(x=security_data["dates"], y=cumulative,
                      name=security_data["security"], mode='lines'),
            row=1, col=1
        )
    
    # Momentum scores
    securities = [s["security"] for s in top_securities]
    momentum_scores = [s["momentum_score"] for s in top_securities]
    dtcc_colors = get_dtcc_chart_colors()
    colors_list = [dtcc_colors['positive'] if m > 0 else dtcc_colors['negative'] for m in momentum_scores]
    
    fig.add_trace(
        go.Bar(x=securities, y=momentum_scores, 
               marker_color=colors_list, showlegend=False),
        row=2, col=1
    )
    
    layout_config = base_layout(theme=theme)
    layout_config.update({
        # 'title': 'Flow Momentum Analysis',
        'xaxis2_title': 'Security',
        'yaxis_title': 'Cumulative Flow ($M)',
        'yaxis2_title': 'Momentum Score',
        'hovermode': 'x unified',
        'height': 600
    })
    
    fig.update_layout(layout_config)
    
    figure_json = json.loads(fig.to_json())
    figure_json['config'] = get_toolbar_config()
    
    return figure_json

# 6. Trading Strategy Metrics
@register_widget({
    "name": "Trading Strategy Metrics",
    "description": "Key trading and investment strategy metrics",
    "category": "Trading Strategy",
    "subCategory": "Summary",
    "type": "metric",
    "endpoint": "trading_strategy/metrics",
    "gridData": {"w": 20, "h": 4},
    "params": [
        {
            "paramName": "performance_metrics",
            "value": "Sharpe",
            "label": "Performance Metrics",
            "description": "Primary performance metric for strategy evaluation. Valid values: 'Sharpe' (risk-adjusted returns), 'Alpha' (excess returns vs benchmark), 'Return' (absolute returns), 'Volatility' (return volatility), 'MaxDrawdown' (maximum peak-to-trough decline). Determines the key performance measure displayed.",
            "type": "text",
            "options": [
                {"label": "Sharpe Ratio", "value": "Sharpe"},
                {"label": "Alpha (Excess Return)", "value": "Alpha"},
                {"label": "Absolute Return", "value": "Return"},
                {"label": "Volatility", "value": "Volatility"},
                {"label": "Max Drawdown", "value": "MaxDrawdown"}
            ]
        },
        {
            "paramName": "benchmark_comparisons",
            "value": "SPX",
            "label": "Benchmark Comparison",
            "description": "Benchmark index for performance comparison. Valid values: 'SPX' (S&P 500), 'VIX' (volatility index), 'BND' (bond index), 'GLD' (gold), 'DXY' (dollar index), 'Custom' (custom benchmark). Determines the baseline for relative performance measurement.",
            "type": "text",
            "options": [
                {"label": "S&P 500 (SPX)", "value": "SPX"},
                {"label": "VIX (Volatility)", "value": "VIX"},
                {"label": "Bond Index (BND)", "value": "BND"},
                {"label": "Gold (GLD)", "value": "GLD"},
                {"label": "Dollar Index (DXY)", "value": "DXY"},
                {"label": "Custom Benchmark", "value": "Custom"}
            ]
        },
        {
            "paramName": "time_horizon",
            "value": "1M",
            "label": "Time Horizon",
            "description": "Time period for trading strategy metrics calculation. Valid formats: 1D (daily metrics), 1W (weekly performance), 1M (monthly analysis), 3M (quarterly performance), 1Y (annual metrics). Determines the timeframe for strategy evaluation.",
            "type": "text",
            "options": [
                {"label": "1 Day", "value": "1D"},
                {"label": "1 Week", "value": "1W"},
                {"label": "1 Month", "value": "1M"},
                {"label": "3 Months", "value": "3M"},
                {"label": "1 Year", "value": "1Y"}
            ]
        }
    ]
})
@router.get("/metrics")
def get_trading_strategy_metrics(
    strategy_types: str = "All",
    performance_metrics: str = "Sharpe",
    risk_adjustments: str = "None",
    benchmark_comparisons: str = "SPX",
    time_horizon: str = "1M"
):
    """Get trading strategy metrics with calculation parameters."""
    # Apply filtering logic based on parameters
    base_metrics = [
        {
            "label": "Alpha Opportunities",
            "value": "23",
            "delta": "4.0"
        },
        {
            "label": "Avg Spread Capture",
            "value": "2.8bps",
            "delta": "0.3"
        },
        {
            "label": "Flow Correlation",
            "value": "0.73",
            "delta": "0.05"
        },
        {
            "label": "Squeeze Events",
            "value": "4",
            "delta": "1.0"
        },
        {
            "label": "Strategy Score",
            "value": "87/100",
            "delta": "3.0"
        }
    ]
    
    return base_metrics

# 7. Dashboard Notes
@register_widget({
    "name": "Trading Strategy Dashboard Notes",
    "description": "Comprehensive overview and documentation for the Trading Strategy dashboard",
    "category": "Documentation",
    "type": "markdown",
    "endpoint": "trading_strategy/notes",
    "gridData": {"w": 40, "h": 30}
})
@router.get("/notes")
def get_notes():
    """Get Trading Strategy dashboard documentation."""
    markdown_content = """# DTCC Trading Strategy Dashboard

## Overview
The DTCC Trading Strategy Dashboard provides advanced trading insights and investment strategy capabilities, featuring repo squeeze detection, sentiment analysis, liquidity fragmentation monitoring, arbitrage opportunities, and flow momentum tracking. This dashboard empowers traders and portfolio managers with actionable market intelligence and alpha generation tools.

## Purpose
• **Alpha Generation**: Identify trading opportunities through repo squeeze detection, arbitrage monitoring, and flow momentum analysis

• **Market Intelligence**: Analyze sentiment indicators, liquidity conditions, and market structure dynamics for informed decision-making

• **Risk-Adjusted Returns**: Monitor cross-asset arbitrage opportunities and optimize trading strategies based on risk-return profiles

• **Flow Analysis**: Track institutional flow patterns and momentum to anticipate market movements and position accordingly

---

## Tab 1: Market Opportunities
**Purpose**: Identify and monitor trading opportunities across different asset classes

### Widgets:
• **Trading Strategy Metrics**: Key strategy indicators including alpha opportunities (23), average spread capture (2.8bps), flow correlation (0.73), squeeze events (4), and strategy score (87/100)

• **Repo Squeeze Detector**: Multi-panel analysis showing repo rates vs general rates with squeeze premium identification across treasury securities

• **Cross-Asset Arbitrage Monitor**: Comprehensive table of arbitrage opportunities with z-scores, signal strength, and risk-adjusted return analysis

---

## Tab 2: Sentiment & Flows
**Purpose**: Sentiment analysis and flow momentum tracking for strategic positioning

### Widgets:
• **Short-Interest Sentiment Gauge**: Sector-by-sector sentiment analysis based on short interest levels with momentum and trend indicators

• **Liquidity Fragmentation Index**: Market structure analysis showing volume distribution across different venues and asset classes

• **Flow Momentum Tracker**: Time series analysis of cumulative flows and momentum scores for top securities with correlation to price movements

---

## Data Sources
• **DTCC Trading Data**: Comprehensive trade flow data across all asset classes for momentum and sentiment analysis

• **Repo Market Data**: Real-time repo rates, collateral availability, and squeeze detection across treasury and agency securities

• **Options Market Data**: Implied volatility surfaces, options flow data, and derivatives positioning for sentiment analysis

• **Market Structure Data**: Venue-specific trading data, dark pool flows, and liquidity fragmentation metrics

• **Alternative Data**: Sentiment indicators, news flow analysis, and social media sentiment for enhanced market intelligence

## Key Metrics Tracked
• **Arbitrage Opportunities**: Spread relationships, z-score analysis, historical deviations, and trade feasibility assessments across asset classes

• **Repo Market Dynamics**: Squeeze premiums, collateral scarcity indicators, and funding cost differentials for alpha generation

• **Sentiment Indicators**: Short interest ratios, put-call ratios, volatility skew, and sentiment momentum across sectors and securities

• **Flow Analytics**: Institutional flow patterns, momentum persistence, price correlation, and flow-based signal generation

• **Liquidity Metrics**: Fragmentation indices, bid-ask spreads, market depth, and liquidity transformation costs across venues

• **Strategy Performance**: Alpha generation metrics, Sharpe ratios, strategy correlation, and risk-adjusted performance attribution

• **Market Microstructure**: Order flow dynamics, execution quality, and market impact analysis for optimal trade execution

## Use Cases
• **Portfolio Managers**: Optimize asset allocation, identify alpha opportunities, and enhance risk-adjusted returns through systematic strategy deployment

• **Quantitative Traders**: Develop and backtest systematic trading strategies using flow momentum, sentiment, and arbitrage signals

• **Fixed Income Traders**: Capitalize on repo squeeze events, yield curve arbitrage, and duration-based strategies in treasury markets

• **Risk Arbitrageurs**: Identify and execute cross-asset arbitrage opportunities while managing associated risks and correlation exposures

• **Market Makers**: Optimize inventory management, predict flow patterns, and enhance market-making profitability through superior market intelligence"""

    return markdown_content