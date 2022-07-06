"""
Contains functions that interacts with RIOT's API.
"""

from datetime import timedelta
from requests import get
from decouple import config
from aiohttp import ClientSession
from asyncio import ensure_future, gather, run
from api.utils import helpers
from api.utils import sessions


API_KEY = config("API")


def get_summoner(server, summoner_name):
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
    response = get(url)

    summoner_json = response.json()
    summoner_json["success"] = response.status_code == 200
    return summoner_json


def get_summoner_league(request, server, summoner_name):
    """Request:
    https://SERVER.api.riotgames.com/lol/league/v4/entries/by-summoner/SUMMONER_ID

    Args:
        server              (string)    Player's region
        summoner_name       (string)    Summoner name

    Returns:
        List of two dictionaries with:
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

    summoner_json = sessions.load_summoner(request, server, summoner_name)

    if summoner_json["success"]:

        url = (
            "https://"
            + server
            + ".api.riotgames.com/lol/league/v4/entries/by-summoner/"
            + summoner_json["id"]
            + "?api_key="
            + API_KEY
        )
        # This json is a list of dictionaries
        summoner_league_list = get(url).json()
        # Set default values for each league
        solo = {"tier": "Unranked"}
        flex = {"tier": "Unranked"}

        for queue in summoner_league_list:
            queue["win_rate"] = round((queue["wins"] / (queue["wins"] + queue["losses"])) * 100)

            if queue["queueType"] == "RANKED_SOLO_5x5":
                solo = queue
            elif queue["queueType"] == "RANKED_FLEX_SR":
                flex = queue

        summoner_league_json = {"RANKED_SOLO_5x5": solo, "RANKED_FLEX_SR": flex}

    else:
        summoner_league_json = {}

    return summoner_json, summoner_league_json


def get_matchlist(server, puuid):
    """Request:
    https://SERVER.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids

    Args:
        server              (string)    Player's region
        puuid          (string)

    Returns:
        List with match ids
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

    matchlist = get(url).json()

    return matchlist


async def get_match_preview_list(matches, summoner_db, puuid):
    """
    Async http request for getting match json and organizing the players data
    """

    match_preview_list = []

    if matches:
        platform = (matches[0].split("_"))[0]
        region = helpers.get_region_by_platform(platform)

        async with ClientSession() as session:
            tasks = []

            for match in matches:
                url = (
                    "https://"
                    + region
                    + ".api.riotgames.com/lol/match/v5/matches/"
                    + match
                    + "?api_key="
                    + API_KEY
                )
                tasks.append(ensure_future(get_match_preview(session, url, puuid)))

            match_preview_list = await gather(*tasks)

            for match in match_preview_list:

                position_dict = match["player_summary"]["teamPosition"]
                # Only if it's a ranked or normal match, not urf, not aram...
                # and position isn't empty, which happens when player went afk and remaked
                if match["info"]["gameMode"] == "CLASSIC" and position_dict != "":
                    summoner_db.roles[position_dict]["NUM"] += 1

                    if match["player_summary"]["win"]:
                        summoner_db.roles[position_dict]["WINS"] += 1
                    else:
                        summoner_db.roles[position_dict]["LOSSES"] += 1

                    summoner_db.roles[position_dict]["WIN_RATE"] = int(
                        summoner_db.roles[position_dict]["WINS"]
                        / summoner_db.roles[position_dict]["NUM"]
                        * 100
                    )

                    summoner_db = add_database_ranked_stats(
                        summoner_db, match, match["player_summary"]
                    )

                    summoner_db = add_database_champion_stats(
                        summoner_db, match, match["player_summary"]
                    )
    return summoner_db, match_preview_list


