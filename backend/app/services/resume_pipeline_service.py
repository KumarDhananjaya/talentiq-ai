from pathlib import Path

from app.schemas.resume_extraction import ResumeExtraction
from app.services.llm_resume_parser import (
    extract_resume_with_llm,
)
from app.services.resume_merge_service import (
    merge_resume_results,
)
from app.services.resume_parser import (
    extract_text_from_pdf,
    parse_resume,
)


def process_resume(
    file_path: str | Path,
) -> tuple[str, ResumeExtraction]:
    """
    Run the complete resume processing pipeline.

    PDF
        ↓
    Text extraction
        ↓
    Rule-based parsing
        ↓
    Gemini LLM extraction
        ↓
    Merge results
    """

    # Step 1: Extract raw text
    resume_text = extract_text_from_pdf(
        str(file_path)
    )

    # Step 2: Rule-based extraction
    rule_resume = parse_resume(
        resume_text
    )

    # Step 3: Gemini extraction
    # The LLM parser safely returns None on failure.
    llm_resume = extract_resume_with_llm(
        resume_text
    )

    # Step 4: Merge both extraction results
    merged_resume = merge_resume_results(
        rule_resume=rule_resume,
        llm_resume=llm_resume,
    )

    return resume_text, merged_resume