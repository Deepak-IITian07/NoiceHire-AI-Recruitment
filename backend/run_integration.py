import os
import django

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings"
)
django.setup()

from resumes.models import Resume
from ai_engine.service import process_resume

resume = Resume.objects.exclude(
    extracted_text=""
).first()

if resume:
    candidate = process_resume(resume)

    print("Extraction successful!")
    print(candidate.model_dump_json(indent=2))
else:
    print("No extracted resume found.")