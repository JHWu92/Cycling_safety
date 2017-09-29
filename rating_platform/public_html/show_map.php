<?php

    session_start();
    require_once 'config.inc.php';
    require_once 'check-login.php';
    $ty = "";
    if(login($_SESSION)){
        $email = $_SESSION[$SESS_EMAIL];
        $uid = $_SESSION[$SESS_USER_ID];
        
        try{
            $pdo = new PDO($GLOBALS['DB_DSN'], $GLOBALS['DB_USER'], $GLOBALS['DB_PASSWD'], array(PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION));
        }catch (PDOException $e) {
            error_log('PDO Exception: '.$e);
            die('Connection failed: ' . $e->getMessage());
        }        
        $sql = "SELECT count(1) from $TABLE_RATING WHERE uid=?";
        $sth = $pdo->prepare($sql);
        $sth->execute(array($uid));
        $result = $sth->fetch();
        $cnt = $result[0];
            
        $ty = "Thank you $email! You've rated $cnt videos. We really appreciate your contribution.<br>";
    }
    session_destroy();
    
?>

<!DOCTYPE html>
<html>
<head>
    <title>Cycling Safety Project</title>

    <link href="css/main.css" rel="stylesheet" >

    <script src="js/jquery-3.1.1.min.js"></script>
    <!-- Bootstrap -->
    <link href="css/bootstrap.min.css" rel="stylesheet" media="screen">
    <script src="js/bootstrap.min.js"></script>
    <!-- leaflet -->
    <link rel="stylesheet" href="css/leaflet.css" />
    <script src="js/leaflet.js"></script>
      
    <style>
        #map {
            width: 100%;
            height: 700px;
        }
        .legend {
            background: white;
            line-height: 18px;
            color: #555;
        }
        .legend i {
            width: 18px;
            height: 18px;
            float: left;
            margin-right: 8px;
            opacity: 0.7;
        }
        .info {
            padding: 6px 8px;
            font: 14px/16px Arial, Helvetica, sans-serif;
            background: white;
            background: rgba(255,255,255,0.8);
            box-shadow: 0 0 15px rgba(0,0,0,0.2);
            border-radius: 5px;
        }
        .info h4 {
            margin: 0 0 5px;
            color: #777;
        }
    </style>
</head>
        
<body>
    
<div class="container">
    <h2><?=$ty?> </h2>
    <h2>Here is our current cycling safety map for D.C., thanks to contributions from you and other cyclists.</h2>
     <h2>You've logged out. But if you want to continue rating, click  <a href="index.html">here</a>. Otherwise, thanks again and come back soon! Remember, the more you rate, the higher your chances of winning a gift card! (we will make the winners public in September)</h2>
    <div id='map'></div>
</div>
<script>
    function getColor(d) {
        return d > 4 ? '#1a9641' :
               d > 3  ? '#a6d96a' :
               d > 2  ? '#ffffbf' :
               d > 1  ? '#fdae61' :
                          '#d7191c';
    }
    
    $.getJSON('mysql2geojson.php', show_map);
    function show_map(seg_rating){
        // use the color property to set the color on html
        function style(feature) { return { color: getColor(feature.properties.safetyScore)};}
        // display all properties for each segment
        function onEachFeature(feature,layer){
            var popUpContent = '';
            for (var key in feature.properties) {
                val = feature.properties[key];
                popUpContent += key + ':' + val + "<br>";
            }
            layer.bindPopup(popUpContent);
        }

        var mbUrl = 'https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoiamVmZnd1IiwiYSI6ImNqN2F3cGNicTBsY3gzMXBsOWR1cjc4bzEifQ.dlG9RH8QJ8lb-Il6Mhsdaw';
        var light = L.tileLayer(mbUrl, {id: 'mapbox.light'});
        var streets = L.tileLayer(mbUrl, {id: 'mapbox.streets'});
        var satellite = L.tileLayer(mbUrl, {id: 'mapbox.satellite'});
        // the map style
        var radio_layers = {
            'gray': light, 'street': streets, 'satellite': satellite, 
        };
                
        // add here if you need more layer
        // var layername = new L.LayerGroup():
        // L.geoJSON(data_var_name,  {style: set_style,onEachFeature: onEachFeature}).addTo(layername);
        var seg_rating_layer = new L.LayerGroup();
        var geojson = L.geoJSON(seg_rating, {style: style,onEachFeature: onEachFeature});
        geojson.addTo(seg_rating_layer);
        
        var check_layers = {
            // 'displaying text on html': layername,
            'seg_rating_layer': seg_rating_layer, 
        };
        
        var map = L.map('map', {
            layers: [streets, seg_rating_layer], // initial layer
            center: [38.9047829846, -77.0163424758],
            zoom: 13,
        });
        map.fitBounds(geojson.getBounds());
        
        L.control.layers(radio_layers).addTo(map);    
                
        // legend on bottom right
        var legend = L.control({position: 'bottomright'});
        legend.onAdd = function (map) {
            var div = L.DomUtil.create('div', 'info legend');
            var grades = [0, 1, 2, 3, 4];
            var labels = ['dangerous', 'quite dangerous', 'normal', 'quite safe', 'safe'];
            // loop through our density intervals and generate a label with a colored square for each interval
            for (var i = 0; i < grades.length; i++) {
                div.innerHTML +=
                    '<i style="background:' + getColor(grades[i] + 0.1, 1) + '"></i> ' + '<label>' +labels[i] + '</label>'+ '<br>';
            }
            return div;
        };
        legend.addTo(map);

    }

</script>

<footer class="footer">
        <div class="container">
            <p class="text-muted footer-text">
   Cycling Safety project is designed and lead by the <a href="http://www.urbancomputinglab.org">Urban Computing Lab</a> at the <a href="http://www.umd.edu/">University of Maryland</a> with support from the <a href="http://www.nsf.gov">National Science Foundation. </a>  If you have any suggestion or question, contact us at <a href="mailto:umdcyclingsafety@gmail.com">umdcyclingsafety@gmail.com</a>
            </p>
        </div>
    </footer>    
</body>
    
