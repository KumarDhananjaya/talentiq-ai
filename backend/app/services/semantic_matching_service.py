import json
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

    if not candidate.embedding or not job.embedding:
        return 0.0

    try:
        cand_raw = candidate.embedding
        if isinstance(cand_raw, str):
            cand_raw = json.loads(cand_raw)

        job_raw = job.embedding
        if isinstance(job_raw, str):
            job_raw = json.loads(job_raw)

        if not isinstance(cand_raw, (list, tuple)) or not isinstance(job_raw, (list, tuple)):
            return 0.0

        if len(cand_raw) == 0 or len(job_raw) == 0:
            return 0.0

        candidate_embedding = np.array(
            cand_raw,
            dtype=np.float32,
        )

        job_embedding = np.array(
            job_raw,
            dtype=np.float32,
        )

        if candidate_embedding.shape != job_embedding.shape:
            return 0.0

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
    except Exception:
        return 0.0