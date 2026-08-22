from datetime import date, datetime

from sqlalchemy import ARRAY, Date, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Scholarship(Base):
    __tablename__ = "scholarships"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    provider_name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    funding_type: Mapped[str | None] = mapped_column(String(30), nullable=True)
    coverage: Mapped[list[str]] = mapped_column(ARRAY(String(150)), nullable=False, server_default="{}")
    degree_levels: Mapped[list[str]] = mapped_column(ARRAY(String(50)), nullable=False, server_default="{}")
    fields_of_study: Mapped[list[str]] = mapped_column(ARRAY(String(100)), nullable=False, server_default="{}")
    destinations: Mapped[list[str]] = mapped_column(ARRAY(String(100)), nullable=False, server_default="{}")
    eligible_nationalities: Mapped[list[str] | None] = mapped_column(ARRAY(String(100)), nullable=True)
    excluded_nationalities: Mapped[list[str] | None] = mapped_column(ARRAY(String(100)), nullable=True)
    eligible_residences: Mapped[list[str] | None] = mapped_column(ARRAY(String(100)), nullable=True)
    min_gpa: Mapped[str | None] = mapped_column(String(20), nullable=True)
    language_test_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    min_language_test_score: Mapped[str | None] = mapped_column(String(20), nullable=True)
    min_experience: Mapped[str | None] = mapped_column(String(255), nullable=True)
    age_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    age_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    eligibility_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    required_documents: Mapped[list[str]] = mapped_column(ARRAY(String(150)), nullable=False, server_default="{}")
    deadline_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    deadline_note: Mapped[str | None] = mapped_column(String(255), nullable=True)
    application_opens_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    official_source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    application_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_label: Mapped[str | None] = mapped_column(String(150), nullable=True)
    last_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="draft")
    fit_reasons: Mapped[list[str]] = mapped_column(ARRAY(String(200)), nullable=False, server_default="{}")
    attention_points: Mapped[list[str]] = mapped_column(ARRAY(String(200)), nullable=False, server_default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
