from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('show/<int:tv_id>/', views.show_seasons, name='show_seasons'),
    path('show/<int:tv_id>/season/<int:season_number>/', views.show_episodes, name='show_episodes'),
    path('show/<int:tv_id>/season/<int:season_number>/episode/<int:episode_number>/', views.episode_detail, name='episode_detail'),

    # 新增 API
    path('api/translate', views.translate_word, name='api_translate'),  # GET ?word=
    path('api/tts', views.tts_word, name='api_tts'),                    # GET ?word=
]
