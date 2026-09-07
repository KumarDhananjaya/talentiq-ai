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
    query = db.query(Candidate)

    if minimum_experience is not None:
        query = query.filter(
            Candidate.experience_years.is_not(None),
            Candidate.experience_years >= minimum_experience,
        )

    candidates = query.all()

    if skills:
        required_skills = {
            normalize_skill(skill) for skill in skills if skill.strip()
        }
        candidates = [
            c for c in candidates
            if required_skills.issubset(
                {normalize_skill(s) for s in (c.skills or [])}
            )
        ]

    return candidates