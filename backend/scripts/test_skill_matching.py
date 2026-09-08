"""
Comprehensive tests for skill normalization, parsing, alias matching,
and overall score calculation.

Tests are self-contained (no database needed) so they run extremely fast.
"""

import pytest

from app.models.candidate import Candidate
from app.models.job import Job
from app.services.matching_service import (
    SKILL_ALIASES,
    normalize_skill,
    parse_skills,
    get_candidate_skills,
    get_job_skills,
    calculate_skill_score,
    calculate_experience_score,
    calculate_match,
    get_match_level,
    get_experience_status,
)
from unittest.mock import patch


# ---------------------------------------------------------------------------
# normalize_skill
# ---------------------------------------------------------------------------

def test_normalize_skill_strips_whitespace():
    assert normalize_skill("  Python  ") == "python"

def test_normalize_skill_lowercases():
    assert normalize_skill("FastAPI") == "fastapi"

def test_normalize_skill_collapses_spaces():
    assert normalize_skill("Machine  Learning") == "machine learning"

def test_normalize_skill_normalizes_hyphens():
    assert normalize_skill("machine-learning") == "machine learning"

def test_normalize_skill_empty():
    assert normalize_skill("") == ""
    assert normalize_skill("   ") == ""

def test_normalize_skill_alias_llms():
    assert normalize_skill("LLMs") == "large language models"

def test_normalize_skill_alias_ml():
    assert normalize_skill("ML") == "machine learning"

def test_normalize_skill_alias_nlp():
    assert normalize_skill("NLP") == "natural language processing"

def test_normalize_skill_no_alias_passthrough():
    assert normalize_skill("Docker") == "docker"
    assert normalize_skill("Python") == "python"
    assert normalize_skill("FastAPI") == "fastapi"


# ---------------------------------------------------------------------------
# parse_skills
# ---------------------------------------------------------------------------

def test_parse_skills_from_list():
    result = parse_skills(["Python", "FastAPI", "Machine Learning"])
    assert "python" in result
    assert "fastapi" in result
    assert "machine learning" in result

def test_parse_skills_from_comma_string():
    result = parse_skills("Python, FastAPI, Machine Learning")
    assert "python" in result
    assert "fastapi" in result
    assert "machine learning" in result

def test_parse_skills_from_list_with_comma_string_items():
    result = parse_skills(["Python, FastAPI", "Machine Learning"])
    assert "python" in result
    assert "fastapi" in result
    assert "machine learning" in result

def test_parse_skills_none():
    assert parse_skills(None) == []

def test_parse_skills_empty_string():
    assert parse_skills("") == []

def test_parse_skills_empty_list():
    assert parse_skills([]) == []

def test_parse_skills_deduplicates():
    result = parse_skills(["Python", "python", "PYTHON"])
    assert len(result) == 1
    assert "python" in result

def test_parse_skills_alias_in_list():
    result = parse_skills(["LLMs", "ML"])
    assert "large language models" in result
    assert "machine learning" in result

def test_parse_skills_never_iterates_chars_of_string():
    result = parse_skills(["Python"])
    assert len(result) == 1
    assert "python" in result

def test_parse_skills_json_string():
    result = parse_skills('["Python", "FastAPI"]')
    assert "python" in result
    assert "fastapi" in result


# ---------------------------------------------------------------------------
# Exact skill matching
# ---------------------------------------------------------------------------

def test_exact_skill_match_100_percent():
    candidate = Candidate(id=1, full_name="A", skills=["Python", "FastAPI"], experience_years=3)
    job = Job(id=1, title="Dev", company="X", description="d", required_skills="Python, FastAPI")
    score, matched, missing = calculate_skill_score(candidate, job)
    assert score == 100.0
    assert "python" in matched
    assert "fastapi" in matched
    assert missing == []

def test_partial_skill_match_60_percent():
    candidate = Candidate(id=1, full_name="A", skills=["Python", "FastAPI", "Machine Learning"], experience_years=3)
    job = Job(id=1, title="Dev", company="X", description="d", required_skills="Python, FastAPI, Machine Learning, Docker, LLMs")
    score, matched, missing = calculate_skill_score(candidate, job)
    assert score == 60.0
    assert "python" in matched
    assert "fastapi" in matched
    assert "machine learning" in matched
    assert len(matched) == 3
    assert "docker" in missing
    assert "large language models" in missing
    assert len(missing) == 2

