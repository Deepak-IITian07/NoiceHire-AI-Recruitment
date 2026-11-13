
"""
Candidate classification.

Thresholds must be calibrated using reviewed candidate assessments.
Until then, the default policy deliberately avoids automatic decisions.
"""


DEFAULT_CLASSIFICATION_POLICY = {
    "minimum_score": None,
    "minimum_score_margin": None,
    "minimum_information_availability_coverage": None,
}


def classify_candidate(
    jd1_result: dict,
    jd2_result: dict,
    policy: dict | None = None,
) -> dict:
    policy = policy or DEFAULT_CLASSIFICATION_POLICY

    required = {
        "minimum_score",
        "minimum_information_availability_coverage",
        "minimum_score_margin",
    }

    if set(policy) != required:
        raise ValueError(
            f"Policy must contain exactly: {sorted(required)}"
        )

    jd1_score = jd1_result.get("score")
    jd2_score = jd2_result.get("score")

    jd1_coverage = jd1_result.get("information_availability_coverage", 0)
    jd2_coverage = jd2_result.get("information_availability_coverage", 0)

    if jd1_score is None or jd2_score is None:
        return {
            "classification": "NEITHER_UNCERTAIN",
            "reason": "Insufficient information to compare both positions.",
        }

    # Thresholds must be explicitly calibrated before classification.
    if any(policy[key] is None for key in required):
        return {
            "classification": "NEITHER_UNCERTAIN",
            "reason": "Classification thresholds have not been calibrated.",
            "score_difference": round(abs(jd1_score - jd2_score), 2),
        }

    minimum_score = policy["minimum_score"]
    minimum_coverage = policy["minimum_information_availability_coverage"]
    minimum_margin = policy["minimum_score_margin"]

    if not 0 <= minimum_score <= 100:
        raise ValueError("Minimum score must be between 0 and 100.")

    if not 0 <= minimum_coverage <= 100:
        raise ValueError("Minimum evidence coverage must be between 0 and 100.")

    if not 0 <= minimum_margin <= 100:
        raise ValueError("Minimum score margin must be between 0 and 100.")

    jd1_eligible = (
        jd1_score >= minimum_score
        and jd1_coverage >= minimum_coverage
    )

    jd2_eligible = (
        jd2_score >= minimum_score
        and jd2_coverage >= minimum_coverage
    )

    difference = abs(jd1_score - jd2_score)

    if jd1_eligible and jd2_eligible:
        if difference <= minimum_margin:
            classification = "BOTH"
            reason = "Both positions meet the calibrated criteria."
        elif jd1_score > jd2_score:
            classification = "JD1_STRONGER"
            reason = "JD1 has the stronger calibrated score."
        else:
            classification = "JD2_STRONGER"
            reason = "JD2 has the stronger calibrated score."

    elif jd1_eligible:
        classification = "JD1_STRONGER"
        reason = "Only JD1 meets the calibrated criteria."

    elif jd2_eligible:
        classification = "JD2_STRONGER"
        reason = "Only JD2 meets the calibrated criteria."

    else:
        classification = "NEITHER_UNCERTAIN"
        reason = "Neither position meets the calibrated criteria."

    return {
        "classification": classification,
        "reason": reason,
        "score_difference": round(difference, 2),
    }
