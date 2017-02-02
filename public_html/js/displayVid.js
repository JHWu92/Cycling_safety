window.addEventListener('load', changeVid);

function changeVid() {
    var player;
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            player = new YT.Player('player', {
                height: '390',
                width: '640',
                videoId: this.responseText,
                events: {
                    'onStateChange': function (event) {
                        switch (event.data) {
                            case 0:
                                document.getElementById("btn-rate").className = document.getElementById("btn-rate").className.replace("disabled","");
                                document.getElementById("btn-rate").disabled=false;
                        }
                    }
                }
            });
        }
    };

    xmlhttp.open("GET", "display_vid.php", true);
    xmlhttp.send();
}

