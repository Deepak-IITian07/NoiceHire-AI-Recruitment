
from django.db import migrations


def copy_candidate_data(apps, schema_editor):
    Resume = apps.get_model("resumes", "Resume")
    CandidateProfile = apps.get_model(
        "resumes", "CandidateProfile"
    )

    for resume in Resume.objects.all().iterator():
        CandidateProfile.objects.update_or_create(
            resume_id=resume.id,
            defaults={
                "candidate_data": resume.candidate_data or {}
            },
        )


def reverse_copy_candidate_data(apps, schema_editor):
    Resume = apps.get_model("resumes", "Resume")
    CandidateProfile = apps.get_model(
        "resumes", "CandidateProfile"
    )

    for profile in CandidateProfile.objects.select_related(
        "resume"
    ).iterator():
        Resume.objects.filter(id=profile.resume_id).update(
            candidate_data=profile.candidate_data
        )


class Migration(migrations.Migration):

    dependencies = [
        ("resumes", "0004_candidateprofile_processinglog"),
    ]

    operations = [
        migrations.RunPython(
            copy_candidate_data,
            reverse_copy_candidate_data,
        ),
    ]
