from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.candidate_job_match import (
    CandidateJobMatch,
)


def save_candidate_job_match(
    db: Session,
    candidate_id: int,
    job_id: int,
    match_result: dict,
    commit: bool = True,
) -> CandidateJobMatch:
    now = datetime.now(timezone.utc)
    existing_match = (
        db.query(CandidateJobMatch)
        .filter(
            CandidateJobMatch.candidate_id == candidate_id,
            CandidateJobMatch.job_id == job_id,
        )
        .first()
    )

    if existing_match:
        for key, value in match_result.items():
            setattr(existing_match, key, value)
        existing_match.updated_at = now
        match_obj = existing_match
    else:
        data = dict(match_result)
        if "created_at" not in data or data["created_at"] is None:
            data["created_at"] = now
        if "updated_at" not in data or data["updated_at"] is None:
            data["updated_at"] = now
        match_obj = CandidateJobMatch(**data)
        db.add(match_obj)

    if commit:
        db.commit()
        db.refresh(match_obj)
    return match_obj