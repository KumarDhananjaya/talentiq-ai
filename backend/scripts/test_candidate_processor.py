from app.schemas.resume import (
    ExperienceItem,
    ParsedResume,
)
from app.services.candidate_processor import (
    parsed_resume_to_candidate,
)


def test_parsed_resume_to_candidate():

    parsed_resume = ParsedResume(
        full_name="Test Candidate",
        email="test@example.com",
        phone="+61400000000",
        skills=[
            "Python",
            "FastAPI",
            "PostgreSQL",
        ],
        total_experience_years=2.5,
        experience=[
            ExperienceItem(
                role="Software Engineer",
                company="Tech Company",
                duration="2023 - Present",
            ),
            ExperienceItem(
                role="Software Developer",
                company="Startup",
                duration="2021 - 2023",
            ),
        ],
    )

    candidate = parsed_resume_to_candidate(
        parsed_resume=parsed_resume,
        resume_text="Sample resume text",
    )

    assert candidate.full_name == "Test Candidate"
    assert candidate.email == "test@example.com"
    assert candidate.phone == "+61400000000"

    assert candidate.skills == [
        "Python",
        "FastAPI",
        "PostgreSQL",
    ]

    assert candidate.experience_years == 2.5

    assert len(candidate.experiences) == 2

    assert (
        candidate.experiences[0].company
        == "Tech Company"
    )

    assert (
        candidate.experiences[0].role
        == "Software Engineer"
    )