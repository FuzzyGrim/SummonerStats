"""Functions that performs computation on the database"""

from api.models import Summoner, Match


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


def find_summaries_not_in_db(matchlist, summoner_name):
    """List of match ids which summaries are not in database"""
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


def save_summaries_to_db(match_summary_list, summoner_name):
    """Save match summaries to database"""
    bulk_save_summary_list = []
    for match in match_summary_list:
        match_object = Match.objects.get(
            match_id=match[0]["metadata"]["matchId"], summoner=summoner_name
        )
        match_object.match_json = match[0]
        match_object.summoner_json = match[1]
        bulk_save_summary_list.append(match_object)
    Match.objects.bulk_update(bulk_save_summary_list, ["match_json", "summoner_json"])