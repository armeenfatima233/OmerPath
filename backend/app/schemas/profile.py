from pydantic import BaseModel, Field


class ProfileUpdateRequest(BaseModel):
    first_name: str | None = Field(None, max_length=100)
    last_name: str | None = Field(None, max_length=100)
    nationality: str | None = Field(None, max_length=100)
    country_of_residence: str | None = Field(None, max_length=100)
