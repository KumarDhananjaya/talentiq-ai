from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.database.database import Base


class CandidateJobMatch(Base):

    __tablename__ = "candidate_job_matches"

    __table_args__ = (
        UniqueConstraint(
            "candidate_id",
            "job_id",
            name=(
                "uq_candidate_job_match"
            ),
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    candidate_id: Mapped[int] = mapped_column(
        ForeignKey(
            "candidates.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    job_id: Mapped[int] = mapped_column(
        ForeignKey(
            "jobs.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    skill_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    experience_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    semantic_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    overall_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        index=True,
    )

    matched_skills: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    missing_skills: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    experience_status: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    match_level: Mapped[str] = mapped_column(
        String,
        nullable=False,
        index=True,
    )

    explanation: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )

    candidate = relationship(
        "Candidate",
        back_populates="job_matches",
    )

    job = relationship(
        "Job",
        back_populates="candidate_matches",
    )