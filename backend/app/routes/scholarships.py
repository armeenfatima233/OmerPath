from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.scholarship import Scholarship
from app.schemas.scholarship import ScholarshipListResponse, ScholarshipResponse

router = APIRouter(
    prefix="/api/scholarships",
    tags=["Scholarships"],
)


@router.get("", response_model=ScholarshipListResponse)
def list_scholarships(db: Session = Depends(get_db)) -> ScholarshipListResponse:
    scholarships = db.scalars(
        select(Scholarship).where(Scholarship.status == "active").order_by(Scholarship.name)
    ).all()
    items = [ScholarshipResponse.model_validate(s) for s in scholarships]
    return ScholarshipListResponse(items=items, total=len(items))


@router.get("/{scholarship_id}", response_model=ScholarshipResponse)
def get_scholarship(scholarship_id: str, db: Session = Depends(get_db)) -> ScholarshipResponse:
    scholarship = db.get(Scholarship, scholarship_id)
    if scholarship is None or scholarship.status != "active":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scholarship not found.")
    return ScholarshipResponse.model_validate(scholarship)
