from pathlib import Path
from typing import Annotated
from fastapi import Depends
from openbb_store.store import Store


transcripts_path = Path(__file__).parent.parent / "data" / "transcripts"

transcripts_store = Store(str(transcripts_path))

pdfs_path = Path(__file__).parent.parent / "data" / "pdfs"

pdf_store = Store(str(pdfs_path))

price_store_path = Path(__file__).parent.parent / "data" / "prices"

price_store = Store(str(price_store_path))


def get_pdf_store() -> Store:
    return pdf_store


def get_transcripts_store() -> Store:
    return transcripts_store


def get_price_store() -> Store:
    return price_store


TranscriptsStore = Annotated[Store, Depends(get_transcripts_store)]

PdfStore = Annotated[Store, Depends(get_pdf_store)]

PriceStore = Annotated[Store, Depends(get_price_store)]
