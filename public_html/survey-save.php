<?php
   session_start();    //Start session
    include_once('config.inc.php');  //$db_name, $host, $db_user, $db_pwd, $PAGE_RATE_VIDEO, $DOMAIN_URL
    

    # Connect to MySQL database
    $con=mysqli_connect($host, $db_user, $db_pwd, $db_name);
    if(mysqli_connect_errno()) { die("failed to connect to mysql:".mysqli_connect_error()); }

    // get session variables
    $user_id = $_SESSION[$SESS_USER_ID];
    
    $cols_update = array();
    # get post form variables
    foreach($SURVEY_COLS as $col){
        if(empty($_POST[$col])){
            continue;
        }
        array_push($cols_update, "$col=$_POST[$col]");
    }
    

    # user answer any questions
    if(!empty($cols_update)){
        $col = $TABL_USERS_FIELD_SURVEY;
        array_push($cols_update, "$col=1");
        $sql = "UPDATE $TABLE_USERS SET ".implode(" ,", $cols_update)." WHERE $TABL_USERS_FIELD_UID=$user_id";
        $result=mysqli_query($con, $sql);
    }    # user doesn't answer any question, redirect without updating user table
    
    $head_url = "Location: ".$DOMAIN_URL.$PAGE_RATE_VIDEO;
    header($head_url); 
    return true;


?>
