# Contains functions that interacts with RIOT's API.

import requests
import datetime
from decouple import config
import aiohttp
import asyncio
from api.utils import helpers

API_KEY = config("API")


def get_identifiable_data(server, summoner_name):
    """Request:
    https://SERVER.api.riotgames.com/lol/summoner/v4/summoners/by-name/SUMMONER_NAME

    Args:
        server              (string)    Player's region
        summoner_name       (string)    Summoner name

    Returns:
        JSON with:
            accountId 	    (string)
            profileIconId 	(int)
            revisionDate 	(long) 	    Date last modified in epoch milliseconds.
            name 	        (string) 	Summoner name.
            id 	            (string) 	Encrypted summoner ID.
            puuid 	        (string) 	Encrypted PUUID.
            summonerLevel 	(long)
    """

    URL = (
        "https://"
        + server
        + ".api.riotgames.com/lol/summoner/v4/summoners/by-name/"
        + summoner_name
        + "?api_key="
        + API_KEY
    )

    response = requests.get(URL)

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

    # If the inputted summoner is found
    if user_json["success"]:

        URL = (
            "https://"
            + server
            + ".api.riotgames.com/lol/league/v4/entries/by-summoner/"
            + user_json["id"]
            + "?api_key="
            + API_KEY
        )

        stats_json = helpers.get_response_json(URL)

        try:
            # Search dictionary corresponding to ranked solo because there
            # is also ranked flex and postion in list is not always the same
            for ranked_mode in stats_json:
                if ranked_mode["queueType"] == "RANKED_SOLO_5x5":
                    stats_json = ranked_mode
                    break

            total_games = int(stats_json["wins"]) + int(stats_json["losses"])
            stats_json["total_games"] = str(total_games)

            stats_json["win_rate"] = str(
                round(((int(stats_json["wins"]) / total_games) * 100), 1)
            )

        # if player haven't played any game
        except StopIteration:
            stats_json = {"no_games": True}

        except TypeError:
            if stats_json["status"]["status_code"] == 429:
                print("Rate limit exceeded")

        user_json["server"] = server

    elif user_json["user_not_found"]:
        stats_json = {}

    return user_json, stats_json


