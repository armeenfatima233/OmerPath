from datetime import datetime

from sqlalchemy import Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class UserSettings(Base):
    __tablename__ = "user_settings"

    # user_id -> auth.users(id) is enforced at the DB level by the Alembic
    # migration only, same pattern as AcademicProfile.user_id.
    user_id: Mapped[str] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    deadline_reminders: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    eligibility_changes: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    advisor_nudges: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    weekly_digest: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    share_analytics: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
