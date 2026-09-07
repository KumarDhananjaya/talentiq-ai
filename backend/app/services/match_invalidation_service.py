from sqlalchemy.orm import Session

from app.models.candidate_job_match import (
    CandidateJobMatch,
)


def invalidate_candidate_matches(
    db: Session,
    candidate_id: int,
) -> None:
    """
    Delete all persisted matches
    for a specific candidate.
    """

    (
        db.query(CandidateJobMatch)
        .filter(
            CandidateJobMatch.candidate_id
            == candidate_id
        )
        .delete(
            synchronize_session=False
        )
    )


def invalidate_job_matches(
    db: Session,
    job_id: int,
) -> None:
    """
    Delete all persisted matches
    for a specific job.
    """

    (
        db.query(CandidateJobMatch)
        .filter(
            CandidateJobMatch.job_id
            == job_id
        )
        .delete(
            synchronize_session=False
        )
    )