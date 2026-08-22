"""Side-effect helper for creating system-generated notifications.

Notifications are never created directly by a client request - only as a
byproduct of a real event (application created/updated, document
uploaded/deleted) that already happened and already committed. This helper
is called AFTER that primary commit, and swallows its own failures so a
notification-insert problem can never turn a successful user action into an
error response.
"""
import logging
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.notification import Notification

logger = logging.getLogger("omerpath.notifications")


def create_notification(db: Session, user_id: UUID, notification_type: str, title: str, message: str) -> None:
    try:
        db.add(Notification(user_id=user_id, type=notification_type, title=title, message=message))
        db.commit()
    except Exception as exc:
        db.rollback()
        logger.warning("Notification creation failed | type=%s | notif_type=%s", type(exc).__name__, notification_type)
