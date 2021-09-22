from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<str:server>/<str:summoner_name>/", views.user_info),
    path("<str:server>/<str:summoner_name>/tmp/<str:gameId>/", views.getGameData),
    path("<str:server>/<str:summoner_name>/In-Game/", views.in_game),
]
