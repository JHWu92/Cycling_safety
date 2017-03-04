<?php
    session_start();
    include_once('config.inc.php');  

    function login($SESS){
        global $SESS_EMAIL, $SESS_USER_ID, $SESS_LOGIN;
        if (isset($SESS[$SESS_EMAIL]) && isset($SESS[$SESS_USER_ID]) && $SESS[$SESS_LOGIN]==True) {
            return True;
        } else {
            return False;
        }     
    } 
    
    function redirect_if_not_login($SESS){
        if(!login($SESS)){
            global $DOMAIN_URL, $PAGE_LOGIN_FIRST;
            exit(header( "Location: $DOMAIN_URL$PAGE_LOGIN_FIRST"));
        }
        
    }
    
?>