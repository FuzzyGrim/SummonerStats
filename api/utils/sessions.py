"""Functions that manages Django's sessions"""

from api.utils import interactions
from requests import get


def load_summoner(request, server, summoner_name):
    """Session related to the summoner info"""
    if summoner_name in request.session:
        summoner_data = request.session[summoner_name]

    else:
        request.session[summoner_name] = interactions.get_summoner(
            server, summoner_name
        )
        summoner_data = request.session[summoner_name]
    return summoner_data

    
def load_summoner_league(request, server, summoner_name):
    """Session related to the summoner league info"""
    summoner_name_league = summoner_name + "_league"

    if summoner_name_league not in request.session:
        request.session[summoner_name_league] = interactions.get_summoner_league(request, server, summoner_name)

    return request.session[summoner_name_league]


def load_match_summary(request, server, match_id, match_json):
    """Session related to the match info"""

    if match_id in request.session:
        match_data = request.session[match_id]

    else:
        request.session[match_id] = interactions.match_summary(server, match_json)
        match_data = request.session[match_id]
    return match_data

def load_perks_json(request):
    """Session related to the perks info"""
    if "perks" not in request.session:
        request.session["perks"] = get("https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/perks.json").json()
        
    return request.session["perks"]