from django.urls import path
from .views import JobRankingView

urlpatterns = [
    path("<str:job_id>/", JobRankingView.as_view(), name="job-ranking"),
]