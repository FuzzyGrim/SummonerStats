import requests
import datetime
from pprint import pprint
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
    user_json['server'] = server
    return user_json

def player_stats(server, summoner_name):
    user_json = get_main_data(server, summoner_name)
    summoner_name = user_json['name']
    summoner_id = user_json['id']
    account_id = user_json['accountId']
    
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

    stats_json['name'] = summoner_name
    stats_json['accountId'] = account_id
    stats_json['server'] = server
    
    return stats_json

def past_games(server, account_id):
    URL = "https://" + server + ".api.riotgames.com/lol/match/v4/matchlists/by-account/" + account_id + "?api_key=" + API_KEY
    response = requests.get(URL)
    old_games_json = response.json()

    old_games_json = old_games_json['matches']
        
    for match in old_games_json:

        key = match['champion']
        key = str(key)

        champ_name = get_champ_name(key)

        match['champion_name'] = champ_name
        
        game_creation = match['timestamp']  
        time_diff = get_time(game_creation)
        match['time_diff'] = time_diff

        if match['role'] == 'SOLO':
            match['position'] = match['lane']
        else:
            match['position'] = match['role'][4:]

        match['game_id'] = str(match['gameId'])

    return old_games_json

def summoner_game_summary(server, gameId, champion_key):
    URL = "https://" + server + ".api.riotgames.com/lol/match/v4/matches/" + str(gameId) + "?api_key=" + API_KEY
    print(URL)

    response = requests.get(URL)
    game_json = response.json()

    game_duration_seconds = game_json['gameDuration'] 
    game_duration = str(datetime.timedelta(seconds=game_duration_seconds))

    summoner_stats = {}

    summoner_stats['game_duration'] = game_duration
    summoner_stats['game_mode'] = game_json['gameMode']

    # Find user's stats through both teams players
    for player in game_json['participants']:
        if str(player['championId']) == champion_key:
            win = player['stats']["win"]
            kills = player['stats']["kills"]
            deaths = player['stats']["deaths"]
            assists = player['stats']["assists"]
            vision_score = player['stats']["visionScore"]
            cs = player['stats']["totalMinionsKilled"]
            cs_min = round(player['timeline']["creepsPerMinDeltas"]["10-20"],2)
    
    summoner_stats['win'] = win
    summoner_stats['kills'] = kills
    summoner_stats['deaths'] = deaths
    summoner_stats['assist'] = assists
    summoner_stats['vision_score'] = vision_score
    summoner_stats['cs'] = cs
    summoner_stats['cs_min'] = cs_min
    
    if summoner_stats['win'] == False:
        summoner_stats['win'] = 'Defeat'
    else:
        summoner_stats['win'] = 'Victory'

    summoner_stats['success'] = True

    summoner_stats['game_id'] = gameId

    return summoner_stats



def champion_information(server, summoner_name, champion_name):
    startTime= datetime.datetime.now()
    r = requests.get("https://ddragon.leagueoflegends.com/realms/na.json")
    j = r.json()
    patch = j['dd']
    r = requests.get("https://ddragon.leagueoflegends.com/cdn/" + patch + "/data/en_US/champion.json")
    json_file = r.json()
    data = json_file["data"]
    by_id = {x['id']: x for x in data.values()}
    champ_key = (by_id.get(champion_name)['key'])
    
    timeElapsed=datetime.datetime.now()-startTime
    user_json = get_main_data(server, summoner_name)
    summoner_name = user_json['name']
    summoner_id = user_json['id']
    account_id = user_json['accountId']
    
    URL = "https://" + server + ".api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/" + summoner_id  + '/by-champion/' + champ_key + "?api_key=" + API_KEY
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
    URL = "https://" + server + ".api.riotgames.com/lol/match/v4/matchlists/by-account/" + account_id  + '?champion=' + champion_id + "&api_key=" + API_KEY
    response = requests.get(URL)
    champ_games_json = response.json()
    del champ_games_json['matches'][20:]
    
    for match in champ_games_json['matches']:
        key = match['champion']
        key = str(key)
        champ_name = get_champ_name(key)
        match['champion_name'] = champ_name
        
        gameid = match['gameId']
        
        URL = "https://" + server + ".api.riotgames.com/lol/match/v4/matches/" + str(gameid) + "?api_key=" + API_KEY
        response = requests.get(URL)
        game_json = response.json()
        
        game_duration_seconds = game_json['gameDuration'] 
        game_duration = str(datetime.timedelta(seconds=game_duration_seconds))
        match['game_duration'] = game_duration
        
        game_mode = game_json['gameMode'] 
        match['gameMode'] = game_mode
        
        game_creation = game_json['gameCreation']  
        time_diff = get_time(game_creation)
        match['time_diff'] = time_diff
        
        for player in game_json['participants']:
            if str(player['championId']) == key:
                win = player['stats']["win"]
                kills = player['stats']["kills"]
                deaths = player['stats']["deaths"]
                assists = player['stats']["assists"]
        
        match['win'] = win
        match['kills'] = kills
        match['deaths'] = deaths
        match['assist'] = assists
        
        if match['win'] == False:
            match['win'] = 'Defeat'
        else:
            match['win'] = 'Victory'
    
    return champ_games_json['matches']
    

def game_information(server, gameid):
    URL = "https://" + server + ".api.riotgames.com/lol/match/v4/matches/" + str(gameid) + "?api_key=" + API_KEY
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
    
    if blue_team_json['win'] == True:
        blue_team_json['win'] = 'Victory'
    else:
        blue_team_json['win'] = 'Defeat'
        
        
    red_team_json = game_json['teams'][1]
    if red_team_json['win'] == True:
        red_team_json['win'] = 'Victory'
    else:
        red_team_json['win'] = 'Defeat'
        
        
    blue_participants_json = game_json['participants'][:5]
    red_participants_json = game_json['participants'][5:]

    for participant in blue_participants_json:
        key = participant['championId']
        key = str(key)
        champ_name = get_champ_name(key)
        participant['champion_name'] = champ_name
        
        kills = participant['stats']['kills']
        deaths = participant['stats']['deaths']
        assists = participant['stats']['assists']
        
        kda = f'{kills}/{deaths}/{assists}'
        
        participant['kda'] = kda
        
        participant_id = participant['stats']['participantId']
        
        for playerid in game_json['participantIdentities']:
            if playerid['participantId'] == participant_id:
                summoner_name = playerid['player']['summonerName']
                
                stats = player_stats(server, summoner_name)
                tier = stats['tier']
                rank = stats['rank']
                
                tier = f'{tier} {rank}'
        
        participant['tier'] = tier
        participant['summoner_name'] = summoner_name
        
        
    for participant in red_participants_json:
        key = participant['championId']
        key = str(key)
        champ_name = get_champ_name(key)
        participant['champion_name'] = champ_name
        
        kills = participant['stats']['kills']
        deaths = participant['stats']['deaths']
        assists = participant['stats']['assists']
        
        kda = f'{kills}/{deaths}/{assists}'
        
        participant['kda'] = kda
        
        participant_id = participant['stats']['participantId']
        
        for playerid in game_json['participantIdentities']:
            if playerid['participantId'] == participant_id:
                summoner_name = playerid['player']['summonerName']
                
                stats = player_stats(server, summoner_name)
                tier = stats['tier']
                rank = stats['rank']
                
                tier = f'{tier} {rank}'
        
        participant['tier'] = tier
        participant['summoner_name'] = summoner_name
        
    return game_json, blue_team_json, blue_participants_json, red_team_json, red_participants_json
    

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
                    
            stats = player_stats(server, summoner_name)
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
                    
            stats = player_stats(server, summoner_name)
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