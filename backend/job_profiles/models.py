
from django.db import models


class JobProfile(models.Model):

    job_id = models.CharField(
        max_length=50,
        unique=True,
    )

    title = models.CharField(
        max_length=255,
    )

    original_description = models.TextField()

    role_summary = models.TextField(
        blank=True,
        null=True,
    )

    mandatory_criteria = models.JSONField(
        default=dict,
        blank=True,
    )

    preferred_criteria = models.JSONField(
        default=dict,
        blank=True,
    )

    responsibilities = models.JSONField(
        default=list,
        blank=True,
    )

    synonyms = models.JSONField(
        default=dict,
        blank=True,
    )

    scoring_criteria = models.JSONField(
        default=dict,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"{self.job_id} - {self.title}"
