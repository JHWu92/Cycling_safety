<?php
    session_start();
    include_once('config.inc.php');
    $email = $_SESSION[$SESS_EMAIL];
    session_destroy();
    
?>

<!DOCTYPE html>
<html>
<head>
    <title>Cycling Safety Map</title>

    <script src="js/jquery-3.1.1.min.js"></script>
    <!-- Bootstrap -->
    <link href="css/bootstrap.min.css" rel="stylesheet" media="screen">
    <script src="js/bootstrap.min.js"></script>
    <!-- leaflet -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.0.1/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.0.1/dist/leaflet.js"></script>
      
    <script src="js/script.js"></script>
    <link href="css/main.css" rel="stylesheet" >

    <style>
        #map {
            width: 90%;
            height: 700px;
        }
    </style>
</head>
        
<body>
    
<div class="container">

    <h2>Thank you! <?=$email?>. Here is our cycling safety map for D.C. so far.</h2>
     <h2>If you want to continue rating, go back to <a href="index.html">Home page</a>. Appreciate your contribution.</h2>
        
    <div id='map'></div>
</div>

<script>
    $.getJSON('mysql2geojson.php', show_map);
    function show_map(seg_rating){
        // use the color property to set the color on html
        function set_style(feature){return {color: '#F00'};}
        
        // display all properties for each segment
        function onEachFeature(feature,layer){
            var popUpContent = '';
            for (var key in feature.properties) {
                val = feature.properties[key];
                popUpContent += key + ':' + val + "<br>";
            }
            layer.bindPopup(popUpContent);
        }

        var mbUrl = 'https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1Ijoic3VyYWpuYWlyIiwiYSI6ImNpdWoyZGQzYjAwMXkyb285b2Q5NmV6amEifQ.WBQAX7ur2T3kOLyi11Nybw';
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
        L.geoJSON(seg_rating, {style: set_style,onEachFeature: onEachFeature}).addTo(seg_rating_layer);
        
        var check_layers = {
            // 'displaying text on html': layername,
            'seg_rating_layer': seg_rating_layer, 
        };
        
        var map = L.map('map', {
            center: [38.9047829846, -77.0163424758],
            zoom: 13,
            layers: [streets, seg_rating_layer] // initial layer
        });
        
        L.control.layers(radio_layers).addTo(map);    
    }

</script>
    
</body>
    