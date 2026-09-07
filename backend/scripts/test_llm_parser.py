from unittest.mock import MagicMock, patch

from app.schemas.resume_extraction import ResumeExtraction
from app.services.llm_resume_parser import (
    extract_resume_with_llm,
)


class TestExtractResumeWithLLM:

    @patch(
        "app.services.llm_resume_parser.get_gemini_client"
    )
    def test_empty_string_returns_none(
        self,
        mock_get_client,
    ):
        result = extract_resume_with_llm("")

        assert result is None
        mock_get_client.assert_not_called()

    @patch(
        "app.services.llm_resume_parser.get_gemini_client"
    )
    def test_whitespace_only_returns_none(
        self,
        mock_get_client,
    ):
        result = extract_resume_with_llm("   ")

        assert result is None
        mock_get_client.assert_not_called()

    @patch(
        "app.services.llm_resume_parser.get_gemini_client"
    )
    def test_gemini_failure_returns_none_safely(
        self,
        mock_get_client,
    ):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mock_client.chats.create.side_effect = Exception(
            "Gemini API failure"
        )

        result = extract_resume_with_llm(
            "John Doe\njohn@example.com"
        )

        assert result is None

    @patch(
        "app.services.llm_resume_parser.get_gemini_client"
    )
    def test_valid_resume_text_returns_extraction(
        self,
        mock_get_client,
    ):
        mock_client = MagicMock()
        mock_chat = MagicMock()

        expected_resume = ResumeExtraction(
            name="John Doe",
            email="john@example.com",
            phone="123456789",
            location=None,
            skills=["Python"],
            experience=[],
            education=[],
            projects=[],
            certifications=[],
            languages=[],
        )

        mock_chat.send_message.return_value.parsed = (
            expected_resume
        )

        mock_client.chats.create.return_value = (
            mock_chat
        )

        mock_get_client.return_value = mock_client

        result = extract_resume_with_llm(
            """
            John Doe
            john@example.com
            123456789

            Skills:
            Python
            """
        )

        assert result is not None
        assert result.name == "John Doe"
        assert result.email == "john@example.com"
        assert result.skills == ["Python"]

        mock_get_client.assert_called_once()
        mock_client.chats.create.assert_called_once()
        mock_chat.send_message.assert_called_once()