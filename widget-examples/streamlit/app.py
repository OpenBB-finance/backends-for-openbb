"""
Streamlit demo app showcasing the OpenBB Iframe Widget Protocol.

Run: cd widget-examples/streamlit && uv run streamlit run app.py
Then paste the Streamlit URL into an Iframe widget in OpenBB Workspace.
"""

import json

import pandas as pd
import plotly.express as px
import streamlit as st

from portfolio import load_holdings, rebalance as rebalance_portfolio

st.set_page_config(page_title="OpenBB Streamlit Demo", layout="wide")

# --- Read params from query string (set by bridge JS on openbb-params-update) ---

active_sector = st.query_params.get("sector", "All")
min_shares = int(st.query_params.get("min_shares", "0"))
show_pnl_pct = st.query_params.get("show_pnl_pct", "true").lower() == "true"
as_of_date = st.query_params.get("as_of_date", "2026-04-07")

# --- Data ---

holdings = pd.DataFrame(load_holdings())

SECTORS = sorted(holdings["sector"].unique().tolist())

# Apply sector filter
if active_sector != "All" and active_sector in SECTORS:
    filtered_holdings = holdings[holdings["sector"] == active_sector]
else:
    filtered_holdings = holdings
    active_sector = "All"

# Apply min shares filter
if min_shares > 0:
    filtered_holdings = filtered_holdings[filtered_holdings["shares"] >= min_shares]

sector_alloc = (
    filtered_holdings.groupby("sector")
    .agg({"market_value": "sum", "pnl": "sum"})
    .reset_index()
)
if not sector_alloc.empty:
    sector_alloc["weight_pct"] = (
        sector_alloc["market_value"] / sector_alloc["market_value"].sum() * 100
    ).round(2)

market_summary_md = f"""# Market Summary — March 2026

**Active filter: {active_sector}** | Showing {len(filtered_holdings)} of {len(holdings)} positions

## Key Observations

- **S&P 500** closed at 5,842 (+0.3%), extending its winning streak to 5 sessions
- **NASDAQ** outperformed with a +0.7% gain, led by semiconductor names
- **VIX** dropped to 14.2, signaling continued low-volatility environment

## Portfolio Highlights

- **Top performer**: NVDA (+81.5% since entry) — AI infrastructure spend accelerating
- **Laggard**: GOOGL (+8.0%) — regulatory overhang persists but valuation attractive
- **Total portfolio PnL**: strong across the board, tech-heavy allocation paying off

## Outlook

> The current rally is broad-based with healthy rotation. **Maintain overweight in tech**
> but consider adding **defensive exposure** (healthcare, utilities) given stretched valuations.
> Watch the **Fed meeting next week** — rate guidance will be the key catalyst.

### Risk Factors
1. Earnings season begins in 3 weeks — high expectations priced in
2. Geopolitical tensions in Asia remain elevated
3. Credit spreads starting to widen in high-yield
"""

# --- Streamlit UI ---

col_title, col_btn = st.columns([4, 1])
with col_title:
    st.title("Portfolio Dashboard")
with col_btn:
    st.write("")
    if st.button("REBALANCE", type="primary", use_container_width=True):
        rebalance_portfolio()
        st.rerun()
st.caption(f"Sector: **{active_sector}** — {len(filtered_holdings)} positions | As of: {as_of_date}")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Holdings")
    display_cols = ["ticker", "shares", "avg_cost", "current_price", "market_value", "pnl"]
    if show_pnl_pct:
        display_cols.append("pnl_pct")
    st.dataframe(
        filtered_holdings[display_cols],
        use_container_width=True,
        hide_index=True,
    )

with col2:
    st.subheader("Sector Allocation")
    if not sector_alloc.empty:
        fig = px.pie(sector_alloc, values="market_value", names="sector", hole=0.4)
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=300)
        st.plotly_chart(fig, use_container_width=True)

