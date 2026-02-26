from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('events/', include('events.urls')),
    path('compiler/', include('compiler.urls')),
    path('', TemplateView.as_view(template_name='index.html'), name='index'),
]
