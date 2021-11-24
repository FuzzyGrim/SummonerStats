"""
Python functions that takes a Web request and returns a Web response.
"""
from django.shortcuts import render, redirect
from django.http import JsonResponse

from api.utils import interactions
from api.utils import sessions
import api.models

def index(request):
    """
    Home page
    """
    user = {}

    # If user submits the form, it will redirect to the user profile page
    if ("summoners_name" and "server") in request.POST:
        summoner_name = request.POST["summoners_name"]
        server = request.POST["server"]
        return redirect("/" + server + "/" + summoner_name + "/")

    return render(request, "api/index.html", {"user": user})


def user_info(request,
              server,
              summoner_name,
              template="api/profile.html"):
    """
    Summoners' profile page
    """

    # If user submits the form, it will redirect to the user profile page
    if ("summoners_name" and "server") in request.POST:
        summoner_name = request.POST["summoners_name"]
        server = request.POST["server"]
        return redirect("/" + server + "/" + summoner_name + "/")

    user_account_info, summoner_stats = api.utils.interactions.get_ranked_stats(
        server, summoner_name
    )

    if user_account_info["success"]:

        games_list = api.utils.interactions.get_matchlist(
            server, user_account_info["puuid"])

        summary_not_in_database = []

        # Add match id to database if it's not in there
        for match in games_list:

            if match == 'status':
                continue

            if not api.models.Match.objects.filter(match_id=match,
                                        summoner=summoner_name).exists():

                match_object = api.models.Match(match_id=match, summoner=summoner_name)
                match_object.save()

            if api.models.Match.objects.filter(match_id=match, summoner=summoner_name,
                                    summary_json__exact={}).exists():
                summary_not_in_database.append(match)

        game_summary_list = api.utils.interactions.get_game_summary_list(
                                                    summary_not_in_database,
                                                    user_account_info["puuid"])

        for game in game_summary_list:
            game_object = api.models.Match.objects.get(match_id=game["game_id"],
                                            summoner=summoner_name)
            game_object.summary_json = game
            game_object.save()

        context = {
            "game_list": api.models.Match.objects.all().filter(summoner=summoner_name),
            "game_summary_list": game_summary_list,
            "user_account_info": user_account_info,
            "summoner_stats": summoner_stats,
        }

        if request.is_ajax():
            template = "api/include/games.html"

    # If user not found
    else:
        # Save summoner search for later indicating error
        user_account_info["name"] = summoner_name

        context = {
            "user_account_info": user_account_info,
            "summoner_stats": summoner_stats,
        }
    return render(request, template, context)


def get_game_data(request, server, summoner_name, game_id):
    """
    Loads game information when load button is pressed in user_info
    """

    game_data = api.models.Match.objects.get(match_id=game_id, summoner=summoner_name)
    game_general_json = game_data.summary_json
    game_info_json = game_general_json['game_summary']['info']
    game_info_json = api.utils.sessions.load_game_summary(request, server,
                                                game_id, game_info_json)

    return JsonResponse(game_info_json)
