import logging
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.academic_profile import AcademicProfile
from app.schemas.academic_profile import AcademicProfileResponse, AcademicProfileUpdateRequest
from app.routes.auth import get_authenticated_session

logger = logging.getLogger("omerpath.academic_profile")

router = APIRouter(
    prefix="/api/academic-profile",
    tags=["Academic Profile"],
)

ALLOWED_STRING_FIELDS = {
    "current_degree",
    "field_of_study",
    "target_degree",
    "gpa",
    "language_test_type",
    "language_test_score",
    "experience_summary",
}


def _to_response(profile: AcademicProfile | None) -> AcademicProfileResponse:
    if profile is None:
        return AcademicProfileResponse()
    return AcademicProfileResponse(
        current_degree=profile.current_degree,
        field_of_study=profile.field_of_study,
        target_degree=profile.target_degree,
        gpa=profile.gpa,
        language_test_type=profile.language_test_type,
        language_test_score=profile.language_test_score,
        experience_summary=profile.experience_summary,
        preferred_destinations=profile.preferred_destinations,
        onboarding_completed_at=profile.onboarding_completed_at,
    )


@router.get(
    "/me",
    response_model=AcademicProfileResponse,
)
def get_me(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> AcademicProfileResponse:
    auth_session = get_authenticated_session(request, response)
    user_id = UUID(str(auth_session.user.id))

    profile = db.get(AcademicProfile, user_id)
    return _to_response(profile)


@router.patch(
    "/me",
    response_model=AcademicProfileResponse,
)
def update_me(
    payload: AcademicProfileUpdateRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> AcademicProfileResponse:
    auth_session = get_authenticated_session(request, response)
    user_id = UUID(str(auth_session.user.id))

    profile = db.get(AcademicProfile, user_id)
    is_new = profile is None
    if profile is None:
        profile = AcademicProfile(user_id=user_id, preferred_destinations=[])

    update_data = payload.model_dump(exclude_unset=True)
    onboarding_completed = update_data.pop("onboarding_completed", None)

    changed = is_new
    for field, value in update_data.items():
        if field not in ALLOWED_STRING_FIELDS and field != "preferred_destinations":
            continue
        if isinstance(value, str):
            value = value.strip()
            if not value:
                # Blank means "no change" for this field, not "clear it".
                continue
        setattr(profile, field, value)
        changed = True

    if onboarding_completed is True:
        profile.onboarding_completed_at = datetime.now(timezone.utc)
        changed = True
    elif onboarding_completed is False:
        profile.onboarding_completed_at = None
        changed = True

    if changed:
        if is_new:
            db.add(profile)
        db.commit()
        db.refresh(profile)

    return _to_response(profile)
