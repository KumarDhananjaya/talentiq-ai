from app.models.candidate import Candidate
from app.models.job import Job
from sqlalchemy.orm import Session


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


def calculate_match(
    candidate: Candidate,
    job: Job,
) -> dict:
    """
    Calculate the overall candidate-job match.

    Weighting:
        70% skills
        30% experience
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

    overall_score = (
        (skill_score * 0.7)
        + (experience_score * 0.3)
    )

    return {
        "candidate_id": candidate.id,
        "job_id": job.id,
        "overall_score": round(
            overall_score,
            2,
        ),
        "skill_score": skill_score,
        "experience_score": experience_score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
    }

def get_job_matches(
    db: Session,
    job: Job,
) -> list[dict]:
    """
    Calculate and rank all candidates
    for a given job.
    """

    candidates = (
        db.query(Candidate)
        .all()
    )

    matches = []

    for candidate in candidates:

        match = calculate_match(
            candidate=candidate,
            job=job,
        )

        matches.append(match)

    matches.sort(
        key=lambda match: match["overall_score"],
        reverse=True,
    )

    return matches