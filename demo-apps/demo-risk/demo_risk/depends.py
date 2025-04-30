from typing import Annotated
from fastapi import Depends
from openbb_store.store import Store


STORE = Store(__file__.replace("depends.py", "portfolios"))


def get_store() -> Store:
    """Get portfolio data."""
    return STORE


PortfolioData = Annotated[
    Store,
    Depends(get_store),
]
