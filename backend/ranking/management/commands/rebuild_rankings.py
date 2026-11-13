
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from resumes.models import CandidateProfile
from job_profiles.models import JobProfile
from ranking.models import MatchResult
from ranking.ranker import rank_for_both_jobs


class Command(BaseCommand):
    help = "Rebuild JD1 and JD2 rankings without AI extraction."

    def handle(self, *args, **options):
        try:
            jd1 = JobProfile.objects.get(job_id="JD1")
            jd2 = JobProfile.objects.get(job_id="JD2")
        except JobProfile.DoesNotExist as error:
            raise CommandError(f"Required job profile missing: {error}")

        profiles = CandidateProfile.objects.select_related(
            "resume"
        ).exclude(candidate_data={}).order_by("resume_id")

        candidates = []
        resume_lookup = {}

        for profile in profiles:
            identifier = f"RESUME-{profile.resume_id}"

            resume_lookup[identifier] = profile.resume

            candidates.append({
                "candidate_identifier": identifier,
                "resume_id": profile.resume_id,
                "candidate_data": profile.candidate_data,
            })

        if not candidates:
            raise CommandError("No valid candidate profiles found.")

        def profile_dict(profile):
            return {
                "job_id": profile.job_id,
                "title": profile.title,
                "mandatory_criteria": profile.mandatory_criteria,
                "preferred_criteria": profile.preferred_criteria,
                "scoring_criteria": profile.scoring_criteria,
            }

        self.stdout.write(
            f"Ranking {len(candidates)} candidates for JD1 and JD2..."
        )

        result = rank_for_both_jobs(
            candidates,
            profile_dict(jd1),
            profile_dict(jd2),
            method="combined",
        )

        classifications = {
            item["candidate_identifier"]: item
            for item in result["classifications"]
        }

        new_results = []

        for job in (jd1, jd2):
            for item in result["rankings"][job.job_id]:
                resume = resume_lookup[item["candidate_identifier"]]

                new_results.append(MatchResult(
                    resume=resume,
                    job_profile=job,
                    score=item["score"],
                    information_availability_coverage=(
                        item["information_availability_coverage"]
                    ),
                    category_scores=item["category_scores"],
                    missing_information=item["missing_information"],
                    explanation={
                        "criteria": item["explanation"],
                        "classification": classifications.get(
                            item["candidate_identifier"], {}
                        ),
                    },
                    matching_method=result["matching_method"],
                    methodology_version=result["methodology_version"],
                ))

        with transaction.atomic():
            MatchResult.objects.filter(
                job_profile__in=[jd1, jd2]
            ).delete()

            MatchResult.objects.bulk_create(new_results)

        self.stdout.write(self.style.SUCCESS(
            "\nRanking completed successfully."
        ))
        self.stdout.write(f"Candidates ranked: {len(candidates)}")
        self.stdout.write(
            f"JD1 results: {len(result['rankings']['JD1'])}"
        )
        self.stdout.write(
            f"JD2 results: {len(result['rankings']['JD2'])}"
        )
        self.stdout.write(
            f"Total MatchResults saved: {len(new_results)}"
        )
        self.stdout.write("Resume 39 excluded: empty extracted text.")
