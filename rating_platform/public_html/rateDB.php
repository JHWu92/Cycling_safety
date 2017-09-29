<?php
    if (!isset($_SESSION))
    {
        session_start();
    }
    require_once 'config.inc.php';
    function parseFormAndInsertRating($pdo, $post_data, $sess_data, $timestamp, $timezone){
        global $TABLE_RATING, $TB_COL_TIMESTAMP, $TB_COL_TIMEZONE, $TB_COL_WATCHED, $TB_COL_INTERACTION, $TB_COL_LID, $DOMAIN_URL, $PAGE_RATE_VIDEO, $PAGE_SHOW_MAP;
        global $POST_FAMILIAR_ST, $POST_SCORE, $POST_COMMENT, $SESS_USER_ID, $SESS_VIDEO_ID, $SESS_LOGIN_ID, $POST_INTERACTION, $POST_TAG, $POST_WATCHED;

        $familiar_st = (isset($post_data[$POST_FAMILIAR_ST]) ? $post_data[$POST_FAMILIAR_ST] : null);
        $score = (isset($post_data[$POST_SCORE]) ? $post_data[$POST_SCORE] : null);
        $tags = (isset($post_data[$POST_TAG]) ? $post_data[$POST_TAG] : null);
        $comment = (isset($post_data[$POST_COMMENT]) ? $post_data[$POST_COMMENT] : null);
        $interaction = (isset($post_data[$POST_INTERACTION]) ? $post_data[$POST_INTERACTION] : null);
        $watched = (isset($post_data[$POST_WATCHED]) ? $post_data[$POST_WATCHED] : null);
        $uid = $sess_data[$SESS_USER_ID];
        $vid = $sess_data[$SESS_VIDEO_ID];
        $lid = $sess_data[$SESS_LOGIN_ID];
        
        if(is_array($tags)){
            $tags = implode(',', $tags);
        }
        
        if(empty($uid)){ 
            error_log('rateDB.php: The uid is missing');
            die('<h3>We are sorry that the connection is lost, click <a href="/index.html">HERE</a> to log in again</h3>. If the problem persists, contact us at <a href="mailto:umdcyclingsafety@gmail.com">umdcyclingsafety@gmail.com</a>');
            
        }
        if(empty($vid)){
            error_log('rateDB.php: the vid is missing');
            die('<h3>We failed to load the next video for you, click <a href="/index.html">HERE</a> to log in again</h3>. If the problem persists, contact us at <a href="mailto:umdcyclingsafety@gmail.com">umdcyclingsafety@gmail.com</a>');
        }
        
        $rid = null;
        if(!empty($score) && !empty($watched)){
            $sql = <<<EOT
            INSERT $TABLE_RATING 
                (uid, vid, score, comment, tags, familiar, $TB_COL_TIMESTAMP, $TB_COL_TIMEZONE, $TB_COL_WATCHED, $TB_COL_INTERACTION, $TB_COL_LID) 
            VALUES 
                (:uid, :vid, :score, :comment, :tags, :familiar_st, :timestamp, :timezone, :watched, :interaction, :lid)
EOT;
            $sth= $pdo->prepare($sql);
            $sth->execute(array(':uid' => $uid, ':vid' => $vid, ':score' => $score, ':comment' => "$comment", ':tags' => "$tags", ':familiar_st' => "$familiar_st", ':timestamp' => "$timestamp", ':timezone' => "$timezone", ':watched' => "$watched", ':interaction' => "$interaction", ':lid' => "$lid"));

            $rid = $pdo->lastInsertId(); 
            
            if(!$rid){  # if error happens when inserting
                    error_log("failed to insert rating for user_id =$uid, video = $vid");
            }
            $sth = null;
        }
        // which button is clicked
        if (isset($post_data['btn-rate'])) {
            $head_url = "Location: ".$DOMAIN_URL.$PAGE_RATE_VIDEO;
        } else if (isset($post_data['btn-done'])) {
            $head_url = "Location: ".$DOMAIN_URL.$PAGE_SHOW_MAP;
        } else {
        }   
        return array('rid'=>$rid, 'head_url'=>$head_url);
    }

?>