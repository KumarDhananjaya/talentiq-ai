from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.job import Job
from app.schemas.job import (
    JobCreate,
    JobResponse,
)
from app.services.matching_service import (
    get_job_matches,
)
from app.schemas.matching import (
    JobMatchResponse,
)

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

    db.add(db_job)
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

@router.get(
    "/{job_id}/matches",
    response_model=list[JobMatchResponse],
)
def get_job_matches_endpoint(
    job_id: int,
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

    matches = get_job_matches(
        db=db,
        job=job,
    )

    return matches