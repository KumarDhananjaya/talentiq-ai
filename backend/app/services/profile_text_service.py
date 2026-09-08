from app.models.candidate import Candidate
from app.models.job import Job
from app.services.matching_service import parse_skills


def build_candidate_profile(
    candidate: Candidate,
) -> str:
    """
    Build a structured text representation of a candidate
    for semantic embedding.
    """

    skills_list = parse_skills(candidate.skills)
    skills = ", ".join(s.title() if len(s) > 3 else s.upper() for s in skills_list) if skills_list else "None listed"

    experience = (
        f"{candidate.experience_years} years"
        if candidate.experience_years is not None
        else "Not specified"
    )

    sections = [
        "Candidate Profile",
        f"Skills: {skills}",
        f"Experience: {experience}",
    ]

    if candidate.resume_text and candidate.resume_text.strip():
        sections.append(
            f"Professional Experience:\n{candidate.resume_text.strip()}"
        )

    return "\n\n".join(sections)


def build_job_profile(
    job: Job,
) -> str:
    """
    Build a structured text representation of a job
    for semantic embedding.
    """

    skills_list = parse_skills(job.required_skills)
    skills = ", ".join(s.title() if len(s) > 3 else s.upper() for s in skills_list) if skills_list else "None listed"

    experience = (
        f"{job.minimum_experience} years"
        if job.minimum_experience is not None
        else "Not specified"
    )

    sections = [
        "Job Profile",
        f"Role: {job.title}",
        f"Required Skills: {skills}",
        f"Minimum Experience: {experience}",
        f"Description:\n{job.description}",
    ]

    return "\n\n".join(sections)