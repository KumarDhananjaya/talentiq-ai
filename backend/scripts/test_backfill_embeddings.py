from unittest.mock import patch

from app.models.candidate import Candidate
from app.models.job import Job

from scripts.backfill_embeddings import (
    backfill_candidate_embeddings,
    backfill_job_embeddings,
)


def test_backfill_candidate_embedding(db):
    candidate = Candidate(
        full_name="John Doe",
        email="john@example.com",
        skills=["Python"],
        experience_years=2,
        embedding=None,
    )

    db.add(candidate)
    db.commit()

    fake_embedding = [
        0.1,
        0.2,
        0.3,
    ]

    with patch(
        "scripts.backfill_embeddings.generate_embedding",
        return_value=fake_embedding,
    ):
        backfill_candidate_embeddings(db)

    db.refresh(candidate)

    assert candidate.embedding == fake_embedding


def test_existing_candidate_embedding_not_overwritten(
    db,
):
    existing_embedding = [
        0.9,
        0.8,
        0.7,
    ]

    candidate = Candidate(
        full_name="Jane Doe",
        email="jane@example.com",
        skills=["FastAPI"],
        experience_years=3,
        embedding=existing_embedding,
    )

    db.add(candidate)
    db.commit()

    with patch(
        "scripts.backfill_embeddings.generate_embedding",
    ) as mock_generate_embedding:

        backfill_candidate_embeddings(db)

    db.refresh(candidate)

    assert candidate.embedding == existing_embedding

    mock_generate_embedding.assert_not_called()


def test_backfill_job_embedding(db):
    job = Job(
        title="Backend Engineer",
        company="Example Company",
        description="Build backend APIs",
        required_skills="Python, FastAPI",
        minimum_experience=2,
        embedding=None,
    )

    db.add(job)
    db.commit()

    fake_embedding = [
        0.1,
        0.2,
        0.3,
    ]

    with patch(
        "scripts.backfill_embeddings.generate_embedding",
        return_value=fake_embedding,
    ):
        backfill_job_embeddings(db)

    db.refresh(job)

    assert job.embedding == fake_embedding


def test_existing_job_embedding_not_overwritten(
    db,
):
    existing_embedding = [
        0.9,
        0.8,
        0.7,
    ]

    job = Job(
        title="Existing Engineer",
        company="Example Company",
        description="Existing job",
        embedding=existing_embedding,
    )

    db.add(job)
    db.commit()

    with patch(
        "scripts.backfill_embeddings.generate_embedding",
    ) as mock_generate_embedding:

        backfill_job_embeddings(db)

    db.refresh(job)

    assert job.embedding == existing_embedding

    mock_generate_embedding.assert_not_called()