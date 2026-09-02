from app.models.candidate import Candidate
from app.models.job import Job


def build_candidate_profile(
    candidate: Candidate,
) -> str:
    """
    Build a text representation of a candidate
    for semantic embedding.
    """

    skills = ", ".join(candidate.skills or [])

    experience = (
        f"{candidate.experience_years} years of experience"
        if candidate.experience_years is not None
        else "Experience not specified"
    )

    return " ".join(
        [
            candidate.resume_text or "",
            f"Skills: {skills}",
            experience,
        ]
    ).strip()


def build_job_profile(
    job: Job,
) -> str:
    """
    Build a text representation of a job
    for semantic embedding.
    """

    skills = job.required_skills or ""

    experience = (
        f"Minimum experience: {job.minimum_experience} years"
        if job.minimum_experience is not None
        else "Experience requirement not specified"
    )

    return " ".join(
        [
            job.title,
            job.description,
            f"Required skills: {skills}",
            experience,
        ]
    ).strip()