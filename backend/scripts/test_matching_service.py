from app.models.candidate import Candidate
from app.models.job import Job

from app.services.matching_service import (
    calculate_skill_score,
    calculate_experience_score,
    calculate_match,
    get_experience_status,
    get_match_level,
)
from unittest.mock import patch
from app.services.matching_service import (
    calculate_and_persist_job_matches,
    get_persisted_job_matches,
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

    with patch(
        "app.services.matching_service.calculate_semantic_score",
        return_value=80.0,
    ):
        result = calculate_match(
            candidate=candidate,
            job=job,
        )

    assert result["candidate_id"] == 1
    assert result["job_id"] == 1

    assert result["skill_score"] == 66.67

    assert result["experience_score"] == 100.0

    assert result["semantic_score"] == 80.0

    assert result["overall_score"] == 78.67

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

  

    matches = calculate_and_persist_job_matches(
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

def test_match_level_excellent():
    assert get_match_level(90) == "Excellent Match"


def test_match_level_strong():
    assert get_match_level(75) == "Strong Match"


def test_match_level_moderate():
    assert get_match_level(60) == "Moderate Match"


def test_match_level_weak():
    assert get_match_level(40) == "Weak Match"


def test_experience_status_meets_requirement(db):
    candidate = Candidate(
        full_name="Test Candidate",
        skills=["Python"],
        experience_years=3,
    )

    job = Job(
        title="Software Engineer",
        company="Test Company",
        description="Python developer",
        required_skills="Python",
        minimum_experience=2,
    )

    assert (
        get_experience_status(candidate, job)
        == "Meets requirement"
    )


def test_experience_status_below_requirement(db):
    candidate = Candidate(
        full_name="Test Candidate",
        skills=["Python"],
        experience_years=1,
    )

    job = Job(
        title="Software Engineer",
        company="Test Company",
        description="Python developer",
        required_skills="Python",
        minimum_experience=3,
    )

    assert (
        get_experience_status(candidate, job)
        == "Below requirement"
    )

def test_get_persisted_job_matches_returns_ranked_matches(
    db,
):
    from app.models.candidate import Candidate
    from app.models.job import Job

    candidate_1 = Candidate(
        full_name="Candidate One",
        email="candidate1@example.com",
        skills=[
            "Python",
            "FastAPI",
            "Docker",
        ],
        experience_years=5,
        embedding=[1.0, 0.0, 0.0],
    )

    candidate_2 = Candidate(
        full_name="Candidate Two",
        email="candidate2@example.com",
        skills=[
            "Python",
        ],
        experience_years=1,
        embedding=[0.0, 1.0, 0.0],
    )

    job = Job(
        title="Backend Engineer",
        company="Example Company",
        description="Backend role",
        required_skills=(
            "Python, FastAPI, Docker"
        ),
        minimum_experience=3,
        embedding=[1.0, 0.0, 0.0],
    )

    db.add_all([
        candidate_1,
        candidate_2,
        job,
    ])

    db.commit()

    calculate_and_persist_job_matches(
        db=db,
        job=job,
    )

    matches = get_persisted_job_matches(
        db=db,
        job=job,
    )

    assert len(matches) == 2

    assert (
        matches[0]["overall_score"]
        >= matches[1]["overall_score"]
    )

    assert (
        matches[0]["candidate_id"]
        == candidate_1.id
    )

    assert (
        matches[1]["candidate_id"]
        == candidate_2.id
    )