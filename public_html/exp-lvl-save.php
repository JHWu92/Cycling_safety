<?php
    session_start();    //Start session
    require_once 'config.inc.php';  //$db_name, $host, $db_user, $db_pwd, $TABLE_USERS, $DOMAIN_URL, $PAGE_RATE_VIDEO, $PAGE_SURVEY
    require_once 'emailExpSurveyDBandRedirect.php';

    //parse data from form 
    $explv=$_POST[$SESS_EXPLV];
    // set session variables
    $_SESSION[$SESS_EXPLV] = $explv;
    // get session variables
    $user_id = $_SESSION[$SESS_USER_ID];
    $has_survey = $_SESSION[$SESS_SURVEY];
    
    # Connect to MySQL database
    try{
        $pdo = new PDO($GLOBALS['DB_DSN'], $GLOBALS['DB_USER'], $GLOBALS['DB_PASSWD']);
    }catch (PDOException $e) {
        echo 'Connection failed: ' . $e->getMessage();
    }
    
    $res = handle_exp_lvl($pdo, $user_id, $has_survey, $explv);
    
    //echo $head_url;    
    # redirect
    header($res['head_url']); 
    return true;

?>