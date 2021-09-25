# Helper functions that doesn´t interact with riot API
import datetime
import requests
from decouple import config

API_KEY = config("API")


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
        "https://ddragon.leagueoflegends.com/cdn/" + patch +
        "/data/en_US/champion.json"
    )
    json = request.json()
    champion_json = json["data"]

    return champion_json


def get_current_patch():
    request = requests.get(
        "https://ddragon.leagueoflegends.com/realms/na.json")
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


def get_region_by_platform(platform):
    if platform in ("NA1", "BR1", "LA1", "LA2", "OC1"):
        region = "AMERICAS"
        return region

    elif platform in ("EUN1", "EUW1", "TR1", "RU"):
        region = "EUROPE"
        return region

    elif platform in ("KR", "JP1"):
        region = "ASIA"
        return region
