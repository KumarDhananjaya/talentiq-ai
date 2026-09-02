from app.models.candidate import Candidate
from app.models.job import Job
from app.services.semantic_matching_service import (
    calculate_semantic_score,
)


def test_calculate_semantic_score():
    candidate = Candidate(
        id=1,
        full_name="John Doe",
        embedding=[1.0, 0.0, 0.0],
    )

    job = Job(
        id=1,
        title="Backend Engineer",
        company="Example",
        description="Backend role",
        embedding=[1.0, 0.0, 0.0],
    )

    score = calculate_semantic_score(
        candidate,
        job,
    )

    assert score == 100.0

def test_calculate_semantic_score_without_embedding():
    candidate = Candidate(
        id=1,
        full_name="John Doe",
    )

    job = Job(
        id=1,
        title="Backend Engineer",
        company="Example",
        description="Backend role",
    )

    score = calculate_semantic_score(
        candidate,
        job,
    )

    assert score == 0.0