"""Deterministic mock data — no API keys, no network, same output every run."""

import math
from datetime import date, timedelta

POSITIONS = [
    # ticker, name, sector, price, change_pct, market_cap, volume
    ("NVDA", "NVIDIA Corp.", "Semiconductors", 132.40, 2.13, 3_255_000_000_000, 241_800_000),
    ("AAPL", "Apple Inc.", "Consumer Tech", 228.52, 0.84, 3_470_000_000_000, 48_300_000),
    ("MSFT", "Microsoft Corp.", "Software", 451.10, -0.32, 3_352_000_000_000, 19_100_000),
    ("GOOGL", "Alphabet Inc.", "Internet", 182.66, 1.07, 2_243_000_000_000, 26_400_000),
    ("AMZN", "Amazon.com Inc.", "E-Commerce", 197.12, -1.24, 2_064_000_000_000, 38_900_000),
    ("META", "Meta Platforms", "Internet", 563.27, 0.41, 1_425_000_000_000, 13_700_000),
    ("TSLA", "Tesla Inc.", "Automotive", 251.77, 4.62, 803_000_000_000, 92_500_000),
    ("AVGO", "Broadcom Inc.", "Semiconductors", 172.19, -2.08, 804_000_000_000, 22_600_000),
    ("JPM", "JPMorgan Chase", "Banks", 221.34, 0.19, 623_000_000_000, 8_900_000),
    ("XOM", "Exxon Mobil", "Energy", 117.85, -0.77, 519_000_000_000, 14_200_000),
    ("UNH", "UnitedHealth Group", "Healthcare", 587.44, 1.93, 540_000_000_000, 3_100_000),
    ("V", "Visa Inc.", "Payments", 291.06, -0.11, 561_000_000_000, 6_400_000),
]

TICKERS = [row[0] for row in POSITIONS]
SECTORS = sorted({row[2] for row in POSITIONS})


def positions(sector: str = "All") -> list[dict]:
    rows = [
        {
            "ticker": t,
            "name": n,
            "sector": s,
            "price": p,
            "change_pct": c,
            "market_cap": m,
            "volume": v,
        }
        for t, n, s, p, c, m, v in POSITIONS
    ]
    if sector and sector != "All":
        rows = [r for r in rows if r["sector"] == sector]
    return rows


def _walk(seed: int, start: float, points: int) -> list[float]:
    """Reproducible pseudo-random walk — no `random`, so the chart never jitters."""
    out, value = [], start
    for i in range(points):
        # Two incommensurable sine terms give a wiggly-but-deterministic path.
        drift = math.sin((i + seed * 7) / 11.3) * 0.9 + math.sin((i + seed * 3) / 4.1) * 0.5
        value *= 1 + drift / 100
        out.append(round(value, 2))
    return out


def series(tickers: list[str], points: int = 120) -> dict:
    """Rebased-to-100 performance series for each ticker, oldest point first."""
    today = date.today()
    labels = [(today - timedelta(days=points - 1 - i)).isoformat() for i in range(points)]
    return {
        "labels": labels,
        "series": [
            {"name": t, "values": _walk(seed=TICKERS.index(t) + 1 if t in TICKERS else 0, start=100.0, points=points)}
            for t in tickers
        ],
    }


def peers(ticker: str, count: int) -> list[str]:
    """`ticker` first, then the next tickers in order — enough to cycle the palette."""
    ticker = ticker.upper() if ticker.upper() in TICKERS else TICKERS[0]
    rest = [t for t in TICKERS if t != ticker]
    return [ticker, *rest][: max(1, min(count, len(TICKERS)))]
