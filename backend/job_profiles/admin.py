from django.contrib import admin
from .models import JobProfile


@admin.register(JobProfile)
class JobProfileAdmin(admin.ModelAdmin):
    list_display = ("job_id", "title", "created_at", "updated_at")
    search_fields = ("job_id", "title")
    readonly_fields = ("created_at", "updated_at")