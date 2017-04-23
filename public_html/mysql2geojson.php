<?php
require_once 'geoPHP/geoPHP.inc';
require_once 'config.inc.php';

function wkt_to_json($wkt) {
    $geom = geoPHP::load($wkt,'wkt');
    return $geom->out('json');
}

function echoGeojson($pdo){
    # Build GeoJSON feature collection array
    $geojson = array(
       'type'      => 'FeatureCollection',
       'features'  => array()
    );

    $sql = 'SELECT geometry, ROUND(sumScore/sumRatio, 3) as safetyScore FROM RoadSegment where sumCnt>0';
    $select = $pdo->prepare($sql);
    $select->execute();
    
    # Loop through rows to build feature arrays
    while ($row = $select->fetch(PDO::FETCH_ASSOC)) {
        $properties = $row;
        # Remove geometry fields from properties
        unset($properties['geometry']);
        $feature = array(
             'type' => 'Feature',
             'geometry' => json_decode(wkt_to_json($row['geometry'])),
             'properties' => $properties
        );
        # Add feature arrays to feature collection array
        array_push($geojson['features'], $feature);
    }
    return json_encode($geojson);
}

# Connect to MySQL database
try{
    $pdo = new PDO($GLOBALS['DB_DSN'], $GLOBALS['DB_USER'], $GLOBALS['DB_PASSWD']);
        $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
}catch (PDOException $e) {
    echo 'Connection failed: ' . $e->getMessage();
}
$geojson = echoGeojson($pdo);

# clear pdo connection
$pdo = null;

header('Content-type: application/json');
echo $geojson;

    

?>