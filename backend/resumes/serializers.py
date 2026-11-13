from rest_framework import serializers
from .models import Resume, CandidateProfile


class ResumeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = [
            "id",
            "candidate_identifier",
            "original_filename",
            "extraction_status",
            "page_count",
            "uploaded_at",
        ]


class ResumeDetailSerializer(serializers.ModelSerializer):
    candidate_data = serializers.SerializerMethodField()

    class Meta:
        model = Resume
        fields = [
            "id",
            "candidate_identifier",
            "original_filename",
            "file_url",
            "extraction_status",
            "extraction_error",
            "page_count",
            "extracted_text",
            "candidate_data",
            "uploaded_at",
        ]

    def get_candidate_data(self, obj):
        try:
            return obj.candidate_profile.candidate_data
        except CandidateProfile.DoesNotExist:
            return {}
    
    file_url = serializers.SerializerMethodField()

    def get_file_url(self, obj):
        if not obj.file:
            return None

        request = self.context.get("request")
        url = obj.file.url

        return request.build_absolute_uri(url) if request else url