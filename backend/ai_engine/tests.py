from types import SimpleNamespace
from unittest.mock import call, patch

from django.test import TestCase

from google.genai import errors as genai_errors

from ai_engine.gemini_extractor import extract_with_gemini
from ai_engine.llm_extractor import normalize_llm_output


class GeminiExtractorTests(TestCase):

	@patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"})
	@patch("ai_engine.gemini_extractor.time.sleep")
	@patch("ai_engine.gemini_extractor.genai.Client")
	def test_retries_transient_error_then_returns_json(
		self,
		mock_client_class,
		mock_sleep,
	):
		mock_client = mock_client_class.return_value
		mock_client.models.generate_content.side_effect = [
			genai_errors.ServerError(
				503,
				{"error": {"status": "UNAVAILABLE", "message": "busy"}},
			),
			SimpleNamespace(text='{"skills": []}'),
		]

		result = extract_with_gemini("Resume text")

		self.assertEqual(result, {"skills": []})
		self.assertEqual(
			mock_client.models.generate_content.call_count,
			2,
		)
		mock_sleep.assert_has_calls([call(1)])

	@patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"})
	@patch("ai_engine.gemini_extractor.time.sleep")
	@patch("ai_engine.gemini_extractor.genai.Client")
	def test_does_not_retry_permanent_api_error(
		self,
		mock_client_class,
		mock_sleep,
	):
		mock_client = mock_client_class.return_value
		error = genai_errors.ClientError(
			401,
			{"error": {"status": "UNAUTHENTICATED", "message": "invalid"}},
		)
		mock_client.models.generate_content.side_effect = error

		with self.assertRaises(genai_errors.ClientError):
			extract_with_gemini("Resume text")

		mock_client.models.generate_content.assert_called_once()
		mock_sleep.assert_not_called()

	@patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"})
	@patch("ai_engine.gemini_extractor.time.sleep")
	@patch("ai_engine.gemini_extractor.genai.Client")
	def test_stops_after_three_transient_attempts(
		self,
		mock_client_class,
		mock_sleep,
	):
		mock_client = mock_client_class.return_value
		mock_client.models.generate_content.side_effect = genai_errors.ServerError(
			503,
			{"error": {"status": "UNAVAILABLE", "message": "busy"}},
		)

		with self.assertRaises(genai_errors.ServerError):
			extract_with_gemini("Resume text")

		self.assertEqual(
			mock_client.models.generate_content.call_count,
			3,
		)
		mock_sleep.assert_has_calls([call(1), call(2)])

	@patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"})
	@patch("ai_engine.gemini_extractor.genai.Client")
	def test_rejects_non_text_gemini_response(self, mock_client_class):
		mock_client = mock_client_class.return_value
		mock_client.models.generate_content.return_value = SimpleNamespace(
			text={"skills": []}
		)

		with self.assertRaises(ValueError):
			extract_with_gemini("Resume text")

	def test_rejects_non_object_normalized_output(self):
		with self.assertRaises(ValueError):
			normalize_llm_output([])
