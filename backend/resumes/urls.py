from django.urls import path
from .views import (
    ResumeUploadView,
    ResumeListView,
    ResumeDetailView,
    ResumeProcessView,
    ResumeStatusView,
)

urlpatterns = [
    path("", ResumeListView.as_view(), name="resume-list"),
    path("upload/", ResumeUploadView.as_view(), name="resume-upload"),
    path("<int:pk>/", ResumeDetailView.as_view(), name="resume-detail"),
    path("<int:pk>/process/", ResumeProcessView.as_view(), name="resume-process"),
    path("<int:pk>/status/", ResumeStatusView.as_view(), name="resume-status"),
]