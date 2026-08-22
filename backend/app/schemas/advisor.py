from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class AdvisorHistoryMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(..., max_length=4000)


class AdvisorChatRequest(BaseModel):
    message: str = Field(..., max_length=2000)
    scholarship_id: str | None = None
    application_id: UUID | None = None
    history: list[AdvisorHistoryMessage] = Field(default_factory=list, max_length=20)


class AdvisorReferencedScholarship(BaseModel):
    id: str
    name: str


class AdvisorReferencedApplication(BaseModel):
    id: str
    scholarship_id: str
    status: str


class AdvisorChatResponse(BaseModel):
    answer: str
    warnings: list[str] = []
    unknowns: list[str] = []
    referenced_scholarships: list[AdvisorReferencedScholarship] = []
    referenced_applications: list[AdvisorReferencedApplication] = []
