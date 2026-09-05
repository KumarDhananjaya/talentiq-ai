from app.models.candidate import Candidate
from app.models.job import Job
from sqlalchemy.orm import Session
from app.services.semantic_matching_service import (
    calculate_semantic_score,
)
from app.services.match_persistence_service import (
    save_candidate_job_match,
)


def normalize_skill(skill: str) -> str:
    """
    Normalize a skill for comparison.
    """

    return skill.strip().lower()


def get_candidate_skills(
    candidate: Candidate,
) -> set[str]:
    """
    Normalize candidate skills.
    """

    if not candidate.skills:
        return set()

    return {
        normalize_skill(skill)
        for skill in candidate.skills
    }


def get_job_skills(
    job: Job,
) -> set[str]:
    """
    Convert comma-separated job skills
    into a normalized set.
    """

    if not job.required_skills:
        return set()

    return {
        normalize_skill(skill)
        for skill in job.required_skills.split(",")
        if skill.strip()
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

def get_job_matches(
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

        match_result = calculate_match(
            candidate=candidate,
            job=job,
        )

        saved_match = (
            save_candidate_job_match(
                db=db,
                candidate_id=candidate.id,
                job_id=job.id,
                match_result=match_result,
            )
        )

        matches.append(
            {
                "candidate_id": (
                    saved_match.candidate_id
                ),
                "job_id": (
                    saved_match.job_id
                ),
                "overall_score": (
                    saved_match.overall_score
                ),
                "skill_score": (
                    saved_match.skill_score
                ),
                "experience_score": (
                    saved_match.experience_score
                ),
                "semantic_score": (
                    saved_match.semantic_score
                ),
                "matched_skills": (
                    saved_match.matched_skills
                ),
                "missing_skills": (
                    saved_match.missing_skills
                ),
                "experience_status": (
                    saved_match.experience_status
                ),
                "match_level": (
                    saved_match.match_level
                ),
                "explanation": (
                    saved_match.explanation
                ),
            }
        )

    matches.sort(
        key=lambda match: match[
            "overall_score"
        ],
        reverse=True,
    )

    return matches