<?php
    session_start();	//resume the session

    # Connect to MySQL database
    include_once('config.inc.php');  //$db_name, $host, $db_user, $db_pwd, $PAGE_RATE_VIDEO, $DOMAIN_URL
    $con=mysqli_connect($host, $db_user, $db_pwd, $db_name);

    if(mysqli_connect_errno()){ die("failed to connect to mysql:" . mysqli_connect_error()); }
    
    include_once('db_helper.php');
    
    // parse which button(rate/Done)
    // parse form data
    // if btn==Done 
    //      if safelvl is not None: insert to db
    //      redirect to show_map.php
    // else
    //      if safelvl is not None: 
    //          insert to db
    //          show next video
    
    $familiar_st = $_POST[$POST_FAMILIAR_ST];
    $score = $_POST[$POST_SCORE];
    $comment = $_POST[$POST_COMMENT];
    $uid = $_SESSION[$SESS_USER_ID];
    $vid = $_SESSION[$SESS_VIDEO_ID];
    $tags = implode(',', $_POST['tag']);
    
    $rid = insert_rate($con, $uid, $vid, $score, $comment, $tags);
    mysqli_close($con);
    
        // which button is clicked
    if (isset($_POST['btn-rate'])) {
        $head_url = "Location: ".$DOMAIN_URL.$PAGE_RATE_VIDEO;
    } else if (isset($_POST['btn-done'])) {
        $head_url = "Location: ".$DOMAIN_URL.$PAGE_SHOW_MAP;
    } else {
    }   
    # redirect
    header($head_url); 
    return true;
    
?>