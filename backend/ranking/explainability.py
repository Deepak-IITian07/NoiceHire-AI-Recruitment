
from ranking.semantic_matching import clean_text


def collect_resume_evidence(candidate_data: dict) -> dict:
    """Collect actual resume text by category."""

    evidence = {
        "skills": [],
        "tools": [],
        "experience": [],
        "projects": [],
        "education": [],
    }

    for item in candidate_data.get("skills", []):
        if isinstance(item, dict):
            text = clean_text(item.get("name"))
            if text:
                evidence["skills"].append(text)
                evidence["tools"].append(text)

    for item in candidate_data.get("experience", []):
        if isinstance(item, dict):
            text = clean_text(
                " ".join([
                    clean_text(item.get("position")),
                    clean_text(item.get("description")),
                ])
            )
            if text:
                evidence["experience"].append(text)

    for item in candidate_data.get("projects", []):
        if isinstance(item, dict):
            text = clean_text(
                " ".join([
                    clean_text(item.get("name")),
                    clean_text(item.get("description")),
                    clean_text(item.get("technologies")),
                ])
            )
            if text:
                evidence["projects"].append(text)

            for technology in item.get("technologies", []):
                if isinstance(technology, str) and technology.strip():
                    evidence["tools"].append(technology.strip())

    for item in candidate_data.get("education", []):
        if isinstance(item, dict):
            text = clean_text(
                " ".join([
                    clean_text(item.get("degree")),
                    clean_text(item.get("field_of_study")),
                    clean_text(item.get("institution")),
                ])
            )
            if text:
                evidence["education"].append(text)

    return evidence



def build_explanation(candidate_data: dict, score_result: dict) -> dict:
    matched_skills = []
    relevant_projects = []
    experience_evidence = []
    matched_tools = []
    education_evidence = []
    missing_information = []

    category_scores = score_result["category_scores"]

    output_mapping = {
        "skills": matched_skills,
        "tools": matched_tools,
        "projects": relevant_projects,
        "experience": experience_evidence,
        "education": education_evidence,
    }

    for category, result in category_scores.items():
        if not result["available"]:
            missing_information.append(category)
            continue

        for criterion in result["criteria"]:
            score = criterion.get("score")
            evidence = criterion.get("matched_evidence")

            if score is None or evidence is None:
                continue

            output_mapping[category].append({
                "criterion": criterion["criterion"],
                "similarity": score,
                "resume_evidence": evidence["text"],
                "evidence_source": evidence["source"],
                "importance": criterion.get("importance"),
            })

    score = score_result.get("score")
    coverage = score_result.get(
        "information_availability_coverage", 0
    )

    if score is None:
        explanation = (
            "Insufficient resume information to calculate a score."
        )
    else:
        explanation = (
            f"Calculated score: {score}/100. "
            f"Information availability: {coverage}%. "
            f"Matched evidence is taken from individual resume entries. "
            f"Missing categories: "
            f"{', '.join(missing_information) if missing_information else 'None'}."
        )

    return {
        "job_id": score_result.get("job_id"),
        "score": score,
        "matched_skills": matched_skills,
        "matched_tools": matched_tools,
        "relevant_projects": relevant_projects,
        "experience_evidence": experience_evidence,
        "education_evidence": education_evidence,
        "missing_information": missing_information,
        "explanation": explanation,
    }
