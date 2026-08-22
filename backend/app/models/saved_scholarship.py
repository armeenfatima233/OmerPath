from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class SavedScholarship(Base):
    __tablename__ = "saved_scholarships"

    # user_id -> auth.users(id) is enforced at the DB level by the Alembic
    # migration only (auth.users lives outside our SQLAlchemy metadata,
    # same pattern as AcademicProfile.user_id and Profile.id).
    user_id: Mapped[str] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    scholarship_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("scholarships.id", ondelete="CASCADE"),
        primary_key=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
