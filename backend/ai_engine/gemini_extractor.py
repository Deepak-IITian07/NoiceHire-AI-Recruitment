
import json
import logging
import os
import time

from google import genai
from google.genai import errors as genai_errors
from google.genai import types

from ai_engine.prompts import SYSTEM_PROMPT, build_extraction_prompt


MODEL_NAME = "gemini-3.5-flash-lite"
MAX_ATTEMPTS = 3
RETRY_BACKOFF_SECONDS = 1

logger = logging.getLogger(__name__)


def _is_retryable_error(error: Exception) -> bool:
    if not isinstance(error, genai_errors.APIError):
        return False

    code = getattr(error, "code", None)
    return code == 429 or 500 <= (code or 0) < 600


def extract_with_gemini(resume_text: str) -> dict:
    """Extract structured candidate information using Gemini."""

    if not isinstance(resume_text, str) or not resume_text.strip():
        raise ValueError("Resume text cannot be empty.")

    if len(resume_text) > 50000:
        raise ValueError("Resume text exceeds the 50000-character limit.")

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    client = genai.Client(api_key=api_key)

    request = {
        "model": MODEL_NAME,
        "contents": build_extraction_prompt(resume_text),
        "config": types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
            temperature=0,
            max_output_tokens=8192,
        ),
    }

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = client.models.generate_content(**request)
            break
        except Exception as error:
            status_code = getattr(error, "code", None)
            status = getattr(error, "status", None)

            if not _is_retryable_error(error) or attempt == MAX_ATTEMPTS:
                logger.error(
                    "Gemini extraction failed: model=%s attempts=%s "
                    "error_type=%s status_code=%s status=%s",
                    MODEL_NAME,
                    attempt,
                    type(error).__name__,
                    status_code,
                    status,
                )
                raise

            delay = RETRY_BACKOFF_SECONDS * 2 ** (attempt - 1)
            logger.warning(
                "Transient Gemini extraction error: model=%s attempt=%s/%s "
                "status_code=%s status=%s retrying_in=%ss",
                MODEL_NAME,
                attempt,
                MAX_ATTEMPTS,
                status_code,
                status,
                delay,
            )
            time.sleep(delay)

    content = response.text

    if not isinstance(content, str) or not content.strip():
        raise ValueError(
            "Gemini returned an empty or non-text response."
        )

    try:
        result = json.loads(content)
    except (TypeError, json.JSONDecodeError) as error:
        raise ValueError("Gemini returned invalid JSON.") from error

    if not isinstance(result, dict):
        raise ValueError("Gemini output must be a JSON object.")

    return result
