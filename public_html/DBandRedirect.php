<?php

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
?>