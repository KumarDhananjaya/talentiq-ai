from unittest.mock import MagicMock

from app.schemas.resume_extraction import ResumeExtraction
from app.schemas.resume import ParsedResume
from app.services.candidate_processor import (
    parsed_resume_to_candidate,
    resume_extraction_to_candidate,
)


def test_parsed_resume_to_candidate_includes_experience_years():
    parsed_resume = ParsedResume(
        full_name="John Doe",
        email="john@example.com",
        phone="123456789",
        skills=["Python"],
        total_experience_years=4.5,
        experience=[],
    )

    candidate = parsed_resume_to_candidate(
        parsed_resume=parsed_resume,
        resume_text="John Doe resume",
    )

    assert candidate.full_name == "John Doe"
    assert candidate.email == "john@example.com"
    assert candidate.phone == "123456789"
    assert candidate.skills == ["Python"]
    assert candidate.experience_years == 4.5
    assert candidate.experiences == []


def test_resume_extraction_to_candidate_includes_experience_years():
    resume = MagicMock(
        spec=ResumeExtraction
    )

    resume.name = "John Doe"
    resume.email = "john@example.com"
    resume.phone = "123456789"
    resume.skills = ["Python"]
    resume.experience = []

    candidate = resume_extraction_to_candidate(
        resume=resume,
        resume_text="John Doe resume",
        experience_years=4.5,
    )

    assert candidate.full_name == "John Doe"
    assert candidate.email == "john@example.com"
    assert candidate.phone == "123456789"
    assert candidate.skills == ["Python"]
    assert candidate.experience_years == 4.5
    assert candidate.experiences == []