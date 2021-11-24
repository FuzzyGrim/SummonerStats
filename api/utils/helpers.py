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
