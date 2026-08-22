from pydantic import BaseModel


class SettingsResponse(BaseModel):
    deadline_reminders: bool
    eligibility_changes: bool
    advisor_nudges: bool
    weekly_digest: bool
    share_analytics: bool


class SettingsUpdateRequest(BaseModel):
    deadline_reminders: bool | None = None
    eligibility_changes: bool | None = None
    advisor_nudges: bool | None = None
    weekly_digest: bool | None = None
    share_analytics: bool | None = None
