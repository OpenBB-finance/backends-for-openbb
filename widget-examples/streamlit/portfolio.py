"""Shared portfolio data module used by both Streamlit app and MCP server."""

import json
import random
from pathlib import Path

STATE_FILE = Path("/tmp/openbb_demo_portfolio_state.json")

BASE_HOLDINGS = [
    {"ticker": "AAPL", "shares": 150, "avg_cost": 142.50, "current_price": 178.72, "sector": "Technology"},
    {"ticker": "MSFT", "shares": 200, "avg_cost": 310.00, "current_price": 378.91, "sector": "Technology"},
    {"ticker": "GOOGL", "shares": 80, "avg_cost": 131.25, "current_price": 141.80, "sector": "Technology"},
    {"ticker": "AMZN", "shares": 120, "avg_cost": 145.80, "current_price": 178.25, "sector": "Consumer Discretionary"},
    {"ticker": "NVDA", "shares": 300, "avg_cost": 48.20, "current_price": 87.50, "sector": "Technology"},
    {"ticker": "META", "shares": 100, "avg_cost": 290.00, "current_price": 355.67, "sector": "Consumer Discretionary"},
    {"ticker": "TSLA", "shares": 250, "avg_cost": 185.50, "current_price": 248.42, "sector": "Financials"},
    {"ticker": "JPM", "shares": 175, "avg_cost": 148.75, "current_price": 171.30, "sector": "Financials"},
]


def _compute_derived(holdings: list[dict]) -> list[dict]:
    for h in holdings:
        h["market_value"] = round(h["shares"] * h["current_price"], 2)
        h["pnl"] = round((h["current_price"] - h["avg_cost"]) * h["shares"], 2)
        h["pnl_pct"] = round(((h["current_price"] / h["avg_cost"]) - 1) * 100, 2)
    return holdings


def load_holdings() -> list[dict]:
    """Load current holdings from persisted state, or return defaults."""
    if STATE_FILE.exists():
        try:
            data = json.loads(STATE_FILE.read_text())
            return _compute_derived(data)
        except (json.JSONDecodeError, KeyError):
            pass
    return _compute_derived([dict(h) for h in BASE_HOLDINGS])


def rebalance() -> list[dict]:
    """Randomly rebalance portfolio and persist new state."""
    holdings = []
    for base in BASE_HOLDINGS:
        h = dict(base)
        h["shares"] = max(10, int(h["shares"] * random.uniform(0.7, 1.3)))
        h["current_price"] = round(h["current_price"] * random.uniform(0.85, 1.15), 2)
        holdings.append(h)
    STATE_FILE.write_text(json.dumps(holdings, indent=2))
    return _compute_derived(holdings)
