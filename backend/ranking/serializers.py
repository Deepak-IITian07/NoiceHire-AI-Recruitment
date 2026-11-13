from rest_framework import serializers
from .models import MatchResult


class MatchResultSerializer(serializers.ModelSerializer):
    candidate_identifier = serializers.CharField(
        source="resume.candidate_identifier",
        read_only=True
    )
    original_filename = serializers.CharField(
        source="resume.original_filename",
        read_only=True
    )
    resume_id = serializers.IntegerField(
        source="resume.id",
        read_only=True
    )
    job_id = serializers.CharField(
        source="job_profile.job_id",
        read_only=True
    )

    class Meta:
        model = MatchResult
        fields = [
            "id",
            "resume_id",
            "candidate_identifier",
            "original_filename",
            "job_id",
            "score",
            "information_availability_coverage",
            "category_scores",
            "missing_information",
            "explanation",
            "matching_method",
            "methodology_version",
            "created_at",
            "updated_at",
        ]