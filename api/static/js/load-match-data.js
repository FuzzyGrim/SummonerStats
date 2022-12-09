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


        if (matchJson.teams[0].win === "Defeat") {
            document.querySelector('#match-'+ matchId + '-thead-blue').style.backgroundColor = "#91c1e4";
            document.querySelector('#match-'+ matchId + '-tbody-blue').style.backgroundColor = "#A3CFEC";
            document.querySelector('#match-'+ matchId + '-thead-red').style.backgroundColor = "#e09a95";
            document.querySelector('#match-'+ matchId + '-tbody-red').style.backgroundColor = "#E2B6B3";
        } else {
            document.querySelector('#match-'+ matchId + '-thead-blue').style.backgroundColor = "#e09a95";
            document.querySelector('#match-'+ matchId + '-tbody-blue').style.backgroundColor = "#E2B6B3";
            document.querySelector('#match-'+ matchId + '-thead-red').style.backgroundColor = "#91c1e4";
            document.querySelector('#match-'+ matchId + '-tbody-red').style.backgroundColor = "#A3CFEC";
        }
                                                        
        $('#match-'+ matchId + '-thead-blue').append(
            '<tr><th>' + matchJson.teams[0].win + ' (Blue Team) </th>'
            + '<th> Rank </th>'
            + '<th> KDA </th>'
            + '<th> DMG </th>'
            + '<th> Cs </th>'
            + '<th> Vs </th>'
            + '<th> GOLD </th>'
            + '<th> KP </th></tr>')
                                                    
        matchJson.participants.slice(0,5).forEach(participant => $('#match-'+ matchId + '-tbody-blue').append(
            '<tr><td>' + participant.championName + ' / <a href="/' + matchJson.platformId + '/' + participant.summonerName + '">' + participant.summonerName + '</a></td>'
            + '<td>' + participant.tier +  '</td>'
            + '<td>' + participant.kills + '/' +  participant.deaths + '/' +  participant.assists + '</td>'
            + '<td>' + participant.totalDamageDealtToChampions + 'k</td>'
            + '<td>' + participant.totalMinionsKilled + '</td>'
            + '<td>' + participant.visionScore + '</td>'
            + '<td>' + participant.goldEarned + 'k</td>'
            + '<td>' + participant.killParticipation + '%</td></tr>'))

        $('#match-'+ matchId + '-thead-red').append(
            '<tr><th>' + matchJson.teams[1].win + ' (Red Team) </th>'
            + '<th> Rank </th>'
            + '<th> KDA </th>'
            + '<th> DMG </th>'
            + '<th> Cs </th>'
            + '<th> Vs </th>'
            + '<th> GOLD </th>'
            + '<th> KP </th></tr>')

        matchJson.participants.slice(5,10).forEach(participant => $('#match-'+ matchId + '-tbody-red').append(
            '<tr><td>' + participant.championName + '/<a href="/' + matchJson.platformId + '/' + participant.summonerName + '">' + participant.summonerName + '</a></td>'
            + '<td>' + participant.tier +  '</td>'
            + '<td>' + participant.kills + '/' +  participant.deaths + '/' +  participant.assists + '</td>'
            + '<td>' + participant.totalDamageDealtToChampions + 'k</td>'
            + '<td>' + participant.totalMinionsKilled + '</td>'
            + '<td>' + participant.visionScore + '</td>'
            + '<td>' + participant.goldEarned + 'k</td>'
            + '<td>' + participant.killParticipation + '%</td></tr>'))
        dict[matchId] = true;
    }
    $('#match-'+matchId).toggle()
        
    }
});
}