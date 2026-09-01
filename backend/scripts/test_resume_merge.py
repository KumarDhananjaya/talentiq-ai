from app.schemas.resume import (
    EducationItem as RuleEducationItem,
    ExperienceItem as RuleExperienceItem,
    ParsedResume,
)

from app.schemas.resume_extraction import (
    EducationItem,
    ExperienceItem,
    ResumeExtraction,
)

from app.services.resume_merge_service import (
    merge_resume_results,
)


def test_successful_rule_and_llm_merge():
    """
    Test merging rule-based and LLM results.
    """

    rule_resume = ParsedResume(
        full_name="John Doe",
        email="john@example.com",
        phone="+61 400 123 456",
        location="Sydney, Australia",
        skills=[
            "Python",
            "FastAPI",
            "Docker",
        ],
        experience=[
            RuleExperienceItem(
                role="Software Engineer",
                company="ABC Technologies",
                duration="Jan 2024 - Present",
            )
        ],
    )

    llm_resume = ResumeExtraction(
        name="John Doe",
        email="john@example.com",
        skills=[
            "Python",
            "FastAPI",
            "PostgreSQL",
            "AWS",
        ],
        experience=[
            ExperienceItem(
                company="ABC Technologies",
                role="Software Engineer",
                start_date="2024-01",
                end_date=None,
                is_current=True,
                description=[
                    "Developed REST APIs.",
                ],
            )
        ],
    )

    result = merge_resume_results(
        rule_resume,
        llm_resume,
    )

    assert result.name == "John Doe"
    assert result.email == "john@example.com"
    assert result.phone == "+61 400 123 456"

    assert "Python" in result.skills
    assert "Docker" in result.skills
    assert "PostgreSQL" in result.skills
    assert "AWS" in result.skills

    assert len(result.experience) == 1
    assert result.experience[0].company == "ABC Technologies"
    assert result.experience[0].role == "Software Engineer"
    assert result.experience[0].start_date == "2024-01"
    assert result.experience[0].is_current is True


def test_llm_failure_uses_rule_based_fallback():
    """
    Test that a valid unified result is returned
    when Gemini extraction fails.
    """

    rule_resume = ParsedResume(
        full_name="Jane Smith",
        email="jane@example.com",
        phone="+61 400 999 888",
        location="Melbourne, Australia",
        skills=[
            "Python",
            "Docker",
        ],
        experience=[
            RuleExperienceItem(
                role="Backend Developer",
                company="Tech Solutions",
                duration="2022 - Present",
            )
        ],
    )

    result = merge_resume_results(
        rule_resume,
        None,
    )

    assert result.name == "Jane Smith"
    assert result.email == "jane@example.com"
    assert result.phone == "+61 400 999 888"
    assert result.location == "Melbourne, Australia"

    assert "Python" in result.skills
    assert "Docker" in result.skills

    assert len(result.experience) == 1
    assert result.experience[0].company == "Tech Solutions"
    assert result.experience[0].role == "Backend Developer"


def test_empty_llm_sections_use_rule_based_fallback():
    """
    Test that rule-based experience and education are used
    when the LLM returns empty sections.
    """

    rule_resume = ParsedResume(
        full_name="Alex Brown",
        email="alex@example.com",
        skills=[
            "Java",
            "Spring Boot",
        ],
        experience=[
            RuleExperienceItem(
                role="Java Developer",
                company="Example Corp",
                duration="2021 - 2024",
            )
        ],
        education=[
            RuleEducationItem(
                institution="University of Sydney",
                degree="Master of Computer Science",
            )
        ],
    )

    llm_resume = ResumeExtraction(
        name="Alex Brown",
        skills=[
            "Java",
            "AWS",
        ],
        experience=[],
        education=[],
    )

    result = merge_resume_results(
        rule_resume,
        llm_resume,
    )

    assert result.name == "Alex Brown"

    assert "Java" in result.skills
    assert "Spring Boot" in result.skills
    assert "AWS" in result.skills

    assert len(result.experience) == 1
    assert result.experience[0].company == "Example Corp"
    assert result.experience[0].role == "Java Developer"

    assert len(result.education) == 1
    assert (
        result.education[0].institution
        == "University of Sydney"
    )


if __name__ == "__main__":
    test_successful_rule_and_llm_merge()
    test_llm_failure_uses_rule_based_fallback()
    test_empty_llm_sections_use_rule_based_fallback()

    print("All resume merge tests passed.")