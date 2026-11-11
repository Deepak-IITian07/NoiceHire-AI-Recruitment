
from pathlib import Path

# Root directory
ROOT = Path(".")

# Directory structure
directories = [
    "backend/config",
    "backend/resumes",
    "backend/job_profiles",
    "backend/ai_engine",
    "backend/ranking",
    "frontend/src/components",
    "frontend/src/pages",
    "frontend/src/services",
    "frontend/src/assets",
    "docs",
]

# Create directories
for directory in directories:
    (ROOT / directory).mkdir(parents=True, exist_ok=True)

# Create empty files
files = [
    "backend/requirements.txt",
    "frontend/package.json",
    "docs/methodology.md",
    "docs/architecture.md",
    ".gitignore",
    "README.md",
]

for file in files:
    (ROOT / file).touch(exist_ok=True)

print("Project directory structure created successfully!")
