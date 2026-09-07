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
        match_obj = existing_match
    else:
        match_obj = CandidateJobMatch(**match_result)
        db.add(match_obj)

    if commit:
        db.commit()
        db.refresh(match_obj)
    return match_obj