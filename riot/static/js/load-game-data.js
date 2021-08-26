var dict = new Object();
function loadGameData(gameId) {
$.ajax({
    url : gameId, // the endpoint
    method: "GET",
    start_time: new Date().getTime(),
    beforeSend: function(){
    $('#spinner-span-'+ gameId).show();
    },
    complete: function(){
    console.log('This request took '+(new Date().getTime() - this.start_time)+' ms');
    $('#spinner-span-'+ gameId).hide();
    },
    error: function(xhr, status, error) {
    alert("Rate limitation error");
    },
    success: function(gameJson){
    if(!( gameId in dict)){
        $('#game-'+ gameId + '-thead-general').append(
            '<tr><th> GameId </th>'
            + '<th> Server </th>'
            + '<th> When </th>'
            + '<th> Duration </th>'
            + '<th> Game Mode </th>'
            + '<th> Patch </th></tr>')

        $('#game-'+ gameId + '-tbody-general').append(
            '<tr><td>' + gameJson.gameId + '</td>'
            + '<td>' + gameJson.platformId + '</td>'
            + '<td>' + gameJson.gameCreation + '</td>'
            + '<td>' + gameJson.gameDuration + '</td>'
            + '<td>' + gameJson.gameMode + '</td>'
            + '<td>' + gameJson.gameVersion + '</td></tr>')
                                                        
        $('#game-'+ gameId + '-thead-blue').append(
            '<tr><th>' + gameJson.teams[0].win + ' (Blue Team) </th>'
            + '<th> Rank </th>'
            + '<th> KDA </th>'
            + '<th> Damage </th>'
            + '<th> CS </th>'
            + '<th> Vision Score </th></tr>')
                                                    
        gameJson.participants.slice(0,5).forEach(participant => $('#game-'+ gameId + '-tbody-blue').append(
            '<tr><td>' + participant.champion_name + '/<a href="/' + gameJson.platformId + '/' + participant.summoner_name + '">' + participant.summoner_name + '</a></td>'
            + '<td>' + participant.tier +  '</td>'
            + '<td>' +  participant.stats.kills + '/' +  participant.stats.deaths + '/' +  participant.stats.assists + '</td>'
            + '<td>' + participant.stats.totalDamageDealtToChampions + '</td>'
            + '<td>' + participant.stats.totalMinionsKilled + '</td>'
            + '<td>' + participant.stats.visionScore + '</td></tr>'))

        $('#game-'+ gameId + '-thead-red').append(
            '<tr><th>' + gameJson.teams[1].win + ' (Red Team) </th>'
            + '<th> Rank </th>'
            + '<th> KDA </th>'
            + '<th> Damage </th>'
            + '<th> CS </th>'
            + '<th> Vision Score </th></tr>')

        gameJson.participants.slice(5,10).forEach(participant => $('#game-'+ gameId + '-tbody-red').append(
            '<tr><td>' + participant.champion_name + '/<a href="/' + gameJson.platformId + '/' + participant.summoner_name + '">' + participant.summoner_name + '</a></td>'
            + '<td>' + participant.tier +  '</td>'
            + '<td>' +  participant.stats.kills + '/' +  participant.stats.deaths + '/' +  participant.stats.assists + '</td>'
            + '<td>' + participant.stats.totalDamageDealtToChampions + '</td>'
            + '<td>' + participant.stats.totalMinionsKilled + '</td>'
            + '<td>' + participant.stats.visionScore + '</td></tr>'))
        dict[gameId] = true;
    }
    $('#game-'+gameId).toggle()
    $('#show-span-'+ gameId).toggle();
    $('#hide-span-'+ gameId).toggle();
        
    }
});
}