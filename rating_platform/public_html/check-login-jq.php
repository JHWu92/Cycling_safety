<?php
    session_start();
    require_once 'check-login.php';
    echo login($_SESSION) ? 'True' : 'False';
?>