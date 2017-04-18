<?php
   
    function parseFormAndInsertRating($pdo, $post_data, $sess_data, $timestamp, $timezone){
        include('config.inc.php');
        $familiar_st = $post_data[$POST_FAMILIAR_ST];
        $score = $post_data[$POST_SCORE];
        $comment = $post_data[$POST_COMMENT];
        $uid = $sess_data[$SESS_USER_ID];
        $vid = $sess_data[$SESS_VIDEO_ID];
        $lid = $sess_data[$SESS_LOGIN_ID];
        $interaction = $post_data[$POST_INTERACTION];
        $tags = $post_data[$POST_TAG];
        $watched = $post_data[$POST_WATCHED];
        if(is_array($tags)){
            $tags = implode(',', $tags);
        }

        if(!empty($score) && !empty($watched)){
            $sql = <<<EOT
            INSERT $TABLE_RATING 
                (uid, vid, score, comment, tags, familiar, $TB_COL_TIMESTAMP, $TB_COL_TIMEZONE, $TB_COL_WATCHED, $TB_COL_INTERACTION, $TB_COL_LID) 
            VALUES 
                ($uid, $vid, $score, '$comment', '$tags', '$familiar_st', '$timestamp', '$timezone', '$watched', '$interaction', '$lid')
EOT;
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