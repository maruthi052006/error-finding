from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.participant_dashboard, name='participant_dashboard'),
    path('language/<int:round_id>/', views.language_selection, name='language_selection'),
    path('problems/<int:round_id>/', views.problem_list, name='problem_list'),
    path('editor/<int:problem_id>/', views.compiler_view, name='compiler_view'),
    path('execute/', views.execute_code, name='execute_code'),
    path('save_code/', views.save_code, name='save_code'),
]
