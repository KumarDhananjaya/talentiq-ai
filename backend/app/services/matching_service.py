import json
import logging
from app.models.candidate import Candidate
from app.models.job import Job
from sqlalchemy.orm import Session
from app.services.semantic_matching_service import (
    calculate_semantic_score,
)
from app.services.match_persistence_service import (
    save_candidate_job_match,
)
from app.models.candidate_job_match import CandidateJobMatch

logger = logging.getLogger(__name__)


def normalize_skill(skill: str) -> str:
    """
    Normalize a skill for comparison.
    """
    if not skill:
        return ""
    return str(skill).strip().lower()


def get_candidate_skills(
    candidate: Candidate,
) -> set[str]:
    """
    Normalize candidate skills safely handling lists, JSON strings, and None.
    """

    if not candidate.skills:
        return set()

    raw_skills = candidate.skills

    if isinstance(raw_skills, str):
        try:
            parsed = json.loads(raw_skills)
            if isinstance(parsed, list):
                raw_skills = parsed
            else:
                raw_skills = raw_skills.split(",")
        except Exception:
            raw_skills = raw_skills.split(",")

    if isinstance(raw_skills, (list, set, tuple)):
        skills_set = set()
        for skill in raw_skills:
            if skill is not None and str(skill).strip():
                normalized = normalize_skill(str(skill))
                if normalized:
                    skills_set.add(normalized)
        return skills_set

    return set()


def get_job_skills(
    job: Job,
) -> set[str]:
    """
    Convert comma-separated job skills
    into a normalized set.
    """

    if not job.required_skills:
        return set()

    raw_skills = job.required_skills
    if isinstance(raw_skills, (list, set, tuple)):
        return {
            normalize_skill(str(s))
            for s in raw_skills
            if s and str(s).strip()
        }

    return {
        normalize_skill(skill)
        for skill in str(job.required_skills).split(",")
        if str(skill).strip()
    }


def calculate_skill_score(
    candidate: Candidate,
    job: Job,
) -> tuple[float, list[str], list[str]]:
    """
    Calculate skill match percentage.

    Returns:
        skill_score
        matched_skills
        missing_skills
    """

    candidate_skills = get_candidate_skills(
        candidate
    )

    job_skills = get_job_skills(
        job
    )

    if not job_skills:
        return (
            100.0,
            [],
            [],
        )

    matched_skills = (
        candidate_skills
        & job_skills
    )

    missing_skills = (
        job_skills
        - candidate_skills
    )

    skill_score = (
        len(matched_skills)
        / len(job_skills)
    ) * 100

    return (
        round(skill_score, 2),
        sorted(matched_skills),
        sorted(missing_skills),
    )


def calculate_experience_score(
    candidate: Candidate,
    job: Job,
) -> float:
    """
    Calculate experience compatibility score.
    """

    if not job.minimum_experience:
        return 100.0

    if not candidate.experience_years:
        return 0.0

    if (
        candidate.experience_years
        >= job.minimum_experience
    ):
        return 100.0

    score = (
        candidate.experience_years
        / job.minimum_experience
    ) * 100

    return round(
        min(score, 100.0),
        2,
    )

def get_experience_status(
    candidate: Candidate,
    job: Job,
) -> str:
    """
    Describe how the candidate's experience
    compares with the job requirement.
    """

    if not job.minimum_experience:
        return "No experience requirement"

    candidate_experience = (
        candidate.experience_years or 0
    )

    if candidate_experience >= job.minimum_experience:
        return "Meets requirement"

    return "Below requirement"


def get_match_level(
    overall_score: float,
) -> str:
    """
    Convert the numerical match score
    into a recruiter-friendly category.
    """

    if overall_score >= 85:
        return "Excellent Match"

    if overall_score >= 70:
        return "Strong Match"

    if overall_score >= 50:
        return "Moderate Match"

    return "Weak Match"


def generate_match_explanation(
    skill_score: float,
    experience_score: float,
    semantic_score: float,
    matched_skills: list[str],
    missing_skills: list[str],
    experience_status: str,
) -> str:
    """
    Generate a human-readable explanation
    for the candidate-job match.
    """

    explanation_parts = [
        f"Skill match score: {skill_score}%.",
        f"Experience match score: {experience_score}%.",
        f"Semantic similarity score: {semantic_score}%.",
    ]

    if matched_skills:
        explanation_parts.append(
            "Matched skills: "
            + ", ".join(matched_skills)
            + "."
        )

    if missing_skills:
        explanation_parts.append(
            "Missing skills: "
            + ", ".join(missing_skills)
            + "."
        )

    explanation_parts.append(
        f"Experience status: {experience_status}."
    )

    return " ".join(explanation_parts)


