
import re


def extract_email(text: str) -> str | None:
    """
    Extract the first email address from resume text.
    """

    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'

    match = re.search(pattern, text)

    if match:
        return match.group(0)

    return None



def extract_phone(text: str) -> str | None:
    """
    Extract an Indian mobile phone number.
    """

    pattern = r'(?<!\d)(?:\+91[\s-]?|91[\s-]?|0)?[6-9]\d{9}(?!\d)'

    match = re.search(pattern, text)

    if match:
        return match.group(0).strip()

    return None


# Limitation: This is a heuristic, not reliable name recognition. It can mistake a heading or university name for a candidate's name. We will let the LLM improve this later.
def extract_name(text: str) -> str | None:
    """
    Basic heuristic for extracting candidate name.
    """

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    ignored = {
        "resume",
        "curriculum vitae",
        "cv",
        "profile",
        "contact",
        "personal details"
    }

    for line in lines[:8]:

        cleaned = re.sub(
            r'[^A-Za-z .\'-]',
            '',
            line
        ).strip()

        if cleaned.lower() in ignored:
            continue

        if "@" in line or re.search(r'\d', line):
            continue

        words = cleaned.split()

        if 2 <= len(words) <= 4:
            return cleaned

    return None



SECTION_ALIASES = {
    "education": [
        "education",
        "academic background",
        "educational qualifications"
    ],
    "skills": [
        "skills",
        "technical skills",
        "core competencies",
        "technical expertise"
    ],
    "experience": [
        "experience",
        "work experience",
        "professional experience",
        "employment history",
        "internships"
    ],
    "projects": [
        "projects",
        "academic projects",
        "personal projects"
    ],
    "certifications": [
        "certifications",
        "certificates",
        "licenses and certifications"
    ]
}



def extract_sections(text: str) -> dict:
    """
    Identify major resume sections and extract their text.
    """

    sections = {
        section: []
        for section in SECTION_ALIASES
    }

    current_section = None

    for line in text.splitlines():

        cleaned = line.strip()

        if not cleaned:
            continue

        # Normalize heading
        heading = re.sub(
            r'[:\-\s]+$',
            '',
            cleaned.lower()
        ).strip()

        matched_section = None

        for section, aliases in SECTION_ALIASES.items():
            if heading in aliases:
                matched_section = section
                break

        if matched_section:
            current_section = matched_section
            continue

        if current_section:
            sections[current_section].append(cleaned)

    return {
        section: "\n".join(lines)
        for section, lines in sections.items()
    }



SKILL_DATABASE = {
    "Programming Languages": [
        "Python",
        "C",
        "C++",
        "Java",
        "JavaScript",
        "TypeScript",
        "Rust",
        "Go",
        "C#"
    ],

    "Web Development": [
        "HTML",
        "CSS",
        "React",
        "Node.js",
        "Express.js",
        "Django",
        "Flask",
        "REST API"
    ],

    "Databases": [
        "MySQL",
        "PostgreSQL",
        "MongoDB",
        "SQL",
        "Redis"
    ],

    "Machine Learning": [
        "Machine Learning",
        "Deep Learning",
        "Scikit-learn",
        "TensorFlow",
        "PyTorch",
        "Pandas",
        "NumPy"
    ],

    "Tools": [
        "Git",
        "GitHub",
        "Docker",
        "Linux",
        "AWS"
    ]
}


def extract_skills(text: str) -> list[dict]:
    """
    Match known technical skills against resume text.
    """

    extracted_skills = []
    normalized_text = text.lower()

    for category, skills in SKILL_DATABASE.items():

        for skill in skills:

            pattern = (
                r'(?<![a-zA-Z0-9])'
                + re.escape(skill.lower())
                + r'(?![a-zA-Z0-9])'
            )

            if re.search(pattern, normalized_text):

                extracted_skills.append({
                    "name": skill,
                    "category": category
                })

    return extracted_skills



DATE_RANGE_PATTERN = re.compile(
    r'\b('
    r'(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|'
    r'Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|'
    r'Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|'
    r'Nov(?:ember)?|Dec(?:ember)?)[, ]+\d{4}'
    r'|\d{4}'
    r')\s*[-–—to]+\s*('
    r'(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|'
    r'Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|'
    r'Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|'
    r'Nov(?:ember)?|Dec(?:ember)?)[, ]+\d{4}'
    r'|\d{4}|Present|Current'
    r')\b',
    re.IGNORECASE
)


def extract_dates(text: str) -> list[dict]:
    """
    Extract date ranges from resume text.
    """

    results = []

    for match in DATE_RANGE_PATTERN.finditer(text):

        results.append({
            "start_date": match.group(1),
            "end_date": match.group(2),
            "evidence": match.group(0)
        })

    return results





def extract_resume_data(text: str) -> dict:
    """
    Run the complete rule-based extraction pipeline.
    """

    if not text or not text.strip():
        raise ValueError("Resume text cannot be empty")

    sections = extract_sections(text)

    return {
        "personal_info": {
            "name": {
                "value": extract_name(text)
            },
            "email": {
                "value": extract_email(text)
            },
            "phone": {
                "value": extract_phone(text)
            }
        },

        "education": [],

        "skills": extract_skills(
            sections["skills"] or text
        ),

        "experience": [],

        "projects": [],

        "certifications": [],

        "total_experience_years": {
            "value": None
        },

        "sections": sections,

        "date_ranges": extract_dates(text)
    }
