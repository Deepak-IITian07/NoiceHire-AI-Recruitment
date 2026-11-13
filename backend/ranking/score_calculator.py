from ranking.semantic_matching import (
    build_candidate_corpus,
    build_candidate_evidence,
    match_criterion,
)
from ranking.scoring import (
    get_profile_weights,
    criterion_importance_weight,
)

def _get_profile_value(profile, field):
    if isinstance(profile, dict):
        return profile.get(field)
    return getattr(profile, field, None)

def _deduplicate_criteria(mandatory, preferred):
    """
    Avoid counting the same criterion twice.
    Mandatory criteria take precedence over preferred duplicates.
    """
    combined = {}
    ordered = []

    for source, groups in [
        ("mandatory", mandatory),
        ("preferred", preferred),
    ]:
        if not isinstance(groups, dict):
            continue

        for category, criteria in groups.items():
            if not isinstance(criteria, list):
                continue

            for criterion in criteria:
                if not isinstance(criterion, dict):
                    continue

                name = str(criterion.get("name", "")).strip()

                if not name or name.lower() == "none specified":
                    continue

                key = (category, " ".join(name.lower().split()))

                if key not in combined:
                    item = dict(criterion)
                    item["_source"] = source
                    combined[key] = item
                    ordered.append((category, item))

    return ordered

def calculate_candidate_score(
    candidate_data: dict,
    job_profile,
    method: str = "combined",
) -> dict:
    """
    Calculate a candidate's evidence-backed score for one job.

    The returned score is normalized to 0-100 over categories
    that contain information. Evidence coverage is reported
    separately to expose missing information.
    """

    weights = get_profile_weights(job_profile)

    mandatory = _get_profile_value(
        job_profile, "mandatory_criteria"
    ) or {}

    preferred = _get_profile_value(
        job_profile, "preferred_criteria"
    ) or {}

    corpus = build_candidate_corpus(candidate_data)
    candidate_evidence = build_candidate_evidence(candidate_data)

    criteria = _deduplicate_criteria(mandatory, preferred)

    category_results = {}

    for category in weights:
        category_results[category] = {
            "score": None,
            "criteria": [],
            "available": False,
            "coverage": 0.0,
        }

    for category, criterion in criteria:
        if category not in category_results:
            continue

        result = match_criterion(
            criterion=criterion,
            candidate_corpus=corpus,
            category=category,
            method=method,
            candidate_evidence=candidate_evidence,
        )

        result["importance"] = criterion.get(
            "importance", "medium"
        )
        result["source"] = criterion.get("_source", "unknown")

        category_results[category]["criteria"].append(result)

    # Calculate category scores and criterion-level coverage.
    for category, result in category_results.items():
        items = result["criteria"]

        applicable = [
            item for item in items
            if item["status"] != "not_applicable"
        ]

        if not applicable:
            continue

        evaluated = [
            item for item in applicable
            if item["score"] is not None
        ]

        total_importance = sum(
            criterion_importance_weight(item["importance"])
            for item in applicable
        )

        evaluated_importance = sum(
            criterion_importance_weight(item["importance"])
            for item in evaluated
        )

        if total_importance > 0:
            result["coverage"] = round(
                evaluated_importance / total_importance, 4
            )

        if not evaluated:
            continue

        denominator = sum(
            criterion_importance_weight(item["importance"])
            for item in evaluated
        )

        numerator = sum(
            item["score"]
            * criterion_importance_weight(item["importance"])
            for item in evaluated
        )

        result["score"] = round(
            (numerator / denominator) * 100, 2
        )

        result["available"] = True

    # Missing categories are excluded from the score denominator.
    available_categories = [
        category
        for category, result in category_results.items()
        if result["available"]
    ]

    available_weight = sum(
        weights[category] for category in available_categories
    )

    if available_weight == 0:
        final_score = None
    else:
        final_score = sum(
            category_results[category]["score"]
            * weights[category]
            for category in available_categories
        ) / available_weight

        final_score = round(final_score, 2)

    # Weighted proportion of the original scoring criteria
    # for which resume information was available.
    evidence_coverage = sum(
        weights[category] * category_results[category]["coverage"]
        for category in weights
    ) / 100

    missing_information = [
        category
        for category, result in category_results.items()
        if not result["available"]
    ]

    return {
        "job_id": _get_profile_value(job_profile, "job_id"),
        "job_title": _get_profile_value(job_profile, "title"),
        "score": final_score,
        "information_availability_coverage": round(
            evidence_coverage * 100, 2
        ),
        "scoring_method": method,
        "category_scores": category_results,
        "missing_information": missing_information,
        "methodology_version": "1.0",
    }
    
    