async def get_match_preview(session, url, puuid):
    """
    Async to get the json from the request
    """
    async with session.get(url, raise_for_status=True) as response:
        match = await response.json()

        # 0 is custom matches; 2000, 2010 and 2020 are tutorial matches
        if match["info"]["queueId"] not in {0, 2000, 2010, 2020}:
            participant_number = 0
            # Find summoner participant number in the match
            while match["metadata"]["participants"][participant_number] != puuid:
                participant_number += 1

            match["player_summary"] = match["info"]["participants"][participant_number]

            kills = match["player_summary"]["kills"]
            assists = match["player_summary"]["assists"]
            deaths = match["player_summary"]["deaths"]
            try:
                match["player_summary"]["kda"] = round((kills + assists) / deaths, 2)
            # Happens when zero deaths
            except ZeroDivisionError:
                match["player_summary"]["kda"] = kills + assists

            match["player_summary"]["cs"] = (
                match["player_summary"]["totalMinionsKilled"]
                + match["player_summary"]["neutralMinionsKilled"]
            )

            match["player_summary"]["cs_per_min"] = round(
                (
                    match["player_summary"]["totalMinionsKilled"]
                    + match["player_summary"]["neutralMinionsKilled"]
                )
                / (match["info"]["gameDuration"] / 60),
                1,
            )

            user_match_data = match["info"]["participants"][participant_number]

            match["player_summary"]["summoner_spell_1"] = helpers.get_summoner_spell(
                user_match_data["summoner1Id"]
            )
            match["player_summary"]["summoner_spell_2"] = helpers.get_summoner_spell(
                user_match_data["summoner2Id"]
            )
            match["player_summary"]["rune_primary"] = helpers.get_rune_primary(
                user_match_data["perks"]["styles"][0]["selections"][0]["perk"]
            )
            match["player_summary"]["rune_secondary"] = helpers.get_rune_secondary(
                user_match_data["perks"]["styles"][1]["style"]
            )

            # Some match modes doesn't have challenges sections such as URF
            if "challenges" in user_match_data:

                # Sometimes the killParticipation challenges is not available, e.g: remake matches
                if "killParticipation" in user_match_data["challenges"]:
                    match["player_summary"]["challenges"][
                        "kill_participation_percentage"
                    ] = round(
                        user_match_data["challenges"]["killParticipation"] * 100,
                        1,
                    )
                else:
                    match["player_summary"]["challenges"][
                        "kill_participation_percentage"
                    ] = "ERROR"
            else:
                match["player_summary"]["challenges"] = {}
                match["player_summary"]["challenges"][
                    "kill_participation_percentage"
                ] = "ERROR"

            match["player_summary"]["gold_short"] = round(
                user_match_data["goldEarned"] / 1000,
                1,
            )
            match["player_summary"]["damage_short"] = round(
                user_match_data["totalDamageDealtToChampions"] / 1000,
                1,
            )

            # Get the date of match creation
            match_date = helpers.get_date_by_timestamp(match["info"]["gameCreation"])
            match["date"] = match_date

            # Get patch for assets, 11.23.409.111 -> 11.23.1
            patch = ".".join(match["info"]["gameVersion"].split(".")[:2]) + ".1"
            match["patch"] = patch

            match["player_summary"]["items"] = [
                match["player_summary"]["item0"],
                match["player_summary"]["item1"],
                match["player_summary"]["item2"],
                match["player_summary"]["item6"],
                match["player_summary"]["item3"],
                match["player_summary"]["item4"],
                match["player_summary"]["item5"],
            ]

            if match["info"]["gameMode"] == "CLASSIC":
                match["match_mode"] = helpers.get_match_mode(match["info"]["queueId"])

            else:
                match["match_mode"] = match["info"]["gameMode"]

            if match["info"]["gameType"] != "CUSTOM_GAME":
                match["info"]["matchups"] = []
                for i in range(0, 5):
                    match["info"]["matchups"].append(
                        [
                            match["info"]["participants"][i],
                            match["info"]["participants"][i + 5],
                        ]
                    )
        return match


def add_database_ranked_stats(summoner_db, match, player_json):
    summoner_db.matches += 1
    summoner_db.minutes += int(round(match["info"]["gameDuration"] / 60, 0))

    summoner_db.stats["kills"]["total"] += player_json["kills"]
    summoner_db.stats["kills"]["per_min"] = round(
        summoner_db.stats["kills"]["total"] / summoner_db.minutes, 2
    )
    summoner_db.stats["kills"]["per_match"] = round(
        summoner_db.stats["kills"]["total"] / summoner_db.matches, 2
    )

    summoner_db.stats["assists"]["total"] += player_json["assists"]
    summoner_db.stats["assists"]["per_min"] = round(
        summoner_db.stats["assists"]["total"] / summoner_db.minutes, 2
    )
    summoner_db.stats["assists"]["per_match"] = round(
        summoner_db.stats["assists"]["total"] / summoner_db.matches, 2
    )

    summoner_db.stats["deaths"]["total"] += player_json["deaths"]
    summoner_db.stats["deaths"]["per_min"] = round(
        summoner_db.stats["deaths"]["total"] / summoner_db.minutes, 2
    )
    summoner_db.stats["deaths"]["per_match"] = round(
        summoner_db.stats["deaths"]["total"] / summoner_db.matches, 2
    )

    if summoner_db.stats["deaths"]["total"] != 0:
        summoner_db.stats["kda"] = round(
            (
                summoner_db.stats["kills"]["total"]
                + summoner_db.stats["assists"]["total"]
            )
            / summoner_db.stats["deaths"]["total"],
            2,
        )
    else:
        summoner_db.stats["kda"] = (
            summoner_db.stats["kills"]["total"] + summoner_db.stats["assists"]["total"]
        )

    summoner_db.stats["vision"]["total"] += player_json["visionScore"]
    summoner_db.stats["vision"]["per_min"] = round(
        summoner_db.stats["vision"]["total"] / summoner_db.minutes, 2
    )
    summoner_db.stats["vision"]["per_match"] = round(
        summoner_db.stats["vision"]["total"] / summoner_db.matches, 2
    )

    summoner_db.stats["minions"]["total"] += (
        player_json["totalMinionsKilled"] + player_json["neutralMinionsKilled"]
    )
    summoner_db.stats["minions"]["per_min"] = round(
        summoner_db.stats["minions"]["total"] / summoner_db.minutes, 2
    )
    summoner_db.stats["minions"]["per_match"] = round(
        summoner_db.stats["minions"]["total"] / summoner_db.matches, 2
    )

    return summoner_db


