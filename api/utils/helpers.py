"""
Functions that performs part of the computation of another function, usually from interactions.py
because the functionality is needed in multiple places.
"""


import datetime
import requests
from decouple import config

API_KEY = config("API")


def get_response_json(url):
    """Get json file from url
    Args:
        url (string): Riot API endpoint url

    Returns:
        dictionary: json
    """

    return requests.get(url).json()


def get_date_by_timestamp(game_timestamp):
    """Game date from unix timestamp

    Args:
        game_timestamp (int): Unix timestamp for when the game is created on the game serve

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
    if queue_id == 400:
        queue_id = "Normal Draft"

    elif queue_id == 420:
        queue_id = "Ranked Solo"

    elif queue_id == 430:
        queue_id = "Normal Blind"

    else:
        queue_id = "Special"

    return queue_id

def get_summoner_spell(summoner_key):
    """
    Get summoner spell by the summoner_key
    """
    if summoner_key == 1:
        summoner_key = "summoner_boost"

    elif summoner_key == 3:
        summoner_key = "summoner_exhaust"

    elif summoner_key == 4:
        summoner_key = "summoner_flash"

    elif summoner_key == 6:
        summoner_key = "summoner_haste"

    elif summoner_key == 7:
        summoner_key = "summoner_heal"

    elif summoner_key == 11:
        summoner_key = "summoner_smite"

    elif summoner_key == 12:
        summoner_key = "summoner_teleport"

    elif summoner_key == 13:
        summoner_key = "summonermana"

    elif summoner_key == 14:
        summoner_key = "summonerignite"
        
    elif summoner_key == 21:
        summoner_key = "summonerbarrier"

    elif summoner_key == 32:
        summoner_key = "summoner_mark"

    else:
        summoner_key = "summoner_empty"
    
    return summoner_key

def get_rune_primary(rune_id):
    url = "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/perks.json"
    response = requests.get(url)
    data_json = response.json()
    rune_dict =  next((item for item in data_json if item['id'] == rune_id), None)
    return rune_dict["iconPath"].split("Styles/",1)[1]

    
def get_rune_secondary(rune_id):
    """
    Get rune by the rune_id
    """
    if rune_id == 8000:
        rune_id = "7201_precision"

    elif rune_id == 8100:
        rune_id = "7200_domination"
    
    elif rune_id == 8200:
        rune_id = "7202_sorcery"
    
    elif rune_id == 8300:
        rune_id = "7203_whimsy"

    else:
        rune_id = "7204_resolve"

    return rune_id