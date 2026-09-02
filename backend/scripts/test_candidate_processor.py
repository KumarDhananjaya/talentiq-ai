from app.schemas.resume import ParsedResume
from app.services.candidate_processor import parsed_resume_to_candidate


def test_parsed_resume_to_candidate():

    parsed_resume = ParsedResume(
        full_name="John Doe",
        email="john@example.com",
        phone="1234567890",
        skills=["Python", "FastAPI", "PostgreSQL"],
        experience=[
            {
                "company": "Google",
                "role": "Software Engineer",
            },
            {
                "company": "Microsoft",
                "role": "Software Engineer Intern",
            },
        ],
        education=[],
    )

    result = parsed_resume_to_candidate(
        parsed_resume=parsed_resume,
        resume_text="John Doe Software Engineer Python FastAPI",
    )

    assert result.full_name == "John Doe"
    assert result.email == "john@example.com"
    assert result.phone == "1234567890"
    assert result.resume_text == (
        "John Doe Software Engineer Python FastAPI"
    )

    assert result.skills == [
        "Python",
        "FastAPI",
        "PostgreSQL",
    ]

    assert len(result.experiences) == 2

    assert result.experiences[0].company == "Google"
    assert result.experiences[0].role == "Software Engineer"

    assert result.experiences[1].company == "Microsoft"
    assert result.experiences[1].role == "Software Engineer Intern"