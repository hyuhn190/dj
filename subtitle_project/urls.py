# subtitle_project/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('finder.urls')),
    path('admin/', admin.site.urls),
]
