"""Functions that manages Django's sessions"""

from api.utils import interactions


def load_summoner(request, server, summoner_name):
    """Session related to the summoner info"""
    if summoner_name in request.session:
        summoner_data = request.session[summoner_name]

    else:
        request.session[summoner_name] = interactions.get_summoner(server, summoner_name)
        summoner_data = request.session[summoner_name]
    return summoner_data


def load_summoner_league(request, server, summoner_name):
    """Session related to the summoner league info"""
    summoner_name_league = summoner_name + "_league"
    if summoner_name_league in request.session:
        summoner_league_data = request.session[summoner_name_league]

    else:
        request.session[summoner_name_league] = interactions.get_summoner_league(request, server, summoner_name)
        summoner_league_data = request.session[summoner_name_league]
    return summoner_league_data


def load_game_summary(request, server, game_id, game_json):
    """Session related to the game info"""

    if game_id in request.session:
        game_data = request.session[game_id]

    else:
        request.session[game_id] = interactions.game_summary(server, game_json)
        game_data = request.session[game_id]
    return game_data
