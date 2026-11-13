
import json
import ollama

from job_profiles.schemas import JobProfileSchema
from job_profiles.prompts import (
    SYSTEM_PROMPT,
    build_jd_extraction_prompt,
)


MODEL_NAME = "llama3.2:latest"

client = ollama.Client(host="http://127.0.0.1:11434", timeout=900.0)


def extract_jd_with_llm(
    jd_text: str,
    job_id: str,
) -> JobProfileSchema:
    """
    Extract and validate a structured job profile using Ollama.
    """

    # 1. Validate input
    if not isinstance(jd_text, str) or not jd_text.strip():
        raise ValueError("Job description cannot be empty.")

    if not isinstance(job_id, str) or not job_id.strip():
        raise ValueError("Job ID cannot be empty.")

    if len(jd_text) > 30000:
        raise ValueError(
            "Job description exceeds the 30000-character limit."
        )

    job_id = job_id.strip()

    # 2. Generate Pydantic JSON schema
    output_schema = JobProfileSchema.model_json_schema()

    # 3. Call Ollama
    response = client.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": build_jd_extraction_prompt(
                    job_id,
                    jd_text,
                ),
            },
        ],
        format=output_schema,
        options={
            "temperature": 0,
        },
    )

    content = response.message.content

    # 4. Parse JSON
    try:
        result = json.loads(content)

    except json.JSONDecodeError as error:
        raise ValueError(
            "LLM returned invalid JSON."
        ) from error

    # 5. Validate with Pydantic
    try:
        profile = JobProfileSchema.model_validate(result)

    except Exception as error:
        raise ValueError(
            f"Job profile validation failed: {error}"
        ) from error

    # 6. Ensure the LLM did not change the supplied job ID
    if profile.job_id != job_id:
        raise ValueError(
            "LLM returned an unexpected job ID."
        )

    return profile
