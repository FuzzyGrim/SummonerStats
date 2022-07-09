from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<str:server>/<str:summoner_name>/", views.user_info),
    path("<str:server>/<str:summoner_name>/refresh", views.summoner_stats_refresh),
    path("<str:server>/<str:summoner_name>/<str:match_id>/", views.get_match_data),
]