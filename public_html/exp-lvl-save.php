<?php
    session_start();    //Start session
    include_once('config.inc.php');  //$db_name, $host, $db_user, $db_pwd, $TABLE_USERS, $DOMAIN_URL, $PAGE_RATE_VIDEO, $PAGE_SURVEY

    //parse data from form 
    $explv=$_POST[$SESS_EXPLV];
    // set session variables
    $_SESSION[$SESS_EXPLV] = $explv;
    // get session variables
    $user_id = $_SESSION[$SESS_USER_ID];
    $has_survey = $_SESSION[$SESS_SURVEY];
    
    // check whether the email exist against DB
    # Connect to MySQL database
    $con=mysqli_connect($host, $db_user, $db_pwd, $db_name);
    # if connection succeed
    if(mysqli_connect_errno()){ die("failed to connect to mysql:" . mysqli_connect_error()); }

    $sql = "UPDATE $TABLE_USERS SET $TABL_USERS_FIELD_EXP = '$explv' WHERE $TABL_USERS_FIELD_UID='$user_id'";
    mysqli_query($con, $sql);
    
    if (empty($has_survey)){
        $head_url = "Location: ".$DOMAIN_URL.$PAGE_SURVEY;
    }else{
        $head_url = "Location: ".$DOMAIN_URL.$PAGE_RATE_VIDEO;
    }
    //echo $head_url;    
    # redirect
    header($head_url); 
    return true;

?>