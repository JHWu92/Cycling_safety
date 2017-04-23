<?php
   session_start();    //Start session
    require_once 'config.inc.php';  //$db_name, $host, $db_user, $db_pwd, $PAGE_RATE_VIDEO, $DOMAIN_URL
    require_once 'check-login.php';
    require 'emailExpSurveyDBandRedirect.php';
    
    redirect_if_not_login($_SESSION);

    // get session variables
    $user_id = $_SESSION[$SESS_USER_ID];
    
    # Connect to MySQL database
    try{
        $pdo = new PDO($GLOBALS['DB_DSN'], $GLOBALS['DB_USER'], $GLOBALS['DB_PASSWD']);
    }catch (PDOException $e) {
        echo 'Connection failed: ' . $e->getMessage();
    }
    
    
    $res = handle_survey($pdo, $user_id, $_POST);
    header($res['head_url']); 
    return true;


?>
