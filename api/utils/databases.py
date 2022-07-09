"""Functions that performs computation on the database"""

from api.models import Summoner, Match
from api.utils import helpers

def update_summoner_db(summoner_db, player_summary_list):
    for player_summary in player_summary_list:
        position_dict = player_summary["teamPosition"].lower()
        # Only if it's a ranked or normal match, not urf, not aram...
        # and position isn't empty, which happens when player went afk and remaked
        if player_summary["gameMode"] == "CLASSIC" and position_dict != "":
            summoner_db.roles[position_dict]["num"] += 1

            if player_summary["win"]:
                summoner_db.roles[position_dict]["wins"] += 1
            else:
                summoner_db.roles[position_dict]["losses"] += 1

            summoner_db.roles[position_dict]["win_rate"] = int(
                summoner_db.roles[position_dict]["wins"]
                / summoner_db.roles[position_dict]["num"]
                * 100
            )

            summoner_db = add_database_ranked_stats(
                summoner_db, player_summary
            )

            summoner_db = add_database_champion_stats(
                summoner_db, player_summary
            )
    
    # order champions in database by number of matches, then by win rate and then by kda
    summoner_db.champions = dict(
        sorted(
            summoner_db.champions.items(),
            key=lambda item: (item[1]["num"], item[1]["win_rate"], item[1]["kda"]),
            reverse=True,
        )
    )
    return summoner_db


def add_database_ranked_stats(summoner_db, summoner_json):
    summoner_db.matches += 1
    summoner_db.minutes += summoner_json["gameDuration"]

    summoner_db.stats["kills"]["total"] += summoner_json["kills"]
    summoner_db.stats["kills"]["per_min"] = round(
        summoner_db.stats["kills"]["total"] / summoner_db.minutes, 2
    )
    summoner_db.stats["kills"]["per_match"] = round(
        summoner_db.stats["kills"]["total"] / summoner_db.matches, 2
    )

    summoner_db.stats["assists"]["total"] += summoner_json["assists"]
    summoner_db.stats["assists"]["per_min"] = round(
        summoner_db.stats["assists"]["total"] / summoner_db.minutes, 2
    )
    summoner_db.stats["assists"]["per_match"] = round(
        summoner_db.stats["assists"]["total"] / summoner_db.matches, 2
    )

    summoner_db.stats["deaths"]["total"] += summoner_json["deaths"]
    summoner_db.stats["deaths"]["per_min"] = round(
        summoner_db.stats["deaths"]["total"] / summoner_db.minutes, 2
    )
    summoner_db.stats["deaths"]["per_match"] = round(
        summoner_db.stats["deaths"]["total"] / summoner_db.matches, 2
    )

    summoner_db.stats["minions"]["total"] += (
        summoner_json["totalMinionsKilled"] + summoner_json["neutralMinionsKilled"]
    )
    summoner_db.stats["minions"]["per_min"] = round(
        summoner_db.stats["minions"]["total"] / summoner_db.minutes, 2
    )
    summoner_db.stats["minions"]["per_match"] = round(
        summoner_db.stats["minions"]["total"] / summoner_db.matches, 2
    )

    summoner_db.stats["vision"]["total"] += summoner_json["visionScore"]
    summoner_db.stats["vision"]["per_min"] = round(
        summoner_db.stats["vision"]["total"] / summoner_db.minutes, 2
    )
    summoner_db.stats["vision"]["per_match"] = round(
        summoner_db.stats["vision"]["total"] / summoner_db.matches, 2
    )

    return summoner_db


