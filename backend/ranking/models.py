from django.db import models

from resumes.models import Resume
from job_profiles.models import JobProfile


class MatchResult(models.Model):

    resume = models.ForeignKey(
        Resume,
        on_delete=models.CASCADE,
        related_name="match_results",
    )

    job_profile = models.ForeignKey(
        JobProfile,
        on_delete=models.CASCADE,
        related_name="match_results",
    )

    score = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
    )

    information_availability_coverage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )

    category_scores = models.JSONField(
        default=dict,
        blank=True,
    )

    missing_information = models.JSONField(
        default=list,
        blank=True,
    )

    explanation = models.JSONField(
        default=dict,
        blank=True,
    )

    matching_method = models.CharField(
        max_length=30,
        default="combined",
    )

    methodology_version = models.CharField(
        max_length=20,
        default="1.0",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["resume", "job_profile"],
                name="unique_resume_job_match",
            )
        ]
        ordering = ["-score"]

    def __str__(self):
        return (
            f"{self.resume.candidate_identifier} - "
            f"{self.job_profile.job_id} - {self.score}"
        )