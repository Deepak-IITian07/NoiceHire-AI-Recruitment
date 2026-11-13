
SKILL_SYNONYMS = {
    "python": ["python3", "python 3"],
    "javascript": ["js", "ecmascript"],
    "typescript": ["ts"],
    "react": ["react.js", "reactjs"],
    "node.js": ["nodejs", "node"],
    "machine learning": ["ml"],
    "deep learning": ["dl"],
    "natural language processing": ["nlp"],
    "large language models": ["llm", "llms"],
    "postgresql": ["postgres", "pgsql"],
    "mongodb": ["mongo"],
    "rest api": ["restful api", "rest apis"],
    "scikit-learn": ["sklearn", "scikit learn"],
    "continuous integration": ["ci"],
    "continuous deployment": ["cd"],
    "figma": ["figma design"],
}


def normalize_skill(skill: str) -> str:
    """Normalize a skill name for comparison."""
    return " ".join(skill.lower().strip().split())


def get_canonical_skill(skill: str) -> str:
    """Return the canonical name of a skill."""

    normalized = normalize_skill(skill)

    for canonical, alternatives in SKILL_SYNONYMS.items():
        all_names = [canonical] + alternatives

        if normalized in [normalize_skill(name) for name in all_names]:
            return canonical

    return normalized


def skills_match(skill_a: str, skill_b: str) -> bool:
    """Check whether two skill names are equivalent."""

    if not skill_a or not skill_b:
        return False

    return get_canonical_skill(skill_a) == get_canonical_skill(skill_b)