st.subheader("PnL by Ticker")
fig_bar = px.bar(
    filtered_holdings.sort_values("pnl", ascending=False),
    x="ticker",
    y="pnl",
    color="pnl",
    color_continuous_scale=["#ef4444", "#22c55e"],
)
fig_bar.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=300)
st.plotly_chart(fig_bar, use_container_width=True)

st.subheader("Market Notes")
st.markdown(market_summary_md)

# --- OpenBB Iframe Protocol Bridge ---

WIDGET_MANIFESTS = [
    {
        "widgetId": "portfolio-holdings",
        "name": "Portfolio Holdings",
        "description": "Current portfolio positions with PnL",
        "category": "Portfolio",
        "dataType": "table",
    },
    {
        "widgetId": "sector-allocation",
        "name": "Sector Allocation",
        "description": "Portfolio allocation breakdown by sector",
        "category": "Portfolio",
        "dataType": "table",
    },
    {
        "widgetId": "market-summary",
        "name": "Market Summary",
        "description": "Weekly market analysis and outlook",
        "category": "Research",
        "dataType": "markdown",
    },
]

PARAM_DEFS = [
    {
        "paramName": "sector",
        "label": "Sector",
        "type": "text",
        "description": "Filter holdings by sector",
        "value": "All",
        "options": [{"label": "All", "value": "All"}]
        + [{"label": s, "value": s} for s in SECTORS],
    },
    {
        "paramName": "min_shares",
        "label": "Min Shares",
        "type": "number",
        "description": "Minimum number of shares to display",
        "value": "0",
        "min": 0,
        "max": 1000,
        "step": 10,
    },
    {
        "paramName": "show_pnl_pct",
        "label": "Show PnL %",
        "type": "boolean",
        "description": "Toggle PnL percentage column visibility",
        "value": "true",
    },
    {
        "paramName": "as_of_date",
        "label": "As Of Date",
        "type": "date",
        "description": "Reference date for portfolio snapshot",
        "value": "2026-04-07",
    },
]

# Pre-compute widget data for the current sector (used by openbb-request)
WIDGET_DATA = {
    "portfolio-holdings": {
        "type": "openbb-data",
        "widgetId": "portfolio-holdings",
        "dataType": "table",
        "data": filtered_holdings[
            ["ticker", "shares", "avg_cost", "current_price", "market_value", "pnl", "pnl_pct"]
        ].to_dict(orient="records"),
    },
    "sector-allocation": {
        "type": "openbb-data",
        "widgetId": "sector-allocation",
        "dataType": "table",
        "data": sector_alloc.to_dict(orient="records"),
    },
    "market-summary": {
        "type": "openbb-data",
        "widgetId": "market-summary",
        "dataType": "markdown",
        "data": market_summary_md,
    },
}

bridge_js = f"""
<script>
(function() {{
  const manifests = {json.dumps(WIDGET_MANIFESTS)};
  const paramDefs = {json.dumps(PARAM_DEFS)};
  const widgetData = {json.dumps(WIDGET_DATA, default=str)};

  const target = window.top || window.parent;

  // Announce available widgets + params
  if (target !== window) {{
    target.postMessage({{ type: "openbb-connect", widgets: manifests, params: paramDefs }}, "*");
    console.debug("[openbb-bridge] sent openbb-connect with params to top");
  }}

  window.addEventListener("message", function(event) {{
    if (!event.data || !event.data.type) return;

    if (event.data.type === "openbb-request") {{
      console.debug("[openbb-bridge] received openbb-request", event.data.widgetId);
      const widgetId = event.data.widgetId;

      if (widgetId === null) {{
        Object.values(widgetData).forEach(function(d) {{
          target.postMessage(d, "*");
        }});
      }} else if (widgetData[widgetId]) {{
        target.postMessage(widgetData[widgetId], "*");
      }}
    }}
  }});
}})();
</script>
"""

# Inject the bridge JS into the Streamlit page
st.components.v1.html(bridge_js, height=0)
