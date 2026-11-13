from rest_framework import serializers
from .models import JobProfile


class JobProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobProfile
        fields = [
            "id",
            "job_id",
            "title",
            "original_description",
            "role_summary",
            "mandatory_criteria",
            "preferred_criteria",
            "responsibilities",
            "synonyms",
            "scoring_criteria",
            "created_at",
            "updated_at",
        ]