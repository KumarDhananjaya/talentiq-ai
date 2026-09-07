from sqlalchemy.orm import Session

from app.models.candidate import Candidate


def normalize_skill(
    skill: str,
) -> str:
    """
    Normalize a skill for comparison.
    """

    return skill.strip().lower()


def search_candidates(
    db: Session,
    skills: list[str] | None = None,
    minimum_experience: float | None = None,
) -> list[Candidate]:
    """
    Search candidates using structured filters.

    Currently supports:
    - Required skills
    - Minimum experience
    """

    candidates = (
        db.query(Candidate)
        .all()
    )

    if skills:
        required_skills = {
            normalize_skill(skill)
            for skill in skills
            if skill.strip()
        }

        candidates = [
            candidate
            for candidate in candidates
            if required_skills.issubset(
                {
                    normalize_skill(skill)
                    for skill in (
                        candidate.skills or []
                    )
                }
            )
        ]

    if minimum_experience is not None:
        candidates = [
            candidate
            for candidate in candidates
            if (
                candidate.experience_years
                is not None
                and candidate.experience_years
                >= minimum_experience
            )
        ]

    return candidates