# Contains functions that interacts with RIOT's API.

import requests
import datetime
from decouple import config
import aiohttp
import asyncio

API_KEY = config("API")


def get_identifiable_data(server, name):
    """Request: https://SERVER.api.riotgames.com/lol/summoner/v4/summoners/by-name/NAME

    Args:
        server (string): Player's region
        summoner_name (string): Summoner name

    Returns:
        JSON with:
            accountId 	    string 	Encrypted account ID. Max length 56 characters.
            profileIconId 	int 	ID of the summoner icon associated with the summoner.
            revisionDate 	long 	Date summoner was last modified specified as epoch milliseconds.
            name 	        string 	Summoner name.
            id 	            string 	Encrypted summoner ID. Max length 63 characters.
            puuid 	        string 	Encrypted PUUID. Exact length of 78 characters.
            summonerLevel 	long 	Summoner level associated with the summoner.
    """

    URL = (
        "https://"
        + server
        + ".api.riotgames.com/lol/summoner/v4/summoners/by-name/"
        + name
        + "?api_key="
        + API_KEY
    )

    response = requests.get(URL)

    user_json = response.json()

    user_json["success"] = response.status_code == 200
    user_json["user_not_found"] = response.status_code == 404
    return user_json


def get_ranked_stats(server, summoner_name):
    """Get summoner's ranked stats

    Args:
        server (string): Player's region
        summoner_name (string): Summoner name

    Returns:
        JSON with:
            leagueId 	    string
            summonerId 	    string 	Player's encrypted summonerId.
            summonerName 	string
            queueType 	    string 	eg: RANKED_SOLO_5x5
            tier 	        string
            rank 	        string 	The player's division within a tier.
            leaguePoints 	int
            wins 	        int 	Winning team on Summoners Rift.
            losses 	        int 	Losing team on Summoners Rift.
    """

    user_json = get_identifiable_data(server, summoner_name)

    # If the inputted summoner is found
    if user_json["success"]:

        summoner_id = user_json["id"]
        URL = (
            "https://"
            + server
            + ".api.riotgames.com/lol/league/v4/entries/by-summoner/"
            + summoner_id
            + "?api_key="
            + API_KEY
        )
        response = requests.get(URL)
        stats_json = response.json()

        try:
            stats_json = stats_json[0]

            # Total games = number of wins + number of defeats
            total_games = int(stats_json["wins"]) + int(stats_json["losses"])
            stats_json["total_games"] = str(total_games)

            stats_json["win_rate"] = str(
                round(((int(stats_json["wins"]) / total_games) * 100), 1)
            )

        # IndexError if player haven't played any game
        except IndexError:
            stats_json = {"no_games": True}

        except KeyError:
            if stats_json["status"]["status_code"] == 429:
                print("Rate limit exceeded")

        user_json["server"] = server

    elif user_json["user_not_found"]:
        stats_json = {}

    return user_json, stats_json


def get_past_games(server, account_id):
    URL = (
        "https://"
        + server
        + ".api.riotgames.com/lol/match/v4/matchlists/by-account/"
        + account_id
        + "?api_key="
        + API_KEY
    )
    response = requests.get(URL)
    old_games_json = response.json()
    old_games_json = old_games_json["matches"]
    return old_games_json


def get_champion_matchlist(server, account_id, champion_id):
    champion_id = str(champion_id)
    URL = (
        "https://"
        + server
        + ".api.riotgames.com/lol/match/v4/matchlists/by-account/"
        + account_id
        + "?champion="
        + champion_id
        + "&api_key="
        + API_KEY
    )
    response = requests.get(URL)
    old_games_json = response.json()
    old_games_json = old_games_json["matches"]
    return old_games_json


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


def get_game_date(timestamp):

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


def get_champion_stats(server, summoner_name, champion_name, champ_json):

    champ_key = get_champion_key(champion_name, champ_json)

    user_json = get_identifiable_data(server, summoner_name)

    if user_json["success"]:

        summoner_id = user_json["id"]
        account_id = user_json["accountId"]

        URL = (
            "https://"
            + server
            + ".api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/"
            + summoner_id
            + "/by-champion/"
            + champ_key
            + "?api_key="
            + API_KEY
        )
        response = requests.get(URL)
        champ_json = response.json()
        champ_json["champ_name"] = champion_name

        champ_json["summoner_name"] = summoner_name
        champ_json["accountId"] = account_id

        last_played = champ_json["lastPlayTime"]
        time_diff = get_game_date(last_played)
        champ_json["last_time"] = time_diff

        champ_json["server"] = server

    elif user_json["user_not_found"]:
        champ_json = {}

    return user_json, champ_json


