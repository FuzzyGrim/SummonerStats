"""
Functions that performs part of the computation of another function, usually from interactions.py
because the functionality is needed in multiple places.
"""


import datetime
import requests
from decouple import config

API_KEY = config("API")

def get_date_by_timestamp(game_timestamp):
    """Game date from unix timestamp

    Args:
        game_timestamp (int): Unix timestamp for when the game is created on the game server

    Returns:
        str: date when game was created, e.g 2021-11-24
    """

    return str((datetime.datetime.fromtimestamp(game_timestamp / 1000.0)).date())


def get_region_by_platform(platform):
    """
    The AMERICAS routing value serves NA, BR, LAN, LAS, and OCE.
    The ASIA routing value serves KR and JP.
    The EUROPE routing value serves EUNE, EUW, TR, and RU.
    """
    if platform in ("NA1", "BR1", "LA1", "LA2", "OC1"):
        region = "AMERICAS"

    elif platform in ("EUN1", "EUW1", "TR1", "RU"):
        region = "EUROPE"

    elif platform in ("KR", "JP1"):
        region = "ASIA"

    return region

def get_game_mode(queue_id):
    """
    Get game mode by the queue_id
    """
    match queue_id:
        case 400:
            return "Normal Draft"
        case 420:
            return "Ranked Solo"
        case 430:
            return "Normal Blind"
        case _:
            return "Special"

def get_summoner_spell(summoner_key):
    """
    Get summoner spell by the summoner_key
    """
    match summoner_key:
        case 1:
            return "summoner_boost"
        case 3:
            return "summoner_exhaust"
        case 4:
            return "summoner_flash"
        case 6:
            return "summoner_haste"
        case 7:
            return "summoner_heal"
        case 11:
            return "summoner_smite"
        case 12:
            return "summoner_teleport"
        case 13:
            return "summonermana"
        case 14:
            return "summonerignite"
        case 21:
            return "summonerbarrier"
        case 32:
            return "summoner_mark"
        case _:
            return "summoner_empty"

def get_rune_primary(rune_id):
    url = "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/perks.json"
    data_json = requests.get(url).json()
    rune_dict =  next((item for item in data_json if item['id'] == rune_id), None)
    return rune_dict["iconPath"].split("Styles/",1)[1]

def get_rune_secondary(rune_id):
    """
    Get rune by the rune_id
    """
    match rune_id:
        case 8000:
            return "7201_precision"
        case 8100:
            return "7200_domination"
        case 8200:
            return "7202_sorcery"
        case 8300:
            return "7203_whimsy"
        case _:
            return "7204_resolve"