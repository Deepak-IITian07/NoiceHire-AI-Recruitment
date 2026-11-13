from django.contrib import admin
from .models import CandidateProfile, ProcessingLog

# Register your models here.
admin.site.register(CandidateProfile)
admin.site.register(ProcessingLog)