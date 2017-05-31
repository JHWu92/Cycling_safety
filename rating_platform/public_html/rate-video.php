<?php
    session_start();	//resume the session

    require_once 'config.inc.php';  //$db_name, $host, $db_user, $db_pwd, $PAGE_RATE_VIDEO, $DOMAIN_URL
    require_once 'rateDB.php';
    
    # Connect to MySQL database
    try{
        $pdo = new PDO($GLOBALS['DB_DSN'], $GLOBALS['DB_USER'], $GLOBALS['DB_PASSWD'], array(PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION));
    }catch (PDOException $e) {
        error_log('rate-video, PDO Exception: '.$e);
        die('Connection failed: ' . $e->getMessage());
    }
   
    $date = new DateTime( "now", new DateTimeZone("UTC") );
    $timestamp = $date->format('Y-m-d H:i:s');    
    $timezone = $_SESSION[$TB_COL_TIMEZONE];
    $res=parseFormAndInsertRating($pdo,$_POST, $_SESSION, $timestamp, $timezone);
    
    # clear pdo connection
    $pdo = null;
    
    # redirect
    header($res['head_url']); 
    return true;
    
?>