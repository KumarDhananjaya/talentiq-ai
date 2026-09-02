import pytest

from app.services.embedding_service import (
    generate_embedding,
)


def test_generate_embedding():
    embedding = generate_embedding(
        "Python FastAPI PostgreSQL"
    )

    assert isinstance(
        embedding,
        list,
    )

    assert len(embedding) > 0

    assert all(
        isinstance(value, float)
        for value in embedding
    )


def test_generate_embedding_empty_text():
    with pytest.raises(
        ValueError,
        match="Text cannot be empty",
    ):
        generate_embedding("")