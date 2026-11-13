
from functools import lru_cache
from typing import Any

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Initial experimental blend, not a calibrated hiring threshold.
TFIDF_WEIGHT = 0.30
EMBEDDING_WEIGHT = 0.70


def clean_text(value: Any) -> str:
    """Convert supported values into clean text."""
    if value is None:
        return ""

    if isinstance(value, str):
        return " ".join(value.split())

    if isinstance(value, (int, float)):
        return str(value)

    if isinstance(value, list):
        return " ".join(
            clean_text(item) for item in value if item is not None
        )

    if isinstance(value, dict):
        return " ".join(
            clean_text(item)
            for item in value.values()
            if item is not None
        )

    return ""


def _value(field: Any) -> str:
    """Extract the value from M3's value/evidence objects."""
    if isinstance(field, dict):
        return clean_text(field.get("value"))
    return clean_text(field)


def build_candidate_corpus(candidate_data: dict) -> dict:
    """
    Build category-specific text from the actual M3 JSON structure.

    We retain the original information rather than relying on
    potentially incorrect skill categories.
    """
    if not isinstance(candidate_data, dict):
        raise ValueError("Candidate data must be a dictionary.")

    personal_info = candidate_data.get("personal_info", {})
    education = candidate_data.get("education", [])
    skills = candidate_data.get("skills", [])
    experience = candidate_data.get("experience", [])
    projects = candidate_data.get("projects", [])
    certifications = candidate_data.get("certifications", [])

    skill_text = []

    for skill in skills:
        if isinstance(skill, dict):
            skill_text.extend([
                clean_text(skill.get("name")),
                clean_text(skill.get("category")),
                clean_text(skill.get("evidence")),
            ])

    experience_text = []

    for item in experience:
        if isinstance(item, dict):
            experience_text.extend([
                clean_text(item.get("position")),
                clean_text(item.get("company")),
                clean_text(item.get("employment_type")),
                clean_text(item.get("description")),
                clean_text(item.get("evidence")),
            ])

    project_text = []

    for item in projects:
        if isinstance(item, dict):
            project_text.extend([
                clean_text(item.get("name")),
                clean_text(item.get("description")),
                clean_text(item.get("technologies")),
                clean_text(item.get("evidence")),
            ])

    education_text = []

    for item in education:
        if isinstance(item, dict):
            education_text.extend([
                clean_text(item.get("degree")),
                clean_text(item.get("field_of_study")),
                clean_text(item.get("institution")),
                clean_text(item.get("grade")),
            ])

    certification_text = []

    for item in certifications:
        certification_text.append(clean_text(item))

    total_experience = _value(
        candidate_data.get("total_experience_years")
    )

    personal_text = " ".join(
        _value(value) for value in personal_info.values()
    ) if isinstance(personal_info, dict) else ""

    corpora = {
        "skills": " ".join(skill_text),
        "tools": " ".join(skill_text + project_text),
        "experience": " ".join(
            experience_text + [total_experience]
        ),
        "projects": " ".join(project_text),
        "education": " ".join(education_text),
    }

    # Certifications and other information remain available as
    # supplementary context for later improvements.
    corpora["supplementary"] = " ".join(
        certification_text + [personal_text]
    )

    return {
        category: text.strip()
        for category, text in corpora.items()
    }
    

def build_candidate_evidence(candidate_data: dict) -> dict:
    """
    Preserve individual resume entries for criterion-level matching.
    Each item contains the original text and its source.
    """
    evidence = {
        "skills": [],
        "tools": [],
        "experience": [],
        "projects": [],
        "education": [],
    }

    for item in candidate_data.get("skills", []):
        if isinstance(item, dict):
            text = clean_text(
                " ".join([
                    clean_text(item.get("name")),
                    clean_text(item.get("category")),
                    clean_text(item.get("evidence")),
                ])
            )
            if text:
                entry = {"text": text, "source": "resume_skill"}
                evidence["skills"].append(entry)
                evidence["tools"].append(entry)

    for item in candidate_data.get("experience", []):
        if isinstance(item, dict):
            text = clean_text(
                " ".join([
                    clean_text(item.get("position")),
                    clean_text(item.get("company")),
                    clean_text(item.get("description")),
                    clean_text(item.get("evidence")),
                ])
            )
            if text:
                evidence["experience"].append({
                    "text": text,
                    "source": "resume_experience",
                })

    for item in candidate_data.get("projects", []):
        if isinstance(item, dict):
            text = clean_text(
                " ".join([
                    clean_text(item.get("name")),
                    clean_text(item.get("description")),
                    clean_text(item.get("technologies")),
                    clean_text(item.get("evidence")),
                ])
            )

            if text:
                entry = {
                    "text": text,
                    "source": "resume_project",
                }
                evidence["projects"].append(entry)

                # Technologies are also valid tool evidence.
                for technology in item.get("technologies", []):
                    technology = clean_text(technology)
                    if technology:
                        evidence["tools"].append({
                            "text": technology,
                            "source": "project_technology",
                        })

    for item in candidate_data.get("education", []):
        if isinstance(item, dict):
            text = clean_text(
                " ".join([
                    clean_text(item.get("degree")),
                    clean_text(item.get("field_of_study")),
                    clean_text(item.get("institution")),
                    clean_text(item.get("grade")),
                ])
            )
            if text:
                evidence["education"].append({
                    "text": text,
                    "source": "resume_education",
                })

    return evidence



