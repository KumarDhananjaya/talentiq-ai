from app.models.job import Job
from app.services.embedding_service import generate_embedding
from app.services.profile_text_service import build_job_profile


def test_job_profile_embedding():
    job = Job(
        id=1,
        title="Backend Engineer",
        company="Example Company",
        description="Build scalable backend APIs.",
        required_skills="Python, FastAPI, PostgreSQL",
        minimum_experience=2,
    )

    profile = build_job_profile(job)
    embedding = generate_embedding(profile)

    assert profile
    assert isinstance(embedding, list)
    assert len(embedding) == 384
    assert all(isinstance(value, float) for value in embedding)