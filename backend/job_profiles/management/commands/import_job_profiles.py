
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from job_profiles.services import process_job_description

from job_profiles.document_reader import read_job_description


class Command(BaseCommand):
    help = "Extract and import job descriptions into the database."

    def add_arguments(self, parser):
        parser.add_argument(
            "--jd1",
            required=True,
            help="Path to JD1 text file",
        )

        parser.add_argument(
            "--jd2",
            required=True,
            help="Path to JD2 text file",
        )

    def handle(self, *args, **options):
        jobs = [
            ("JD1", options["jd1"]),
            ("JD2", options["jd2"]),
        ]

        for job_id, file_path in jobs:
            path = Path(file_path)

            if not path.is_file():
                raise CommandError(
                    f"{job_id} file not found: {path}"
                )

            try:
                jd_text = read_job_description(file_path)

                profile, created = process_job_description(
                    job_id=job_id,
                    jd_text=jd_text,
                )

                action = "Created" if created else "Updated"

                self.stdout.write(
                    self.style.SUCCESS(
                        f"{action}: {profile.job_id} - {profile.title}"
                    )
                )

            except Exception as error:
                self.stderr.write(
                    self.style.ERROR(
                        f"Failed to process {job_id}: {error}"
                    )
                )
                raise CommandError(
                    f"Import stopped while processing {job_id}."
                ) from error

        self.stdout.write(
            self.style.SUCCESS("Job profile import completed.")
        )
