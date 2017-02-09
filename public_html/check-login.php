<?php
    session_start();
    include_once('config.inc.php');  
    if (isset($_SESSION[$SESS_EMAIL]) && isset($_SESSION[$SESS_USER_ID]) && $_SESSION[$SESS_LOGIN]==True) {
        echo 'True';
    } else {
        echo 'False';
    }     
    
?>