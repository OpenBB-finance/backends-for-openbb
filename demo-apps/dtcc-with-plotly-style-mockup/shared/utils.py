"""Shared utility functions for the DTCC OpenBB dashboard system."""

import pandas as pd
from pathlib import Path

def get_tickers_list():
    """Get list of available tickers."""
    return [
        "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "AMD",
        "JPM", "BAC", "GS", "MS", "C", "WFC", "USB", "PNC",
        "SPY", "QQQ", "IWM", "EEM", "GLD", "TLT", "HYG", "LQD"
    ]

def get_csv_data(filename: str):
    """Load CSV data from the data directory."""
    try:
        data_path = Path(__file__).parent.parent / "data" / filename
        if data_path.exists():
            return pd.read_csv(data_path)
        else:
            # Return mock data if file doesn't exist
            return pd.DataFrame({
                "symbol": get_tickers_list()[:10],
                "price": [100 + i * 10 for i in range(10)],
                "volume": [1000000 + i * 100000 for i in range(10)]
            })
    except Exception as e:
        print(f"Error loading CSV data: {e}")
        return pd.DataFrame()