# Functions that manages Django's sessions

from api.utils import api_interaction


def load_game_summary(request, server, gameId, game_json):
    if gameId in request.session:
        game_data = request.session[gameId]
        print('already in session')

    else:
        request.session[gameId] = api_interaction.game_summary(server,
                                                               game_json)
        request.session.set_expiry(0)
        game_data = request.session[gameId]
    return game_data
