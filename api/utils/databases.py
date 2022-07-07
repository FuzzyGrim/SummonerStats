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
            "TOP": {"NUM": 0, "WIN_RATE": 0, "WINS": 0, "LOSSES": 0},
            "JUNGLE": {"NUM": 0, "WIN_RATE": 0, "WINS": 0, "LOSSES": 0},
            "MIDDLE": {"NUM": 0, "WIN_RATE": 0, "WINS": 0, "LOSSES": 0},
            "BOTTOM": {"NUM": 0, "WIN_RATE": 0, "WINS": 0, "LOSSES": 0},
            "UTILITY": {"NUM": 0, "WIN_RATE": 0, "WINS": 0, "LOSSES": 0},
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
            match_id=match, summoner=summoner_name, summary_json__exact={}
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
            match_id=match["metadata"]["matchId"], summoner=summoner_name
        )
        match_object.summary_json = match
        bulk_save_summary_list.append(match_object)
    Match.objects.bulk_update(bulk_save_summary_list, ["summary_json"])