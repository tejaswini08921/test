from django.urls import path
from . import views  # Import from current app

urlpatterns = [
    path('create-resume/', views.create_ats_friendly_resume, name='create_resume'),
]