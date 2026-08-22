from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: UUID
    document_type: str
    original_filename: str
    mime_type: str
    file_size: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DocumentDownloadResponse(BaseModel):
    url: str
