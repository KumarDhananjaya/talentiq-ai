import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.database import Base
from app.models.candidate import Candidate
from app.models.candidate_experience import CandidateExperience
from app.schemas.candidate import (
    CandidateCreate,
    CandidateExperienceCreate,
)
from app.services.candidate_service import create_candidate
from fastapi import HTTPException
from app.schemas.candidate import (
    CandidateCreate,
    CandidateExperienceCreate,
    CandidateUpdate,
)
from app.services.candidate_service import (
    create_candidate,
    update_candidate,
)



@pytest.fixture
def db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={
            "check_same_thread": False
        },
    )

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


def test_create_candidate(db):

    candidate_data = CandidateCreate(
        full_name="John Doe",
        email="john@example.com",
        phone="1234567890",
        resume_text="John Doe Software Engineer",
        skills=[
            "Python",
            "FastAPI",
            "PostgreSQL",
        ],
        experience_years=2.5,
        experiences=[
            CandidateExperienceCreate(
                company="Google",
                role="Software Engineer",
                start_date="2023-01",
                end_date="2025-06",
                is_current=False,
                description="Backend development",
            )
        ],
    )

    candidate = create_candidate(
        db=db,
        candidate=candidate_data,
    )

    assert candidate.id is not None
    assert candidate.full_name == "John Doe"
    assert candidate.email == "john@example.com"
    assert candidate.phone == "1234567890"
    assert candidate.resume_text == (
        "John Doe Software Engineer"
    )

    assert candidate.experience_years == 2.5

    assert len(candidate.experiences) == 1

    experience = candidate.experiences[0]

    assert experience.company == "Google"
    assert experience.role == "Software Engineer"
    assert experience.start_date == "2023-01"
    assert experience.end_date == "2025-06"
    assert experience.is_current is False
    assert experience.description == (
        "Backend development"
    )

def test_create_candidate_duplicate_email(db):
    
    candidate_data = CandidateCreate(
        full_name="John Doe",
        email="john@example.com",
        phone="1234567890",
        resume_text="Software Engineer",
        skills=["Python"],
        experience_years=2.0,
    )

    # First candidate should be created successfully
    create_candidate(
        db=db,
        candidate=candidate_data,
    )

    # Second candidate with the same email
    # should be rejected
    with pytest.raises(HTTPException) as exc_info:

        create_candidate(
            db=db,
            candidate=candidate_data,
        )

    assert exc_info.value.status_code == 400

    assert exc_info.value.detail == (
        "Candidate with this email already exists"
    )

def test_update_candidate(db):
    
    candidate_data = CandidateCreate(
        full_name="John Doe",
        email="john@example.com",
        phone="1234567890",
        resume_text="Software Engineer",
        skills=["Python"],
        experience_years=2.0,
    )

    candidate = create_candidate(
        db=db,
        candidate=candidate_data,
    )

    update_data = CandidateUpdate(
        full_name="John Updated",
        skills=["Python", "FastAPI"],
        experience_years=3.5,
    )

    updated_candidate = update_candidate(
        db=db,
        candidate_id=candidate.id,
        candidate=update_data,
    )

    assert updated_candidate.id == candidate.id
    assert updated_candidate.full_name == "John Updated"
    assert updated_candidate.email == "john@example.com"
    assert updated_candidate.skills == [
        "Python",
        "FastAPI",
    ]
    assert updated_candidate.experience_years == 3.5


def test_update_candidate_experiences(db):

    candidate_data = CandidateCreate(
        full_name="John Doe",
        email="john@example.com",
        skills=["Python"],
        experiences=[
            CandidateExperienceCreate(
                company="Google",
                role="Software Engineer",
                start_date="2023-01",
                end_date="2025-01",
            )
        ],
    )

    candidate = create_candidate(
        db=db,
        candidate=candidate_data,
    )

    update_data = CandidateUpdate(
        experiences=[
            CandidateExperienceCreate(
                company="Microsoft",
                role="Senior Software Engineer",
                start_date="2025-02",
                end_date=None,
                is_current=True,
                description="Backend development",
            )
        ],
    )

    updated_candidate = update_candidate(
        db=db,
        candidate_id=candidate.id,
        candidate=update_data,
    )

    assert len(updated_candidate.experiences) == 1

    experience = updated_candidate.experiences[0]

    assert experience.company == "Microsoft"
    assert experience.role == "Senior Software Engineer"
    assert experience.start_date == "2025-02"
    assert experience.is_current is True


def test_update_candidate_not_found(db):

    update_data = CandidateUpdate(
        full_name="Updated Name",
    )

    with pytest.raises(HTTPException) as exc_info:

        update_candidate(
            db=db,
            candidate_id=999999,
            candidate=update_data,
        )

    assert exc_info.value.status_code == 404


def test_update_candidate_duplicate_email(db):

    create_candidate(
        db=db,
        candidate=CandidateCreate(
            full_name="Candidate One",
            email="one@example.com",
        ),
    )

    candidate_two = create_candidate(
        db=db,
        candidate=CandidateCreate(
            full_name="Candidate Two",
            email="two@example.com",
        ),
    )

    update_data = CandidateUpdate(
        email="one@example.com",
    )

    with pytest.raises(HTTPException) as exc_info:

        update_candidate(
            db=db,
            candidate_id=candidate_two.id,
            candidate=update_data,
        )

    assert exc_info.value.status_code == 400

    assert exc_info.value.detail == (
        "Candidate with this email already exists"
    )