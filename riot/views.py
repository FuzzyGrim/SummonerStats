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

    # Show the index page by default
    return render(request, 'riot/index.html', {'user': user})

def user_info(request, server, summoner_name):
    """
    Get the main data of player from the summoner name and server
    """
    
    # If user uses navbar search
    if ('summoners_name' and 'server') in request.POST:
        summoner_name = request.POST['summoners_name']
        server = request.POST['server']

        return redirect("/"+server+"/"+summoner_name+"/")

    user_account_info, ranked_stats = player_ranked_stats(server, summoner_name)
    
    if user_account_info['success']:

        account_id = user_account_info['accountId']

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

        if ('load') in request.POST:
            gameId = (request.POST['load'])
            
            game_data = game_summary(server, gameId)

            return render(request, 'riot/user-profile.html', {'user_account_info': user_account_info, 'ranked_stats': ranked_stats, "games": games, "game_info_list": game_info_list, 'game_data': game_data})

        else:
            return render(request, 'riot/user-profile.html', {'user_account_info': user_account_info, 'ranked_stats': ranked_stats, "games": games, "game_info_list": game_info_list})
    
    return render(request, 'riot/user-profile.html', {'user_account_info': user_account_info, 'ranked_stats': ranked_stats})

def champ_info(request, server, summoner_name, champion_name):
    
    champ = champion_stats(server, summoner_name, champion_name)

    server = champ['server']
    account_id = champ['accountId']
    champion_id = champ['championId'] 
    
    champ_games = champion_games_json(server, account_id, champion_id)

    page = request.GET.get('page', 1)
    paginator = Paginator(champ_games, 20)

    try:
        games = paginator.page(page)
        start = games.start_index() - 1

        end = games.end_index()
        
        game_info_list = []

        for match in champ_games[start:end]:

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

    if ('load') in request.POST:
        gameId = (request.POST['load'])
        
        game_data = game_summary(server, gameId)
        return render(request, 'riot/champ.html', {'champ': champ, "games": games, "game_info_list": game_info_list, 'game_data': game_data})
    
    return render(request, 'riot/champ.html', {'champ': champ, "games": games, "game_info_list": game_info_list})

def game_info(request, server, game_id):
    game_info= game_summary(server, game_id)
    
    return render(request, 'riot/game.html', {'game_info': game_info})

def in_game(request, server, summoner_name):
    user, stats = player_ranked_stats(server, summoner_name)
    summoner_id = stats['summonerId']

    game_info, blue_players, red_players = in_game_info(server, summoner_id)
    game_info['summoner_name'] = summoner_name
    
    return render(request, 'riot/current.html', {'game_info': game_info, 'blue_players': blue_players, 'red_players': red_players})