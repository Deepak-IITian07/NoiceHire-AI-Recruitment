
from django.urls import path
from .auth_views import HRLoginView, HRLogoutView

urlpatterns = [
    path('login/', HRLoginView.as_view(), name='hr-login'),
    path('logout/', HRLogoutView.as_view(), name='hr-logout'),
]
