<?php
   
    function parseFormAndInsertRating($pdo, $post_data, $sess_data, $timestamp){
        include('config.inc.php');
        $familiar_st = $post_data[$POST_FAMILIAR_ST];
        $score = $post_data[$POST_SCORE];
        $comment = $post_data[$POST_COMMENT];
        $uid = $sess_data[$SESS_USER_ID];
        $vid = $sess_data[$SESS_VIDEO_ID];
        $tags = $post_data[$POST_TAG];
        if(is_array($tags)){
            $tags = implode(',', $tags);
        }

        if(!empty($score)){
            $sql = "INSERT $TABLE_RATING (uid, vid, score, comment, tags, familiar, timestamp) VALUES ($uid, $vid, $score, '$comment', '$tags', '$familiar_st', '$timestamp')";
            $pdo->exec($sql);
            $rid = $pdo->lastInsertId(); 
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