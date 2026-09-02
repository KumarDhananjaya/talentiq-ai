from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache
def get_embedding_model() -> SentenceTransformer:
    """
    Load and cache the embedding model.

    The model is loaded only once during
    the application lifetime.
    """

    return SentenceTransformer(
        MODEL_NAME
    )


def generate_embedding(
    text: str,
) -> list[float]:
    """
    Generate a semantic embedding vector
    for the provided text.
    """

    if not text or not text.strip():
        raise ValueError(
            "Text cannot be empty"
        )

    model = get_embedding_model()

    embedding = model.encode(
        text,
        normalize_embeddings=True,
    )

    return embedding.astype(
        np.float32
    ).tolist()