import unittest
from unittest.mock import patch, MagicMock
from app.schemas.resume_extraction import ResumeExtraction
from app.services.llm_resume_parser import extract_resume_with_llm

class TestLLMResumeParser(unittest.TestCase):

    @patch("app.services.llm_resume_parser.client")
    def test_valid_resume_text_returns_extraction(self, mock_client):
        """Test 1: Valid resume text should return a valid ResumeExtraction."""
        
        # Setup mock behavior
        mock_chat = MagicMock()
        mock_response = MagicMock()
        
        # Create a mock validated Pydantic object simulating the SDK's behavior
        expected_extraction = ResumeExtraction(
            name="John Doe", 
            email="john@example.com"
        )
        mock_response.parsed = expected_extraction
        
        mock_chat.send_message.return_value = mock_response
        mock_client.chats.create.return_value = mock_chat

        resume_text = "John Doe. Software Engineer. Email: john@example.com."
        result = extract_resume_with_llm(resume_text)

        self.assertIsInstance(result, ResumeExtraction)
        self.assertEqual(result.name, "John Doe")
        self.assertEqual(result.email, "john@example.com")
        mock_client.chats.create.assert_called_once()

    @patch("app.services.llm_resume_parser.client")
    def test_empty_string_returns_none(self, mock_client):
        """Test 2: Empty string should return None without calling API."""
        result = extract_resume_with_llm("")
        
        self.assertIsNone(result)
        mock_client.chats.create.assert_not_called()

    @patch("app.services.llm_resume_parser.client")
    def test_whitespace_only_returns_none(self, mock_client):
        """Test 3: Whitespace-only input should return None without calling API."""
        result = extract_resume_with_llm("   \n   \t  ")
        
        self.assertIsNone(result)
        mock_client.chats.create.assert_not_called()

    @patch("app.services.llm_resume_parser.client")
    def test_gemini_failure_returns_none_safely(self, mock_client):
        """Test 4: Unexpected Gemini failure should not crash the application."""
        
        # Setup mock to raise a generic exception
        mock_client.chats.create.side_effect = Exception("Simulated API Down or Quota Exceeded")
        
        resume_text = "Valid resume text but API is broken."
        
        # This should safely catch the exception and return None, not crash
        result = extract_resume_with_llm(resume_text)
        
        self.assertIsNone(result)
        mock_client.chats.create.assert_called_once()


if __name__ == "__main__":
    unittest.main()