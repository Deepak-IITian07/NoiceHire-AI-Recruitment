from pathlib import Path
from docx import Document


def read_job_description(file_path):
    path = Path(file_path)
    extension = path.suffix.lower()

    if extension == ".txt":
        text = path.read_text(encoding="utf-8")

    elif extension == ".docx":
        document = Document(path)
        text = "\n".join(
            paragraph.text
            for paragraph in document.paragraphs
        )

    else:
        raise ValueError("Only .txt and .docx files are supported.")

    if not text.strip():
        raise ValueError("Job description file is empty.")

    return text