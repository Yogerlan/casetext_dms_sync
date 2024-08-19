from typing import Literal, Optional

from pydantic import BaseModel, Field


class PingResponse(BaseModel):
    msg: str = Field(
        description="The response message.",
        examples=["pong"]
    )


class FileResponse(BaseModel):
    id: str = Field(
        description="The file ID in UUID format.",
        min_length=36,
        max_length=36,
        examples=["67e5e9ed-baab-49f7-8290-1e9885ba8fa0"]
    )
    name: Optional[str] = Field(
        description="The file name.",
        examples=["msj-a"]
    )
    meta: Optional[dict] = Field(
        description="The file metadata blob.",
        examples=[{"matter": "uber"}]
    )


class SyncResponse(BaseModel):
    op: Literal["createFile", "deleteFile", "updateFileName", "updateFileMeta"] = Field(
        description="The Research Service operation."
    )
    file: FileResponse = Field(
        description="The operation target file."
    )
