from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.notification import Notification
from app.schemas.notification import NotificationResponse
from app.routes.auth import get_authenticated_session

router = APIRouter(
    prefix="/api/notifications",
    tags=["Notifications"],
)


@router.get("", response_model=list[NotificationResponse])
def list_notifications(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> list[NotificationResponse]:
    auth_session = get_authenticated_session(request, response)
    user_id = UUID(str(auth_session.user.id))

    notifications = db.scalars(
        select(Notification).where(Notification.user_id == user_id).order_by(Notification.created_at.desc())
    ).all()
    return [NotificationResponse.model_validate(n) for n in notifications]


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
def mark_read(
    notification_id: UUID,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> NotificationResponse:
    auth_session = get_authenticated_session(request, response)
    user_id = UUID(str(auth_session.user.id))

    notification = db.get(Notification, notification_id)
    if notification is None or notification.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found.")

    if not notification.is_read:
        notification.is_read = True
        db.commit()
        db.refresh(notification)
    return NotificationResponse.model_validate(notification)


@router.post("/mark-all-read", response_model=list[NotificationResponse])
def mark_all_read(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> list[NotificationResponse]:
    auth_session = get_authenticated_session(request, response)
    user_id = UUID(str(auth_session.user.id))

    db.execute(
        update(Notification)
        .where(Notification.user_id == user_id, Notification.is_read.is_(False))
        .values(is_read=True)
    )
    db.commit()

    notifications = db.scalars(
        select(Notification).where(Notification.user_id == user_id).order_by(Notification.created_at.desc())
    ).all()
    return [NotificationResponse.model_validate(n) for n in notifications]
