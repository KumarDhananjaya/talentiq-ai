import json

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.candidate import Candidate
from app.models.candidate_experience import (
    CandidateExperience,
)
from app.schemas.candidate import CandidateCreate


def create_candidate(
    db: Session,
    candidate: CandidateCreate,
) -> Candidate:

    if candidate.email:
        existing_candidate = (
            db.query(Candidate)
            .filter(
                Candidate.email == candidate.email
            )
            .first()
        )

        if existing_candidate:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Candidate with this email "
                    "already exists"
                ),
            )

    db_candidate = Candidate(
        full_name=candidate.full_name,
        email=(
            str(candidate.email)
            if candidate.email
            else None
        ),
        phone=candidate.phone,
        resume_text=candidate.resume_text,
        skills=json.dumps(candidate.skills),
        experience_years=(
            candidate.experience_years
        ),
    )

    for experience in candidate.experiences:

        db_experience = CandidateExperience(
            company=experience.company,
            role=experience.role,
            start_date=experience.start_date,
            end_date=experience.end_date,
            is_current=experience.is_current,
            description=experience.description,
        )

        db_candidate.experiences.append(
            db_experience
        )

    try:

        db.add(db_candidate)
        db.commit()
        db.refresh(db_candidate)

    except Exception:

        db.rollback()
        raise

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
        .filter(
            Candidate.id == candidate_id
        )
        .first()
    )

    if not candidate:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found",
        )

    return candidate