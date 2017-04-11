<?php
require 'DBFixture.php';
require dirname(__FILE__).'/../rateDB.php';
include_once(dirname(__FILE__).'/../config.inc.php');
class loginTest extends DBFixtureTestCase{
    
    public function testRateOnlyScore(){
        # T15
        $conn = $this->getConnection();            
        $tags = array();
        $post_data = array($GLOBALS['POST_SCORE']=>5, 'btn-rate'=>1, 'btn-done'=>null, 
                                        $GLOBALS['POST_FAMILIAR_ST']=>'', $GLOBALS['POST_COMMENT']=>'', 
                                        $GLOBALS['POST_TAG']=>$tags, $GLOBALS['POST_WATCHED']=>'yes');
        $sess_data = array($GLOBALS['SESS_USER_ID']=>1, $GLOBALS['SESS_VIDEO_ID']=>4);
        $timestamp = '2017-03-27 20:13:36';
        $timezone = 'GMT -4';
        $res = parseFormAndInsertRating(self::$pdo,$post_data, $sess_data, $timestamp, $timezone);
        
        $this->assertEquals("Location: ".$GLOBALS['DOMAIN_URL'].$GLOBALS['PAGE_RATE_VIDEO'], $res['head_url']);
        $this->assertEquals(3, $res['rid']);
        
        $queryTable = $conn->createQueryTable('Rating', 'SELECT * FROM Rating');
        $expectedTable = $this->getDataSet('insertRatingOnlyScore')->getTable('Rating');
        $this->assertTablesEqual($expectedTable, $queryTable);
    }
    
    public function testRateDoneForTodayOnlyScore(){
        # T16
        $conn = $this->getConnection();            
        $tags = array();
        $post_data = array($GLOBALS['POST_SCORE']=>5, 'btn-rate'=>null, 'btn-done'=>1, 
                                        $GLOBALS['POST_FAMILIAR_ST']=>'', $GLOBALS['POST_COMMENT']=>'', 
                                        $GLOBALS['POST_TAG']=>$tags, $GLOBALS['POST_WATCHED']=>'yes');
        $sess_data = array($GLOBALS['SESS_USER_ID']=>1, $GLOBALS['SESS_VIDEO_ID']=>4);
        $timestamp = '2017-03-27 20:13:36';
        $timezone = 'GMT -4';
        
        $res = parseFormAndInsertRating(self::$pdo,$post_data, $sess_data, $timestamp, $timezone);
        
        $this->assertEquals("Location: ".$GLOBALS['DOMAIN_URL'].$GLOBALS['PAGE_SHOW_MAP'], $res['head_url']);
        $this->assertEquals(3, $res['rid']);
        
        $queryTable = $conn->createQueryTable('Rating', 'SELECT * FROM Rating');
        $expectedTable = $this->getDataSet('insertRatingOnlyScore')->getTable('Rating');
        $this->assertTablesEqual($expectedTable, $queryTable);
    }
    
    public function testRateDoneForTodayNoScore(){
        # T17
        $conn = $this->getConnection();            
        $tags = array('tag1','tag2');
        $post_data = array($GLOBALS['POST_SCORE']=>null, 'btn-rate'=>null, 'btn-done'=>1, 
                                        $GLOBALS['POST_FAMILIAR_ST']=>1, $GLOBALS['POST_COMMENT']=>'test done for today', 
                                        $GLOBALS['POST_TAG']=>$tags, $GLOBALS['POST_WATCHED']=>'yes');
        $sess_data = array($GLOBALS['SESS_USER_ID']=>1, $GLOBALS['SESS_VIDEO_ID']=>4);
        $timestamp = '2017-03-27 20:13:36';
        $timezone = 'GMT -4';
        
        $res = parseFormAndInsertRating(self::$pdo,$post_data, $sess_data, $timestamp, $timezone);
        
        $this->assertEquals("Location: ".$GLOBALS['DOMAIN_URL'].$GLOBALS['PAGE_SHOW_MAP'], $res['head_url']);
        $this->assertNull($res['rid']);
        
        $queryTable = $conn->createQueryTable('Rating', 'SELECT * FROM Rating');
        $expectedTable = $this->getDataSet()->getTable('Rating');
        $this->assertTablesEqual($expectedTable, $queryTable);
    }
    
    public function testRateWithMoreInformation(){
        # T18
        $conn = $this->getConnection();
        $tags = array('tag1','tag2');
        $post_data = array($GLOBALS['POST_SCORE']=>5, 'btn-rate'=>1, 'btn-done'=>null, 
                                        $GLOBALS['POST_FAMILIAR_ST']=>0, $GLOBALS['POST_COMMENT']=>'saving comment', 
                                        $GLOBALS['POST_TAG']=>$tags, $GLOBALS['POST_WATCHED']=>'yes');
        $sess_data = array($GLOBALS['SESS_USER_ID']=>1, $GLOBALS['SESS_VIDEO_ID']=>4);
        $timestamp = '2017-03-27 20:13:36';
        $timezone = 'GMT -4';
        
        $res = parseFormAndInsertRating(self::$pdo,$post_data, $sess_data, $timestamp, $timezone);
        
        $this->assertEquals("Location: ".$GLOBALS['DOMAIN_URL'].$GLOBALS['PAGE_RATE_VIDEO'], $res['head_url']);
        $this->assertEquals(3, $res['rid']);
        
        $queryTable = $conn->createQueryTable('Rating', 'SELECT * FROM Rating');
        $expectedTable = $this->getDataSet('insertRatingWithMoreInformation')->getTable('Rating');
        $this->assertTablesEqual($expectedTable, $queryTable);
    }
    
