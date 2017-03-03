<?php
    session_start();    //Start session
    include_once('config.inc.php');  //$db_name, $host, $db_user, $db_pwd, $TABLE_USERS, $DOMAIN_URL, $PAGE_RATE_VIDEO, $PAGE_SURVEY

    //parse data from form 
    $email=$_POST[$SESS_EMAIL];
    
    // check whether the email exist against DB
    # Connect to MySQL database
    $con=mysqli_connect($host, $db_user, $db_pwd, $db_name);
    # if connection succeed
    if(mysqli_connect_errno()){ die("failed to connect to mysql:" . mysqli_connect_error()); }

    # check if user exists
    $sql="SELECT $TABL_USERS_FIELD_UID, $TABL_USERS_FIELD_EXP, $TABL_USERS_FIELD_SURVEY FROM " . $TABLE_USERS . " WHERE email= '$email'";
    $result=mysqli_query($con, $sql);
    $count=mysqli_num_rows($result);

    if($count == 0){  # this is a new user
        $sql_insert = "INSERT INTO $TABLE_USERS (Email) VALUES ('$email')";
        $result_insert = mysqli_query($con, $sql_insert);
        if(!$result_insert){  # if error happens when inserting
            die("<h3>error happens in creating your account, click <a href='/index2.html'>HERE</a> to enter your email again</h3>");
        }
        # get the auto-id
        $user_id = mysqli_insert_id($con);
    }else{  # user exists
        $row = mysqli_fetch_row($result);
        $user_id = $row[0];
        $exp_lvl = $row[1];
        $has_survey = $row[2];
    }
    
    // Store log in Info in session
    $_SESSION[$SESS_EMAIL] = $email;  
    $_SESSION[$SESS_USER_ID] = $user_id;
    $_SESSION[$SESS_LOGIN] = True;  // logged in
    $_SESSION[$SESS_EXPLV] = $exp_lvl;  // logged in
    $_SESSION[$SESS_SURVEY] = $has_survey;  // logged in
    
    
    if(empty($exp_lvl)){
        $head_url = "Location: ".$DOMAIN_URL.$PAGE_EXP;
    } else if (empty($has_survey)){
        $head_url = "Location: ".$DOMAIN_URL.$PAGE_SURVEY;
    }else{
        $head_url = "Location: ".$DOMAIN_URL.$PAGE_RATE_VIDEO;
    }
    //echo $head_url;    
    # redirect
    header($head_url); 
    return true;
?>