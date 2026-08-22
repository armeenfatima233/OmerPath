from datetime import datetime
from uuid import UUID

from sqlalchemy import ARRAY, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class AcademicProfile(Base):
    __tablename__ = "academic_profiles"

    # The FK to auth.users(id) is enforced at the DB level by the Alembic
    # migration only, not declared here — auth.users lives outside our
    # SQLAlchemy metadata (same pattern as Profile.id).
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
    )
    current_degree: Mapped[str | None] = mapped_column(String(150), nullable=True)
    field_of_study: Mapped[str | None] = mapped_column(String(150), nullable=True)
    target_degree: Mapped[str | None] = mapped_column(String(50), nullable=True)
    gpa: Mapped[str | None] = mapped_column(String(20), nullable=True)
    language_test_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    language_test_score: Mapped[str | None] = mapped_column(String(20), nullable=True)
    experience_summary: Mapped[str | None] = mapped_column(String(255), nullable=True)
    preferred_destinations: Mapped[list[str]] = mapped_column(
        ARRAY(String(100)),
        nullable=False,
        server_default="{}",
    )
    onboarding_completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
