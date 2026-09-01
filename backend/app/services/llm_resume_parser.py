import logging
from typing import Optional

from pydantic import ValidationError
from google import genai
from google.genai import errors

from app.core.config import settings
from app.schemas.resume_extraction import ResumeExtraction

# Set up standard Python logging
logger = logging.getLogger(__name__)

# Initialize the Gemini client
try:
    client = genai.Client(api_key=settings.gemini_api_key)
except Exception as e:
    logger.error(f"Failed to initialize Gemini Client: {str(e)}")
    client = None


def extract_resume_with_llm(resume_text: str) -> Optional[ResumeExtraction]:
    """
    Extract structured information from resume text using Gemini.
    Safely handles empty inputs, API errors, and invalid responses.
    """
    # 1. Validate empty input
    if not resume_text or not resume_text.strip():
        logger.warning("Empty or whitespace-only resume text provided. Skipping LLM extraction.")
        return None

    clean_text = resume_text.strip()

    # 2. Improve the extraction prompt
    prompt = f"""You are an expert resume parser. Extract structured information from the resume below.

    RULES FOR EXTRACTION:

    1. Personal Information:
       - Extract Name, Email, Phone, and Location.
       - Do not invent missing information; use null when unavailable.
       
    2. Skills:
       - Extract all explicitly mentioned technical and professional skills.
       - Do not infer skills that are not present.

    3. Experience:
       - Extract every work experience entry (Company, Role, Start date, End date, Current status, Description).
       - Do not invent companies, roles, or infer dates.
       - DATE NORMALIZATION RULES:
         * Format dates as YYYY-MM (e.g., "January 2024" -> "2024-01", "Jan 2024" -> "2024-01").
         * If only the year is given, use YYYY (e.g., "2024" -> "2024").
         * Do not invent missing months.
         * If the role is ongoing (e.g., "Present", "Current"), set end_date to null.
       - Only set is_current to true when explicitly indicated by "Present", "Current", or an ongoing role.

    4. Education:
       - Extract Institution, Degree, Field of study, Start year, End year.

    5. Projects:
       - Extract Project name, Description, and explicitly mentioned Technologies.

    6. Certifications:
       - Extract Certification name, Issuer, and Year.

    7. Languages:
       - Extract spoken or programming languages ONLY if explicitly mentioned.

    RESUME TEXT:
    {clean_text}
    """

    # 3. Production-safe API Call and Error Handling
    if not client:
        logger.error("Gemini client is not initialized. Cannot perform extraction.")
        return None

    try:
        chat = client.chats.create(
            model="gemini-3.6-flash",
            config={
                "response_mime_type": "application/json",
                "response_schema": ResumeExtraction,
            },
        )
        
        response = chat.send_message(prompt)
        
        # 4. Return validated parsed output
        if not response.parsed:
            logger.error("LLM extraction failed: No parsed response returned from Gemini.")
            return None

        # Log success securely without dumping the entire Pydantic object/PII
        extracted_name = getattr(response.parsed, 'name', 'Unknown Candidate')
        logger.info(f"Successfully extracted resume data via LLM for: {extracted_name}")
        
        return response.parsed

    except errors.APIError as e:
        logger.error(f"Gemini API Error during resume extraction: {str(e)}")
        return None
    except ValidationError as e:
        logger.error(f"Pydantic Validation Error for LLM output: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during LLM resume extraction: {str(e)}")
        return None