def add_database_champion_stats(summoner_db, match, player_json):
    kills = player_json["kills"]
    assists = player_json["assists"]
    deaths = player_json["deaths"]
    if player_json["championName"] not in summoner_db.champions:
        summoner_db.champions[player_json["championName"]] = {
            "num": 1,
            "kills": kills,
            "assists": assists,
            "deaths": deaths,
            "kda": round((kills + assists) / deaths, 2)
            if deaths != 0
            else kills + assists,
            "wins": 1 if player_json["win"] else 0,
            "losses": 1 if not player_json["win"] else 0,
            "win_rate": 100 if player_json["win"] else 0,
            "play_rate": 1 / summoner_db.matches,
            "minions": player_json["totalMinionsKilled"]
            + player_json["neutralMinionsKilled"],
            "vision": player_json["visionScore"],
            "gold": player_json["goldEarned"],
            "damage": player_json["totalDamageDealtToChampions"],
            "last_played": helpers.get_date_by_timestamp(match["info"]["gameCreation"]),
        }
    else:
        champion_data = summoner_db.champions[player_json["championName"]]
        champion_data["num"] += 1
        champion_data["kills"] += kills
        champion_data["assists"] += assists
        champion_data["deaths"] += deaths
        if champion_data["deaths"] != 0:
            champion_data["kda"] = round(
                (champion_data["kills"] + champion_data["assists"])
                / champion_data["deaths"],
                2,
            )
        else:
            champion_data["kda"] = champion_data["kills"] + champion_data["assists"]
        if player_json["win"]:
            champion_data["wins"] += 1
        else:
            champion_data["losses"] += 1
        champion_data["win_rate"] = round(
            champion_data["wins"] / champion_data["num"] * 100, 2
        )
        champion_data["play_rate"] = round(champion_data["num"] / summoner_db.matches, 2)
        champion_data["minions"] += (
            player_json["totalMinionsKilled"] + player_json["neutralMinionsKilled"]
        )
        champion_data["vision"] += player_json["visionScore"]
        champion_data["gold"] += player_json["goldEarned"]
        champion_data["damage"] += player_json["totalDamageDealtToChampions"]
        champion_data["last_played"] = helpers.get_date_by_timestamp(
            match["info"]["gameCreation"]
        )

    return summoner_db


def match_summary(server, match_json):
    """Request: https://SERVER.api.riotgames.com/lol/match/v4/matches/GAME_ID

    Args:
        server          (string)
        match_json       (dictionary)

    Returns:
        JSON: Participants stats and game info
    """

    match_duration_seconds = match_json["gameDuration"]
    match_duration = str(timedelta(seconds=match_duration_seconds))
    match_json["gameDuration"] = match_duration

    match_creation = match_json["gameCreation"]
    match_creation = helpers.get_date_by_timestamp(match_creation)
    match_json["gameCreation"] = match_creation

    summoner_id_list = []

    for participant in match_json["participants"]:
        participant["totalMinionsKilled"] = (
            participant["totalMinionsKilled"] + participant["neutralMinionsKilled"]
        )
        summoner_id_list.append(participant["summonerId"])

    # Change vocabulary from Win/Fail to Victory/Defeat
    for team in match_json["teams"]:
        if team["win"]:
            team["win"] = "Victory"
        else:
            team["win"] = "Defeat"

    # Get new match_json with the rank of each player. An API
    # call is needed for each player so asyncio was used.
    match_json = run(get_players_ranks(server, match_json, summoner_id_list))

    return match_json


async def get_players_ranks(server, match_json, summoner_id_list):
    """
    Async to get each player's rank from the match
    """
    async with ClientSession() as session:
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

            tasks.append(ensure_future(get_json(session, url)))

        stats_json_list = await gather(*tasks)
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

            # If the player doesn't have rank, display Unranked
            if stats_json["rank"] is None:
                match_json["participants"][current_player][
                    "tier"
                ] = f"{stats_json['tier']}"

            else:
                match_json["participants"][current_player][
                    "tier"
                ] = f"{stats_json['tier']} {stats_json['rank']}"

            current_player += 1

    return match_json


async def get_json(session, url):
    """
    Async to get the json from the request
    """
    async with session.get(url, raise_for_status=True) as response:
        stats_json = await response.json()
        return stats_json
