from uuid import UUID

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user_settings import UserSettings
from app.schemas.user_settings import SettingsResponse, SettingsUpdateRequest
from app.routes.auth import get_authenticated_session

router = APIRouter(
    prefix="/api/settings",
    tags=["Settings"],
)


def _to_response(settings: UserSettings | None) -> SettingsResponse:
    if settings is None:
        return SettingsResponse(
            deadline_reminders=True,
            eligibility_changes=True,
            advisor_nudges=True,
            weekly_digest=False,
            share_analytics=False,
        )
    return SettingsResponse(
        deadline_reminders=settings.deadline_reminders,
        eligibility_changes=settings.eligibility_changes,
        advisor_nudges=settings.advisor_nudges,
        weekly_digest=settings.weekly_digest,
        share_analytics=settings.share_analytics,
    )


@router.get("", response_model=SettingsResponse)
def get_settings(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> SettingsResponse:
    auth_session = get_authenticated_session(request, response)
    user_id = UUID(str(auth_session.user.id))

    settings = db.get(UserSettings, user_id)
    return _to_response(settings)


@router.patch("", response_model=SettingsResponse)
def update_settings(
    payload: SettingsUpdateRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> SettingsResponse:
    auth_session = get_authenticated_session(request, response)
    user_id = UUID(str(auth_session.user.id))

    settings = db.get(UserSettings, user_id)
    is_new = settings is None
    if settings is None:
        settings = UserSettings(user_id=user_id)

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(settings, field, value)

    if is_new:
        db.add(settings)
    db.commit()
    db.refresh(settings)
    return _to_response(settings)
