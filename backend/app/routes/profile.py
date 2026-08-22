import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.profile import Profile
from app.schemas.auth import CurrentUserResponse
from app.schemas.profile import ProfileUpdateRequest
from app.routes.auth import get_authenticated_session

logger = logging.getLogger("omerpath.profile")

router = APIRouter(
    prefix="/api/profile",
    tags=["Profile"],
)

ALLOWED_FIELDS = {
    "first_name",
    "last_name",
    "nationality",
    "country_of_residence",
}


@router.patch(
    "/me",
    response_model=CurrentUserResponse,
)
def update_me(
    payload: ProfileUpdateRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> CurrentUserResponse:
    auth_session = get_authenticated_session(request, response)
    user_id = UUID(str(auth_session.user.id))

    profile = db.get(Profile, user_id)

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found.",
        )

    update_data = payload.model_dump(exclude_unset=True)

    changed = False
    for field, value in update_data.items():
        if field not in ALLOWED_FIELDS:
            continue
        if isinstance(value, str):
            value = value.strip()
            if not value:
                # Blank means "no change" for this field, not "clear it".
                continue
        setattr(profile, field, value)
        changed = True

    if changed:
        db.commit()
        db.refresh(profile)

    return CurrentUserResponse(
        user_id=user_id,
        email=auth_session.user.email,
        first_name=profile.first_name,
        last_name=profile.last_name,
        nationality=profile.nationality,
        country_of_residence=profile.country_of_residence,
    )
