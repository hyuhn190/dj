# finder/urls.py
from django.urls import path
from . import views


# finder/urls.py
urlpatterns = [
    path('', views.index, name='index'),
    path('show/<int:tv_id>/', views.show_seasons, name='show_seasons'),
    path('show/<int:tv_id>/season/<int:season_number>/', views.show_episodes, name='show_episodes'),
    path('show/<int:tv_id>/season/<int:season_number>/episode/<int:episode_number>/', views.episode_detail, name='episode_detail'),
]


