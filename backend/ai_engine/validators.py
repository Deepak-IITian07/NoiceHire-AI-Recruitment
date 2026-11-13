
from pydantic import ValidationError
from ai_engine.schemas import CandidateProfile


def validate_candidate(data: dict) -> CandidateProfile:
    try:
        return CandidateProfile.model_validate(data)

    except ValidationError as error:
        raise ValueError(
            f"Candidate validation failed: {error}"
        ) from error
