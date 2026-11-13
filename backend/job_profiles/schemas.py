
from typing import Literal

from pydantic import BaseModel, Field, ConfigDict


class JobCriterion(BaseModel):
    """One requirement extracted from a job description."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str = Field(min_length=1)
    description: str | None = None

    importance: Literal["high", "medium", "low"] = "medium"

    # Exact supporting text from the original JD
    evidence: str | None = None


class CriteriaGroup(BaseModel):
    """Requirements grouped by category."""

    model_config = ConfigDict(extra="forbid")

    skills: list[JobCriterion] = Field(default_factory=list)
    tools: list[JobCriterion] = Field(default_factory=list)
    experience: list[JobCriterion] = Field(default_factory=list)
    projects: list[JobCriterion] = Field(default_factory=list)
    education: list[JobCriterion] = Field(default_factory=list)


class JobProfileSchema(BaseModel):
    """Complete structured job description."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    job_id: str = Field(min_length=1)
    title: str = Field(min_length=1)

    role_summary: str | None = None

    mandatory_criteria: CriteriaGroup = Field(
        default_factory=CriteriaGroup
    )

    preferred_criteria: CriteriaGroup = Field(
        default_factory=CriteriaGroup
    )

    responsibilities: list[str] = Field(default_factory=list)

    # These will be populated in later M4 steps.
    synonyms: dict[str, list[str]] = Field(default_factory=dict)

    scoring_criteria: dict[str, float] = Field(default_factory=dict)
