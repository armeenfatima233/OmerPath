from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.saved_scholarship import SavedScholarship
from app.models.scholarship import Scholarship
from app.schemas.saved_scholarship import SavedScholarshipsResponse
from app.routes.auth import get_authenticated_session

router = APIRouter(
    prefix="/api/saved-scholarships",
    tags=["Saved Scholarships"],
)


def _list_saved_ids(db: Session, user_id: UUID) -> list[str]:
    return list(
        db.scalars(
            select(SavedScholarship.scholarship_id)
            .where(SavedScholarship.user_id == user_id)
            .order_by(SavedScholarship.created_at)
        ).all()
    )


@router.get("", response_model=SavedScholarshipsResponse)
def list_saved(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> SavedScholarshipsResponse:
    auth_session = get_authenticated_session(request, response)
    user_id = UUID(str(auth_session.user.id))
    return SavedScholarshipsResponse(scholarship_ids=_list_saved_ids(db, user_id))


@router.post("/{scholarship_id}", response_model=SavedScholarshipsResponse)
def save_scholarship(
    scholarship_id: str,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> SavedScholarshipsResponse:
    auth_session = get_authenticated_session(request, response)
    user_id = UUID(str(auth_session.user.id))

    scholarship = db.get(Scholarship, scholarship_id)
    if scholarship is None or scholarship.status != "active":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scholarship not found.")

    existing = db.get(SavedScholarship, (user_id, scholarship_id))
    if existing is None:
        db.add(SavedScholarship(user_id=user_id, scholarship_id=scholarship_id))
        db.commit()

    return SavedScholarshipsResponse(scholarship_ids=_list_saved_ids(db, user_id))


@router.delete("/{scholarship_id}", response_model=SavedScholarshipsResponse)
def unsave_scholarship(
    scholarship_id: str,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> SavedScholarshipsResponse:
    auth_session = get_authenticated_session(request, response)
    user_id = UUID(str(auth_session.user.id))

    existing = db.get(SavedScholarship, (user_id, scholarship_id))
    if existing is not None:
        db.delete(existing)
        db.commit()

    return SavedScholarshipsResponse(scholarship_ids=_list_saved_ids(db, user_id))
