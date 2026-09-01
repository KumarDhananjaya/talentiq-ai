from sqlalchemy import (
    Boolean,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.database.database import Base


class CandidateExperience(Base):
    __tablename__ = "candidate_experiences"

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

    company: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    role: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    start_date: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    end_date: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    is_current: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    candidate = relationship(
        "Candidate",
        back_populates="experiences",
    )