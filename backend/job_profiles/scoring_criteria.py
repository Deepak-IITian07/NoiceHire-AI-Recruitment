
SCORING_TEMPLATES = {
    "JD1": {
        "skills": 35,
        "tools": 20,
        "experience": 25,
        "projects": 15,
        "education": 5,
    },

    "JD2": {
        "skills": 35,
        "tools": 20,
        "experience": 15,
        "projects": 25,
        "education": 5,
    },
}


def validate_scoring_weights(weights: dict) -> bool:
    """Validate scoring weights."""

    if not isinstance(weights, dict) or not weights:
        raise ValueError("Scoring weights must be a non-empty dictionary.")

    allowed = {"skills", "tools", "experience", "projects", "education"}

    if set(weights) != allowed:
        raise ValueError("Scoring categories are missing or invalid.")

    for category, weight in weights.items():
        if (
            isinstance(weight, bool)
            or not isinstance(weight, (int, float))
            or weight < 0
        ):
            raise ValueError(f"Invalid weight for {category}.")

    if sum(weights.values()) != 100:
        raise ValueError("Scoring weights must total exactly 100.")

    return True


def get_scoring_criteria(job_id: str) -> dict:
    """Get validated scoring configuration for a job."""

    if job_id not in SCORING_TEMPLATES:
        raise ValueError(f"No scoring template found for {job_id}.")

    weights = SCORING_TEMPLATES[job_id].copy()
    validate_scoring_weights(weights)

    return weights
