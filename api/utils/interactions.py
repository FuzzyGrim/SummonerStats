"""
Contains functions that interacts with RIOT's API.
"""

import asyncio
import datetime
import requests
from decouple import config
import aiohttp
from api.utils import helpers

from pprint import pprint


API_KEY = config("API")


def get_identifiable_data(server, summoner_name):
    """Request:
    https://SERVER.api.riotgames.com/lol/summoner/v4/summoners/by-name/SUMMONER_NAME

    Args:
        server              (string)    Player's region
        summoner_name       (string)    Summoner name

    Returns:
        JSON with:
            profileIconId 	(int)
            revisionDate 	(long) 	    Date last modified in epoch milliseconds.
            name 	        (string) 	Summoner name.
            id 	            (string) 	Encrypted summoner ID.
            puuid 	        (string) 	Encrypted PUUID.
            summonerLevel 	(long)
    """

    url = (
        "https://"
        + server
        + ".api.riotgames.com/lol/summoner/v4/summoners/by-name/"
        + summoner_name
        + "?api_key="
        + API_KEY
    )
    response = requests.get(url)

    user_json = response.json()
    user_json["success"] = response.status_code == 200
    user_json["user_not_found"] = response.status_code == 404
    return user_json


def get_ranked_stats(server, summoner_name):
    """Request:
    https://SERVER.api.riotgames.com/lol/league/v4/entries/by-summoner/SUMMONER_ID

    Args:
        server              (string)    Player's region
        summoner_name       (string)    Summoner name

    Returns:
        JSON with:
            leagueId 	    (string)
            summonerId 	    (string) 	Player's encrypted summonerId.
            summonerName 	(string)
            queueType 	    (string) 	eg: RANKED_SOLO_5x5
            tier 	        (string)
            rank 	        (string) 	The player's division within a tier.
            leaguePoints 	(int)       Ranked LP
            wins 	        (int) 	    Winning team on Summoners Rift.
            losses 	        (int) 	    Losing team on Summoners Rift.
    """

    user_json = get_identifiable_data(server, summoner_name)

    if user_json["success"]:

        url = (
            "https://"
            + server
            + ".api.riotgames.com/lol/league/v4/entries/by-summoner/"
            + user_json["id"]
            + "?api_key="
            + API_KEY
        )

        # This json is a list of dictionaries
        ranked_json = helpers.get_response_json(url)

        # Get dictionary of ranked solo from the list
        try:
            solo = next(mode for mode in ranked_json if mode["queueType"] == "RANKED_SOLO_5x5")

        # If it doesn't exist, set as default unranked
        except StopIteration:
            solo = {"tier" : "Unranked"}

        # Same for ranked flex
        try:
            flex = next(mode for mode in ranked_json if mode["queueType"] == "RANKED_FLEX_SR")
        except StopIteration:
            flex = {"tier" : "Unranked"}

        stats_json = {"RANKED_SOLO_5x5": solo, "RANKED_FLEX_SR": flex}

        for game_mode in stats_json:

            try:
                wins = stats_json[game_mode]["wins"]
                losses = stats_json[game_mode]["losses"]
                total_games = wins + losses
                stats_json[game_mode]["win_rate"] = round((wins / total_games) * 100)

            # Error when player is unranked in that game mode
            except KeyError:
                pass

        user_json["server"] = server

    elif user_json["user_not_found"]:
        stats_json = {}

    return user_json, stats_json


def get_matchlist(server, puuid):
    """Request:
    https://SERVER.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids

    Args:
        server              (string)    Player's region
        account_id          (string)

    Returns:
        JSON with list of dictionaries with:
            gameId 	        (long) 	    ID associated with the game
            role 	        (string)
            season 	        (int)
            platformId 	    (string) 	Server, e.g. EUW
            champion 	    (int) 	    Champion ID
            queue 	        (int)
            lane 	        (string)
            timestamp 	    (long)      Unix timestamp
    """

    server = helpers.get_region_by_platform(server)

    url = (
        "https://"
        + server
        + ".api.riotgames.com/lol/match/v5/matches/by-puuid/"
        + puuid
        + "/ids?start=0&count=100&api_key="
        + API_KEY
    )

    matchlist = helpers.get_response_json(url)

    return matchlist


def get_game_summary_list(games, puuid):
    """
    Gets the main data from each game to show on the user profile page
    """
    game_summary_list = []
    if games:

        platform = (games[0].split("_"))[0]

        region = helpers.get_region_by_platform(platform)

        game_summary_list = asyncio.run(get_match_preview(region,
                                                          games[:10],
                                                          puuid))

    return game_summary_list


