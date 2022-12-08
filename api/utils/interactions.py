"""
Contains functions that interacts with RIOT's API.
"""
from api.utils import helpers, sessions
from api.models import Match
from asgiref.sync import sync_to_async
from datetime import timedelta
from decouple import config
from aiohttp import ClientSession
from asyncio import ensure_future, gather, run, sleep


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
    response = helpers.get_response(url)
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
        summoner_league_list = helpers.get_response(url).json()
        # Set default values for each league
        solo = {"tier": "Unranked"}
        flex = {"tier": "Unranked"}

        for queue in summoner_league_list:
            queue["win_rate"] = round(
                (queue["wins"] / (queue["wins"] + queue["losses"])) * 100
            )

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

    matchlist = helpers.get_response(url).json()

    return matchlist


async def get_match_json_list(matches):
    """Async http request for getting match json and organizing the players data"""

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
            tasks.append(ensure_future(get_match_json(session, url, match)))

        return await gather(*tasks)


async def get_match_json(session, url, match):
    """Async to get the json from the request"""

    max_attempts = 3
    attempts = 0
    while attempts < max_attempts:
        # Search for match json in database
        matches = await sync_to_async(list)(
            Match.objects.filter(match_id=match).exclude(match_json__exact={})
        )
        if matches:
            return matches[0].match_json
        else:
            async with session.get(url) as response:
                if response.status == 200:
                    match = await response.json()
                    # 0 is custom matches; 2000, 2010 and 2020 are tutorial matches
                    if match["info"]["queueId"] not in {0, 2000, 2010, 2020}:

                        # Get the date of match creation
                        match["date"] = helpers.get_date_by_timestamp(
                            match["info"]["gameCreation"]
                        )

                        # Get patch for assets, 11.23.409.111 -> 11.23.1
                        patch = (
                            ".".join(match["info"]["gameVersion"].split(".")[:2]) + ".1"
                        )
                        match["patch"] = patch
                        if match["info"]["gameMode"] == "CLASSIC":
                            match["match_mode"] = helpers.get_match_mode(
                                match["info"]["queueId"]
                            )
                        else:
                            match["match_mode"] = match["info"]["gameMode"]

                        match["info"]["matchups"] = []
                        for i in range(0, 5):
                            match["info"]["matchups"].append(
                                [
                                    match["info"]["participants"][i],
                                    match["info"]["participants"][i + 5],
                                ]
                            )
                    return match

                elif response.status == 429:
                    print(
                        "Rate limit exceeded, sleeping for "
                        + response.headers["Retry-After"]
                        + " seconds"
                    )
                    await sleep(int(response.headers["Retry-After"]))
                attempts += 1

    if attempts >= max_attempts:
        raise Exception("Failed: Maxed out attempts")


async def get_player_summary_list(matches, puuid, perks_json):
    """Async to get a list of players summaries from match list"""
    tasks = []

    for match in matches:
        tasks.append(ensure_future(get_player_summary(match, puuid, perks_json)))

    return await gather(*tasks)


async def get_player_summary(match, puuid, perks_json):
    """Async to organize the players data"""

    participant_number = helpers.get_participant_number(match, puuid)

    player_summary = match["info"]["participants"][participant_number]

    try:
        player_summary["kda"] = round(
            (player_summary["kills"] + player_summary["assists"])
            / player_summary["deaths"],
            2,
        )
    # Happens when zero deaths
    except ZeroDivisionError:
        player_summary["kda"] = player_summary["kills"] + player_summary["assists"]

    player_summary["summoner_spell_1"] = helpers.get_summoner_spell(
        player_summary["summoner1Id"]
    )
    player_summary["summoner_spell_2"] = helpers.get_summoner_spell(
        player_summary["summoner2Id"]
    )

    player_summary["rune_primary"] = helpers.get_rune_primary(
        player_summary["perks"]["styles"][0]["selections"][0]["perk"], perks_json
    )
    player_summary["rune_secondary"] = helpers.get_rune_secondary(
        player_summary["perks"]["styles"][1]["style"]
    )

    player_summary = helpers.get_preview_stats(
        player_summary, match["info"]["gameDuration"] / 60
    )

    player_summary["items"] = [
        player_summary["item0"],
        player_summary["item1"],
        player_summary["item2"],
        player_summary["item6"],
        player_summary["item3"],
        player_summary["item4"],
        player_summary["item5"],
    ]

    player_summary["matchId"] = match["metadata"]["matchId"]
    player_summary["gameMode"] = match["info"]["gameMode"]
    player_summary["gameDuration"] = int(round(match["info"]["gameDuration"] / 60, 0))
    player_summary["gameCreation"] = helpers.get_date_by_timestamp(
        match["info"]["gameCreation"]
    )

    return player_summary


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
    """Async to get each player's rank from the match"""

    async with ClientSession() as session:
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
            tasks.append(ensure_future(get_leagues_json(session, url)))

        summoners_leagues_list = await gather(*tasks)
        current_player = 0
        for leagues in summoners_leagues_list:
            try:
                # If it's a flex match, search for flex rank
                if match_json["queueId"] == 440:
                    leagues = next(
                        item
                        for item in leagues
                        if item["queueType"] == "RANKED_FLEX_SR"
                    )
                else:
                    leagues = next(
                        item
                        for item in leagues
                        if item["queueType"] == "RANKED_SOLO_5x5"
                    )

            # If the player doesn't have rank, set tier to Unranked
            except StopIteration:
                leagues = {
                    "tier": "Unranked",
                    "rank": None,
                }

            # If the player doesn't have rank, display Unranked
            if leagues["rank"] is None:
                match_json["participants"][current_player][
                    "tier"
                ] = f"{leagues['tier']}"

            else:
                match_json["participants"][current_player][
                    "tier"
                ] = f"{leagues['tier']} {leagues['rank']}"

            current_player += 1

    return match_json


async def get_leagues_json(session, url):
    """Async to get the json from the request"""

    max_attempts = 3
    attempts = 0
    while attempts < max_attempts:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()

            elif response.status == 429:
                print(
                    "Rate limit exceeded, sleeping for "
                    + response.headers["Retry-After"]
                    + "seconds"
                )
                await sleep(int(response.headers["Retry-After"]))
            attempts += 1

    if attempts >= max_attempts:
        raise Exception("Failed: Maxed out attempts")
