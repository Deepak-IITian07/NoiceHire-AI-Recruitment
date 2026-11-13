
from django.db import transaction

from job_profiles.models import JobProfile
from job_profiles.jd_extractor import extract_jd_with_llm
from job_profiles.synonyms import SKILL_SYNONYMS
from job_profiles.scoring_criteria import get_scoring_criteria


@transaction.atomic
def process_job_description(job_id: str, jd_text: str):
    """
    Extract, validate and store a job description.

    Reprocessing an existing job_id updates its profile
    instead of creating a duplicate.
    """

    if not job_id or not job_id.strip():
        raise ValueError("Job ID cannot be empty.")

    if not jd_text or not jd_text.strip():
        raise ValueError("Job description cannot be empty.")

    job_id = job_id.strip()

    # 1. Extract and validate using LLM + Pydantic
    profile = extract_jd_with_llm(
        jd_text=jd_text,
        job_id=job_id,
    )

    # 2. Get default scoring configuration
    scoring = get_scoring_criteria(job_id)

    # 3. Convert Pydantic object to dictionary
    profile_data = profile.model_dump(mode="json")

    # 4. Store synonyms and scoring separately
    profile_data["synonyms"] = SKILL_SYNONYMS
    profile_data["scoring_criteria"] = scoring

    # 5. Persist profile
    job_profile, created = JobProfile.objects.update_or_create(
        job_id=job_id,
        defaults={
            "title": profile.title,
            "original_description": jd_text,
            "role_summary": profile.role_summary,
            "mandatory_criteria": profile_data["mandatory_criteria"],
            "preferred_criteria": profile_data["preferred_criteria"],
            "responsibilities": profile_data["responsibilities"],
            "synonyms": profile_data["synonyms"],
            "scoring_criteria": profile_data["scoring_criteria"],
        },
    )

    return job_profile, created