def calculate_match(
    candidate: Candidate,
    job: Job,
) -> dict:
    """
    Calculate the hybrid candidate-job match.

    Weighting:
        40% skills
        20% experience
        40% semantic similarity
    """

    (
        skill_score,
        matched_skills,
        missing_skills,
    ) = calculate_skill_score(
        candidate=candidate,
        job=job,
    )

    experience_score = (
        calculate_experience_score(
            candidate=candidate,
            job=job,
        )
    )

    semantic_score = (
        calculate_semantic_score(
            candidate=candidate,
            job=job,
        )
    )

    overall_score = round(
        (skill_score * 0.4)
        + (experience_score * 0.2)
        + (semantic_score * 0.4),
        2,
    )

    experience_status = (
        get_experience_status(
            candidate=candidate,
            job=job,
        )
    )

    match_level = get_match_level(
        overall_score
    )

    explanation = generate_match_explanation(
        skill_score=skill_score,
        experience_score=experience_score,
        semantic_score=semantic_score,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        experience_status=experience_status,
    )

    return {
        "candidate_id": candidate.id,
        "job_id": job.id,
        "overall_score": overall_score,
        "skill_score": skill_score,
        "experience_score": experience_score,
        "semantic_score": semantic_score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "experience_status": experience_status,
        "match_level": match_level,
        "explanation": explanation,
    }

def calculate_and_persist_job_matches(
    db: Session,
    job: Job,
) -> list[dict]:
    """
    Calculate, persist, and rank all candidates
    for a given job.
    """

    candidates = (
        db.query(Candidate)
        .all()
    )

    matches = []

    for candidate in candidates:
        try:
            match_result = calculate_match(
                candidate=candidate,
                job=job,
            )

            saved_match = save_candidate_job_match(
                db=db,
                candidate_id=candidate.id,
                job_id=job.id,
                match_result=match_result,
                commit=False,
            )

            matches.append(
                {
                    "candidate_id": saved_match.candidate_id,
                    "job_id": saved_match.job_id,
                    "candidate_name": candidate.full_name,
                    "candidate_email": candidate.email,
                    "overall_score": saved_match.overall_score,
                    "skill_score": saved_match.skill_score,
                    "experience_score": saved_match.experience_score,
                    "semantic_score": saved_match.semantic_score,
                    "matched_skills": saved_match.matched_skills,
                    "missing_skills": saved_match.missing_skills,
                    "experience_status": saved_match.experience_status,
                    "match_level": saved_match.match_level,
                    "explanation": saved_match.explanation,
                }
            )
        except Exception as e:
            logger.warning(
                f"Failed to calculate match for candidate {candidate.id} on job {job.id}: {str(e)}"
            )

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to commit matches for job {job.id}: {str(e)}")
        raise e

    matches.sort(
        key=lambda match: match["overall_score"],
        reverse=True,
    )

    return matches

def get_persisted_job_matches(
    db: Session,
    job: Job,
) -> list[dict]:
    """
    Return persisted matches for a given job,
    ranked by overall score.
    """

    saved_matches = (
        db.query(CandidateJobMatch)
        .filter(
            CandidateJobMatch.job_id == job.id
        )
        .order_by(
            CandidateJobMatch.overall_score.desc()
        )
        .all()
    )

    return [
        {
            "candidate_id": match.candidate_id,
            "job_id": match.job_id,
            "candidate_name": match.candidate.full_name if match.candidate else None,
            "candidate_email": match.candidate.email if match.candidate else None,
            "overall_score": match.overall_score,
            "skill_score": match.skill_score,
            "experience_score": match.experience_score,
            "semantic_score": match.semantic_score,
            "matched_skills": match.matched_skills,
            "missing_skills": match.missing_skills,
            "experience_status": match.experience_status,
            "match_level": match.match_level,
            "explanation": match.explanation,
        }
        for match in saved_matches
    ]
