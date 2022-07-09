var dict = new Object();
function loadMatchData(matchId) {
$.ajax({
    url : matchId, // the endpoint
    method: "GET",
    start_time: new Date().getTime(),
    error: function(xhr) {
    alert("Error: " + xhr.status + " - " + xhr.statusText);
    },
    success: function(matchJson){
    if(!( matchId in dict)){
        $('#match-'+ matchId + '-thead-general').append(
            '<tr><th> Id </th>'
            + '<th> Server </th>'
            + '<th> Date </th>'
            + '<th> Duration </th>'
            + '<th> Mode </th>'
            + '<th> Patch </th></tr>')

        $('#match-'+ matchId + '-tbody-general').append(
            '<tr><td>' + matchJson.gameId + '</td>'
            + '<td>' + matchJson.platformId + '</td>'
            + '<td>' + matchJson.gameCreation + '</td>'
            + '<td>' + matchJson.gameDuration + '</td>'
            + '<td>' + matchJson.gameMode + '</td>'
            + '<td>' + matchJson.gameVersion + '</td></tr>')
                                                        
        $('#match-'+ matchId + '-thead-blue').append(
            '<tr><th>' + matchJson.teams[0].win + ' (Blue Team) </th>'
            + '<th> Rank </th>'
            + '<th> KDA </th>'
            + '<th> Damage </th>'
            + '<th> CS </th>'
            + '<th> Vision Score </th></tr>')
                                                    
        matchJson.participants.slice(0,5).forEach(participant => $('#match-'+ matchId + '-tbody-blue').append(
            '<tr><td>' + participant.championName + '/<a href="/' + matchJson.platformId + '/' + participant.summonerName + '">' + participant.summonerName + '</a></td>'
            + '<td>' + participant.tier +  '</td>'
            + '<td>' + participant.kills + '/' +  participant.deaths + '/' +  participant.assists + '</td>'
            + '<td>' + participant.totalDamageDealtToChampions + '</td>'
            + '<td>' + participant.totalMinionsKilled + '</td>'
            + '<td>' + participant.visionScore + '</td></tr>'))

        $('#match-'+ matchId + '-thead-red').append(
            '<tr><th>' + matchJson.teams[1].win + ' (Red Team) </th>'
            + '<th> Rank </th>'
            + '<th> KDA </th>'
            + '<th> Damage </th>'
            + '<th> CS </th>'
            + '<th> Vision Score </th></tr>')

        matchJson.participants.slice(5,10).forEach(participant => $('#match-'+ matchId + '-tbody-red').append(
            '<tr><td>' + participant.championName + '/<a href="/' + matchJson.platformId + '/' + participant.summonerName + '">' + participant.summonerName + '</a></td>'
            + '<td>' + participant.tier +  '</td>'
            + '<td>' + participant.kills + '/' +  participant.deaths + '/' +  participant.assists + '</td>'
            + '<td>' + participant.totalDamageDealtToChampions + '</td>'
            + '<td>' + participant.totalMinionsKilled + '</td>'
            + '<td>' + participant.visionScore + '</td></tr>'))
        dict[matchId] = true;
    }
    $('#match-'+matchId).toggle()
        
    }
});
}