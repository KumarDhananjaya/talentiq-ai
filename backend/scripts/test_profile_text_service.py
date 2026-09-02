from app.models.candidate import Candidate
from app.models.job import Job

from app.services.profile_text_service import (
    build_candidate_profile,
    build_job_profile,
)


def test_build_candidate_profile():
    candidate = Candidate(
        full_name="John Doe",
        resume_text="Backend developer building REST APIs.",
        skills=["Python", "FastAPI"],
        experience_years=3,
    )

    profile = build_candidate_profile(candidate)

    assert "Backend developer" in profile
    assert "Python, FastAPI" in profile
    assert "3 years of experience" in profile


def test_build_job_profile():
    job = Job(
        title="Backend Engineer",
        company="Tech Corp",
        description="Build scalable backend APIs.",
        required_skills="Python, FastAPI",
        minimum_experience=2,
    )

    profile = build_job_profile(job)

    assert "Backend Engineer" in profile
    assert "scalable backend APIs" in profile
    assert "Python, FastAPI" in profile
    assert "Minimum experience: 2 years" in profile