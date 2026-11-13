import logging

from django.db import transaction

from resumes.models import CandidateProfile, ProcessingLog
from job_profiles.models import JobProfile
from ranking.models import MatchResult
from ranking.ranker import rank_for_both_jobs
from ai_engine.service import process_resume
from ai_engine.validators import validate_candidate

logger = logging.getLogger(__name__)


def run_full_pipeline(resume):
    """
    Extract, validate, rank against JD1 and JD2,
    and persist the results.
    """

    log = ProcessingLog.objects.create(
        resume=resume,
        stage="full_pipeline",
        status=ProcessingLog.Status.STARTED,
        message="Full processing pipeline started."
    )

    try:
        # 1. AI extraction
        candidate = process_resume(resume)

        # 2. Structured data validation
        candidate_data = candidate.model_dump(mode="json")
        validated_candidate = validate_candidate(candidate_data)
        candidate_data = validated_candidate.model_dump(mode="json")

        # Keep prior rankings available when extraction fails and is retried.
        MatchResult.objects.filter(resume=resume).delete()

        CandidateProfile.objects.update_or_create(
            resume=resume,
            defaults={"candidate_data": candidate_data}
        )

        # 3. Load both job profiles
        jd1 = JobProfile.objects.get(job_id="JD1")
        jd2 = JobProfile.objects.get(job_id="JD2")

        def profile_dict(profile):
            return {
                "job_id": profile.job_id,
                "title": profile.title,
                "mandatory_criteria": profile.mandatory_criteria,
                "preferred_criteria": profile.preferred_criteria,
                "scoring_criteria": profile.scoring_criteria,
            }

        # 4. Load all candidates with structured data
        profiles = CandidateProfile.objects.select_related(
            "resume"
        ).all()

        candidates = []
        resume_lookup = {}

        for profile in profiles:
            if not profile.candidate_data:
                continue

            rank_id = f"RESUME-{profile.resume_id}"
            resume_lookup[rank_id] = profile.resume

            candidates.append({
                "candidate_identifier": rank_id,
                "resume_id": profile.resume_id,
                "candidate_data": profile.candidate_data,
            })

        # 5. Rank candidates for both jobs
        ranking_result = rank_for_both_jobs(
            candidates,
            profile_dict(jd1),
            profile_dict(jd2),
            method="combined",
        )

        classifications = {
            item["candidate_identifier"]: item
            for item in ranking_result["classifications"]
        }

        # 6. Persist both rankings
        with transaction.atomic():

            for job in (jd1, jd2):
                job_id = job.job_id

                for item in ranking_result["rankings"][job_id]:
                    target_resume = resume_lookup[
                        item["candidate_identifier"]
                    ]

                    explanation = {
                        "criteria": item["explanation"],
                        "classification": classifications.get(
                            item["candidate_identifier"], {}
                        ),
                    }

                    MatchResult.objects.update_or_create(
                        resume=target_resume,
                        job_profile=job,
                        defaults={
                            "score": item["score"],
                            "information_availability_coverage": (
                                item["information_availability_coverage"]
                            ),
                            "category_scores": item["category_scores"],
                            "missing_information": (
                                item["missing_information"]
                            ),
                            "explanation": explanation,
                            "matching_method": ranking_result[
                                "matching_method"
                            ],
                            "methodology_version": ranking_result[
                                "methodology_version"
                            ],
                        }
                    )

        log.status = ProcessingLog.Status.SUCCESS
        log.message = (
            f"Pipeline completed. Ranked {len(candidates)} candidates "
            "for JD1 and JD2."
        )
        log.details = {
            "candidates_ranked": len(candidates),
            "jobs_processed": ["JD1", "JD2"],
        }
        log.save(update_fields=["status", "message", "details"])

        # 7. Return this resume's results
        current_id = f"RESUME-{resume.id}"

        return {
            "success": True,
            "resume_id": resume.id,
            "processing_status": "success",
            "rankings": {
                job_id: next(
                    item
                    for item in ranking_result["rankings"][job_id]
                    if item["candidate_identifier"] == current_id
                )
                for job_id in ("JD1", "JD2")
            },
            "classification": classifications.get(current_id, {}),
            "candidates_ranked": len(candidates),
        }

    except Exception as error:
        logger.exception(
            "Full pipeline failed for resume %s", resume.id
        )

        log.status = ProcessingLog.Status.FAILED
        log.message = str(error)
        log.details = {"error_type": type(error).__name__}
        log.save(update_fields=["status", "message", "details"])

        raise