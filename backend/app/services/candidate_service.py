from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.candidate import Candidate
from app.schemas.candidate import CandidateCreate


def create_candidate(
    db: Session,
    candidate: CandidateCreate,
) -> Candidate:
    existing_candidate = (
        db.query(Candidate)
        .filter(Candidate.email == candidate.email)
        .first()
    )

    if existing_candidate:
        raise HTTPException(
            status_code=400,
            detail="Candidate with this email already exists",
        )

    db_candidate = Candidate(
        **candidate.model_dump()
    )

    db.add(db_candidate)
    db.commit()
    db.refresh(db_candidate)

    return db_candidate


def get_candidates(
    db: Session,
) -> list[Candidate]:
    return db.query(Candidate).all()


def get_candidate(
    db: Session,
    candidate_id: int,
) -> Candidate:
    candidate = (
        db.query(Candidate)
        .filter(Candidate.id == candidate_id)
        .first()
    )

    if not candidate:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found",
        )

    return candidate