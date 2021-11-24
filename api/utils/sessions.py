"""
Functions that manages Django's sessions
"""

from api.utils import interactions


def load_game_summary(request, server, game_id, game_json):
    """
    Session related to the game info
    """
    if game_id in request.session:
        game_data = request.session[game_id]

    else:
        request.session[game_id] = interactions.game_summary(server,
                                                               game_json)
        request.session.set_expiry(0)
        game_data = request.session[game_id]
    return game_data
