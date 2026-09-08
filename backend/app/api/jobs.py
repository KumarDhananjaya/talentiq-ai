from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.schemas.job import (
    JobCreate,
    JobUpdate,
    JobResponse,
)

from app.schemas.matching import (
    JobMatchListResponse,
)

from app.services.job_service import (
    create_job,
    get_jobs,
    get_job,
    update_job,
    delete_job,
)

from app.services.matching_service import (
    calculate_and_persist_job_matches,
    get_persisted_job_matches,
)


router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"],
)


@router.post(
    "/",
    response_model=JobResponse,
)
def create_job_endpoint(
    job: JobCreate,
    db: Session = Depends(get_db),
):
    return create_job(
        db=db,
        job=job,
    )


@router.get(
    "/",
    response_model=list[JobResponse],
)
def get_jobs_endpoint(
    db: Session = Depends(get_db),
):
    return get_jobs(
        db=db,
    )


@router.get(
    "/{job_id}",
    response_model=JobResponse,
)
def get_job_endpoint(
    job_id: int,
    db: Session = Depends(get_db),
):
    return get_job(
        db=db,
        job_id=job_id,
    )


@router.put(
    "/{job_id}",
    response_model=JobResponse,
)
def update_job_endpoint(
    job_id: int,
    job: JobUpdate,
    db: Session = Depends(get_db),
):
    return update_job(
        db=db,
        job_id=job_id,
        job=job,
    )


@router.delete(
    "/{job_id}",
    status_code=204,
)
def delete_job_endpoint(
    job_id: int,
    db: Session = Depends(get_db),
):
    delete_job(
        db=db,
        job_id=job_id,
    )


@router.post(
    "/{job_id}/matches/recalculate",
    response_model=JobMatchListResponse,
)
def recalculate_job_matches(
    job_id: int,
    db: Session = Depends(get_db),
):
    """
    Recalculate and persist matches
    for all candidates for a specific job.
    """

    job = get_job(
        db=db,
        job_id=job_id,
    )

    try:
        matches = calculate_and_persist_job_matches(
            db=db,
            job=job,
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate matches: {str(e)}",
        )

    return {
        "job_id": job.id,
        "total_matches": len(matches),
        "matches": matches,
    }


@router.get(
    "/{job_id}/matches",
    response_model=JobMatchListResponse,
)
def get_job_matches_endpoint(
    job_id: int,
    min_score: float = Query(
        default=0,
        ge=0,
        le=100,
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_db),
):
    """
    Return persisted and ranked candidates
    for a specific job.
    """

    job = get_job(
        db=db,
        job_id=job_id,
    )

    matches = get_persisted_job_matches(
        db=db,
        job=job,
    )

    matches = [
        match
        for match in matches
        if match["overall_score"] >= min_score
    ]

    matches = matches[:limit]

    return {
        "job_id": job.id,
        "total_matches": len(matches),
        "matches": matches,
    }