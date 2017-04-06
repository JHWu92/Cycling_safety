<?php
    function logLogin($pdo, $user_id, $timestamp, $timezone){
        include('config.inc.php'); 
        $sql = "INSERT INTO $TABLE_LOGINLOG (`$TABL_USERS_FIELD_UID`, `$TB_COL_TIMESTAMP`, `$TB_COL_TIMEZONE`) VALUES ($user_id, '$timestamp', '$timezone')";
        $result_insert = $pdo->exec($sql);
        if(!$result_insert){  # if error happens when inserting
                die("<h3>error happens in logging your login, click <a href='/index.html'>HERE</a> to enter your email again</h3>");
        }
        
    }
    
    function handle_input_email($pdo, $email){
        include('config.inc.php'); 
        # check if user exists

        $sql="SELECT $TABL_USERS_FIELD_UID, $TABL_USERS_FIELD_EXP, $TABL_USERS_FIELD_SURVEY FROM  $TABLE_USERS WHERE email= '$email'";
        $select = $pdo->prepare($sql);
        $select->execute();
        $count=$select->rowCount();

        if($count == 0){  # this is a new user
            $sql_insert = "INSERT INTO $TABLE_USERS (Email) VALUES ('$email')";
            $result_insert = $pdo->exec($sql_insert);
            if(!$result_insert){  # if error happens when inserting
                die("<h3>error happens in creating your account, click <a href='/index.html'>HERE</a> to enter your email again</h3>");
            }
            # get the auto-id
            $user_id = $pdo->lastInsertId(); 
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
        include('config.inc.php'); 
        
        $sql = "UPDATE $TABLE_USERS SET $TABL_USERS_FIELD_EXP = '$explv' WHERE $TABL_USERS_FIELD_UID='$user_id'";
        $pdo->exec($sql);
        
        if (empty($has_survey)){
            $head_url = "Location: ".$DOMAIN_URL.$PAGE_SURVEY;
        }else{
            $head_url = "Location: ".$DOMAIN_URL.$PAGE_RATE_VIDEO;
        }
        return array('head_url'=>$head_url);
    }
    
    function handle_survey($pdo, $user_id, $post_data){
        include('config.inc.php');
        $cols_update = array();
        # get post form variables
        foreach($SURVEY_COLS as $col){
            if(empty($post_data[$col])){
                continue;
            }
            array_push($cols_update, "$col=$post_data[$col]");
        }
        

        # user answer any questions
        if(!empty($cols_update)){
            $col = $TABL_USERS_FIELD_SURVEY;
            array_push($cols_update, "$col=1");
            
            $sql = "UPDATE $TABLE_USERS SET ".implode(" ,", $cols_update)." WHERE $TABL_USERS_FIELD_UID=$user_id";
            $pdo->exec($sql);
        }    # user doesn't answer any question, redirect without updating user table
        
        $head_url = "Location: ".$DOMAIN_URL.$PAGE_RATE_VIDEO;
        
        return array('head_url'=>$head_url);
    }
?>