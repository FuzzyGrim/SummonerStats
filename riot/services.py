import requests
import datetime
from pprint import pprint

ApiKey = "RGAPI-7626556c-f7f2-49a8-aef3-9f0e71934b0f"

def get_main_data(server, name):
    URL = "https://" + server + ".api.riotgames.com/lol/summoner/v4/summoners/by-name/" + name + "?api_key=" + ApiKey
    response = requests.get(URL)
    search_was_successful = (response.status_code == 200)
    search_summoner_not_found = (response.status_code == 404)
    error_api_key = (response.status_code == 403)
    user_json = response.json()
    user_json['success'] = search_was_successful
    user_json['fail'] = search_summoner_not_found
    user_json['api_error'] = error_api_key
    user_json['server'] = server
    return user_json

def player_stats(server, summoner_name):
    user_json = get_main_data(server, summoner_name)
    summoner_name = user_json['name']
    summoner_id = user_json['id']
    account_id = user_json['accountId']
    
    URL = "https://" + server + ".api.riotgames.com/lol/league/v4/entries/by-summoner/" + summoner_id + "?api_key=" + ApiKey
    response = requests.get(URL)
    stats_json = response.json()
    
    try:
        stats_json = stats_json[0]
    
    except IndexError:
        stats_json = {'tier': 'Unranked', 'rank': '0',
                    'summonerId': summoner_id, 
                    'leaguePoints': '0', 
                    'wins': '0', 'losses': '0', 
                    'hotStreak': False}

    wins = stats_json['wins']
    defeats = stats_json['losses']
    total_games = int(wins) + int(defeats)
    stats_json['total_games'] = str(total_games)
    
    try: 
        stats_json['win_rate'] = str(round(((int(wins) / total_games) * 100), 1))
    except ZeroDivisionError: 
        stats_json['win_rate'] = 0

    stats_json['name'] = summoner_name
    stats_json['accountId'] = account_id
    stats_json['server'] = server
    
    return stats_json

def past_games(server, account_id):
    URL = "https://" + server + ".api.riotgames.com/lol/match/v4/matchlists/by-account/" + account_id + "?api_key=" + ApiKey
    response = requests.get(URL)
    old_games_json = response.json()
    old_games_json = old_games_json['matches']
    old_games_json = old_games_json[:10]
    
    for index in range(len(old_games_json)):
        key = (old_games_json[index]['champion'])
        key = str(key)
        r = requests.get("http://ddragon.leagueoflegends.com/cdn/10.13.1/data/en_US/champion.json")
        j = r.json()
        data = j["data"]
        by_key = {x['key']: x for x in data.values()}
        champ_name = (by_key.get(key)['id'])
        old_games_json[index]['champion_name'] = champ_name
        
        gameid = (old_games_json[index]['gameId'])
        
        URL = "https://" + server + ".api.riotgames.com/lol/match/v4/matches/" + str(gameid) + "?api_key=" + ApiKey
        response = requests.get(URL)
        game_json = response.json()
        
        game_duration_seconds = game_json['gameDuration'] 
        game_duration = str(datetime.timedelta(seconds=game_duration_seconds))
        old_games_json[index]['game_duration'] = game_duration
        
        game_mode = game_json['gameMode'] 
        old_games_json[index]['gameMode'] = game_mode
        
        game_creation = game_json['gameCreation']  
        time_diff = get_time(game_creation)
        old_games_json[index]['time_diff'] = time_diff
        
        
        for player in range(len(game_json['participants'])):
            if str(game_json['participants'][player]['championId']) == key:
                win = game_json['participants'][player]['stats']["win"]
                kills = game_json['participants'][player]['stats']["kills"]
                deaths = game_json['participants'][player]['stats']["deaths"]
                assists = game_json['participants'][player]['stats']["assists"]
        
        old_games_json[index]['win'] = win
        old_games_json[index]['kills'] = kills
        old_games_json[index]['deaths'] = deaths
        old_games_json[index]['assist'] = assists
        
        del old_games_json[index]['timestamp']
        del old_games_json[index]['queue']
        del old_games_json[index]['platformId']
        
        if old_games_json[index]['win'] == False:
            old_games_json[index]['win'] = 'False'
        else:
            old_games_json[index]['win'] = 'True'
    
    return old_games_json

