
import os

from ai_engine.gemini_extractor import extract_with_gemini
from ai_engine.llm_extractor import (
    extract_with_llm,
    normalize_llm_output,
)
from resumes.models import CandidateProfile


def process_resume(resume):
    """
    Extract candidate information using the configured LLM provider
    and save it to CandidateProfile.
    """

    if not resume.extracted_text:
        raise ValueError("Resume has no extracted text.")

    provider = os.getenv("RESUME_LLM_PROVIDER", "gemini").strip().lower()

    if provider == "gemini":
        raw_result = extract_with_gemini(resume.extracted_text)

    elif provider == "ollama":
        raw_result = extract_with_llm(resume.extracted_text)

    else:
        raise ValueError(
            f"Unsupported LLM provider: {provider}. "
            "Use 'gemini' or 'ollama'."
        )

    candidate = normalize_llm_output(raw_result)

    CandidateProfile.objects.update_or_create(
        resume=resume,
        defaults={
            "candidate_data": candidate.model_dump(mode="json")
        }
    )

    return candidate
