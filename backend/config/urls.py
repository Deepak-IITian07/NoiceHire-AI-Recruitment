from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from .views import test_api

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/test/', test_api),
    path('api/resumes/', include('resumes.urls')),
    path("api/jobs/", include("job_profiles.urls")),
    path("api/rankings/", include("ranking.urls")),
    path('api/auth/', include('config.auth_urls')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
