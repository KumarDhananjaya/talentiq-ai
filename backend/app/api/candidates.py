from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.candidate import (
    CandidateCreate,
    CandidateResponse,
)
from app.services.candidate_service import (
    create_candidate,
    get_candidate,
    get_candidates,
)


router = APIRouter(
    prefix="/candidates",
    tags=["Candidates"],
)


@router.post(
    "/",
    response_model=CandidateResponse,
)
def create_candidate_endpoint(
    candidate: CandidateCreate,
    db: Session = Depends(get_db),
):
    return create_candidate(
        db=db,
        candidate=candidate,
    )


@router.get(
    "/",
    response_model=list[CandidateResponse],
)
def get_candidates_endpoint(
    db: Session = Depends(get_db),
):
    return get_candidates(db=db)


@router.get(
    "/{candidate_id}",
    response_model=CandidateResponse,
)
def get_candidate_endpoint(
    candidate_id: int,
    db: Session = Depends(get_db),
):
    return get_candidate(
        db=db,
        candidate_id=candidate_id,
    )