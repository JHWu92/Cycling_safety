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

    <script src="js/script.js"></script>
    <link href="css/main.css" rel="stylesheet" >

    <script src="js/jquery-3.1.1.min.js"></script>
    <!-- Bootstrap -->
    <link href="css/bootstrap.min.css" rel="stylesheet" media="screen">
    <script src="js/bootstrap.min.js"></script>
    <!-- leaflet -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.0.1/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.0.1/dist/leaflet.js"></script>
      
    <style>
        #map {
            width: 90%;
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

    <h2>Thank you! <?=$email?>. Here is our cycling safety map for D.C. so far.</h2>
     <h2>If you want to continue rating, go back to <a href="index.html">Home page</a>. Appreciate your contribution.</h2>
        
    <div id='map'></div>
</div>

<script>
    function getColor(score, ratio) {
        d = score/ratio;
        console.log(score, ratio, d);
        return d > 4 ? '#005824' :
               d > 3  ? '#238b45' :
               d > 2  ? '#41ae76' :
               d > 1  ? '#66c2a4' :
                          '#99d8c9';
    }
    
    $.getJSON('mysql2geojson.php', show_map);
    function show_map(seg_rating){
        // use the color property to set the color on html
        function style(feature) { return { color: getColor(feature.properties.sumScore, feature.properties.sumRatio)};}
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
        L.geoJSON(seg_rating, {style: style,onEachFeature: onEachFeature}).addTo(seg_rating_layer);
        
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
                
        // legend on bottom right
        var legend = L.control({position: 'bottomright'});
        legend.onAdd = function (map) {
            var div = L.DomUtil.create('div', 'info legend');
            var grades = [0, 1, 2, 3, 4];
            var labels = ['<1', '1~2', '2~3', '3~4', '4~5'];
            // loop through our density intervals and generate a label with a colored square for each interval
            for (var i = 0; i < grades.length; i++) {
                div.innerHTML +=
                    '<i style="background:' + getColor(grades[i] + 0.1, 1) + '"></i> ' + '<label>' +
                    grades[i] + (grades[i + 1] ? '&ndash;' + grades[i + 1]  : '+') + '</label>'+ '<br>';
            }
            return div;
        };
        legend.addTo(map);

    }

</script>
    
</body>
    