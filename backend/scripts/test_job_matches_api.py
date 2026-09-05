def test_get_job_matches_api(
    client,
    db,
):
    from app.models.candidate import Candidate
    from app.models.job import Job

    candidate = Candidate(
        full_name="John Doe",
        email="john@example.com",
        skills=[
            "Python",
            "FastAPI",
            "Docker",
        ],
        experience_years=3,
        embedding=[1.0, 0.0, 0.0],

    )

    job = Job(
        title="Backend Engineer",
        company="Example Company",
        description="Backend role",
        required_skills=(
            "Python, FastAPI, Docker"
        ),
        minimum_experience=2,
        embedding=[1.0, 0.0, 0.0],

    )

    db.add_all([
        candidate,
        job,
    ])

    db.commit()

    response = client.get(
        f"/jobs/{job.id}/matches"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["job_id"] == job.id
    assert data["total_matches"] == 1
    assert len(data["matches"]) == 1

    assert (
        data["matches"][0]["candidate_id"]
        == candidate.id
    )

    assert data["matches"][0]["job_id"] == job.id

    assert 0 <= data["matches"][0]["overall_score"] <= 100

    assert 0 <= data["matches"][0]["skill_score"] <= 100

    assert 0 <= data["matches"][0]["experience_score"] <= 100

    assert 0 <= data["matches"][0]["semantic_score"] <= 100

    assert data["matches"][0]["skill_score"] == 100.0

    assert data["matches"][0]["experience_score"] == 100.0

    assert data["matches"][0]["matched_skills"] == [
        "docker",
        "fastapi",
        "python",
    ]

    assert data["matches"][0]["missing_skills"] == []

    assert data["matches"][0]["experience_status"] == (
        "Meets requirement"
    )

    assert data["matches"][0]["match_level"] == (
        "Excellent Match"
    )

    assert data["matches"][0]["explanation"]

def test_get_job_matches_job_not_found(
    client,
):
    response = client.get(
        "/jobs/99999/matches"
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Job not found"
    }

def test_get_job_matches_with_filters(
    client,
    db,
):
    from app.models.candidate import Candidate
    from app.models.job import Job

    candidate = Candidate(
        full_name="Jane Doe",
        email="jane@example.com",
        skills=[
            "Python",
            "FastAPI",
        ],
        experience_years=4,
        embedding=[1.0, 0.0, 0.0],
    )

    job = Job(
        title="Backend Engineer",
        company="Example Company",
        description="Backend role",
        required_skills=(
            "Python, FastAPI"
        ),
        minimum_experience=2,
        embedding=[1.0, 0.0, 0.0],
    )

    db.add_all([
        candidate,
        job,
    ])

    db.commit()

    response = client.get(
        f"/jobs/{job.id}/matches"
        "?min_score=80"
        "&limit=1"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_matches"] == 1

    assert len(data["matches"]) == 1

    assert (
        data["matches"][0]["overall_score"]
        >= 80
    )