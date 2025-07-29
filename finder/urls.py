# finder/urls.py
from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('show/<int:tv_id>/', views.show_seasons, name='show_seasons'),
]


