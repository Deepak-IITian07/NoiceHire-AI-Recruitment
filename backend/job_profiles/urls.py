from django.urls import path
from .views import JobProfileListView, JobProfileDetailView

urlpatterns = [
    path("", JobProfileListView.as_view(), name="job-list"),
    path("<int:pk>/", JobProfileDetailView.as_view(), name="job-detail"),
]