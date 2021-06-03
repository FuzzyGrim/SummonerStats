from django.shortcuts import render
from django.http import Http404, HttpResponse
import requests
from .services import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def index(request):
    user = {}
    if ('summoners_name' and 'server') in request.GET:
        username = request.GET['summoners_name']
        server = request.GET['server']

        user = get_main_data(server, username)

    return render(request, 'riot/index.html', {'user': user})

def user_info(request, server, summoner_name):

    stats = player_stats(server, summoner_name)
    
    account_id = stats['accountId']

    games_list = past_games_json(server, account_id)

    page = request.GET.get('page', 1)

    paginator = Paginator(games_list, 20)
    try:
        games = paginator.page(page)
        start = games.start_index() - 1

        end = games.end_index()
        
        game_info_list = []

        for match in games_list[start:end]:

            game_dict = {}

            champion_key = match['champion']
            lane = match['lane']
            role = match['role']
            timestamp = match['timestamp']
            champ_name, position, game_length = past_games(champion_key, lane, role, timestamp)
            game_dict['champion_name'] = champ_name
            game_dict['position'] = position
            game_dict['time_diff'] = game_length
            game_dict['game_id'] = str(match['gameId'])
            game_dict['champion'] = champion_key

            game_info_list.append(game_dict)

    except PageNotAnInteger:
        games = paginator.page(1)
    except EmptyPage:
        games = paginator.page(paginator.num_pages)

    summoner = {}

    if ('load') in request.POST:
        
        gameId, champ_key = (request.POST['load']).split("|")
        
        summoner = summoner_game_summary(server, gameId, champ_key)
    
    return render(request, 'riot/record.html', {'stats': stats, "games_list": games_list, "games": games, "game_info_list": game_info_list, "summoner": summoner})

def champ_info(request, server, summoner_name, champion_name):
    
    champ = champion_information(server, summoner_name, champion_name)
    
    server = champ['server']
    
    account_id = champ['accountId']
    
    champion_id = champ['championId'] 
    
    champ_games = champion_games(server, account_id, champion_id)
    
    return render(request, 'riot/champ.html', {'champ': champ, "champ_games": champ_games})

def game_info(request, server, game_id):
    game_info, blue_team, blue_players, red_team, red_players = game_information(server, game_id)
    
    return render(request, 'riot/game.html', {'game_info': game_info, 'blue_team': blue_team, 'blue_players': blue_players, 'red_team': red_team, 'red_players': red_players})

def in_game(request, server, summoner_name):
    stats = player_stats(server, summoner_name)
    summoner_id = stats['summonerId']

    game_info, blue_players, red_players = in_game_info(server, summoner_id)
    game_info['summoner_name'] = summoner_name
    
    return render(request, 'riot/current.html', {'game_info': game_info, 'blue_players': blue_players, 'red_players': red_players})