def game_summary(server, gameid, champ_json):

    URL = (
        "https://"
        + server
        + ".api.riotgames.com/lol/match/v4/matches/"
        + str(gameid)
        + "?api_key="
        + API_KEY
    )
    response = requests.get(URL)

    game_json = response.json()


    game_json["game_id"] = str(game_json["gameId"])
    game_json["success"] = True

    game_duration_seconds = game_json["gameDuration"]
    game_duration = str(datetime.timedelta(seconds=game_duration_seconds))
    game_json["gameDuration"] = game_duration

    game_creation = game_json["gameCreation"]
    game_creation = get_game_date(game_creation)
    game_json["gameCreation"] = game_creation

    for participant in game_json["participants"]:
        key = participant["championId"]
        key = str(key)
        champ_name = get_champion_name(key, champ_json)
        participant["champion_name"] = champ_name
        participant["stats"]["totalMinionsKilled"] = (
            participant["stats"]["totalMinionsKilled"]
            + participant["stats"]["neutralMinionsKilled"]
        )

        # Add order variable to each participant depending on their position for later sorting them.
        position, order = get_position(participant["timeline"]["lane"], participant["timeline"]["role"])
        participant["order"] = order


    # Change vocabulary from Win/Fail to Victory/Defeat
    for team in game_json["teams"]:
        if team['win'] == "Win":
            team['win'] = "Victory"
        else:
            team['win'] = "Defeat"

    # Get new game_json with the rank of each player. An API call is needed for each player so asyncio was used.
    game_json = asyncio.run(get_players_ranks(server, game_json, game_json["participantIdentities"]))

    ## Sort participants by their role TEAM A: TOP, JNG, MID, ADC, SUPP / TEAM B: TOP, MID, ADC, SUPP
    # Order first half, which correspond to the blue side
    blue_side = sorted(game_json["participants"][:5], key=lambda k: k['order'])
    # Order last 5 players which are from the red team
    red_side = sorted(game_json["participants"][5:], key=lambda k: k['order'])
    all_participants = blue_side + red_side
    game_json["participants"] = all_participants

    return game_json


async def get_players_ranks (server, game_json, players_json):
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
                stats_json = stats_json[0]

            # IndexError if player haven't played any game
            except IndexError:
                stats_json = {"tier": "Unranked", "rank": None, "summonerId": summonerId}

            tier = stats_json["tier"]
            rank = stats_json["rank"]

            if rank != None:
                game_json["participants"][current_player]["tier"] = f"{tier} {rank}"
            elif rank == None:
                game_json["participants"][current_player]["tier"] = f"{tier}"

            game_json["participants"][current_player]["summoner_name"] = players_json[current_player]["player"]["summonerName"]

            current_player += 1

    return game_json

async def get_rank(session, url):
    async with session.get(url) as response:
        stats_json = await response.json()
        return stats_json



def in_game_info(server, summoner_id, champ_json):
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
            champ_name = get_champion_name(key, champ_json)
            participant["champion_name"] = champ_name

            summoner_name = participant["summonerName"]

            user, stats = get_ranked_stats(server, summoner_name)
            tier = stats["tier"]
            rank = stats["rank"]
            tier = f"{tier} {rank}"
            participant["tier"] = tier

            wins = stats["wins"]
            defeats = stats["losses"]
            total_games = stats["total_games"]
            win_rate = stats["win_rate"]

            ranked_stats = f"{wins}/{defeats}   W={win_rate}% ({total_games} Played)"
            participant["ranked_stats"] = ranked_stats

        for participant in red_participants_json:
            key = participant["championId"]
            key = str(key)
            champ_name = get_champion_name(key, champ_json)
            participant["champion_name"] = champ_name

            summoner_name = participant["summonerName"]

            user, stats = get_ranked_stats(server, summoner_name)
            tier = stats["tier"]
            rank = stats["rank"]
            tier = f"{tier} {rank}"
            participant["tier"] = tier

            wins = stats["wins"]
            defeats = stats["losses"]
            total_games = stats["total_games"]
            win_rate = stats["win_rate"]

            ranked_stats = f"{wins}/{defeats}   W={win_rate}% ({total_games} Played)"
            participant["ranked_stats"] = ranked_stats

        return in_game_json, blue_participants_json, red_participants_json

    elif not_in_game:
        blue_participants_json = {}
        red_participants_json = {}
        return in_game_json, blue_participants_json, red_participants_json


def load_champ_json_session(request):
    if "patch" in request.session:
        patch = request.session["patch"]
    else:
        request.session["patch"] = get_current_patch()
        request.session.set_expiry(0)
        patch = request.session["patch"]
    if "ddragon_champion_json" in request.session:
        champ_json = request.session["ddragon_champion_json"]
    else:
        request.session["ddragon_champion_json"] = get_ddragon_champion_json(patch)
        request.session.set_expiry(0)
        champ_json = request.session["ddragon_champion_json"]
    return champ_json
