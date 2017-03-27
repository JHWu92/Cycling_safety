<?php
    session_start();	//resume the session

    include_once('config.inc.php');  //$db_name, $host, $db_user, $db_pwd, $PAGE_RATE_VIDEO, $DOMAIN_URL
    require 'rateDB.php';
    
    # Connect to MySQL database
    try{
        $pdo = new PDO($GLOBALS['DB_DSN'], $GLOBALS['DB_USER'], $GLOBALS['DB_PASSWD']);
    }catch (PDOException $e) {
        echo 'Connection failed: ' . $e->getMessage();
    }
   
    $res=parseFormAndInsertRating($pdo,$_POST, $_SESSION);
    $pdo = null;
    

    # redirect
    header($res['head_url']); 
    return true;
    
?>