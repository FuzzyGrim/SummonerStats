# Helper functions that doesn´t interact with riot API
import datetime
import requests

def get_response_json(URL):
    return requests.get(URL).json()

def get_date_by_timestamp(timestamp):

    unix_milliseconds = datetime.date.fromtimestamp(timestamp / 1000.0)
    today = datetime.date.today()
    time_diff = abs((today - unix_milliseconds).days)
    if time_diff == 0:
        game_date = "Today"
    elif time_diff == 1:
        game_date = "Yesterday"
    else:
        game_date = str(time_diff) + " days ago"

    return game_date

def get_champion_name(champion_key, champ_json):

    key = str(champion_key)
    by_key = {x["key"]: x for x in champ_json.values()}
    champ_name = by_key.get(key)["id"]

    return champ_name

def get_champion_key(champion_name, champ_json):
    by_id = {x["id"]: x for x in champ_json.values()}
    champ_key = by_id.get(champion_name)["key"]

    return champ_key

def get_ddragon_champion_json(patch):
    request = requests.get(
        "https://ddragon.leagueoflegends.com/cdn/" + patch + "/data/en_US/champion.json"
    )
    json = request.json()
    champion_json = json["data"]

    return champion_json

def get_current_patch():
    request = requests.get("https://ddragon.leagueoflegends.com/realms/na.json")
    json = request.json()
    patch = json["dd"]
    return patch

def get_position(lane, role):

    if lane == "BOTTOM":
        position = role[4:]
    else:
        position = lane

    if position == "TOP":
        order = 1
    elif position == "JUNGLE":
        order = 2
    elif position == "MIDDLE":
        order = 3
    elif position == "CARRY":
        order = 4
    elif position == "SUPPORT":
        order = 5
    else:
        order = 0

    return position, order

def get_game_summary_list(games, champ_json):
    game_summary_list = []

    for match in games:
        game_dict = {}
        champ_name = get_champion_name(match['champion'], champ_json)
        position, order = get_position(match['lane'], match['role'])
        game_date = get_date_by_timestamp(match['timestamp'])
        game_dict['champion_name'] = champ_name
        game_dict['position'] = position
        game_dict['date'] = game_date
        game_dict['game_id'] = str(match['gameId'])
        game_dict['champion'] = match['champion']

        game_summary_list.append(game_dict)

    return game_summary_list