<?php
/**
 * Title:   MySQL to GeoJSON (Requires https://github.com/phayes/geoPHP)
 * Notes:   Query a MySQL table or view and return the results in GeoJSON format, suitable for use in OpenLayers, Leaflet, etc.
 * Author:  Bryan R. McBride, GISP
 * Contact: bryanmcbride.com
 * GitHub:  https://github.com/bmcbride/PHP-Database-GeoJSON
 */

# Include required geoPHP library and define wkb_to_json function
include_once('geoPHP/geoPHP.inc');
function wkb_to_json($wkb) {
    $geom = geoPHP::load($wkb,'wkb');
    return $geom->out('json');
}

# Connect to MySQL database
include_once('config.inc.php');  //$db_name, $host, $db_user, $db_pwd 
$con=mysqli_connect($host, $db_user, $db_pwd, $db_name);

if(mysqli_connect_errno())
	{
		echo"failed to connect to mysql:".mysqli_connect_error();
	}
else
    {
        # Build SQL SELECT statement and return the geometry as a WKB element
        $sql = 'SELECT *, AsWKB(geometry) AS wkb FROM RoadSegment';

        # Try query or error
        $rs = $conn->query($sql);
        
        if (!$rs) {
            echo 'An SQL error occured.\n';
            exit;
        }

        # Build GeoJSON feature collection array
        $geojson = array(
           'type'      => 'FeatureCollection',
           'features'  => array()
        );

        # Loop through rows to build feature arrays
        while ($row = $rs->fetch_assoc()) {
            $properties = $row;
            # Remove wkb and geometry fields from properties
            unset($properties['wkb']);
            unset($properties['geometry']);
            $feature = array(
                 'type' => 'Feature',
                 'geometry' => json_decode(wkb_to_json($row['wkb'])),
                 'properties' => $properties
            );
            # Add feature arrays to feature collection array
            array_push($geojson['features'], $feature);
        }

        header('Content-type: application/json');
        echo json_encode($geojson);
        $conn = NULL;
    }

?>