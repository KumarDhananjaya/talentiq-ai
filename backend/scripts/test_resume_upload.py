from io import BytesIO

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.database import Base, get_db
from app.models.candidate import Candidate
from app.services import resume_parser
from app.api import candidates


from sqlalchemy.pool import StaticPool

engine = create_engine(
    "sqlite://",
    connect_args={
        "check_same_thread": False
    },
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db):

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)

    app.dependency_overrides.clear()


def test_upload_resume(
    client,
    db,
    monkeypatch,
):
    candidate = Candidate(
        full_name="John Doe",
        email="john@example.com",
    )

    db.add(candidate)
    db.commit()
    db.refresh(candidate)

    def mock_extract_text(file_path):
        return (
            "John Doe\n"
            "john@example.com\n"
            "Software Engineer\n"
            "Python FastAPI PostgreSQL"
        )

    def mock_parse_resume(text):
        return resume_parser.parse_resume(text)

    def mock_llm_parser(text):
        return None

    monkeypatch.setattr(
        candidates,
        "extract_text_from_pdf",
        mock_extract_text,
    )

    monkeypatch.setattr(
        candidates,
        "parse_resume",
        mock_parse_resume,
    )

    monkeypatch.setattr(
        candidates,
        "extract_resume_with_llm",
        mock_llm_parser,
    )

    response = client.post(
        f"/candidates/{candidate.id}/resume",
        files={
            "file": (
                "resume.pdf",
                BytesIO(b"fake pdf content"),
                "application/pdf",
            )
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == (
        "Resume uploaded and analyzed successfully"
    )

    assert data["candidate_id"] == candidate.id

    assert data["original_filename"] == "resume.pdf"

    assert data["file_size"] == len(
        b"fake pdf content"
    )

    assert "parsed_resume" in data

def test_upload_resume_candidate_not_found(
    client,
):
    response = client.post(
        "/candidates/99999/resume",
        files={
            "file": (
                "resume.pdf",
                BytesIO(b"fake pdf content"),
                "application/pdf",
            )
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "Candidate not found"
    )

def test_upload_resume_invalid_file_type(
    client,
    db,
):
    candidate = Candidate(
        full_name="John Doe",
        email="john@example.com",
    )

    db.add(candidate)
    db.commit()
    db.refresh(candidate)

    response = client.post(
        f"/candidates/{candidate.id}/resume",
        files={
            "file": (
                "resume.txt",
                BytesIO(b"not a pdf"),
                "text/plain",
            )
        },
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "Only PDF files are allowed. Received: .txt"
    )

def test_upload_resume_file_too_large(
    client,
    db,
):
    candidate = Candidate(
        full_name="John Doe",
        email="john@example.com",
    )

    db.add(candidate)
    db.commit()
    db.refresh(candidate)

    large_file = b"x" * (5 * 1024 * 1024 + 1)

    response = client.post(
        f"/candidates/{candidate.id}/resume",
        files={
            "file": (
                "large_resume.pdf",
                BytesIO(large_file),
                "application/pdf",
            )
        },
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "Resume must be smaller than 5 MB"
    )

def test_upload_resume_llm_failure_fallback(
    client,
    db,
    monkeypatch,
):
    candidate = Candidate(
        full_name="John Doe",
        email="john@example.com",
    )

    db.add(candidate)
    db.commit()
    db.refresh(candidate)

    def mock_extract_text(file_path):
        return (
            "John Doe\n"
            "john@example.com\n"
            "Software Engineer\n"
            "Python FastAPI PostgreSQL"
        )

    def mock_parse_resume(text):
        return resume_parser.parse_resume(text)

    def mock_llm_parser(text):
        raise Exception("Gemini API failed")

    monkeypatch.setattr(
        candidates,
        "extract_text_from_pdf",
        mock_extract_text,
    )

    monkeypatch.setattr(
        candidates,
        "parse_resume",
        mock_parse_resume,
    )

    monkeypatch.setattr(
        candidates,
        "extract_resume_with_llm",
        mock_llm_parser,
    )

    response = client.post(
        f"/candidates/{candidate.id}/resume",
        files={
            "file": (
                "resume.pdf",
                BytesIO(b"fake pdf content"),
                "application/pdf",
            )
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == (
        "Resume uploaded and analyzed successfully"
    )

    assert data["candidate_id"] == candidate.id

    assert "parsed_resume" in data