def test_case_normalization_100_percent():
    candidate = Candidate(id=1, full_name="A", skills=["PYTHON", "FastAPI"], experience_years=3)
    job = Job(id=1, title="Dev", company="X", description="d", required_skills="python, fastapi")
    score, matched, missing = calculate_skill_score(candidate, job)
    assert score == 100.0
    assert missing == []

def test_comma_separated_candidate_skills():
    candidate = Candidate(id=1, full_name="A", skills="Python, FastAPI, Machine Learning", experience_years=3)
    job = Job(id=1, title="Dev", company="X", description="d", required_skills="Python, FastAPI, Machine Learning")
    score, matched, missing = calculate_skill_score(candidate, job)
    assert score == 100.0
    assert missing == []

def test_alias_matching_llms():
    candidate = Candidate(id=1, full_name="A", skills=["LLMs"], experience_years=2)
    job = Job(id=1, title="AI Engineer", company="X", description="d", required_skills="Large Language Models")
    score, matched, missing = calculate_skill_score(candidate, job)
    assert score == 100.0
    assert missing == []

def test_alias_matching_ml():
    candidate = Candidate(id=1, full_name="A", skills=["ML"], experience_years=2)
    job = Job(id=1, title="AI Engineer", company="X", description="d", required_skills="Machine Learning")
    score, matched, missing = calculate_skill_score(candidate, job)
    assert score == 100.0
    assert missing == []

def test_zero_skill_match():
    candidate = Candidate(id=1, full_name="A", skills=["Java", "Spring"], experience_years=2)
    job = Job(id=1, title="AI Engineer", company="X", description="d", required_skills="Python, FastAPI, Machine Learning, LLMs, Docker")
    score, matched, missing = calculate_skill_score(candidate, job)
    assert score == 0.0
    assert matched == []
    assert len(missing) == 5

def test_no_job_skills_returns_100():
    candidate = Candidate(id=1, full_name="A", skills=["Python"], experience_years=2)
    job = Job(id=1, title="Intern", company="X", description="d", required_skills=None)
    score, matched, missing = calculate_skill_score(candidate, job)
    assert score == 100.0
    assert matched == []
    assert missing == []


# ---------------------------------------------------------------------------
# Alex Johnson scenario: 4/5 = 80%
# ---------------------------------------------------------------------------

def test_alex_johnson_skill_match():
    candidate = Candidate(id=1, full_name="Alex Johnson", skills=["Python", "FastAPI", "Machine Learning", "Docker"], experience_years=3)
    job = Job(id=1, title="AI Engineer", company="TechCorp", description="AI engineering role", required_skills="Python, FastAPI, Machine Learning, LLMs, Docker", minimum_experience=2)
    score, matched, missing = calculate_skill_score(candidate, job)
    assert score == 80.0, f"Expected 80.0 but got {score}"
    assert "python" in matched
    assert "fastapi" in matched
    assert "machine learning" in matched
    assert "docker" in matched
    assert "large language models" in missing
    assert len(matched) == 4
    assert len(missing) == 1


# ---------------------------------------------------------------------------
# Sarah Williams scenario: 3/5 = 60%
# ---------------------------------------------------------------------------

def test_sarah_williams_skill_match():
    candidate = Candidate(id=1, full_name="Sarah Williams", skills=["Python", "FastAPI", "NLP", "Machine Learning"], experience_years=4)
    job = Job(id=1, title="AI Engineer", company="TechCorp", description="AI engineering role", required_skills="Python, FastAPI, Machine Learning, LLMs, Docker", minimum_experience=2)
    score, matched, missing = calculate_skill_score(candidate, job)
    assert score == 60.0, f"Expected 60.0 but got {score}"
    assert "python" in matched
    assert "fastapi" in matched
    assert "machine learning" in matched
    assert len(matched) == 3
    assert "large language models" in missing
    assert "docker" in missing
    assert len(missing) == 2


