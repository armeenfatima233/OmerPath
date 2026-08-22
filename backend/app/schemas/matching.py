from pydantic import BaseModel


class MatchResponse(BaseModel):
    scholarship_id: str
    eligibility_status: str
    match_score: int | None = None
    matched_criteria: list[str] = []
    unmet_criteria: list[str] = []
    unknown_criteria: list[str] = []
    reasons: list[str] = []


class MatchListResponse(BaseModel):
    items: list[MatchResponse]
