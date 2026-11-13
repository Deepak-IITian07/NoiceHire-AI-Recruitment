from django.db import models


class Resume(models.Model):

    class ExtractionStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        SUCCESS = "success", "Success"
        EMPTY_TEXT = "empty_text", "Empty Text"
        OCR_UNAVAILABLE = "ocr_unavailable", "OCR Unavailable"
        FAILED = "failed", "Failed"

    # Candidate information
    candidate_identifier = models.CharField(
        max_length=100,
        db_index=True
    )

    candidate_data = models.JSONField(
        default=dict,
        blank=True
    )

    # Original document
    original_filename = models.CharField(max_length=255)

    file = models.FileField(upload_to="resumes/")

    file_hash = models.CharField(
        max_length=64,
        unique=True
    )

    # Extraction information
    extracted_text = models.TextField(blank=True)

    extracted_pages = models.JSONField(default=list)

    page_count = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    extraction_status = models.CharField(
        max_length=30,
        choices=ExtractionStatus.choices,
        default=ExtractionStatus.PENDING
    )

    extraction_error = models.TextField(blank=True)

    # Timestamp
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.candidate_identifier} - {self.original_filename}"


class CandidateProfile(models.Model):
    resume = models.OneToOneField(
        Resume,
        on_delete=models.CASCADE,
        related_name="candidate_profile",
    )

    candidate_data = models.JSONField(
        default=dict,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile - {self.resume.candidate_identifier}"


class ProcessingLog(models.Model):

    class Status(models.TextChoices):
        STARTED = "started", "Started"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"
        SKIPPED = "skipped", "Skipped"

    resume = models.ForeignKey(
        Resume,
        on_delete=models.CASCADE,
        related_name="processing_logs",
    )

    stage = models.CharField(max_length=100)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
    )

    message = models.TextField(blank=True)

    details = models.JSONField(
        default=dict,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.resume_id} - {self.stage} - {self.status}"