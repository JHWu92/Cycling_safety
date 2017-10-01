<?php
    session_start();    //Start session
    require_once 'config.inc.php';  //$db_name, $host, $db_user, $db_pwd, $TABLE_USERS, $DOMAIN_URL, $PAGE_RATE_VIDEO, $PAGE_SURVEY
    require_once 'emailExpSurveyDBandRedirect.php';

    
    if(!isset($_SESSION[$SESS_USER_ID])){
        error_log('exp-lvl-save.php, no user id , Session array: '.json_encode($_SESSION).', _POST: '.json_encode($_POST));
    }
    
    //parse data from form 
    $explv=$_POST[$SESS_EXPLV];
    // set session variables
    $_SESSION[$SESS_EXPLV] = $explv;
    // get session variables
    $user_id = $_SESSION[$SESS_USER_ID];
    $has_survey = $_SESSION[$SESS_SURVEY];
    error_log('exp-lvl-save.php, user_id: '.$user_id.', has_survey: '.$has_survey.', explv: '.$explv);
        
    # Connect to MySQL database
    try{
        $pdo = new PDO($GLOBALS['DB_DSN'], $GLOBALS['DB_USER'], $GLOBALS['DB_PASSWD'], array(PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION));
    }catch (PDOException $e) {
        error_log('PDO Exception: '.$e);
        die('Connection failed: ' . $e->getMessage());
    }
    
    $res = handle_exp_lvl($pdo, $user_id, $has_survey, $explv);
    
    # clear pdo connection
    $pdo = null;
    
    //echo $head_url;    
    # redirect
    header($res['head_url']); 
    exit();

?>