# ---------------------------------------------------------------------------
# missing_skills never includes a matched skill
# ---------------------------------------------------------------------------

def test_missing_skills_never_includes_matched():
    candidate = Candidate(id=1, full_name="A", skills=["Python", "FastAPI", "Machine Learning"], experience_years=3)
    job = Job(id=1, title="Dev", company="X", description="d", required_skills="Python, FastAPI, Machine Learning, Docker")
    _, matched, missing = calculate_skill_score(candidate, job)
    for skill in matched:
        assert skill not in missing, f"Matched skill '{skill}' appears in missing_skills!"


# ---------------------------------------------------------------------------
# Experience scoring
# ---------------------------------------------------------------------------

def test_experience_meets_requirement():
    candidate = Candidate(id=1, full_name="A", skills=[], experience_years=3)
    job = Job(id=1, title="D", company="X", description="d", minimum_experience=2)
    assert calculate_experience_score(candidate, job) == 100.0

def test_experience_below_requirement():
    candidate = Candidate(id=1, full_name="A", skills=[], experience_years=1)
    job = Job(id=1, title="D", company="X", description="d", minimum_experience=2)
    assert calculate_experience_score(candidate, job) == 50.0

def test_experience_no_requirement():
    candidate = Candidate(id=1, full_name="A", skills=[], experience_years=0)
    job = Job(id=1, title="D", company="X", description="d", minimum_experience=None)
    assert calculate_experience_score(candidate, job) == 100.0


# ---------------------------------------------------------------------------
# Overall score calculation
# ---------------------------------------------------------------------------

def test_overall_score_weighted_correctly():
    """
    skill_score=80, experience_score=100, semantic_score=50
    overall = (80*0.4) + (100*0.2) + (50*0.4) = 32+20+20 = 72
    """
    candidate = Candidate(id=1, full_name="Alex", skills=["Python", "FastAPI", "Machine Learning", "Docker"], experience_years=3, embedding=[1.0, 0.0, 0.0])
    job = Job(id=1, title="AI Engineer", company="X", description="d", required_skills="Python, FastAPI, Machine Learning, LLMs, Docker", minimum_experience=2, embedding=[1.0, 0.0, 0.0])
    with patch("app.services.matching_service.calculate_semantic_score", return_value=50.0):
        result = calculate_match(candidate=candidate, job=job)
    assert result["skill_score"] == 80.0
    assert result["experience_score"] == 100.0
    assert result["semantic_score"] == 50.0
    assert result["overall_score"] == 72.0

def test_overall_score_no_double_multiplication():
    candidate = Candidate(id=1, full_name="A", skills=["Python", "FastAPI"], experience_years=5, embedding=[1.0, 0.0, 0.0])
    job = Job(id=1, title="D", company="X", description="d", required_skills="Python, FastAPI", minimum_experience=2, embedding=[1.0, 0.0, 0.0])
    with patch("app.services.matching_service.calculate_semantic_score", return_value=100.0):
        result = calculate_match(candidate=candidate, job=job)
    assert result["overall_score"] == 100.0
    assert result["skill_score"] <= 100.0
    assert result["experience_score"] <= 100.0
    assert result["semantic_score"] <= 100.0


# ---------------------------------------------------------------------------
# Match level thresholds
# ---------------------------------------------------------------------------

def test_match_levels():
    assert get_match_level(90) == "Excellent Match"
    assert get_match_level(85) == "Excellent Match"
    assert get_match_level(84.9) == "Strong Match"
    assert get_match_level(70) == "Strong Match"
    assert get_match_level(69.9) == "Moderate Match"
    assert get_match_level(50) == "Moderate Match"
    assert get_match_level(49.9) == "Weak Match"
    assert get_match_level(0) == "Weak Match"


# ---------------------------------------------------------------------------
# SKILL_ALIASES sanity
# ---------------------------------------------------------------------------

def test_skill_aliases_not_empty():
    assert len(SKILL_ALIASES) > 0

def test_skill_aliases_llm_variants():
    assert SKILL_ALIASES["llm"] == "large language models"
    assert SKILL_ALIASES["llms"] == "large language models"
    assert SKILL_ALIASES["large language model"] == "large language models"
