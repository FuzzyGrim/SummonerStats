# Functions that manages Django's sessions

from api.utils import api_interaction  # pylint: disable=import-error
from api.utils import helpers  # pylint: disable=import-error

def load_champ_json_session(request):
    if 'patch' in request.session:
            patch = request.session['patch']
    else:
        request.session['patch'] = helpers.get_current_patch()
        request.session.set_expiry(0)
        patch = request.session['patch']
    if 'ddragon_champion_json' in request.session:
        champ_json = request.session['ddragon_champion_json']
    else:
        request.session['ddragon_champion_json'] = helpers.get_ddragon_champion_json(patch)
        request.session.set_expiry(0)
        champ_json = request.session['ddragon_champion_json']
    return champ_json

def load_game_summary(request, server, gameId, champ_json):
    if gameId in request.session:
        game_data = request.session[gameId]

    else:
        request.session[gameId] = api_interaction.game_summary(server, gameId, champ_json)
        request.session.set_expiry(0)
        game_data = request.session[gameId]
    return game_data
