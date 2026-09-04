from sqlalchemy.orm import Session

from app.models.candidate import Candidate
from app.models.job import Job
from app.models.candidate_job_match import (
    CandidateJobMatch,
)


def save_candidate_job_match(
    db: Session,
    candidate: Candidate,
    job: Job,
    match_result: dict,
) -> CandidateJobMatch:
    """
    Create or update a persisted
    candidate-job match result.
    """

    existing_match = (
        db.query(CandidateJobMatch)
        .filter(
            CandidateJobMatch.candidate_id
            == candidate.id,
            CandidateJobMatch.job_id
            == job.id,
        )
        .first()
    )

    if existing_match:

        existing_match.skill_score = (
            match_result["skill_score"]
        )

        existing_match.experience_score = (
            match_result["experience_score"]
        )

        existing_match.semantic_score = (
            match_result["semantic_score"]
        )

        existing_match.overall_score = (
            match_result["overall_score"]
        )

        existing_match.matched_skills = (
            match_result["matched_skills"]
        )

        existing_match.missing_skills = (
            match_result["missing_skills"]
        )

        existing_match.experience_status = (
            match_result["experience_status"]
        )

        existing_match.match_level = (
            match_result["match_level"]
        )

        existing_match.explanation = (
            match_result["explanation"]
        )

        db.commit()
        db.refresh(existing_match)

        return existing_match

    new_match = CandidateJobMatch(
        candidate_id=candidate.id,
        job_id=job.id,
        skill_score=match_result["skill_score"],
        experience_score=match_result[
            "experience_score"
        ],
        semantic_score=match_result[
            "semantic_score"
        ],
        overall_score=match_result["overall_score"],
        matched_skills=match_result[
            "matched_skills"
        ],
        missing_skills=match_result[
            "missing_skills"
        ],
        experience_status=match_result[
            "experience_status"
        ],
        match_level=match_result["match_level"],
        explanation=match_result["explanation"],
    )

    db.add(new_match)
    db.commit()
    db.refresh(new_match)

    return new_match