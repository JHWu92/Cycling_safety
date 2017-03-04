<?php
    session_start();
    include_once('check-login.php');  
    echo login($_SESSION) ? 'True' : 'False';
?>