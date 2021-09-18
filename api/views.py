from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from api.utils import api_interaction
from api.utils import sessions
from api.utils import helpers


def index(request):

    user = {}

    # If user submits the form, it will redirect to the user profile page
    if ("summoners_name" and "server") in request.POST:
        summoner_name = request.POST["summoners_name"]
        server = request.POST["server"]
        return redirect("/" + server + "/" + summoner_name + "/")

    sessions.load_champ_json_session(request)

    return render(request, "api/index.html", {"user": user})


def user_info(request, server, summoner_name, template="api/user-profile.html"):
    """
    Get the main data of player from the summoner name and server
    """

    # If user submits the form, it will redirect to the user profile page
    if ("summoners_name" and "server") in request.POST:
        summoner_name = request.POST["summoners_name"]
        server = request.POST["server"]
        return redirect("/" + server + "/" + summoner_name + "/")

    user_account_info, summoner_stats = api_interaction.get_ranked_stats(
        server, summoner_name
    )

    if user_account_info["success"]:

        games_list = api_interaction.get_matchlist(server, user_account_info["puuid"])

        champ_json = sessions.load_champ_json_session(request)

        game_summary_list = helpers.get_game_summary_list(games_list, champ_json, user_account_info["puuid"])

        context = {
            "game_summary_list": game_summary_list,
            "user_account_info": user_account_info,
            "summoner_stats": summoner_stats,
        }

        if request.is_ajax():
            template = "api/include/user-profile-page.html"

        return render(request, template, context)

    # If user not found
    else:
        # Add summoner name searched to display error message indicating that this summoner does not exist
        user_account_info["name"] = summoner_name

        context = {
            "user_account_info": user_account_info,
            "summoner_stats": summoner_stats,
        }
        return render(request, template, context)


def champ_info(request, server, summoner_name, champion_name, template="api/user-champ.html"):
    # If user submits the form, it will redirect to the user profile page
    if ("summoners_name" and "server") in request.POST:
        summoner_name = request.POST["summoners_name"]
        server = request.POST["server"]
        return redirect("/" + server + "/" + summoner_name + "/")

    champ_json = sessions.load_champ_json_session(request)

    user_account_info, summoner_stats = api_interaction.get_champion_stats(
        server, summoner_name, champion_name, champ_json
    )

    if user_account_info["success"]:
        account_id = summoner_stats["accountId"]
        champion_id = summoner_stats["championId"]

        champ_games = api_interaction.get_matchlist(
            server, account_id, champion_id
        )

        game_summary_list = helpers.get_game_summary_list(champ_games, champ_json)

        context = {
            "summoner_stats": summoner_stats,
            "user_account_info": user_account_info,
            "game_summary_list": game_summary_list,
        }

        if request.is_ajax():
            template = "api/include/user-profile-page.html"

        return render(request, template, context)

    # If user not found
    else:
        # Add summoner name searched to display error message indicating that this summoner does not exist
        user_account_info["name"] = summoner_name

        context = {
            "summoner_stats": summoner_stats,
            "user_account_info": user_account_info,
        }
        return render(request, template, context)


def in_game(request, server, summoner_name):
    user, stats = api_interaction.get_ranked_stats(server, summoner_name)
    summoner_id = stats["summonerId"]

    champ_json = sessions.load_champ_json_session(request)

    game_info, blue_players, red_players = api_interaction.in_game_info(
        server, summoner_id, champ_json
    )
    game_info["summoner_name"] = summoner_name

    return render(
        request,
        "api/current.html",
        {
            "game_info": game_info,
            "blue_players": blue_players,
            "red_players": red_players,
        },
    )


def getGameData(request, server, summoner_name, gameId, champion_name = ''):
    champ_json = sessions.load_champ_json_session(request)
    game_data = sessions.load_game_summary(request, server, gameId, champ_json)

    return JsonResponse(game_data)
