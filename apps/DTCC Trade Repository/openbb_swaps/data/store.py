"""Swaps Data Store Dependency."""

from pathlib import Path
from typing import Annotated

from fastapi import Depends
from openbb_store.store import Store


store_path = Path(__file__).parent / "swaps_data"
swaps_store = Store(str(store_path))


def get_swaps_store() -> Store:
    """Get the swaps store."""
    return swaps_store


SwapsStore = Annotated[
    Store,
    Depends(get_swaps_store),
]
