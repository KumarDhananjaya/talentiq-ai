import json
import logging
import re
from typing import Any
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

SKILL_ALIASES: dict[str, str] = {
    # Large Language Models
    "llm": "large language models",
    "llms": "large language models",
    "large language model": "large language models",
    "large language models": "large language models",

    # Machine Learning & AI
    "ml": "machine learning",
    "machine-learning": "machine learning",
    "machine learning": "machine learning",
    "ai": "artificial intelligence",
    "artificial intelligence": "artificial intelligence",
    "nlp": "natural language processing",
    "natural language processing": "natural language processing",
    "deep learning": "deep learning",
    "deep-learning": "deep learning",

    # JavaScript / TypeScript / Frontend
    "nodejs": "node.js",
    "node": "node.js",
    "node.js": "node.js",
    "react.js": "react",
    "reactjs": "react",
    "react": "react",
    "vue.js": "vue",
    "vuejs": "vue",
    "vue": "vue",
    "ts": "typescript",
    "typescript": "typescript",
    "js": "javascript",
    "javascript": "javascript",

    # Databases
    "postgres": "postgresql",
    "postgre sql": "postgresql",
    "postgresql": "postgresql",
    "mongo": "mongodb",
    "mongodb": "mongodb",

    # Cloud & DevOps
    "golang": "go",
    "k8s": "kubernetes",
    "kubernetes": "kubernetes",
    "aws": "amazon web services",
    "amazon web services": "amazon web services",
    "gcp": "google cloud platform",
    "google cloud platform": "google cloud platform",
}


def normalize_skill(skill: str) -> str:
    """
    Normalize a skill for comparison:
    1. Remove leading/trailing whitespace.
    2. Convert to lowercase.
    3. Normalize repeated whitespace to a single space.
    4. Normalize hyphens where appropriate.
    5. Map through SKILL_ALIASES.
    """
    if not skill:
        return ""

    s = str(skill).strip().lower()
    if not s:
        return ""

    s = re.sub(r"\s+", " ", s)

    if s in SKILL_ALIASES:
        return SKILL_ALIASES[s]

    if "-" in s:
        hyphen_normalized = re.sub(r"\s*-\s*", " ", s).strip()
        if hyphen_normalized in SKILL_ALIASES:
            return SKILL_ALIASES[hyphen_normalized]
        s = hyphen_normalized

    return SKILL_ALIASES.get(s, s)


def parse_skills(value: Any) -> list[str]:
    """
    Safely parse skills from any input format (str, list, set, JSON, dict).
    Never treats a skill string as an iterable of individual characters.
    Returns a clean list of normalized, deduplicated skills.
    """
    if value is None:
        return []

    raw_items: list[str] = []

    if isinstance(value, str):
        v = value.strip()
        if not v:
            return []
        if (v.startswith("[") and v.endswith("]")) or (v.startswith("{") and v.endswith("}")):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, (list, tuple, set)):
                    return parse_skills(parsed)
                elif isinstance(parsed, dict):
                    return parse_skills(list(parsed.keys()))
            except Exception:
                pass

        parts = re.split(r"[,;\n\r|]+", v)
        raw_items.extend(parts)

    elif isinstance(value, (list, tuple, set)):
        for item in value:
            if item is None:
                continue
            if isinstance(item, str):
                parts = re.split(r"[,;\n\r|]+", item.strip())
                raw_items.extend(parts)
            elif isinstance(item, (list, tuple, set)):
                raw_items.extend(parse_skills(item))
            else:
                raw_items.append(str(item))

    elif isinstance(value, dict):
        return parse_skills(list(value.keys()))
    else:
        raw_items.append(str(value))

    normalized_list: list[str] = []
    seen: set[str] = set()

    for item in raw_items:
        norm = normalize_skill(item)
        if norm and norm not in seen:
            seen.add(norm)
            normalized_list.append(norm)

    return normalized_list


def get_candidate_skills(
    candidate: Candidate,
) -> set[str]:
    """
    Extract and normalize candidate skills into a clean set.
    """
    return set(parse_skills(candidate.skills))


def get_job_skills(
    job: Job,
) -> set[str]:
    """
    Extract and normalize job required skills into a clean set.
    """
    return set(parse_skills(job.required_skills))


def calculate_skill_score(
    candidate: Candidate,
    job: Job,
) -> tuple[float, list[str], list[str]]:
    """
    Calculate skill match percentage.

    Returns:
        skill_score (0.0 to 100.0)
        matched_skills (sorted list)
        missing_skills (sorted list)
    """
    candidate_skills = get_candidate_skills(candidate)
    job_skills = get_job_skills(job)

    if not job_skills:
        return (
            100.0,
            [],
            [],
        )

    matched_skills = candidate_skills & job_skills
    missing_skills = job_skills - candidate_skills

    skill_score = (len(matched_skills) / len(job_skills)) * 100.0

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
    minimum_experience: int | None = None,
    overall_score: float | None = None,
) -> str:
    """
    Generate a human-readable explanation
    for the candidate-job match.
    """

    explanation_parts = [
        f"Skill match score: {skill_score:.0f}%.",
    ]

    if matched_skills:
        explanation_parts.append(
            "Matched skills: "
            + ", ".join(s.title() if len(s) > 3 else s.upper() for s in matched_skills)
            + "."
        )

    if missing_skills:
        explanation_parts.append(
            "Missing skills: "
            + ", ".join(s.title() if len(s) > 3 else s.upper() for s in missing_skills)
            + "."
        )

    if minimum_experience is not None:
        if experience_status == "Meets requirement":
            explanation_parts.append(
                f"Experience: Meets the minimum requirement of {minimum_experience} years."
            )
        else:
            explanation_parts.append(
                f"Experience: Below the minimum requirement of {minimum_experience} years."
            )
    else:
        explanation_parts.append(
            f"Experience: {experience_status}."
        )

    explanation_parts.append(
        f"Semantic similarity: {semantic_score:.0f}%."
    )

    if overall_score is not None:
        explanation_parts.append(
            f"Overall match: {overall_score:.0f}%."
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
        minimum_experience=job.minimum_experience,
        overall_score=overall_score,
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
