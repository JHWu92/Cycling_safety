window.addEventListener('load', changeVid);

function changeVid() {
    var player;
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            player = new YT.Player('player', {
                height: '480px',
                width: '100%',
                videoId: this.responseText,
                playerVars:{rel:0, autohide:0,},
                events: { 
                  'onReady': onPlayerReady,
                  'onStateChange': onPlayerStateChange
                }
            });
        }
    };

    xmlhttp.open("GET", "display_vid.php", true);
    xmlhttp.send();
}

function updateInteraction(event, action){
    var nowISO = new Date().toISOString();
    action_log = action+","+nowISO+','+event.target.getCurrentTime()+";";
    $('#interaction').val($('#interaction').val()+action_log);
}

function onPlayerReady(event) {
    updateInteraction(event, 'playerReady');
}

function onPlayerStateChange(event) {
    var color;
    playerStatus = event.data;
    if (playerStatus == -1) {
        updateInteraction(event, 'unstarted');
    } else if (playerStatus == 0) {
        document.getElementById("btn-rate").className = document.getElementById("btn-rate").className.replace("disabled","");
        $('#wrapper').tooltip('disable');
        document.getElementById("btn-rate").disabled=false;
        document.getElementById("watched").value = '1';
        updateInteraction(event, 'end');
    } else if (playerStatus == 1) {
        updateInteraction(event, 'playing');
    } else if (playerStatus == 2) {
        updateInteraction(event, 'paused');
    } else if (playerStatus == 3) {
        updateInteraction(event, 'buffering');
    } else if (playerStatus == 5) {
        updateInteraction(event, 'cued');
    }
}
