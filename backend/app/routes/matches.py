from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.matching import compute_match
from app.models.academic_profile import AcademicProfile
from app.models.profile import Profile
from app.models.scholarship import Scholarship
from app.schemas.matching import MatchListResponse, MatchResponse
from app.routes.auth import get_authenticated_session

router = APIRouter(
    prefix="/api/matches",
    tags=["Matching"],
)


def _load_context(db: Session, user_id: UUID) -> tuple[Profile | None, AcademicProfile | None]:
    profile = db.get(Profile, user_id)
    academic_profile = db.get(AcademicProfile, user_id)
    return profile, academic_profile


@router.get("", response_model=MatchListResponse)
def list_matches(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> MatchListResponse:
    auth_session = get_authenticated_session(request, response)
    user_id = UUID(str(auth_session.user.id))
    profile, academic_profile = _load_context(db, user_id)

    scholarships = db.scalars(select(Scholarship).where(Scholarship.status == "active")).all()
    results = [compute_match(profile, academic_profile, s) for s in scholarships]
    return MatchListResponse(items=[MatchResponse(**r.__dict__) for r in results])


@router.get("/{scholarship_id}", response_model=MatchResponse)
def get_match(
    scholarship_id: str,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> MatchResponse:
    auth_session = get_authenticated_session(request, response)
    user_id = UUID(str(auth_session.user.id))
    profile, academic_profile = _load_context(db, user_id)

    scholarship = db.get(Scholarship, scholarship_id)
    if scholarship is None or scholarship.status != "active":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scholarship not found.")

    result = compute_match(profile, academic_profile, scholarship)
    return MatchResponse(**result.__dict__)