def champion_information(server, summoner_name, champion_name):
    r = requests.get("http://ddragon.leagueoflegends.com/cdn/10.13.1/data/en_US/champion.json")
    j = r.json()
    data = j["data"]
    by_id = {x['id']: x for x in data.values()}
    champ_key = (by_id.get(champion_name)['key'])
    
    user_json = get_main_data(server, summoner_name)
    summoner_name = user_json['name']
    summoner_id = user_json['id']
    account_id = user_json['accountId']
    
    URL = "https://" + server + ".api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/" + summoner_id  + '/by-champion/' + champ_key + "?api_key=" + ApiKey
    response = requests.get(URL)
    champ_json = response.json()
    champ_json['champ_name'] = champion_name
    
    champ_json['name'] = summoner_name
    champ_json['accountId'] = account_id
    
    last_played = champ_json['lastPlayTime']  
    time_diff = get_time(last_played)
    
    champ_json['last_time'] = time_diff
    
    champ_json['server'] = server
    
    return champ_json

def champion_games(server, account_id, champion_id):
    champion_id = str(champion_id)
    URL = "https://" + server + ".api.riotgames.com/lol/match/v4/matchlists/by-account/" + account_id  + '?champion=' + champion_id + "&api_key=" + ApiKey
    response = requests.get(URL)
    champ_games_json = response.json()
    champ_games_json = champ_games_json['matches']
    champ_games_json = champ_games_json[:8]
    
    for index in range(len(champ_games_json)):
        key = (champ_games_json[index]['champion'])
        key = str(key)
        r = requests.get("http://ddragon.leagueoflegends.com/cdn/10.13.1/data/en_US/champion.json")
        j = r.json()
        data = j["data"]
        by_key = {x['key']: x for x in data.values()}
        champ_name = (by_key.get(key)['id'])
        champ_games_json[index]['champion_name'] = champ_name
        
        gameid = (champ_games_json[index]['gameId'])
        
        URL = "https://" + server + ".api.riotgames.com/lol/match/v4/matches/" + str(gameid) + "?api_key=" + ApiKey
        response = requests.get(URL)
        game_json = response.json()
        
        game_duration_seconds = game_json['gameDuration'] 
        game_duration = str(datetime.timedelta(seconds=game_duration_seconds))
        champ_games_json[index]['game_duration'] = game_duration
        
        game_mode = game_json['gameMode'] 
        champ_games_json[index]['gameMode'] = game_mode
        
        game_creation = game_json['gameCreation']  
        time_diff = get_time(game_creation)
        champ_games_json[index]['time_diff'] = time_diff
        
        
        for player in range(len(game_json['participants'])):
            if str(game_json['participants'][player]['championId']) == key:
                win = game_json['participants'][player]['stats']["win"]
                kills = game_json['participants'][player]['stats']["kills"]
                deaths = game_json['participants'][player]['stats']["deaths"]
                assists = game_json['participants'][player]['stats']["assists"]
        
        champ_games_json[index]['win'] = win
        champ_games_json[index]['kills'] = kills
        champ_games_json[index]['deaths'] = deaths
        champ_games_json[index]['assist'] = assists
        
        del champ_games_json[index]['timestamp']
        del champ_games_json[index]['queue']
        del champ_games_json[index]['platformId']
        
        if champ_games_json[index]['win'] == False:
            champ_games_json[index]['win'] = 'False'
        else:
            champ_games_json[index]['win'] = 'True'
    
    pprint(champ_games_json)
    
    return champ_games_json
    

def game_information(server, gameid):
    URL = "https://" + server + ".api.riotgames.com/lol/match/v4/matches/" + str(gameid) + "?api_key=" + ApiKey
    response = requests.get(URL)
    game_json = response.json()
    
    game_json['server'] = server
    
    game_duration_seconds = game_json['gameDuration'] 
    game_duration = str(datetime.timedelta(seconds=game_duration_seconds))
    
    game_json['gameDuration'] = game_duration
    
    game_creation = game_json['gameCreation']
    game_creation = get_time(game_creation)
    
    game_json['gameCreation'] = game_creation
    
    blue_team_json = game_json['teams'][0]
    red_team_json = game_json['teams'][1]
    
    blue_participants_json = game_json['participants'][:5]
    red_participants_json = game_json['participants'][5:]
    
    
    
    del game_json['teams']
    del game_json['participants']
    del game_json['participantIdentities']
    
    pprint(game_json)
    
    return game_json
    
    
    

def get_time(unix_millisecons):
    unix_millisecons = datetime.date.fromtimestamp(unix_millisecons/1000.0)
    today = datetime.date.today()
    time_diff = abs((today - unix_millisecons).days)
    if time_diff == 0:
        time_diff = 'Today'
    elif time_diff == 1:
        time_diff = 'Yesterday'
    else:
        time_diff = str(time_diff) + ' days ago'
    return time_diff