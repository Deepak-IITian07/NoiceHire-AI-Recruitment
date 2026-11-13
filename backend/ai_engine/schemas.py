
from typing import Optional, Generic, TypeVar, Literal
from pydantic import BaseModel, ConfigDict, Field


T = TypeVar("T")


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True
    )


class Evidence(BaseSchema):
    text: str
    page: Optional[int] = None
    start: Optional[int] = None
    end: Optional[int] = None


class ExtractedField(BaseSchema, Generic[T]):
    value: Optional[T] = None
    evidence: list[Evidence] = Field(default_factory=list)
    confidence: Optional[float] = Field(
        default=None, ge=0.0, le=1.0
    )
    verification_status: Literal[
        "unverified",
        "verified",
        "needs_review"
    ] = "unverified"


class PersonalInfo(BaseSchema):
    name: ExtractedField[str] = Field(
        default_factory=ExtractedField
    )
    email: ExtractedField[str] = Field(
        default_factory=ExtractedField
    )
    phone: ExtractedField[str] = Field(
        default_factory=ExtractedField
    )
    location: ExtractedField[str] = Field(
        default_factory=ExtractedField
    )


class Education(BaseSchema):
    institution: Optional[str] = None
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    grade: Optional[str] = None

    evidence: list[Evidence] = Field(default_factory=list)
    confidence: Optional[float] = Field(
        default=None, ge=0.0, le=1.0
    )
    verification_status: Literal[
        "unverified", "verified", "needs_review"
    ] = "unverified"


class Skill(BaseSchema):
    name: str
    category: Optional[str] = None

    evidence: list[Evidence] = Field(default_factory=list)
    confidence: Optional[float] = Field(
        default=None, ge=0.0, le=1.0
    )


class Experience(BaseSchema):
    company: Optional[str] = None
    position: Optional[str] = None
    employment_type: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None

    evidence: list[Evidence] = Field(default_factory=list)
    confidence: Optional[float] = Field(
        default=None, ge=0.0, le=1.0
    )
    verification_status: Literal[
        "unverified", "verified", "needs_review"
    ] = "unverified"


class Project(BaseSchema):
    name: str
    description: Optional[str] = None
    technologies: list[str] = Field(default_factory=list)

    evidence: list[Evidence] = Field(default_factory=list)
    confidence: Optional[float] = Field(
        default=None, ge=0.0, le=1.0
    )
    verification_status: Literal[
        "unverified", "verified", "needs_review"
    ] = "unverified"


class Certification(BaseSchema):
    name: str
    issuer: Optional[str] = None
    issue_date: Optional[str] = None

    evidence: list[Evidence] = Field(default_factory=list)
    confidence: Optional[float] = Field(
        default=None, ge=0.0, le=1.0
    )
    verification_status: Literal[
        "unverified", "verified", "needs_review"
    ] = "unverified"


class CandidateProfile(BaseSchema):
    personal_info: PersonalInfo = Field(
        default_factory=PersonalInfo
    )

    education: list[Education] = Field(default_factory=list)
    skills: list[Skill] = Field(default_factory=list)
    experience: list[Experience] = Field(default_factory=list)
    projects: list[Project] = Field(default_factory=list)
    certifications: list[Certification] = Field(
        default_factory=list
    )

    total_experience_years: ExtractedField[float] = Field(
        default_factory=ExtractedField
    )
