# Contains functions that consists of code that will be used multiple times in views.py
from api import api_interaction

def load_champ_json_session(request):
    if 'patch' in request.session:
            patch = request.session['patch']
    else:
        request.session['patch'] = api_interaction.get_current_patch()
        request.session.set_expiry(0)
        patch = request.session['patch']
    if 'ddragon_champion_json' in request.session:
        champ_json = request.session['ddragon_champion_json']
    else:
        request.session['ddragon_champion_json'] = api_interaction.get_ddragon_champion_json(patch)
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

def get_game_summary_list(games, champ_json):
    game_summary_list = []

    for match in games:
        game_dict = {}
        champ_name = api_interaction.get_champion_name(match['champion'], champ_json)
        position, order = api_interaction.get_position(match['lane'], match['role'])
        game_date = api_interaction.get_game_date(match['timestamp'])
        game_dict['champion_name'] = champ_name
        game_dict['position'] = position
        game_dict['date'] = game_date
        game_dict['game_id'] = str(match['gameId'])
        game_dict['champion'] = match['champion']

        game_summary_list.append(game_dict)

    return game_summary_list