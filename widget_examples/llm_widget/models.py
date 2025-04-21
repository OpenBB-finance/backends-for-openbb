from typing import Any, Literal
from uuid import UUID
from pydantic import BaseModel, Field


class DataFormat(BaseModel):
    data_type: str
    parse_as: Literal["text", "table", "chart"]


class SourceInfo(BaseModel):
    type: Literal["widget"]
    uuid: UUID | None = Field(default=None)
    origin: str | None = Field(default=None)
    widget_id: str | None = Field(default=None)
    name: str
    description: str | None = Field(default=None)
    metadata: dict[str, Any] | None = Field(default=None)


class ExtraCitation(BaseModel):
    source_info: SourceInfo | None = Field(default=None)
    details: list[dict] | None = Field(default=None)


class PromptResponse(BaseModel):
    content: str
    data_format: DataFormat
    extra_citations: list[ExtraCitation] | None = Field(default=None)
    citable: bool = Field(default=True)


class PromptRequest(BaseModel):
    prompt: str
