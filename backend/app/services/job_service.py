from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.job import Job
from app.schemas.job import (
    JobCreate,
    JobUpdate,
)
from app.services.embedding_service import (
    generate_embedding,
)
from app.services.profile_text_service import (
    build_job_profile,
)
from app.services.match_invalidation_service import (
    invalidate_job_matches,
)

def create_job(
    db: Session,
    job: JobCreate,
) -> Job:

    db_job = Job(
        **job.model_dump()
    )

    job_profile = build_job_profile(
        db_job
    )

    db_job.embedding = generate_embedding(
        job_profile
    )

    try:
        db.add(db_job)
        db.commit()
        db.refresh(db_job)

    except Exception:
        db.rollback()
        raise

    return db_job

def get_jobs(
    db: Session,
) -> list[Job]:

    return (
        db.query(Job)
        .order_by(Job.created_at.desc())
        .all()
    )

def get_job(
    db: Session,
    job_id: int,
) -> Job:

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

    return job

def update_job(
    db: Session,
    job_id: int,
    job: JobUpdate,
) -> Job:

    db_job = get_job(
        db=db,
        job_id=job_id,
    )

    update_data = job.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(
            db_job,
            field,
            value,
        )

    job_profile = build_job_profile(
        db_job
    )

    db_job.embedding = generate_embedding(
        job_profile
    )

    try:
        invalidate_job_matches(
            db=db,
            job_id=db_job.id,
        )

        db.commit()
        db.refresh(db_job)

    except Exception:
        db.rollback()
        raise

    return db_job

def delete_job(
    db: Session,
    job_id: int,
) -> None:

    db_job = get_job(
        db=db,
        job_id=job_id,
    )

    try:
        invalidate_job_matches(
            db=db,
            job_id=db_job.id,
        )

        db.delete(db_job)

        db.commit()

    except Exception:
        db.rollback()
        raise