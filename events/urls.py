from django.urls import path
from . import views

urlpatterns = [
    path('coordinator/', views.coordinator_dashboard, name='coordinator_dashboard'),
    path('coordinator/upload/', views.upload_problem, name='upload_problem'),
    path('coordinator/analytics/', views.analytics_view, name='analytics'),
]
