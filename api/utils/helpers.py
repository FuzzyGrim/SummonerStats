# Helper functions that doesn´t interact with riot API
import datetime
import requests
from decouple import config
import aiohttp
import asyncio

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

def get_game_summary_list(games, champ_json, puuid=None):
    game_summary_list = []

    for match in games:
        game_dict = {}
        platform = (match.split("_"))[0]
        region = get_region_by_platform(platform)
        URL = "https://" + region + ".api.riotgames.com/lol/match/v5/matches/" + match + "?api_key=" + API_KEY
        game_json = get_response_json(URL)
        participant_number = 0
        for player in game_json["metadata"]["participants"]:

            if player == puuid:
                break
            else:
                participant_number += 1

        player_json = game_json["info"]["participants"][participant_number]
        champ_name = player_json["championName"]
        position = player_json["teamPosition"]
        game_date = get_date_by_timestamp(game_json["info"]['gameCreation'])
        game_dict['champion_name'] = champ_name
        game_dict['position'] = position
        game_dict['date'] = game_date
        game_dict['game_id'] = str(game_json["metadata"]['matchId'])
        
        game_summary_list.append(game_dict)

    return game_summary_list

def get_region_by_platform(platform):
    if platform == "NA1" or platform == "BR1" or platform == "LA1" or platform == "LA2" or platform == "OC1":
        region = "AMERICAS"
        return region

    elif platform == "EUN1" or platform == "EUW1" or platform == "TR1" or platform == "RU":
        region = "EUROPE"
        return region
        
    elif platform == "KR" or platform == "JP1":
        region = "ASIA"
        return region