async def get_match_preview(region, games, puuid):
    """
    Async http request for getting game json and organizing the players data
    """
    async with aiohttp.ClientSession() as session:
        tasks = []

        for match in games:
            url = "https://" + region + \
                ".api.riotgames.com/lol/match/v5/matches/" + \
                match + "?api_key=" + API_KEY
            tasks.append(asyncio.ensure_future(get_preview(session, url)))

        preview_list = await asyncio.gather(*tasks)
        game_preview_list = []

        for match in preview_list:


            game_dict = {}
            participant_number = 0

            # Find summoner participant number in the match
            while match["metadata"]["participants"][participant_number] != puuid:
                participant_number += 1

            player_json = match["info"]["participants"][participant_number]
            game_dict["player_summary"] = player_json

            kills = game_dict["player_summary"]["kills"]
            assists = game_dict["player_summary"]["assists"]
            deaths = game_dict["player_summary"]["deaths"]
            try:
                game_dict["player_summary"]["kda"] = round((kills + assists) / deaths, 2)

            # Happens when zero deaths
            except ZeroDivisionError:
                game_dict["player_summary"]["kda"] = kills + assists

            # Get the date of game creation
            game_date = helpers.get_date_by_timestamp(match["info"]
                                                        ["gameCreation"])
            game_dict["date"] = game_date

            # Get patch for assets, 11.23.409.111 -> 11.23.1
            patch = ".".join(match["info"]["gameVersion"].split(".")[:2]) + ".1"
            game_dict["patch"] = patch

            game_dict["player_summary"]["items"] = [game_dict["player_summary"]["item0"],
                                                    game_dict["player_summary"]["item1"],
                                                    game_dict["player_summary"]["item2"],
                                                    game_dict["player_summary"]["item6"],
                                                    game_dict["player_summary"]["item3"],
                                                    game_dict["player_summary"]["item4"],
                                                    game_dict["player_summary"]["item5"]]

            game_dict["game_id"] = str(match["metadata"]["matchId"])

            game_dict["game_summary"] = match

            if match["info"]["gameMode"] == "CLASSIC":
                game_dict["game_mode"] = helpers.get_game_mode(match["info"]["queueId"])

            else:
                game_dict["game_mode"] = match["info"]["gameMode"]

            if match["info"]["gameType"] != "CUSTOM_GAME":
                game_dict["game_summary"]["info"]["matchups"] = []
                game_base = game_dict["game_summary"]["info"]
                # pprint(game_base["participants"])
                print(game_dict["game_summary"]["info"]["gameId"])
                for i in range(0, 5):
                    game_base["matchups"].append([game_base["participants"][i],
                                                game_base["participants"][i + 5]])

            game_preview_list.append(game_dict)

    return game_preview_list


async def get_preview(session, url):
    """
    Async to get the json from the request
    """
    async with session.get(url, raise_for_status=True) as response:

        stats_json = await response.json()
        return stats_json


def game_summary(server, game_json):
    """Request: https://SERVER.api.riotgames.com/lol/match/v4/matches/GAME_ID

    Args:
        server          (string)
        game_json       (dictionary)

    Returns:
        JSON: Participants stats and game info
    """

    game_duration_seconds = game_json["gameDuration"]
    game_duration = str(datetime.timedelta(seconds=game_duration_seconds))
    game_json["gameDuration"] = game_duration

    game_creation = game_json["gameCreation"]
    game_creation = helpers.get_date_by_timestamp(game_creation)
    game_json["gameCreation"] = game_creation

    summoner_id_list = []

    for participant in game_json["participants"]:
        participant["totalMinionsKilled"] = (
            participant["totalMinionsKilled"]
            + participant["neutralMinionsKilled"]
        )
        summoner_id_list.append(participant['summonerId'])

    # Change vocabulary from Win/Fail to Victory/Defeat
    for team in game_json["teams"]:
        if team["win"]:
            team["win"] = "Victory"
        else:
            team["win"] = "Defeat"

    # Get new game_json with the rank of each player. An API
    # call is needed for each player so asyncio was used.
    game_json = asyncio.run(
        get_players_ranks(server, game_json, summoner_id_list)
    )

    return game_json


async def get_players_ranks(server, game_json, summoner_id_list):
    """
    Async to get each player's rank from the game
    """
    async with aiohttp.ClientSession() as session:
        current_player = 0
        tasks = []

        for summoner_id in summoner_id_list:

            url = (
                "https://"
                + server
                + ".api.riotgames.com/lol/league/v4/entries/by-summoner/"
                + summoner_id
                + "?api_key="
                + API_KEY
            )

            tasks.append(asyncio.ensure_future(get_rank(session, url)))

        stats_json_list = await asyncio.gather(*tasks)
        for stats_json in stats_json_list:
            try:
                stats_json = next(
                    item
                    for item in stats_json
                    if item["queueType"] == "RANKED_SOLO_5x5"
                )

            # If the player doesn't have rank, set tier to Unranked
            except StopIteration:
                stats_json = {
                    "tier": "Unranked",
                    "rank": None,
                }

            tier = stats_json["tier"]
            rank = stats_json["rank"]

            if rank is not None:
                game_json["participants"][current_player][
                    "tier"] = f"{tier} {rank}"

            # If the player doesn't have rank, display Unranked
            elif rank is None:
                game_json["participants"][current_player]["tier"] = f"{tier}"

            current_player += 1

    return game_json


async def get_rank(session, url):
    """
    Async to get the json from the request
    """
    async with session.get(url) as response:
        stats_json = await response.json()
        return stats_json
