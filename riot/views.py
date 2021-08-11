from django.shortcuts import render, redirect
from django.http import Http404, HttpResponse
import requests
from .services import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def index(request):

    user = {}

    # If user submits the form, it will redirect to the user profile page
    if ('summoners_name' and 'server') in request.POST:
        summoner_name = request.POST['summoners_name']
        server = request.POST['server']

        return redirect(server+"/"+summoner_name+"/")

    load_champ_json_session(request)

    return render(request, 'riot/index.html', {'user': user})

def user_info(request, server, summoner_name, template='riot/user-profile.html'):
    """
    Get the main data of player from the summoner name and server
    """
    
    # If user uses navbar search
    if ('summoners_name' and 'server') in request.POST:
        summoner_name = request.POST['summoners_name']
        server = request.POST['server']

        return redirect("/"+server+"/"+summoner_name+"/")

    user_account_info, ranked_stats = get_ranked_stats(server, summoner_name)
    
    if user_account_info['success']:

        account_id = user_account_info['accountId']

        games_list = get_past_games(server, account_id)

        champ_json = load_champ_json_session(request)

        game_info_list = []

        for match in games_list:

            game_dict = {}

            champ_name = get_champion_name(match['champion'], champ_json)
            position = get_position(match['lane'], match['role'])
            game_date = get_game_date(match['timestamp'])
            game_dict['champion_name'] = champ_name
            game_dict['position'] = position
            game_dict['date'] = game_date
            game_dict['game_id'] = str(match['gameId'])
            game_dict['champion'] = 'champion_key'

            game_info_list.append(game_dict)

        context = {'game_info_list': game_info_list,
                    'user_account_info': user_account_info, 
                   'ranked_stats': ranked_stats, 
        }
        if request.is_ajax():
            template = 'riot/include/user-profile-page.html'

        if ('load') in request.POST:
            gameId = (request.POST['load'])
            
            game_data = game_summary(server, gameId, champ_json)

            return render(request, 'riot/user-profile.html', {'user_account_info': user_account_info, 'ranked_stats': ranked_stats, "game_info_list": game_info_list, 'game_data': game_data})

        else:
            return render(request, template, context)
    
    return render(request, 'riot/user-profile.html', {'user_account_info': user_account_info, 'ranked_stats': ranked_stats})

def champ_info(request, server, summoner_name, champion_name):
    if ('summoners_name' and 'server') in request.POST:
        summoner_name = request.POST['summoners_name']
        server = request.POST['server']

        return redirect("/"+server+"/"+summoner_name+"/")

    champ_json = load_champ_json_session(request)

    champ = get_champion_stats(server, summoner_name, champion_name, champ_json)

    server = champ['server']
    account_id = champ['accountId']
    champion_id = champ['championId'] 
    
    champ_games = get_champion_matchlist(server, account_id, champion_id)
        
    game_info_list = []

    for match in champ_games:

        game_dict = {}
        champ_name = get_champion_name(match['champion'], champ_json)
        position = get_position(match['lane'], match['role'])
        game_date = get_game_date(match['timestamp'])
        game_dict['champion_name'] = champ_name
        game_dict['position'] = position
        game_dict['date'] = game_date
        game_dict['game_id'] = str(match['gameId'])
        game_dict['champion'] = match['champion']

        game_info_list.append(game_dict)

    if ('load') in request.POST:
        gameId = (request.POST['load'])
        
        game_data = game_summary(server, gameId, champ_json)
        return render(request, 'riot/champ.html', {'champ': champ, "game_info_list": game_info_list, 'game_data': game_data})
    
    return render(request, 'riot/champ.html', {'champ': champ, "game_info_list": game_info_list})

def in_game(request, server, summoner_name):
    user, stats = get_ranked_stats(server, summoner_name)
    summoner_id = stats['summonerId']

    champ_json = load_champ_json_session(request)

    game_info, blue_players, red_players = in_game_info(server, summoner_id, champ_json)
    game_info['summoner_name'] = summoner_name
    
    return render(request, 'riot/current.html', {'game_info': game_info, 'blue_players': blue_players, 'red_players': red_players})