<?php
    require_once 'config.inc.php';  
    function login($SESS){
        return isset($SESS[$GLOBALS['SESS_USER_ID']]) && isset($SESS[$GLOBALS['SESS_EMAIL']]) && $SESS[$GLOBALS['SESS_LOGIN']];
    } 
    
    function redirect_if_not_login($SESS){
        if(!login($SESS)){
            global $DOMAIN_URL, $PAGE_LOGIN_FIRST;
            error_log("not logged in, Session array: ".implode(",", $SESS));
            exit(header( "Location: $DOMAIN_URL$PAGE_LOGIN_FIRST"));
        }
        
    }
    
?>