    public function testRateSumPerSeg(){
    # T19
        $conn = $this->getConnection();
        $timestamp = '2017-03-27 20:13:36';
        $timezone = 'GMT -4';
        $data = array(
            [array($GLOBALS['POST_SCORE']=>5, 'btn-rate'=>1, $GLOBALS['POST_WATCHED']=>'yes'), array($GLOBALS['SESS_USER_ID']=>1, $GLOBALS['SESS_VIDEO_ID']=>4)],
            [array($GLOBALS['POST_SCORE']=>4, 'btn-rate'=>1, $GLOBALS['POST_WATCHED']=>'yes'), array($GLOBALS['SESS_USER_ID']=>1, $GLOBALS['SESS_VIDEO_ID']=>5)],
            [array($GLOBALS['POST_SCORE']=>3, 'btn-rate'=>1, $GLOBALS['POST_WATCHED']=>'yes'), array($GLOBALS['SESS_USER_ID']=>1, $GLOBALS['SESS_VIDEO_ID']=>3)],
            [array($GLOBALS['POST_SCORE']=>1, 'btn-rate'=>1, $GLOBALS['POST_WATCHED']=>'yes'), array($GLOBALS['SESS_USER_ID']=>2, $GLOBALS['SESS_VIDEO_ID']=>4)],
            [array($GLOBALS['POST_SCORE']=>2, 'btn-rate'=>1, $GLOBALS['POST_WATCHED']=>'yes'), array($GLOBALS['SESS_USER_ID']=>2, $GLOBALS['SESS_VIDEO_ID']=>3)],
            [array($GLOBALS['POST_SCORE']=>3, 'btn-rate'=>1, $GLOBALS['POST_WATCHED']=>'yes'), array($GLOBALS['SESS_USER_ID']=>2, $GLOBALS['SESS_VIDEO_ID']=>2)],
            [array($GLOBALS['POST_SCORE']=>5, 'btn-rate'=>1, $GLOBALS['POST_WATCHED']=>'yes'), array($GLOBALS['SESS_USER_ID']=>2, $GLOBALS['SESS_VIDEO_ID']=>6)],
            );
        foreach($data as $rate){
            $res = parseFormAndInsertRating(self::$pdo,$rate[0], $rate[1], $timestamp, $timezone);
        }
    
        $queryTable = $conn->createQueryTable('RoadSegment', 'SELECT * FROM RoadSegment');
        $expectedTable = $this->getDataSet('RoadSegmentAfterSomeRating')->getTable('RoadSegment');
        $this->assertTablesEqual($expectedTable, $queryTable);
    }
    
    public function testSubmitWithoutWatched(){
        $conn = $this->getConnection();
        $timestamp = '2017-03-27 20:13:36';
        $timezone = 'GMT -4';
        $data = array(
            [array($GLOBALS['POST_SCORE']=>5, 'btn-rate'=>1, $GLOBALS['POST_WATCHED']=>''), array($GLOBALS['SESS_USER_ID']=>1, $GLOBALS['SESS_VIDEO_ID']=>4)],
            [array($GLOBALS['POST_SCORE']=>4, 'btn-rate'=>1, $GLOBALS['POST_WATCHED']=>''), array($GLOBALS['SESS_USER_ID']=>1, $GLOBALS['SESS_VIDEO_ID']=>5)],
            [array($GLOBALS['POST_SCORE']=>3, 'btn-rate'=>1, $GLOBALS['POST_WATCHED']=>''), array($GLOBALS['SESS_USER_ID']=>1, $GLOBALS['SESS_VIDEO_ID']=>3)],
            [array($GLOBALS['POST_SCORE']=>1, 'btn-rate'=>1, $GLOBALS['POST_WATCHED']=>''), array($GLOBALS['SESS_USER_ID']=>2, $GLOBALS['SESS_VIDEO_ID']=>4)],
            [array($GLOBALS['POST_SCORE']=>2, 'btn-rate'=>1, $GLOBALS['POST_WATCHED']=>''), array($GLOBALS['SESS_USER_ID']=>2, $GLOBALS['SESS_VIDEO_ID']=>3)],
            [array($GLOBALS['POST_SCORE']=>3, 'btn-rate'=>1, $GLOBALS['POST_WATCHED']=>''), array($GLOBALS['SESS_USER_ID']=>2, $GLOBALS['SESS_VIDEO_ID']=>2)],
            [array($GLOBALS['POST_SCORE']=>5, 'btn-rate'=>1, $GLOBALS['POST_WATCHED']=>''), array($GLOBALS['SESS_USER_ID']=>2, $GLOBALS['SESS_VIDEO_ID']=>6)],
            );
        foreach($data as $rate){
            $res = parseFormAndInsertRating(self::$pdo,$rate[0], $rate[1], $timestamp, $timezone);
        }
        $origin_db = $this->getDataSet();
        $queryTable = $conn->createQueryTable('RoadSegment', 'SELECT * FROM RoadSegment');
        $expectedTable = $origin_db->getTable('RoadSegment');
        $this->assertTablesEqual($expectedTable, $queryTable);
    
        $queryTable = $conn->createQueryTable('Rating', 'SELECT * FROM Rating');
        $expectedTable = $origin_db->getTable('Rating');
        $this->assertTablesEqual($expectedTable, $queryTable);
    
    
        
    }
}


?>