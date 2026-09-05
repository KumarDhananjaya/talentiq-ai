def test_get_job_matches_api(
    client,
    db,
):
    from app.models.candidate import Candidate
    from app.models.job import Job
    from app.services.matching_service import (
        calculate_and_persist_job_matches,
    )

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

    calculate_and_persist_job_matches(
        db=db,
        job=job,
    )

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
    from app.services.matching_service import (
        calculate_and_persist_job_matches,
    )

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

    calculate_and_persist_job_matches(
        db=db,
        job=job,
    )

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

def test_recalculate_job_matches_api(
    client,
    db,
):
    from app.models.candidate import Candidate
    from app.models.job import Job

    candidate = Candidate(
        full_name="Recalculate Candidate",
        email="recalculate@example.com",
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

    response = client.post(
        f"/jobs/{job.id}/matches/recalculate"
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

    assert (
        data["matches"][0]["job_id"]
        == job.id
    )

    assert data["matches"][0]["skill_score"] == 100.0

    assert data["matches"][0]["experience_score"] == 100.0

    assert data["matches"][0]["matched_skills"] == [
        "docker",
        "fastapi",
        "python",
    ]

    assert data["matches"][0]["missing_skills"] == []


def test_recalculate_job_matches_job_not_found(
    client,
):
    response = client.post(
        "/jobs/99999/matches/recalculate"
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Job not found"
    }


def test_recalculate_job_matches_updates_existing_match(
    client,
    db,
):
    from app.models.candidate import Candidate
    from app.models.job import Job
    from app.models.candidate_job_match import (
        CandidateJobMatch,
    )

    candidate = Candidate(
        full_name="Update Candidate",
        email="update@example.com",
        skills=[
            "Python",
            "FastAPI",
        ],
        experience_years=3,
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

    first_response = client.post(
        f"/jobs/{job.id}/matches/recalculate"
    )

    assert first_response.status_code == 200

    first_data = first_response.json()

    assert first_data["total_matches"] == 1

    first_match_id = (
        db.query(CandidateJobMatch)
        .filter(
            CandidateJobMatch.candidate_id
            == candidate.id,
            CandidateJobMatch.job_id
            == job.id,
        )
        .first()
        .id
    )

    second_response = client.post(
        f"/jobs/{job.id}/matches/recalculate"
    )

    assert second_response.status_code == 200

    second_data = second_response.json()

    assert second_data["total_matches"] == 1

    matches = (
        db.query(CandidateJobMatch)
        .filter(
            CandidateJobMatch.candidate_id
            == candidate.id,
            CandidateJobMatch.job_id
            == job.id,
        )
        .all()
    )

    assert len(matches) == 1

    assert matches[0].id == first_match_id

def test_update_job(
    client,
    db,
):
    from app.models.job import Job

    job = Job(
        title="Backend Engineer",
        company="Example Company",
        description="Backend role",
        required_skills="Python, FastAPI",
        minimum_experience=2,
        embedding=[1.0, 0.0, 0.0],
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    response = client.put(
        f"/jobs/{job.id}",
        json={
            "title": "Senior Backend Engineer",
            "description": "Senior backend role",
            "required_skills": "Python, FastAPI, Docker",
            "minimum_experience": 4,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == job.id
    assert data["title"] == "Senior Backend Engineer"
    assert data["company"] == "Example Company"
    assert data["description"] == "Senior backend role"
    assert data["required_skills"] == (
        "Python, FastAPI, Docker"
    )
    assert data["minimum_experience"] == 4


def test_update_job_partial_update(
    client,
    db,
):
    from app.models.job import Job

    job = Job(
        title="Backend Engineer",
        company="Example Company",
        description="Backend role",
        required_skills="Python",
        minimum_experience=2,
        embedding=[1.0, 0.0, 0.0],
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    response = client.put(
        f"/jobs/{job.id}",
        json={
            "title": "Senior Backend Engineer",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == "Senior Backend Engineer"
    assert data["company"] == "Example Company"
    assert data["description"] == "Backend role"
    assert data["required_skills"] == "Python"
    assert data["minimum_experience"] == 2


def test_update_job_not_found(
    client,
):
    response = client.put(
        "/jobs/99999",
        json={
            "title": "Updated Job",
        },
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Job not found"
    }