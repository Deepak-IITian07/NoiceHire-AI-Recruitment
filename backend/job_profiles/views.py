from rest_framework.generics import ListAPIView, RetrieveAPIView

from .models import JobProfile
from .serializers import JobProfileSerializer


class JobProfileListView(ListAPIView):
    queryset = JobProfile.objects.all().order_by("id")
    serializer_class = JobProfileSerializer


class JobProfileDetailView(RetrieveAPIView):
    queryset = JobProfile.objects.all()
    serializer_class = JobProfileSerializer