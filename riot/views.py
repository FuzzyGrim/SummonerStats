from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from riot import api_interaction
from riot import services

def index(request):

    user = {}

    # If user submits the form, it will redirect to the user profile page
    if ("summoners_name" and "server") in request.POST:
        summoner_name = request.POST["summoners_name"]
        server = request.POST["server"]
        return redirect("/" + server + "/" + summoner_name + "/")

    services.load_champ_json_session(request)

    return render(request, "riot/index.html", {"user": user})


def user_info(request, server, summoner_name, template="riot/user-profile.html"):
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

        account_id = user_account_info["accountId"]

        games_list = api_interaction.get_past_games(server, account_id)

        champ_json = services.load_champ_json_session(request)

        game_summary_list = services.get_game_summary_list(games_list, champ_json)

        context = {
            "game_summary_list": game_summary_list,
            "user_account_info": user_account_info,
            "summoner_stats": summoner_stats,
        }

        if request.is_ajax():
            template = "riot/include/user-profile-page.html"

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


def champ_info(
    request, server, summoner_name, champion_name, template="riot/user-champ.html"
):
    # If user submits the form, it will redirect to the user profile page
    if ("summoners_name" and "server") in request.POST:
        summoner_name = request.POST["summoners_name"]
        server = request.POST["server"]
        return redirect("/" + server + "/" + summoner_name + "/")

    champ_json = services.load_champ_json_session(request)

    user_account_info, summoner_stats = api_interaction.get_champion_stats(
        server, summoner_name, champion_name, champ_json
    )

    if user_account_info["success"]:
        server = summoner_stats["server"]
        account_id = summoner_stats["accountId"]
        champion_id = summoner_stats["championId"]

        champ_games = api_interaction.get_champion_matchlist(
            server, account_id, champion_id
        )

        game_summary_list = services.get_game_summary_list(champ_games, champ_json)

        context = {
            "summoner_stats": summoner_stats,
            "user_account_info": user_account_info,
            "game_summary_list": game_summary_list,
        }

        if request.is_ajax():
            template = "riot/include/user-profile-page.html"

        if ("load") in request.POST:
            gameId = request.POST["load"]

            game_data = api_interaction.game_summary(server, gameId, champ_json)
            context["game_data"] = game_data
            return render(request, template, context)

        return render(request, template, context)

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

    champ_json = services.load_champ_json_session(request)

    game_info, blue_players, red_players = api_interaction.in_game_info(
        server, summoner_id, champ_json
    )
    game_info["summoner_name"] = summoner_name

    return render(
        request,
        "riot/current.html",
        {
            "game_info": game_info,
            "blue_players": blue_players,
            "red_players": red_players,
        },
    )


def getGameData(request, server, summoner_name, gameId):
    champ_json = services.load_champ_json_session(request)
    game_data = api_interaction.game_summary(server, gameId, champ_json)

    return JsonResponse(game_data)