def get_matchlist(server, puuid):
    """Request:
    https://SERVER.api.riotgames.com/lol/match/v4/matchlists/by-account/ACCOUND_ID

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

    URL = (
        "https://"
        + server
        + ".api.riotgames.com/lol/match/v5/matches/by-puuid/"
        + puuid
        + "/ids?start=0&count=10&api_key="
        + API_KEY
    )

    matchlist = helpers.get_response_json(URL)

    return matchlist


def get_champion_stats(server, summoner_name, champion_name, champ_json):
    """Request:
    https://SERVER.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/SUMMONER_NAME/by-champion/CHAMPION_ID

    Args:
        server              (string)
        summoner_name       (string)
        champion_name       (string)
        champ_json          (string)    Relating champion key with its name

    Returns:
        JSON with:
            championPointsUntilNextLevel 	(long)
            chestGranted 	                (boolean)
            championId 	                    (long)
            championLevel 	                (int)
            summonerId 	                    (string)
            championPoints 	                (int)
            championPointsSinceLastLevel 	(long)
            tokensEarned 	                (int)
    """

    champ_key = helpers.get_champion_key(champion_name, champ_json)

    user_json = get_identifiable_data(server, summoner_name)

    if user_json["success"]:

        summoner_id = user_json["id"]
        account_id = user_json["accountId"]

        URL = (
            "https://"
            + server
            + ".api.riotgames.com/lol/champion-mastery/v4/"
            + "champion-masteries/by-summoner/"
            + summoner_id
            + "/by-champion/"
            + champ_key
            + "?api_key="
            + API_KEY
        )

        champ_json = helpers.get_response_json(URL)
        champ_json["champ_name"] = champion_name

        champ_json["summoner_name"] = summoner_name
        champ_json["accountId"] = account_id

        last_played = champ_json["lastPlayTime"]
        time_diff = helpers.get_date_by_timestamp(last_played)
        champ_json["last_time"] = time_diff

        champ_json["server"] = server

    elif user_json["user_not_found"]:
        champ_json = {}

    return user_json, champ_json


def game_summary(server, gameid, champ_json):
    """Request: https://SERVER.api.riotgames.com/lol/match/v4/matches/GAME_ID

    Args:
        server          (string)
        gameid          (long)
        champ_json      (string)    Relating champion key with its name

    Returns:
        JSON: Participants stats and game info
    """

    URL = (
        "https://"
        + server
        + ".api.riotgames.com/lol/match/v4/matches/"
        + str(gameid)
        + "?api_key="
        + API_KEY
    )

    game_json = helpers.get_response_json(URL)

    game_json["game_id"] = str(game_json["gameId"])
    game_json["success"] = True

    game_duration_seconds = game_json["gameDuration"]
    game_duration = str(datetime.timedelta(seconds=game_duration_seconds))
    game_json["gameDuration"] = game_duration

    game_creation = game_json["gameCreation"]
    game_creation = helpers.get_date_by_timestamp(game_creation)
    game_json["gameCreation"] = game_creation

    for participant in game_json["participants"]:
        key = participant["championId"]
        key = str(key)
        champ_name = helpers.get_champion_name(key, champ_json)
        participant["champion_name"] = champ_name
        participant["stats"]["totalMinionsKilled"] = (
            participant["stats"]["totalMinionsKilled"]
            + participant["stats"]["neutralMinionsKilled"]
        )

        # Add order variable to each participant depending on their
        # position for later sorting them.
        position, order = helpers.get_position(
            participant["timeline"]["lane"], participant["timeline"]["role"]
        )
        participant["order"] = order

    # Change vocabulary from Win/Fail to Victory/Defeat
    for team in game_json["teams"]:
        if team["win"] == "Win":
            team["win"] = "Victory"
        else:
            team["win"] = "Defeat"

    # Get new game_json with the rank of each player. An API
    # call is needed for each player so asyncio was used.
    game_json = asyncio.run(
        get_players_ranks(server, game_json,
                          game_json["participantIdentities"])
    )

    # Sort participants by their role
    # Order first half, which correspond to the blue side
    blue_side = sorted(game_json["participants"][:5], key=lambda k: k["order"])
    # Order last 5 players which are from the red team
    red_side = sorted(game_json["participants"][5:], key=lambda k: k["order"])
    all_participants = blue_side + red_side
    game_json["participants"] = all_participants

    return game_json


async def get_players_ranks(server, game_json, players_json):
    async with aiohttp.ClientSession() as session:
        current_player = 0
        tasks = []

        for player in players_json:
            summonerId = player["player"]["summonerId"]

            URL = (
                "https://"
                + server
                + ".api.riotgames.com/lol/league/v4/entries/by-summoner/"
                + summonerId
                + "?api_key="
                + API_KEY
            )

            tasks.append(asyncio.ensure_future(get_rank(session, URL)))

        stats_json_list = await asyncio.gather(*tasks)
        for stats_json in stats_json_list:
            try:
                stats_json = next(
                    item
                    for item in stats_json
                    if item["queueType"] == "RANKED_SOLO_5x5"
                )

            # If the player doesn´t have rank, set tier to Unranked
            except StopIteration:
                stats_json = {
                    "tier": "Unranked",
                    "rank": None,
                    "summonerId": summonerId,
                }

            tier = stats_json["tier"]
            rank = stats_json["rank"]

            if rank is not None:
                game_json["participants"][current_player][
                    "tier"] = f"{tier} {rank}"

            # If the player doesn´t have rank, display Unranked
            elif rank is None:
                game_json["participants"][current_player]["tier"] = f"{tier}"

            game_json["participants"][current_player][
                "summoner_name"] = players_json[
                    current_player]["player"]["summonerName"]

            current_player += 1

    return game_json


async def get_rank(session, url):
    async with session.get(url) as response:
        stats_json = await response.json()
        return stats_json


def in_game_info(server, summoner_id, champ_json):
    """Request:https://SERVER.api.riotgames.com/lol/spectator/v4/active-games/by-summoner/SUMMONER_ID

    Args:
        server              (string)
        summoner_id         (string)    Encrypted summoner ID.
        champ_json          (string)    Relating champion key with its name

    Returns:
        JSON: Participants stats and game info
    """
    URL = (
        "https://"
        + server
        + ".api.riotgames.com/lol/spectator/v4/active-games/by-summoner/"
        + (summoner_id)
        + "?api_key="
        + API_KEY
    )
    response = requests.get(URL)
    search_was_successful = response.status_code == 200
    not_in_game = response.status_code == 404

    in_game_json = response.json()

    in_game_json["success"] = search_was_successful
    in_game_json["fail"] = not_in_game

    if search_was_successful:

        blue_participants_json = in_game_json["participants"][:5]
        red_participants_json = in_game_json["participants"][5:]

        for participant in blue_participants_json:
            key = participant["championId"]
            key = str(key)
            champ_name = helpers.get_champion_name(key, champ_json)
            participant["champion_name"] = champ_name

            summoner_name = participant["summonerName"]

            user, stats = get_ranked_stats(server, summoner_name)
            tier = stats["tier"]
            rank = stats["rank"]
            tier = f"{tier} {rank}"
            participant["tier"] = tier

            participant["wins"] = stats["wins"]
            participant["losses"] = stats["losses"]
            participant["total_games"] = stats["total_games"]
            participant["win_rate"] = stats["win_rate"]

        for participant in red_participants_json:
            key = participant["championId"]
            key = str(key)
            champ_name = helpers.get_champion_name(key, champ_json)
            participant["champion_name"] = champ_name

            summoner_name = participant["summonerName"]

            user, stats = get_ranked_stats(server, summoner_name)
            tier = stats["tier"]
            rank = stats["rank"]
            tier = f"{tier} {rank}"
            participant["tier"] = tier

            participant["wins"] = stats["wins"]
            participant["losses"] = stats["losses"]
            participant["total_games"] = stats["total_games"]
            participant["win_rate"] = stats["win_rate"]

        return in_game_json, blue_participants_json, red_participants_json

    elif not_in_game:
        blue_participants_json = {}
        red_participants_json = {}
        return in_game_json, blue_participants_json, red_participants_json
