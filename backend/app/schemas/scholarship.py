from datetime import date, datetime

from pydantic import BaseModel


class ScholarshipResponse(BaseModel):
    id: str
    name: str
    provider_name: str
    description: str | None = None
    funding_type: str | None = None
    coverage: list[str] = []
    degree_levels: list[str] = []
    fields_of_study: list[str] = []
    destinations: list[str] = []
    eligible_nationalities: list[str] | None = None
    excluded_nationalities: list[str] | None = None
    eligible_residences: list[str] | None = None
    min_gpa: str | None = None
    language_test_type: str | None = None
    min_language_test_score: str | None = None
    min_experience: str | None = None
    age_min: int | None = None
    age_max: int | None = None
    eligibility_notes: str | None = None
    required_documents: list[str] = []
    deadline_at: date | None = None
    deadline_note: str | None = None
    application_opens_at: date | None = None
    official_source_url: str | None = None
    application_url: str | None = None
    source_label: str | None = None
    last_verified_at: datetime | None = None
    status: str
    fit_reasons: list[str] = []
    attention_points: list[str] = []

    model_config = {"from_attributes": True}


class ScholarshipListResponse(BaseModel):
    items: list[ScholarshipResponse]
    total: int
