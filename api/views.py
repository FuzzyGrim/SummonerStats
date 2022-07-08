"""
Python functions that takes a Web request and returns a Web response.
"""
from django.shortcuts import render, redirect
from django.http import JsonResponse

from api.utils import databases
from api.utils import interactions
from api.utils import sessions
from api.models import Summoner, Match

from asyncio import run

def index(request):
    """Home page"""

    # If user submits the form, it will redirect to the user profile page
    if ("summoners_name" and "server") in request.POST:
        return redirect(
            "/" + request.POST["server"] + "/" + request.POST["summoners_name"] + "/"
        )

    return render(request, "api/index.html")


def user_info(request, server, summoner_name, template="api/profile.html"):
    """Summoners' profile page"""

    # If user submits the form, it will redirect to the user profile page
    if ("summoners_name" and "server") in request.POST:
        return redirect(
            "/" + request.POST["server"] + "/" + request.POST["summoners_name"] + "/"
        )

    summoner, summoner_league = sessions.load_summoner_league(
        request, server, summoner_name
    )

    if summoner["success"]:
        # if summoner not in database, create object for the stats database
        if not Summoner.objects.filter(summoner=summoner_name).exists():
            databases.create_user_db(summoner_name)

        matchlist = interactions.get_matchlist(server, summoner["puuid"])
        databases.add_matches_to_db(matchlist, summoner_name)
        match_not_in_database = databases.find_summaries_not_in_db(
            matchlist, summoner_name
        )

        summoner_db = Summoner.objects.get(summoner=summoner_name)
        summoner_db, match_preview_list = run(interactions.get_match_preview_list(
            match_not_in_database, summoner_db, summoner["puuid"]
        ))

        # order champions in database by number of matches, then by win rate and then by kda
        summoner_db.champions = dict(
            sorted(
                summoner_db.champions.items(),
                key=lambda item: (item[1]["num"], item[1]["win_rate"], item[1]["kda"]),
                reverse=True,
            )
        )
        summoner_db.save()
        databases.save_summaries_to_db(match_preview_list, summoner_name)

        context = {
            "match_list": Match.objects.all().filter(summoner=summoner_name),
            "summoner": summoner,
            "summoner_league": summoner_league,
            "summoner_db": summoner_db,
        }

        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            template = "api/include/matches.html"

    # If user not found
    else:
        context = {"summoner": summoner}

    return render(request, template, context)


def get_match_data(request, server, summoner_name, match_id):
    """
    Loads match information when load button is pressed in user_info
    """
    match_object = Match.objects.get(match_id=match_id, summoner=summoner_name)
    match_info_json = sessions.load_match_summary(
        request, server, match_id, match_object.summary_json["info"]
    )

    return JsonResponse(match_info_json)
