import numpy as np

from app.models.candidate import Candidate
from app.models.job import Job


def calculate_semantic_score(
    candidate: Candidate,
    job: Job,
) -> float:
    """
    Calculate semantic similarity using
    persisted candidate and job embeddings.

    Returns a score between 0 and 100.
    """

    if not candidate.embedding:
        return 0.0

    if not job.embedding:
        return 0.0

    candidate_embedding = np.array(
        candidate.embedding,
        dtype=np.float32,
    )

    job_embedding = np.array(
        job.embedding,
        dtype=np.float32,
    )

    similarity = np.dot(
        candidate_embedding,
        job_embedding,
    )

    similarity = max(
        0.0,
        min(1.0, float(similarity)),
    )

    return round(
        similarity * 100,
        2,
    )