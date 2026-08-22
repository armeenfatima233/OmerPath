from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.application import Application
from app.models.scholarship import Scholarship
from app.notifications import create_notification
from app.schemas.application import ApplicationCreateRequest, ApplicationResponse, ApplicationUpdateRequest
from app.routes.auth import get_authenticated_session

router = APIRouter(
    prefix="/api/applications",
    tags=["Applications"],
)

VALID_STATUSES = {"Preparing", "Ready to apply", "Submitted"}


def _apply_status_transition(application: Application, new_status: str) -> None:
    application.status = new_status
    if new_status == "Submitted":
        application.progress = 100
        application.next_action = "Track result and correspondence"
    elif new_status == "Ready to apply":
        application.progress = max(application.progress, 90)
        application.next_action = "Submit when final checks are complete"
    else:
        application.progress = min(application.progress, 89)
        # next_action is left unchanged when moving back to Preparing


@router.get("", response_model=list[ApplicationResponse])
def list_applications(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> list[ApplicationResponse]:
    auth_session = get_authenticated_session(request, response)
    user_id = UUID(str(auth_session.user.id))

    applications = db.scalars(
        select(Application).where(Application.user_id == user_id).order_by(Application.created_at)
    ).all()
    return [ApplicationResponse.model_validate(a) for a in applications]


@router.get("/{application_id}", response_model=ApplicationResponse)
def get_application(
    application_id: UUID,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> ApplicationResponse:
    auth_session = get_authenticated_session(request, response)
    user_id = UUID(str(auth_session.user.id))

    application = db.get(Application, application_id)
    if application is None or application.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found.")
    return ApplicationResponse.model_validate(application)


@router.post("", response_model=ApplicationResponse)
def create_application(
    payload: ApplicationCreateRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> ApplicationResponse:
    auth_session = get_authenticated_session(request, response)
    user_id = UUID(str(auth_session.user.id))

    scholarship = db.get(Scholarship, payload.scholarship_id)
    if scholarship is None or scholarship.status != "active":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scholarship not found.")

    existing = db.scalar(
        select(Application).where(
            Application.user_id == user_id,
            Application.scholarship_id == payload.scholarship_id,
        )
    )
    if existing is not None:
        response.status_code = status.HTTP_200_OK
        return ApplicationResponse.model_validate(existing)

    application = Application(user_id=user_id, scholarship_id=payload.scholarship_id)
    db.add(application)
    db.commit()
    db.refresh(application)

    create_notification(
        db, user_id, "application_started",
        "Application started",
        f"You started an application for {scholarship.name}.",
    )

    response.status_code = status.HTTP_201_CREATED
    return ApplicationResponse.model_validate(application)


@router.patch("/{application_id}", response_model=ApplicationResponse)
def update_application(
    application_id: UUID,
    payload: ApplicationUpdateRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> ApplicationResponse:
    auth_session = get_authenticated_session(request, response)
    user_id = UUID(str(auth_session.user.id))

    if payload.status not in VALID_STATUSES:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid status.")

    application = db.get(Application, application_id)
    if application is None or application.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found.")

    _apply_status_transition(application, payload.status)
    db.commit()
    db.refresh(application)

    scholarship = db.get(Scholarship, application.scholarship_id)
    scholarship_name = scholarship.name if scholarship else "your scholarship"
    create_notification(
        db, user_id, "application_status_changed",
        "Application status changed",
        f"Your {scholarship_name} application is now \"{payload.status}\".",
    )

    return ApplicationResponse.model_validate(application)
