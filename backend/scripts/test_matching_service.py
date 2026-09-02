from app.models.candidate import Candidate
from app.models.job import Job

from app.services.matching_service import (
    calculate_match,
)


def test_calculate_match():
    candidate = Candidate(
        id=1,
        full_name="John Doe",
        skills=[
            "Python",
            "FastAPI",
            "PostgreSQL",
        ],
        experience_years=3,
    )

    job = Job(
        id=1,
        title="Backend Engineer",
        company="Example Company",
        description="Backend engineering role",
        required_skills=(
            "Python, FastAPI, Docker"
        ),
        minimum_experience=2,
    )

    result = calculate_match(
        candidate=candidate,
        job=job,
    )

    assert result["candidate_id"] == 1
    assert result["job_id"] == 1

    assert result["skill_score"] == 66.67

    assert result["experience_score"] == 100.0

    assert result["overall_score"] == 76.67

    assert "python" in result["matched_skills"]
    assert "fastapi" in result["matched_skills"]

    assert "docker" in result["missing_skills"]

def test_get_job_matches(
    db,
):
    candidate_one = Candidate(
        full_name="Strong Candidate",
        skills=[
            "Python",
            "FastAPI",
            "PostgreSQL",
            "Docker",
        ],
        experience_years=5,
    )

    candidate_two = Candidate(
        full_name="Partial Candidate",
        skills=[
            "Python",
        ],
        experience_years=1,
    )

    job = Job(
        title="Backend Engineer",
        company="Example Company",
        description="Backend engineering role",
        required_skills=(
            "Python, FastAPI, Docker"
        ),
        minimum_experience=3,
    )

    db.add_all([
        candidate_one,
        candidate_two,
        job,
    ])

    db.commit()

    from app.services.matching_service import (
        get_job_matches,
    )

    matches = get_job_matches(
        db=db,
        job=job,
    )

    assert len(matches) == 2

    assert (
        matches[0]["candidate_id"]
        == candidate_one.id
    )

    assert (
        matches[0]["overall_score"]
        > matches[1]["overall_score"]
    )