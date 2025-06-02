from typing import List, Literal
from pydantic import BaseModel

class FileOption(BaseModel):
    label: str
    value: str

class FileRequest(BaseModel):
    filenames: List[str]

class DataFormat(BaseModel):
    data_type: Literal["pdf"]
    filename: str


class DataContent(BaseModel):
    content: str
    data_format: DataFormat


class DataUrl(BaseModel):
    url: str
    data_format: DataFormat


class DataError(BaseModel):
    error_type: Literal["not_found"]
    content: str


FileOptions = List[FileOption]
FileResponse = List[DataContent | DataUrl | DataError]
