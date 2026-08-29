from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.candidate import Candidate
from app.schemas.candidate import (
    CandidateCreate,
    CandidateResponse,
)


router = APIRouter(
    prefix="/candidates",
    tags=["Candidates"],
)


@router.post(
    "/",
    response_model=CandidateResponse,
)
def create_candidate(
    candidate: CandidateCreate,
    db: Session = Depends(get_db),
):
    existing_candidate = db.query(Candidate).filter(
        Candidate.email == candidate.email
    ).first()

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


@router.get(
    "/",
    response_model=list[CandidateResponse],
)
def get_candidates(
    db: Session = Depends(get_db),
):
    candidates = db.query(Candidate).all()

    return candidates


@router.get(
    "/{candidate_id}",
    response_model=CandidateResponse,
)
def get_candidate(
    candidate_id: int,
    db: Session = Depends(get_db),
):
    candidate = db.query(Candidate).filter(
        Candidate.id == candidate_id
    ).first()

    if not candidate:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found",
        )

    return candidate