import requests
import datetime
from secret import API

API_KEY = API

def get_main_data(server, name):
    URL = "https://" + server + ".api.riotgames.com/lol/summoner/v4/summoners/by-name/" + name + "?api_key=" + API_KEY

    response = requests.get(URL)
    search_was_successful = (response.status_code == 200)
    summoner_not_found = (response.status_code == 404)
    user_json = response.json()

    user_json['success'] = search_was_successful
    user_json['fail'] = summoner_not_found
    return user_json

def player_ranked_stats(server, summoner_name):

    user_json = get_main_data(server, summoner_name)

    if user_json['success']:
        
        summoner_id = user_json['id']
        URL = "https://" + server + ".api.riotgames.com/lol/league/v4/entries/by-summoner/" + summoner_id + "?api_key=" + API_KEY
        response = requests.get(URL)
        stats_json = response.json()
        
        try:
            stats_json = stats_json[0]
        
        # IndexError if player haven't played any game
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

        stats_json['server'] = server
        
    elif user_json['fail']:
            stats_json = {}

    return user_json, stats_json

def past_games_json(server, account_id):
    URL = "https://" + server + ".api.riotgames.com/lol/match/v4/matchlists/by-account/" + account_id + "?api_key=" + API_KEY
    response = requests.get(URL)
    old_games_json = response.json()
    old_games_json = old_games_json['matches']
    return old_games_json

def champion_games_json(server, account_id, champion_id):
    champion_id = str(champion_id)
    URL = "https://" + server + ".api.riotgames.com/lol/match/v4/matchlists/by-account/" + account_id  + '?champion=' + champion_id + "&api_key=" + API_KEY
    response = requests.get(URL)
    old_games_json = response.json()
    old_games_json = old_games_json['matches']
    return old_games_json

def past_games(champion_key, lane, role, timestamp):

    key = champion_key
    key = str(key)

    champ_name = get_champ_name(key)
        
    if role == 'SOLO' or role == 'DUO' or role == 'NONE':
        position = lane
    else:
        position = role[4:]

    game_creation = timestamp
    game_length = get_time(game_creation)

    return champ_name, position, game_length


def champion_stats(server, summoner_name, champion_name):
    r = requests.get("https://ddragon.leagueoflegends.com/realms/na.json")
    j = r.json()
    patch = j['dd']
    r = requests.get("https://ddragon.leagueoflegends.com/cdn/" + patch + "/data/en_US/champion.json")
    json_file = r.json()
    data = json_file["data"]
    by_id = {x['id']: x for x in data.values()}
    champ_key = (by_id.get(champion_name)['key'])
    
    user_json = get_main_data(server, summoner_name)

    summoner_id = user_json['id']
    account_id = user_json['accountId']
    
    URL = "https://" + server + ".api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/" + summoner_id  + '/by-champion/' + champ_key + "?api_key=" + API_KEY
    response = requests.get(URL)
    champ_json = response.json()
    champ_json['champ_name'] = champion_name
    
    champ_json['summoner_name'] = summoner_name
    champ_json['accountId'] = account_id
    
    last_played = champ_json['lastPlayTime']  
    time_diff = get_time(last_played)
    champ_json['last_time'] = time_diff
    
    champ_json['server'] = server
    
    return champ_json
    

def game_summary(server, gameid):

    URL = "https://" + server + ".api.riotgames.com/lol/match/v4/matches/" + str(gameid) + "?api_key=" + API_KEY
    response = requests.get(URL)
    game_json = response.json()
    
    game_json['game_id'] = str(game_json['gameId'])
    game_json['success'] = True
    
    game_duration_seconds = game_json['gameDuration'] 
    game_duration = str(datetime.timedelta(seconds=game_duration_seconds))
    game_json['gameDuration'] = game_duration
    
    
    game_creation = game_json['gameCreation']
    game_creation = get_time(game_creation)
    game_json['gameCreation'] = game_creation

    for participant in game_json['participants']:
        key = participant['championId']
        key = str(key)
        champ_name = get_champ_name(key)
        participant['champion_name'] = champ_name
    
    current_player= -1

    for player in game_json['participantIdentities']:

        current_player += 1
        
        summonerId = player['player']['summonerId']
        URL = "https://" + server + ".api.riotgames.com/lol/league/v4/entries/by-summoner/" + summonerId + "?api_key=" + API_KEY
        response = requests.get(URL)
        stats_json = response.json()
        
        try:
            stats_json = stats_json[0]
        
        # IndexError if player haven't played any game
        except IndexError:
            stats_json = {'tier': 'Unranked', 'rank': '0',
                        'summonerId': summonerId, 
                        'leaguePoints': '0', 
                        'wins': '0', 'losses': '0', 
                        'hotStreak': False}
        
        tier = stats_json['tier']
        rank = stats_json['rank']

        game_json['participants'][current_player]['tier'] = f'{tier} {rank}'
        game_json['participants'][current_player]['summoner_name'] = player['player']['summonerName']        

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

def get_champ_name(key):
    r = requests.get("https://ddragon.leagueoflegends.com/realms/na.json")
    j = r.json()
    patch = j['dd']
    r = requests.get("https://ddragon.leagueoflegends.com/cdn/" + patch + "/data/en_US/champion.json")
    j = r.json()
    data = j["data"]
    by_key = {x['key']: x for x in data.values()}
    champ_name = (by_key.get(key)['id'])
    
    return champ_name

def in_game_info(server, summoner_id):
    URL = "https://" + server + ".api.riotgames.com/lol/spectator/v4/active-games/by-summoner/" + (summoner_id) + "?api_key=" + API_KEY
    response = requests.get(URL)
    search_was_successful = (response.status_code == 200)
    not_in_game = (response.status_code == 404)

    in_game_json = response.json()
    
    in_game_json['success'] = search_was_successful
    in_game_json['fail'] = not_in_game

    if search_was_successful:

        blue_participants_json = in_game_json['participants'][:5]
        red_participants_json = in_game_json['participants'][5:]

        for participant in blue_participants_json:
            key = participant['championId']
            key = str(key)
            champ_name = get_champ_name(key)
            participant['champion_name'] = champ_name
            
            summoner_name = participant['summonerName']
                    
            user, stats = player_ranked_stats(server, summoner_name)
            tier = stats['tier']
            rank = stats['rank']
            tier = f'{tier} {rank}'
            participant['tier'] = tier
            
            
            wins = stats['wins']
            defeats = stats['losses']
            total_games = stats['total_games']
            win_rate = stats['win_rate']
            
            ranked_stats = f"{wins}/{defeats}   W={win_rate}% ({total_games} Played)"
            participant['ranked_stats'] = ranked_stats
            
            
        for participant in red_participants_json:
            key = participant['championId']
            key = str(key)
            champ_name = get_champ_name(key)
            participant['champion_name'] = champ_name
            
            summoner_name = participant['summonerName']
                    
            user, stats = player_ranked_stats(server, summoner_name)
            tier = stats['tier']
            rank = stats['rank']
            tier = f'{tier} {rank}'
            participant['tier'] = tier
            
            
            wins = stats['wins']
            defeats = stats['losses']
            total_games = stats['total_games']
            win_rate = stats['win_rate']

            ranked_stats = f"{wins}/{defeats}   W={win_rate}% ({total_games} Played)"
            participant['ranked_stats'] = ranked_stats
            
        return in_game_json, blue_participants_json, red_participants_json
    
    elif not_in_game:
        blue_participants_json = {}
        red_participants_json = {}
        return in_game_json, blue_participants_json, red_participants_json