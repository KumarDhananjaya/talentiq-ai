from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.job import Job
from app.schemas.job import (
    JobCreate,
    JobUpdate,
    JobResponse,
)
from app.services.matching_service import (
    calculate_and_persist_job_matches,
    get_persisted_job_matches,
)

from app.schemas.matching import (
    JobMatchListResponse,
)

from app.services.embedding_service import generate_embedding
from app.services.profile_text_service import build_job_profile

router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"],
)


@router.post(
    "/",
    response_model=JobResponse,
)

def create_job(
    job: JobCreate,
    db: Session = Depends(get_db),
):
    db_job = Job(
        **job.model_dump()
    )

    job_profile = build_job_profile(
        db_job
    )

    db_job.embedding = generate_embedding(
        job_profile
    )

    db.add(db_job)
    db.commit()
    db.refresh(db_job)

    return db_job

@router.put(
    "/{job_id}",
    response_model=JobResponse,
)
def update_job(
    job_id: int,
    job: JobUpdate,
    db: Session = Depends(get_db),
):
    db_job = (
        db.query(Job)
        .filter(Job.id == job_id)
        .first()
    )

    if not db_job:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    update_data = job.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(db_job, field, value)

    job_profile = build_job_profile(
        db_job
    )

    db_job.embedding = generate_embedding(
        job_profile
    )

    db.commit()
    db.refresh(db_job)

    return db_job


@router.get(
    "/",
    response_model=list[JobResponse],
)
def get_jobs(
    db: Session = Depends(get_db),
):
    jobs = db.query(Job).all()

    return jobs

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

    job = (
        db.query(Job)
        .filter(Job.id == job_id)
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    matches = calculate_and_persist_job_matches(
        db=db,
        job=job,
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
    Return ranked candidates
    for a specific job.
    """

    job = (
        db.query(Job)
        .filter(Job.id == job_id)
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
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