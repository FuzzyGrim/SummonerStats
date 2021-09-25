from django.shortcuts import render, redirect
from django.http import JsonResponse
# from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from api.utils import api_interaction
from api.utils import sessions

from el_pagination import utils
from api.models import Match


def index(request):

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
              template="api/user-profile.html"):
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

        games_list = api_interaction.get_matchlist(
            server, user_account_info["puuid"])

        summary_not_in_database = []

        # Add match id to database if it's not in there
        for match in games_list:

            if match == 'status':
                continue

            if not Match.objects.filter(match_id=match,
                                        summoner=summoner_name).exists():

                match_object = Match(match_id=match, summoner=summoner_name)
                match_object.save()

            if Match.objects.filter(match_id=match, summoner=summoner_name,
                                    summary_json__exact={}).exists():
                summary_not_in_database.append(match)

        page = utils.get_page_number_from_request(request)

        game_summary_list = api_interaction.get_game_summary_list(
                                                    summary_not_in_database,
                                                    user_account_info["puuid"],
                                                    summoner_name,
                                                    page)

        for game in game_summary_list:
            game_object = Match.objects.get(match_id=game["game_id"],
                                            summoner=summoner_name)
            game_object.summary_json = game
            game_object.save()

        context = {
            "game_list": Match.objects.all().filter(summoner=summoner_name),
            "game_summary_list": game_summary_list,
            "user_account_info": user_account_info,
            "summoner_stats": summoner_stats,
        }

        if request.is_ajax():
            template = "api/include/user-profile-page.html"

        return render(request, template, context)

    # If user not found
    else:
        # Save summoner search for later indicating error
        user_account_info["name"] = summoner_name

        context = {
            "user_account_info": user_account_info,
            "summoner_stats": summoner_stats,
        }
        return render(request, template, context)


def getGameData(request, server, summoner_name, gameId):

    game_data = Match.objects.get(match_id=gameId, summoner=summoner_name)
    game_general_json = game_data.summary_json
    game_info_json = game_general_json['game_summary']['info']
    game_info_json = sessions.load_game_summary(request, server,
                                                gameId, game_info_json)

    return JsonResponse(game_info_json)