def add_database_champion_stats(summoner_db, summoner_json):
    kills = summoner_json["kills"]
    assists = summoner_json["assists"]
    deaths = summoner_json["deaths"]
    if summoner_json["championName"] not in summoner_db.champions:
        summoner_db.champions[summoner_json["championName"]] = {
            "num": 1,
            "kills": kills,
            "assists": assists,
            "deaths": deaths,
            "kda": round((kills + assists) / deaths, 2)
            if deaths != 0
            else kills + assists,
            "wins": 1 if summoner_json["win"] else 0,
            "losses": 1 if not summoner_json["win"] else 0,
            "win_rate": 100 if summoner_json["win"] else 0,
            "play_rate": 1 / summoner_db.matches,
            "minions": summoner_json["totalMinionsKilled"]
            + summoner_json["neutralMinionsKilled"],
            "vision": summoner_json["visionScore"],
            "gold": summoner_json["goldEarned"],
            "damage": summoner_json["totalDamageDealtToChampions"],
            "last_played": summoner_json["gameCreation"]
        }
    else:
        champion_data = summoner_db.champions[summoner_json["championName"]]
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
        if summoner_json["win"]:
            champion_data["wins"] += 1
        else:
            champion_data["losses"] += 1
        champion_data["win_rate"] = round(
            champion_data["wins"] / champion_data["num"] * 100, 2
        )
        champion_data["play_rate"] = round(
            champion_data["num"] / summoner_db.matches, 2
        )
        champion_data["minions"] += (
            summoner_json["totalMinionsKilled"] + summoner_json["neutralMinionsKilled"]
        )
        champion_data["vision"] += summoner_json["visionScore"]
        champion_data["gold"] += summoner_json["goldEarned"]
        champion_data["damage"] += summoner_json["totalDamageDealtToChampions"]
        champion_data["last_played"] = summoner_json["gameCreation"]
    return summoner_db


def create_user_db(summoner_name):
    """Create user in database"""
    Summoner.objects.create(
        summoner=summoner_name,
        stats={
            "kills": {"total": 0, "per_min": 0, "per_match": 0},
            "deaths": {"total": 0, "per_min": 0, "per_match": 0},
            "assists": {"total": 0, "per_min": 0, "per_match": 0},
            "minions": {"total": 0, "per_min": 0, "per_match": 0},
            "vision": {"total": 0, "per_min": 0, "per_match": 0},
        },
        roles={
            "top": {"num": 0, "win_rate": 0, "wins": 0, "losses": 0},
            "jungle": {"num": 0, "win_rate": 0, "wins": 0, "losses": 0},
            "middle": {"num": 0, "win_rate": 0, "wins": 0, "losses": 0},
            "bottom": {"num": 0, "win_rate": 0, "wins": 0, "losses": 0},
            "utility": {"num": 0, "win_rate": 0, "wins": 0, "losses": 0},
        },
    )


def add_matches_to_db(matchlist, summoner_name):
    """Add matches to database"""
    add_match_bulk_list = []
    for match in matchlist:
        # if match id with summoner name not found, create object in database
        if Match.objects.filter(match_id=match, summoner=summoner_name).exists():
            break
        add_match_bulk_list.append(Match(match_id=match, summoner=summoner_name))
    Match.objects.bulk_create(add_match_bulk_list)


def find_matches_not_in_db(matchlist, summoner_name):
    """List of match ids which are not in database"""
    summary_not_in_database = []
    for match in matchlist:
        # If match summary not in database, create object in database
        if Match.objects.filter(
            match_id=match, summoner=summoner_name, match_json__exact={}
        ).exists():
            summary_not_in_database.append(match)
            # Limit to 7 for lazy load pagination
            if len(summary_not_in_database) == 7:
                break
    return summary_not_in_database


def save_matches_to_db(match_summary_list, summoner_name):
    """Save matches to database"""
    bulk_save_summary_list = []
    for match in match_summary_list:
        match_object = Match.objects.get(
            match_id=match["metadata"]["matchId"], summoner=summoner_name
        )
        match_object.match_json = match
        bulk_save_summary_list.append(match_object)
    Match.objects.bulk_update(bulk_save_summary_list, ["match_json"])

def save_player_summaries_to_db(player_summary_list, summoner_name):
    """Save player summaries to database"""
    bulk_save_summary_list = []
    for player_summary in player_summary_list:
        match_object = Match.objects.get(
            match_id=player_summary["matchId"], summoner=summoner_name
        )
        match_object.summoner_json = player_summary
        bulk_save_summary_list.append(match_object)
    Match.objects.bulk_update(bulk_save_summary_list, ["summoner_json"])