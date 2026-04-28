"""
MCP server exposing portfolio dashboard data as tools.

Run: cd widget-examples/streamlit && uv run python mcp_server.py
Connect in the iframe widget MCP popover: http://localhost:7769/mcp
"""

import json

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from portfolio import load_holdings, rebalance

mcp = FastMCP("Portfolio Dashboard", host="0.0.0.0", port=7769)


@mcp.tool()
def get_portfolio_holdings(
    sector: str = "All",
    min_shares: int = 0,
    show_pnl_pct: bool = True,
    as_of_date: str = "2026-04-07",
) -> str:
    """Get current portfolio positions with PnL data.
    Filter by sector (All, Technology, Consumer Discretionary, Financials) and minimum share count.
    Set show_pnl_pct to include/exclude the PnL percentage column. as_of_date is the reference date."""
    filtered = load_holdings()
    if sector != "All":
        filtered = [h for h in filtered if h["sector"] == sector]
    if min_shares > 0:
        filtered = [h for h in filtered if h["shares"] >= min_shares]
    if not show_pnl_pct:
        filtered = [{k: v for k, v in h.items() if k != "pnl_pct"} for h in filtered]
    return json.dumps(filtered, indent=2)


@mcp.tool()
def get_sector_allocation(sector: str = "All") -> str:
    """Get portfolio allocation breakdown by sector with market value, PnL, and weight percentage."""
    filtered = load_holdings()
    if sector != "All":
        filtered = [h for h in filtered if h["sector"] == sector]

    sectors: dict[str, dict] = {}
    for h in filtered:
        s = h["sector"]
        if s not in sectors:
            sectors[s] = {"sector": s, "market_value": 0.0, "pnl": 0.0}
        sectors[s]["market_value"] += h["market_value"]
        sectors[s]["pnl"] += h["pnl"]

    total_mv = sum(s["market_value"] for s in sectors.values())
    result = []
    for s in sectors.values():
        s["market_value"] = round(s["market_value"], 2)
        s["pnl"] = round(s["pnl"], 2)
        s["weight_pct"] = round(s["market_value"] / total_mv * 100, 2) if total_mv > 0 else 0
        result.append(s)

    return json.dumps(result, indent=2)


@mcp.tool()
def get_market_summary() -> str:
    """Get weekly market analysis and outlook including key observations, portfolio highlights, and risk factors."""
    return (
        "# Market Summary — March 2026\n\n"
        "## Key Observations\n\n"
        "- **S&P 500** closed at 5,842 (+0.3%), extending its winning streak to 5 sessions\n"
        "- **NASDAQ** outperformed with a +0.7% gain, led by semiconductor names\n"
        "- **VIX** dropped to 14.2, signaling continued low-volatility environment\n\n"
        "## Portfolio Highlights\n\n"
        "- **Top performer**: NVDA (+81.5% since entry) — AI infrastructure spend accelerating\n"
        "- **Laggard**: GOOGL (+8.0%) — regulatory overhang persists but valuation attractive\n"
        "- **Total portfolio PnL**: strong across the board, tech-heavy allocation paying off\n\n"
        "## Outlook\n\n"
        "The current rally is broad-based with healthy rotation. **Maintain overweight in tech** "
        "but consider adding **defensive exposure** (healthcare, utilities) given stretched valuations. "
        "Watch the **Fed meeting next week** — rate guidance will be the key catalyst.\n\n"
        "### Risk Factors\n"
        "1. Earnings season begins in 3 weeks — high expectations priced in\n"
        "2. Geopolitical tensions in Asia remain elevated\n"
        "3. Credit spreads starting to widen in high-yield"
    )


@mcp.tool(annotations=ToolAnnotations(destructiveHint=True))
def rebalance_portfolio() -> str:
    """Rebalance the portfolio by randomly adjusting position sizes and simulating market movement.
    Returns the new portfolio state after rebalancing."""
    new_holdings = rebalance()
    return json.dumps(new_holdings, indent=2)


if __name__ == "__main__":
    import argparse

    import uvicorn
    from starlette.middleware.cors import CORSMiddleware

    parser = argparse.ArgumentParser(description="Portfolio Dashboard MCP Server")
    parser.add_argument("--port", type=int, default=7769, help="Port to run the server on (default: 7769)")
    args = parser.parse_args()

    app = mcp.streamable_http_app()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["mcp-session-id"],
    )
    uvicorn.run(app, host="0.0.0.0", port=args.port)
