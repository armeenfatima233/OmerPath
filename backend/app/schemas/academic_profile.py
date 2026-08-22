from datetime import datetime

from pydantic import BaseModel, Field


class AcademicProfileResponse(BaseModel):
    current_degree: str | None = None
    field_of_study: str | None = None
    target_degree: str | None = None
    gpa: str | None = None
    language_test_type: str | None = None
    language_test_score: str | None = None
    experience_summary: str | None = None
    preferred_destinations: list[str] = []
    onboarding_completed_at: datetime | None = None


class AcademicProfileUpdateRequest(BaseModel):
    current_degree: str | None = Field(None, max_length=150)
    field_of_study: str | None = Field(None, max_length=150)
    target_degree: str | None = Field(None, max_length=50)
    gpa: str | None = Field(None, max_length=20)
    language_test_type: str | None = Field(None, max_length=50)
    language_test_score: str | None = Field(None, max_length=20)
    experience_summary: str | None = Field(None, max_length=255)
    preferred_destinations: list[str] | None = None
    onboarding_completed: bool | None = None
