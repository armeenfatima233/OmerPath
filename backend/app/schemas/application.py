from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ApplicationResponse(BaseModel):
    id: UUID
    scholarship_id: str
    status: str
    progress: int
    next_action: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ApplicationCreateRequest(BaseModel):
    scholarship_id: str


class ApplicationUpdateRequest(BaseModel):
    status: str
