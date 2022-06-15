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

    user_account_info, ranked_data = api.utils.interactions.get_ranked_stats(
        server, summoner_name
    )

    if user_account_info["success"]:
#"deaths" : 0, "assists" : 0, "minions" : 0, "vision" : 0, "minutes" : 0
        # if summoner not in database, create object for the stats database
        if not api.models.Summoner.objects.filter(summoner=summoner_name).exists():
            api.models.Summoner.objects.create(summoner=summoner_name,
            stats={"kills" : {"total" : 0, "per_min" : 0, "per_game": 0},
                   "deaths" : {"total" : 0, "per_min" : 0, "per_game": 0},
                   "assists" : {"total" : 0, "per_min" : 0, "per_game": 0},
                   "minions" : {"total" : 0, "per_min" : 0, "per_game": 0},
                   "vision" : {"total" : 0, "per_min" : 0, "per_game": 0}},
            roles={"TOP": {"NUM" : 0,  "WR" : 0, "WINS" : 0, "LOSSES" : 0},
                   "JUNGLE": {"NUM" : 0, "WR" : 0, "WINS" : 0, "LOSSES" : 0},
                   "MIDDLE": {"NUM" : 0, "WR" : 0, "WINS" : 0, "LOSSES" : 0},
                   "BOTTOM": {"NUM" : 0, "WR" : 0, "WINS" : 0, "LOSSES" : 0},
                   "UTILITY": {"NUM" : 0, "WR" : 0, "WINS" : 0, "LOSSES" : 0}})

        games_list = api.utils.interactions.get_matchlist(
            server, user_account_info["puuid"])

        summary_not_in_database = []

        for match in games_list:

            if match == 'status':
                continue

            # if match id with summoner name not found, create object in database
            if not api.models.Match.objects.filter(match_id=match,
                                        summoner=summoner_name).exists():

                api.models.Match.objects.create(match_id=match, summoner=summoner_name)

            # if match summary not in database, add it to the list
            if api.models.Match.objects.filter(match_id=match, summoner=summoner_name,
                                    summary_json__exact={}).exists():
                summary_not_in_database.append(match)

        summoner_db = api.models.Summoner.objects.get(summoner=summoner_name)

        summoner_db, game_summary_list = api.utils.interactions.get_game_summary_list(
                                                    summary_not_in_database,
                                                    summoner_db,
                                                    user_account_info["puuid"])
        
        # order champions in database by number of games
        summoner_db.champions = dict(sorted(summoner_db.champions.items(), key=lambda item: item[1]["num"], reverse=True))

        summoner_db.save()

        for game in game_summary_list:
            game_object = api.models.Match.objects.get(match_id=game["game_id"],
                                            summoner=summoner_name)
            game_object.summary_json = game
            game_object.save()

        context = {
            "game_list": api.models.Match.objects.all().filter(summoner=summoner_name).order_by('-match_id'),
            "game_summary_list": game_summary_list,
            "user_account_info": user_account_info,
            "ranked_data": ranked_data,
            "summoner_db": summoner_db,
        }

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            template = "api/include/games.html"

    # If user not found
    else:
        # Save summoner search for later indicating error
        user_account_info["name"] = summoner_name

        context = {
            "user_account_info": user_account_info,
            "ranked_data": ranked_data,
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

def is_ajax(request):
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'