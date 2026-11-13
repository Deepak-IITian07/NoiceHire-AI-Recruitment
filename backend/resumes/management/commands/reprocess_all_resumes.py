
import time

from django.core.management.base import BaseCommand
from resumes.models import Resume, ProcessingLog
from ai_engine.service import process_resume


class Command(BaseCommand):
    help = "Process resumes not yet successfully extracted by Gemini."

    def handle(self, *args, **options):
        successful_ids = ProcessingLog.objects.filter(
            stage="gemini_extraction",
            status=ProcessingLog.Status.SUCCESS
        ).values_list("resume_id", flat=True)

        resumes = Resume.objects.exclude(
            extracted_text=""
        ).exclude(
            id__in=successful_ids
        ).order_by("id")

        total = resumes.count()
        success = 0
        failed = 0

        self.stdout.write(f"Pending Gemini extractions: {total}")

        for index, resume in enumerate(resumes, start=1):
            self.stdout.write(
                f"\n[{index}/{total}] {resume.original_filename}"
            )

            log = ProcessingLog.objects.create(
                resume=resume,
                stage="gemini_extraction",
                status=ProcessingLog.Status.STARTED,
                message="Gemini extraction started."
            )

            for attempt in range(1, 4):
                try:
                    candidate = process_resume(resume)

                    log.status = ProcessingLog.Status.SUCCESS
                    log.message = "Gemini extraction completed."
                    log.details = {
                        "skills": len(candidate.skills),
                        "education": len(candidate.education),
                        "experience": len(candidate.experience),
                        "projects": len(candidate.projects),
                        "attempts": attempt,
                    }
                    log.save()

                    success += 1
                    self.stdout.write(self.style.SUCCESS("SUCCESS"))
                    break

                except Exception as error:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Attempt {attempt}/3 failed: {error}"
                        )
                    )

                    if attempt == 3:
                        log.status = ProcessingLog.Status.FAILED
                        log.message = str(error)
                        log.details = {
                            "error_type": type(error).__name__,
                            "attempts": attempt,
                        }
                        log.save()

                        failed += 1
                        self.stdout.write(
                            self.style.ERROR("FAILED after 3 attempts")
                        )
                    else:
                        time.sleep(5 * attempt)

        self.stdout.write("\n========== SUMMARY ==========")
        self.stdout.write(f"Attempted: {total}")
        self.stdout.write(self.style.SUCCESS(f"Successful: {success}"))
        self.stdout.write(self.style.ERROR(f"Failed: {failed}"))
