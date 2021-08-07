from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<str:server>/<str:summoner_name>/', views.user_info, name="user_info"),
    path('<str:server>/<str:summoner_name>/<str:champion_name>/info', views.champ_info, name="champs_info"),
    path('<str:server>/<str:summoner_name>/In-Game/', views.in_game, name="in_game"),
]   