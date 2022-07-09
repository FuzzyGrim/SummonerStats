"""
Functions that performs part of the computation of another function, usually from interactions.py
because the functionality is needed in multiple places.
"""

from datetime import datetime
from requests import get
from decouple import config
from time import sleep

API_KEY = config("API")


def get_response(url):
    """Get response from url"""
    max_attempts = 3
    attempts = 0
    while attempts < max_attempts:
        response = get(url)
        if response.status_code == 200:
            return response
        elif response.status_code == 429:
            print(
                "Rate limit exceeded, sleeping for "
                + response.headers["Retry-After"]
                + " seconds"
            )
            sleep(int(response.headers["Retry-After"]))
        attempts += 1
    if attempts >= max_attempts:
        raise Exception("Failed: Maxed out attempts")


def get_participant_number(match, puuid):
    """ind summoner participant number in the match"""
    participant_number = 0
    while match["metadata"]["participants"][participant_number] != puuid:
        participant_number += 1
    return participant_number


def get_preview_stats(player_summary, game_duration):
    player_summary["cs"] = (
        player_summary["totalMinionsKilled"] + player_summary["neutralMinionsKilled"]
    )

    player_summary["cs_per_min"] = round(
        (player_summary["totalMinionsKilled"] + player_summary["neutralMinionsKilled"])
        / game_duration,
        1,
    )
    # Some match modes doesn't have challenges sections such as URF
    if "challenges" in player_summary:

        # Sometimes the killParticipation challenges is not available, e.g: remake matches
        if "killParticipation" in player_summary["challenges"]:
            player_summary["challenges"]["kill_participation_percentage"] = round(
                player_summary["challenges"]["killParticipation"] * 100,
                1,
            )
        else:
            player_summary["challenges"]["kill_participation_percentage"] = "ERROR"
    else:
        player_summary["challenges"] = {}
        player_summary["challenges"]["kill_participation_percentage"] = "ERROR"

    player_summary["gold_short"] = round(
        player_summary["goldEarned"] / 1000,
        1,
    )
    player_summary["damage_short"] = round(
        player_summary["totalDamageDealtToChampions"] / 1000,
        1,
    )
    return player_summary


def get_date_by_timestamp(match_timestamp):
    """match date from unix timestamp

    Args:
        match_timestamp (int): Unix timestamp for when the match is created on the match server

    Returns:
        str: date when match was created, e.g 2021-11-24
    """

    return str((datetime.fromtimestamp(match_timestamp / 1000.0)).date())


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


def get_match_mode(queue_id):
    """Get match mode by the queue_id"""
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
    """Get summoner spell by the summoner_key"""
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
    data_json = get(url).json()
    rune_dict = next((item for item in data_json if item["id"] == rune_id), None)
    return rune_dict["iconPath"].split("Styles/", 1)[1]


def get_rune_secondary(rune_id):
    """Get rune by the rune_id"""
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
