<?php

    session_start();    //Start session
    require_once 'config.inc.php';  //$db_name, $host, $db_user, $db_pwd, $TABLE_USERS, $DOMAIN_URL, $PAGE_RATE_VIDEO, $PAGE_SURVEY
    require_once 'emailExpSurveyDBandRedirect.php';
    require_once './mobiledetect/Mobile_Detect.php';

    //parse data from form 
    $email=$_POST[$SESS_EMAIL];
    $timezone = $_POST[$TB_COL_TIMEZONE];
    
    // check whether the email exist against DB
    # Connect to MySQL database
    try{
        $pdo = new PDO($GLOBALS['DB_DSN'], $GLOBALS['DB_USER'], $GLOBALS['DB_PASSWD']);
        $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    }catch (PDOException $e) {
        echo 'Connection failed: ' . $e->getMessage();
    }
    //$con=mysqli_connect($host, $db_user, $db_pwd, $db_name);
    # if connection succeed
    //if(mysqli_connect_errno()){ die("failed to connect to mysql:" . mysqli_connect_error()); }

    $res = handle_input_email($pdo, $email);

    $date = new DateTime( "now", new DateTimeZone("UTC") );
    $timestamp = $date->format('Y-m-d H:i:s');    
    $useragent=$_SERVER['HTTP_USER_AGENT'];
    $detect = new Mobile_Detect;    
    $lid = logLogin($pdo, $res[$SESS_USER_ID], $timestamp, $timezone, $useragent, 
        $detect->isMobile(), $detect->isTablet(), $detect->isAndroidOS(),$detect->isIOS());
    
    # clear pdo connection
    $pdo = null;
    
    // Store log in Info in session
    $_SESSION[$SESS_EMAIL] = $email;  
    $_SESSION[$SESS_USER_ID] = $res[$SESS_USER_ID];
    $_SESSION[$SESS_LOGIN_ID] = $lid;
    $_SESSION[$SESS_LOGIN] = True;  // logged in
    $_SESSION[$SESS_EXPLV] = $res[$SESS_EXPLV];  
    $_SESSION[$SESS_SURVEY] = $res[$SESS_SURVEY];  
    $_SESSION[$TB_COL_TIMEZONE]= $timezone ;
    
    
    //echo $head_url;    
    # redirect
    header($res['head_url']); 
    return true;

?>