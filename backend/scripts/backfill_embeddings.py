from sqlalchemy.orm import Session

from app.database.database import SessionLocal

from app.models.candidate import Candidate
from app.models.job import Job

from app.services.embedding_service import (
    generate_embedding,
)

from app.services.profile_text_service import (
    build_candidate_profile,
    build_job_profile,
)
from sqlalchemy import or_


def backfill_candidate_embeddings(
    db: Session | None = None,
):
    """
    Generate embeddings for candidates
    that do not already have embeddings.
    """

    owns_session = db is None

    if owns_session:
        db = SessionLocal()

    try:

        candidates = (
            db.query(Candidate)
            .filter(
                or_(
                    Candidate.embedding.is_(None),
                    Candidate.embedding == None,
                )
            )
            .all()
        )

        print(
            f"Found {len(candidates)} candidates "
            "without embeddings."
        )

        for candidate in candidates:

            profile = build_candidate_profile(
                candidate
            )

            candidate.embedding = (
                generate_embedding(profile)
            )

            print(
                "Generated embedding for "
                f"candidate {candidate.id}"
            )

        db.commit()

    except Exception:

        db.rollback()
        raise

    finally:

        if owns_session:
            db.close()


def backfill_job_embeddings(
    db: Session | None = None,
):
    """
    Generate embeddings for jobs
    that do not already have embeddings.
    """

    owns_session = db is None

    if owns_session:
        db = SessionLocal()

    try:

        jobs = (
            db.query(Job)
            .filter(
                Job.embedding.is_(None)
            )
            .all()
        )

        print(
            f"Found {len(jobs)} jobs "
            "without embeddings."
        )

        for job in jobs:

            profile = build_job_profile(
                job
            )

            job.embedding = (
                generate_embedding(profile)
            )

            print(
                "Generated embedding for "
                f"job {job.id}"
            )

        db.commit()

    except Exception:

        db.rollback()
        raise

    finally:

        if owns_session:
            db.close()


def backfill_embeddings():
    """
    Backfill embeddings for both
    candidates and jobs.
    """

    backfill_candidate_embeddings()
    backfill_job_embeddings()


if __name__ == "__main__":

    backfill_embeddings()