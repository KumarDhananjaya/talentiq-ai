from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text, Float, JSON, func
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.database.database import Base


class Candidate(Base):
    __tablename__ = "candidates"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        unique=True,
    )

    phone: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    resume_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    skills: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    embedding: Mapped[list[float] | None] = mapped_column(
        JSON(none_as_null=True),
        nullable=True,
    )

    experiences = relationship(
        "CandidateExperience",
        back_populates="candidate",
        cascade="all, delete-orphan",
    )

    experience_years: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    job_matches = relationship(
        "CandidateJobMatch",
        back_populates="candidate",
        cascade="all, delete-orphan",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )
