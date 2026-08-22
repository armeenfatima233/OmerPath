from pydantic import BaseModel


class SavedScholarshipsResponse(BaseModel):
    scholarship_ids: list[str]
