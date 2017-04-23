<?php
    require_once 'config.inc.php';
    function logLogin($pdo, $user_id, $timestamp, $timezone, $userAgent, $isMobile, $isTablet, $isAndroid, $isIOS){
        global $TABLE_LOGINLOG, $TABL_USERS_FIELD_UID, $TB_COL_TIMESTAMP, $TB_COL_TIMEZONE, $TB_COL_USERAGENT, $TB_COL_ISMOBILE, $TB_COL_ISTABLET, $TB_COL_ISANDROID, $TB_COL_ISIOS;
        
        $sql = <<<EOT
            INSERT INTO $TABLE_LOGINLOG 
                (`$TABL_USERS_FIELD_UID`, `$TB_COL_TIMESTAMP`, `$TB_COL_TIMEZONE`, `$TB_COL_USERAGENT`, `$TB_COL_ISMOBILE`, `$TB_COL_ISTABLET`, `$TB_COL_ISANDROID`, `$TB_COL_ISIOS`) 
            VALUES 
                (:user_id, :timestamp, :timezone, :userAgent, :isMobile, :isTablet, :isAndroid, :isIOS)
EOT;
        
        $sth = $pdo->prepare($sql);
        $sth->execute(array(':user_id' => $user_id, ':timestamp' => "$timestamp", ':timezone' => "$timezone", ':userAgent' => "$userAgent", ':isMobile' => "$isMobile", ':isTablet' => "$isTablet", ':isAndroid' => "$isAndroid", ':isIOS' => "$isIOS", ));
        $lid = $pdo->lastInsertId(); 
        if(!$lid){  # if error happens when inserting
                die("<h3>error happens in logging your login, click <a href='/index.html'>HERE</a> to enter your email again</h3>");
        }        
        return $lid;
    }


    function handle_input_email($pdo, $email){
        # check if user exists
        global $TABL_USERS_FIELD_UID, $TABL_USERS_FIELD_EXP, $TABL_USERS_FIELD_SURVEY, $TABLE_USERS;
        global $SESS_USER_ID, $SESS_EXPLV, $SESS_SURVEY;
        
        $sql="SELECT $TABL_USERS_FIELD_UID, $TABL_USERS_FIELD_EXP, $TABL_USERS_FIELD_SURVEY FROM  $TABLE_USERS WHERE email= ?";
        $select = $pdo->prepare($sql);
        $select->execute(array("$email"));
        $count=$select->rowCount();

        if($count == 0){  # this is a new user
            $sql_insert = "INSERT INTO $TABLE_USERS (Email) VALUES (?)";
            $insert = $pdo->prepare($sql_insert);
            $insert->execute(array("$email"));
            # get the auto-id
            $user_id = $pdo->lastInsertId(); 
            if(!$user_id){  # if error happens when inserting
                die("<h3>error happens in creating your account, click <a href='/index.html'>HERE</a> to enter your email again</h3>");
            }
        }else{  # user exists
            $result = $select->fetch(PDO::FETCH_ASSOC);
            $user_id = $result[$TABL_USERS_FIELD_UID];
            $exp_lvl = $result[$TABL_USERS_FIELD_EXP];
            $has_survey = $result[$TABL_USERS_FIELD_SURVEY];
        }
        
        
        if(empty($exp_lvl)){
            $head_url = "Location: ".$GLOBALS['DOMAIN_URL'].$GLOBALS['PAGE_EXP'];
        } else if (empty($has_survey)){
            $head_url = "Location: ".$GLOBALS['DOMAIN_URL'].$GLOBALS['PAGE_SURVEY'];
        }else{
            $head_url = "Location: ".$GLOBALS['DOMAIN_URL'].$GLOBALS['PAGE_RATE_VIDEO'];
        }
        return array($SESS_USER_ID=>$user_id, 'head_url'=>$head_url, $SESS_EXPLV=>$exp_lvl, $SESS_SURVEY=>$has_survey);
        
    }
    
    function handle_exp_lvl($pdo, $user_id, $has_survey, $explv){
        global $TABLE_USERS, $TABL_USERS_FIELD_EXP, $TABL_USERS_FIELD_UID, $TABL_USERS_FIELD_SURVEY, $DOMAIN_URL, $PAGE_SURVEY, $PAGE_RATE_VIDEO, $SURVEY_COLS;

        $sql = "UPDATE $TABLE_USERS SET $TABL_USERS_FIELD_EXP = ? WHERE $TABL_USERS_FIELD_UID=?";
        $sth = $pdo->prepare($sql);
        $sth->execute(array("$explv",$user_id));
        
        if (empty($has_survey)){
            $head_url = "Location: ".$DOMAIN_URL.$PAGE_SURVEY;
        }else{
            $head_url = "Location: ".$DOMAIN_URL.$PAGE_RATE_VIDEO;
        }
        return array('head_url'=>$head_url);
    }
    
    function handle_survey($pdo, $user_id, $post_data){
        global $TABLE_USERS, $TABL_USERS_FIELD_EXP, $TABL_USERS_FIELD_UID, $TABL_USERS_FIELD_SURVEY, $DOMAIN_URL, $PAGE_SURVEY, $PAGE_RATE_VIDEO, $SURVEY_COLS;

        $cols_update_sql = array();
        $cols_update_data = array();
        # get post form variables
        foreach($SURVEY_COLS as $col){
            if(empty($post_data[$col])){
                continue;
            }
            array_push($cols_update_sql, "$col=?");
            array_push($cols_update_data, "$post_data[$col]");
        }

        # user answer any questions
        if(!empty($cols_update_sql)){
            array_push($cols_update_sql, "$TABL_USERS_FIELD_SURVEY=?");
            array_push($cols_update_data, 1);
            
            $sql = "UPDATE $TABLE_USERS SET ".implode(" ,", $cols_update_sql)." WHERE $TABL_USERS_FIELD_UID=?";
            array_push($cols_update_data, $user_id);

            $sth = $pdo->prepare($sql);
            $sth->execute($cols_update_data);
        }    # user doesn't answer any question, redirect without updating user table
        
        $head_url = "Location: ".$DOMAIN_URL.$PAGE_RATE_VIDEO;
        
        return array('head_url'=>$head_url);
    }
?>