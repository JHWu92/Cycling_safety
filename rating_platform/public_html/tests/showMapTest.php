<?php
require 'DBFixture.php';
require dirname(__FILE__).'/../mysql2geojson.php';

class mapTest extends DBFixtureTestCase{
    public function testGeojson(){
        $geojson = echoGeojson(self::$pdo);
        $file = file_get_contents(dirname(__FILE__)."/test_data/showMap.geojson");
        echo $file;
        $this->assertEquals($file, $geojson);
    }
} 
?>