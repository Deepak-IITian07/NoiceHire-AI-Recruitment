from django.shortcuts import get_object_or_404
from django.db.models import F
from rest_framework.generics import ListAPIView

from job_profiles.models import JobProfile
from .models import MatchResult
from .serializers import MatchResultSerializer


class JobRankingView(ListAPIView):
    serializer_class = MatchResultSerializer

    def get_queryset(self):
        job_id = self.kwargs["job_id"]

        job = get_object_or_404(
            JobProfile,
            job_id=job_id
        )

        return (
            MatchResult.objects
            .filter(job_profile=job)
            .select_related("resume", "job_profile")
            .order_by(F("score").desc(nulls_last=True), "-updated_at")
        )