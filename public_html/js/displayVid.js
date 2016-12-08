window.addEventListener('load', changeVid);

function changeVid() {

    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            document.getElementById("video").src = "https://www.youtube.com/embed/" + this.responseText;
        }
    };
    xmlhttp.open("GET", "display_vid.php", true);
    xmlhttp.send();
}