from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<str:server>/<str:summoner_name>/', views.user_info, name="user_info"),
    path('<str:server>/<str:summoner_name>/<str:champion_name>/', views.champ_info, name="champs_info"),
    path('<str:server>/<game_id>/info', views.game_info, name="game_info"),
]   