def tfidf_similarity(query: str, document: str) -> float | None:
    """Return TF-IDF cosine similarity between two text inputs."""
    query = clean_text(query)
    document = clean_text(document)

    if not query or not document:
        return None

    try:
        vectorizer = TfidfVectorizer(
            lowercase=True,
            ngram_range=(1, 2),
            sublinear_tf=True,
        )

        matrix = vectorizer.fit_transform([query, document])

        score = cosine_similarity(
            matrix[0:1],
            matrix[1:2],
        )[0][0]

        return float(np.clip(score, 0.0, 1.0))

    except ValueError:
        return 0.0


@lru_cache(maxsize=1)
def _load_embedding_model():
    """Load the sentence-transformer model only once."""
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(MODEL_NAME)


def embedding_similarity(query: str, document: str) -> float | None:
    """Return sentence embedding cosine similarity."""
    query = clean_text(query)
    document = clean_text(document)

    if not query or not document:
        return None

    model = _load_embedding_model()

    embeddings = model.encode(
        [query, document],
        normalize_embeddings=True,
        convert_to_numpy=True,
    )

    score = float(np.dot(embeddings[0], embeddings[1]))

    # Cosine similarity can be negative. Convert to a 0–1 scale.
    return float(np.clip((score + 1.0) / 2.0, 0.0, 1.0))


def calculate_semantic_similarity(
    query: str,
    document: str,
    method: str = "combined",
) -> dict:
    """
    Compare a job criterion against candidate information.

    Supported methods:
    - tfidf
    - embedding
    - combined
    """
    query = clean_text(query)
    document = clean_text(document)

    if not query or not document:
        return {
            "score": None,
            "tfidf_score": None,
            "embedding_score": None,
            "status": "unknown",
        }

    if method not in {"tfidf", "embedding", "combined"}:
        raise ValueError(f"Unsupported matching method: {method}")

    tfidf_score = None
    embedding_score = None

    if method in {"tfidf", "combined"}:
        tfidf_score = tfidf_similarity(query, document)

    if method in {"embedding", "combined"}:
        embedding_score = embedding_similarity(query, document)

    if method == "tfidf":
        score = tfidf_score

    elif method == "embedding":
        score = embedding_score

    else:
        score = (
            TFIDF_WEIGHT * tfidf_score
            + EMBEDDING_WEIGHT * embedding_score
        )

    return {
        "score": round(score, 4),
        "tfidf_score": (
            round(tfidf_score, 4)
            if tfidf_score is not None else None
        ),
        "embedding_score": (
            round(embedding_score, 4)
            if embedding_score is not None else None
        ),
        "status": "evaluated",
    }


def match_criterion(
    criterion: dict,
    candidate_corpus: dict,
    category: str,
    method: str = "combined",
    candidate_evidence: dict | None = None,
) -> dict:
    """Match a JD criterion and identify its strongest resume evidence."""

    name = clean_text(criterion.get("name"))
    description = clean_text(criterion.get("description"))

    if not name or name.lower() == "none specified":
        return {
            "criterion": name,
            "category": category,
            "score": None,
            "status": "not_applicable",
            "matched_evidence": None,
        }

    query = " ".join([name, description]).strip()

    # Prefer individual evidence entries over category-wide text.
    entries = (
        candidate_evidence.get(category, [])
        if candidate_evidence is not None
        else []
    )

    if not entries:
        document = clean_text(candidate_corpus.get(category))

        result = calculate_semantic_similarity(
            query, document, method
        )

        return {
            "criterion": name,
            "category": category,
            **result,
            "matched_evidence": None,
        }

    best_result = None
    best_evidence = None

    for entry in entries:
        text = clean_text(entry.get("text"))

        if not text:
            continue

        result = calculate_semantic_similarity(
            query, text, method
        )

        if result["score"] is None:
            continue

        if (
            best_result is None
            or result["score"] > best_result["score"]
        ):
            best_result = result
            best_evidence = {
                "text": text,
                "source": entry.get("source", "resume"),
            }

    if best_result is None:
        return {
            "criterion": name,
            "category": category,
            "score": None,
            "status": "unknown",
            "matched_evidence": None,
        }

    return {
        "criterion": name,
        "category": category,
        **best_result,
        "matched_evidence": best_evidence,
    }
