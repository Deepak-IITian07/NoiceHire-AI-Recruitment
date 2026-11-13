
ALLOWED_CATEGORIES = {
    "skills",
    "tools",
    "experience",
    "projects",
    "education",
}


def validate_weights(weights: dict) -> bool:
    if not isinstance(weights, dict):
        raise ValueError("Scoring weights must be a dictionary.")

    if set(weights) != ALLOWED_CATEGORIES:
        raise ValueError(
            f"Weights must contain exactly: {sorted(ALLOWED_CATEGORIES)}"
        )

    for category, weight in weights.items():
        if isinstance(weight, bool) or not isinstance(weight, (int, float)):
            raise ValueError(f"Invalid weight for {category}.")

        if weight < 0:
            raise ValueError(f"Negative weight for {category}.")

    if not abs(sum(weights.values()) - 100.0) < 0.000001:
        raise ValueError("Scoring weights must total exactly 100.")

    return True


def get_profile_weights(job_profile) -> dict:
    """
    Accept either:
    - A Django JobProfile object
    - A standalone dictionary containing scoring_criteria
    """
    if isinstance(job_profile, dict):
        weights = job_profile.get("scoring_criteria")
    else:
        weights = getattr(job_profile, "scoring_criteria", None)

    if not isinstance(weights, dict):
        raise ValueError("Job profile has no valid scoring criteria.")

    validate_weights(weights)

    return {
        category: float(weight)
        for category, weight in weights.items()
    }


def criterion_importance_weight(importance: str) -> float:
    """
    Relative weight of an individual JD criterion.
    These are initial engineering defaults, not HR-calibrated values.
    """
    weights = {
        "high": 3.0,
        "medium": 2.0,
        "low": 1.0,
    }

    return weights.get(str(importance).lower(), 1.0)
