
import json
import ollama

from ai_engine.prompts import SYSTEM_PROMPT, build_extraction_prompt
from ai_engine.schemas import CandidateProfile


MODEL_NAME = "llama3.2:latest"

client = ollama.Client(
    host="http://127.0.0.1:11434",
    timeout=300.0,
)


def extract_with_llm(resume_text: str) -> dict:
    """Extract structured candidate information using Ollama."""

    if not isinstance(resume_text, str) or not resume_text.strip():
        raise ValueError("Resume text cannot be empty.")

    if len(resume_text) > 50000:
        raise ValueError("Resume text exceeds the 50000-character limit.")

    response = client.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": build_extraction_prompt(resume_text),
            },
        ],
        format="json",
        options={"temperature": 0},
    )

    content = response.message.content

    if not isinstance(content, str) or not content.strip():
        raise ValueError(
            "LLM returned an empty or non-text response."
        )

    try:
        result = json.loads(content)
    except (TypeError, json.JSONDecodeError) as error:
        raise ValueError("LLM returned invalid JSON.") from error

    if not isinstance(result, dict):
        raise ValueError("LLM output must be a JSON object.")

    return result


def normalize_llm_output(data: dict) -> CandidateProfile:
    """Normalize inconsistent LLM output into CandidateProfile."""

    if not isinstance(data, dict):
        raise ValueError("LLM output must be a JSON object.")

    # ---------- Helper functions ----------

    def as_list(value):
        if isinstance(value, list):
            return value
        if isinstance(value, dict):
            return [value]
        return []

    def values(value):
        if isinstance(value, list):
            return value
        return [value]

    def get_dict(value):
        return value if isinstance(value, dict) else {}

    def normalize_text(value):
        if value is None:
            return None

        if isinstance(value, dict):
            value = value.get("value")

        if isinstance(value, list):
            return normalize_text(value[0]) if value else None

        if isinstance(value, str):
            value = value.strip()
            return value if value else None

        if isinstance(value, (int, float)):
            return str(value)

        return None

    def get_at(value, index):
        items = values(value)
        return items[index] if index < len(items) else None

    def normalize_date(value):
        return normalize_text(value)

    def normalize_technologies(value):
        result = []

        for item in values(value):
            text = normalize_text(item)
            if text:
                result.append(text)

        return result

    def get_field_value(value):
        if isinstance(value, dict):
            return normalize_text(value.get("value"))
        return normalize_text(value)

    def make_field(value):
        return {
            "value": get_field_value(value),
            "evidence": [],
            "confidence": None,
        }

    # ---------- Personal information ----------

    personal = get_dict(
        data.get("personalInformation")
        or data.get("personal_information")
        or data.get("personal_info")
    )

    personal_info = {
        "name": make_field(personal.get("name")),
        "email": make_field(personal.get("email")),
        "phone": make_field(personal.get("phone")),
        "location": make_field(personal.get("location")),
    }

    # ---------- Education ----------

    education = []

    for item in as_list(data.get("education")):
        item = get_dict(item)

        dates = item.get("dates")

        if isinstance(dates, list):
            start = normalize_date(
                dates[0] if len(dates) > 0 else None
            )
            end = normalize_date(
                dates[1] if len(dates) > 1 else None
            )

        elif isinstance(dates, str):
            start, separator, end = dates.partition("-")
            start = normalize_date(start)
            end = normalize_date(end) if separator else None

        else:
            start = normalize_date(item.get("start_date"))
            end = normalize_date(item.get("end_date"))

        education.append({
            "institution": normalize_text(item.get("institution")),
            "degree": normalize_text(item.get("degree")),
            "field_of_study": normalize_text(
                item.get("field_of_study") or item.get("field")
            ),
            "start_date": start,
            "end_date": end,
            "grade": normalize_text(item.get("grade")),
        })

    # ---------- Skills ----------

    skills = []

    raw_skills = (
            data.get("technicalSkills")
            or data.get("technical_skills")
            or data.get("skills")
        )

    for item in as_list(raw_skills):
        if isinstance(item, dict):
            names = item.get("skillName") or item.get("name")
            categories = item.get("category")

            for index, name in enumerate(values(names)):
                name = normalize_text(name)

                if name:
                    skills.append({
                        "name": name,
                        "category": normalize_text(
                            get_at(categories, index)
                        ),
                    })

        elif isinstance(item, str):
            name = normalize_text(item)

            if name:
                skills.append({
                    "name": name,
                    "category": None,
                })

    # ---------- Work experience ----------

    experience = []

    for item in as_list(
        data.get("workExperience")
        or data.get("work_experience")
        or data.get("experience")
    ):
        item = get_dict(item)

        fields = {
            "company": item.get("company"),
            "position": item.get("position") or item.get("role"),
            "employment_type": item.get("employment_type"),
            "start_date": item.get("start_date"),
            "end_date": item.get("end_date"),
            "description": item.get("description"),
        }

        count = max(
            [len(values(value)) for value in fields.values()
             if value is not None] or [1]
        )

        for index in range(count):
            record = {
                key: normalize_text(get_at(value, index))
                for key, value in fields.items()
            }

            if any(value is not None for value in record.values()):
                experience.append(record)

    # ---------- Projects ----------

    projects = []

    for item in as_list(data.get("projects")):
        item = get_dict(item)

        names = values(item.get("name"))

        for index, name in enumerate(names):
            name = normalize_text(name)

            if not name:
                continue

            projects.append({
                "name": name,
                "description": normalize_text(
                    get_at(item.get("description"), index)
                ),
                "technologies": normalize_technologies(
                    get_at(item.get("technologies"), index)
                ),
            })

    # ---------- Certifications ----------

    certifications = []

    for item in as_list(data.get("certifications")):
        item = get_dict(item)

        for index, name in enumerate(values(item.get("name"))):
            name = normalize_text(name)

            if not name:
                continue

            certifications.append({
                "name": name,
                "issuer": normalize_text(
                    get_at(item.get("issuer"), index)
                ),
                "issue_date": normalize_date(
                    get_at(
                        item.get("issue_date") or item.get("date"),
                        index,
                    )
                ),
            })

    # ---------- Final structured profile ----------

    normalized = {
        "personal_info": personal_info,
        "education": education,
        "skills": skills,
        "experience": experience,
        "projects": projects,
        "certifications": certifications,
        "total_experience_years": {
            "value": None,
            "evidence": [],
            "confidence": None,
        },
    }

    return CandidateProfile.model_validate(normalized)
