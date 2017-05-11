<?php
require 'DBFixture.php';
require dirname(__FILE__).'/../emailExpSurveyDBandRedirect.php';
include_once(dirname(__FILE__).'/../config.inc.php');
require dirname(__FILE__).'/../rateDB.php';
include_once(dirname(__FILE__).'/../mobiledetect/Mobile_Detect.php');

class largeVolTest extends DBFixtureTestCase{
    function testLargeVol(){

        $conn = $this->getConnection();
        $pdo = self::$pdo;
        $start_date = new DateTime( "now", new DateTimeZone("America/New_York") );

        $total_seg = 100;
        $total_video = 98;
        $total_user = 10000;
        $select_user_cnt = $total_user/100;
        
        # insert 100 segments starts from sid 10;
        for($s=0; $s<$total_seg; $s++){
            $sid = $s+10;
            $sql = "INSERT INTO `RoadSegment` (`sid`) VALUES ($sid)";
            $pdo->exec($sql);
            
    #        echo "insert sid = $sid<br>";
        }
        # insert 98 videos and corresponding seg
        for($v=0; $v<$total_video; $v++){
            $vid = $v + 10;
            $sql = "INSERT INTO `Video`(`vid`, `clip_name`, `title`, `URL`) VALUES ($vid, 'clip_$vid', 'title_$vid', 'url_$vid')";
            $pdo->exec($sql);            
            for($vs=0; $vs<3; $vs++){
                $sid_to_be = $vid+$vs;
                $sql = "INSERT INTO `VideoRoadSeg`( `vid`, `sid`, `ratio`) VALUES ($vid, $sid_to_be, 0.5)";
                $pdo->exec($sql);   
            }
        }
        # insert user and login and rating
        for($i=0; $i<$total_user; $i++){
            # user signup
            $uid = $i+4;
            $email = "user$uid@g.com";
            $res = handle_input_email($pdo, $email);
            
            # user login and rate
            $to_rate_vid = 10;
            $login_times_and_score = intdiv($i,2000)+1;
            for($j=1; $j<=$login_times_and_score; $j++){
                # user login
                $date = new DateTime( "now", new DateTimeZone("UTC") );
                $timestamp = $date->format('Y-m-d H:i:s');    
                $useragent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36';
                $detect = new Mobile_Detect;    
                logLogin($pdo, $uid, $timestamp, 'UTC -4', $useragent, 
                    $detect->isMobile(), $detect->isTablet(), $detect->isAndroidOS(),$detect->isIOS());
                # user rate 17 videos, vid increased from 10.
                for($k=0; $k<17; $k++){
                    # rate
                    # increase vid
                    $tags = array();
                    $post_data = array($GLOBALS['POST_SCORE']=>$login_times_and_score, 'btn-rate'=>1, 'btn-done'=>null, 
                                                    $GLOBALS['POST_FAMILIAR_ST']=>'', $GLOBALS['POST_COMMENT']=>'', 
                                                    $GLOBALS['POST_TAG']=>$tags, $GLOBALS['POST_WATCHED']=>'yes');
                    $sess_data = array($GLOBALS['SESS_USER_ID']=>$uid, $GLOBALS['SESS_VIDEO_ID']=>$to_rate_vid);
                    $date = new DateTime( "now", new DateTimeZone("UTC") );
                    $timestamp = $date->format('Y-m-d H:i:s');    
                    $res=parseFormAndInsertRating($pdo,$post_data, $sess_data, $timestamp, 'UTC -4');
                    $to_rate_vid ++;
                }
                
            }
            
        }    
        
        $after_insert_date = new DateTime( "now", new DateTimeZone("America/New_York") );
        echo "insert-start : ".$after_insert_date->diff($start_date)->format('%Y-%m-%d %H:%i:%s')."\n";
        # select 1% users by email
        for($i=0; $i<$select_user_cnt; $i++){
            $uid = $i*100+4;
            $email = "user$uid@g.com";
            $res = handle_input_email($pdo, $email);
            $this->assertEquals($uid, $res['user_id']);
        }
        
        $select_date = new DateTime( "now", new DateTimeZone("America/New_York") );
        echo "select - insert: ".$select_date->diff($after_insert_date)->format('%Y-%m-%d %H:%i:%s')."\n";
        
        # check segment score
        $data = [
            [0, 15000, 5000, 10000],
            [1, 30000, 10000, 20000],
            [40, 36000, 9000, 18000],
            [51, 33000, 8000, 16000],
            [86, 5000, 1000, 2000],
        ];


        foreach($data as $d){
            $sid = $d[0]+10;
            $sql="SELECT sumScore, sumRatio, sumCnt FROM RoadSegment  WHERE sid=$sid";
            $select = $pdo->prepare($sql);
            $select->execute();
            $result = $select->fetch(PDO::FETCH_ASSOC);
            $this->assertEquals($d[1], $result['sumScore']);
            $this->assertEquals($d[2], $result['sumRatio']);
            $this->assertEquals($d[3], $result['sumCnt']);
            
        }
        
        $end_date = new DateTime( "now", new DateTimeZone("America/New_York") );
        echo "check score - select: ".$end_date->diff($select_date)->format('%Y-%m-%d %H:%i:%s')."\n";
        
    }
}

    
?>