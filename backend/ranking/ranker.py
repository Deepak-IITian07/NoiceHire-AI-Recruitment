
"""
Standalone candidate ranking engine.

This module accepts plain Python dictionaries.
It does not import Django or access the database.
"""

from ranking.score_calculator import calculate_candidate_score
from ranking.classification import classify_candidate
from ranking.explainability import build_explanation


METHODOLOGY_VERSION = "1.0"


def _candidate_id(candidate: dict) -> str:
    identifier = candidate.get("candidate_identifier")

    if identifier and str(identifier).strip().upper() != "UNKNOWN":
        return str(identifier).strip()

    resume_id = candidate.get("resume_id") or candidate.get("id")

    if resume_id is not None:
        return f"RESUME-{resume_id}"

    raise ValueError(
        "Candidate must have a candidate_identifier or resume_id."
    )


def _sort_candidates(results: list) -> list:
    """
    Sort descending by score.
    Unknown scores remain visible at the bottom.
    Ties are resolved alphabetically by candidate identifier.
    """
    return sorted(
        results,
        key=lambda item: (
            item["score"] is None,
            -(item["score"] if item["score"] is not None else 0),
            item["candidate_identifier"].casefold(),
        ),
    )


def rank_candidates(
    candidates: list,
    job_profile: dict,
    method: str = "combined",
) -> list:
    """
    Rank candidates for one job profile.

    Candidate format:
    {
        "candidate_identifier": "CAND-001",
        "candidate_data": {...}
    }

    Job profile format:
    {
        "job_id": "JD1",
        "title": "...",
        "mandatory_criteria": {...},
        "preferred_criteria": {...},
        "scoring_criteria": {...}
    }
    """
    results = []

    for candidate in candidates:
        candidate_data = candidate.get("candidate_data", {})

        score_result = calculate_candidate_score(
            candidate_data=candidate_data,
            job_profile=job_profile,
            method=method,
        )

        explanation = build_explanation(
            candidate_data=candidate_data,
            score_result=score_result,
        )

        results.append({
            "candidate_identifier": _candidate_id(candidate),
            "job_id": job_profile.get("job_id"),
            "job_title": job_profile.get("title"),
            "score": score_result["score"],
            "information_availability_coverage": (
                score_result["information_availability_coverage"]
            ),
            "category_scores": score_result["category_scores"],
            "missing_information": score_result["missing_information"],
            "explanation": explanation,
            "methodology_version": METHODOLOGY_VERSION,
        })

    return _sort_candidates(results)


def rank_for_both_jobs(
    candidates: list,
    jd1: dict,
    jd2: dict,
    method: str = "combined",
    classification_policy: dict | None = None,
) -> dict:
    """
    Produce separate rankings and cross-job classifications.
    """
    jd1_ranking = rank_candidates(candidates, jd1, method)
    jd2_ranking = rank_candidates(candidates, jd2, method)

    jd1_lookup = {
        item["candidate_identifier"]: item
        for item in jd1_ranking
    }

    jd2_lookup = {
        item["candidate_identifier"]: item
        for item in jd2_ranking
    }

    classifications = []

    for candidate in candidates:
        identifier = _candidate_id(candidate)

        first = jd1_lookup[identifier]
        second = jd2_lookup[identifier]

        classification = classify_candidate(
            first,
            second,
            policy=classification_policy,
        )

        classifications.append({
            "candidate_identifier": identifier,
            **classification,
        })

    return {
        "methodology_version": METHODOLOGY_VERSION,
        "matching_method": method,
        "rankings": {
            "JD1": jd1_ranking,
            "JD2": jd2_ranking,
        },
        "classifications": classifications,
    }
