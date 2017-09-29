<?php
    session_start();    //Start session
    include_once('config.inc.php');  //$db_name, $host, $db_user, $db_pwd, $TABLE_USERS, $DOMAIN_URL, $PAGE_RATE_VIDEO, $PAGE_SURVEY

    //parse data from form 
    $email=$_POST[$SESS_EMAIL];
    $explv = $_POST[$SESS_EXPLV];

    // check whether the email exist against DB
    # Connect to MySQL database
    $con=mysqli_connect($host, $db_user, $db_pwd, $db_name);
    # if connection succeed
    if(mysqli_connect_errno()){ die("failed to connect to mysql:" . mysqli_connect_error()); }

    # check if user exists
    $sql="SELECT * FROM " . $TABLE_USERS . " WHERE email= '$email'";
    $result=mysqli_query($con, $sql);
    $count=mysqli_num_rows($result);

    if($count == 0){  # this is a new user
        $sql_insert = "INSERT INTO ".$TABLE_USERS." (Email, experienceLevel) VALUES ('".$email."', '".$explv."')";
        $result_insert = mysqli_query($con, $sql_insert);
        if(!$result_insert){  # if error happens when inserting
            die("<h3>error happens in creating your account, click <a href='/user_info.html'>HERE</a> to enter your email again</h3>");
        }
        # get the auto-id
        $user_id = mysqli_insert_id($con);
    }else{  # user exists
        $row = mysqli_fetch_row($result);
        $user_id = $row[0];
        // update the experience level every time a user log in
        $sql_update = "UPDATE " . $TABLE_USERS . " SET experienceLevel = '" . $explv . "' WHERE email='" . $email . "'";
        mysqli_query($con, $sql_update);
    }

    // Store log in Info in session
    $_SESSION[$SESS_EMAIL] = $email;  
    $_SESSION[$SESS_USER_ID] = $user_id;
    $_SESSION[$SESS_LOGIN] = True;  // logged in
    $_SESSION[$SESS_EXPLV] = $explv;

    // which button is clicked
    if (isset($_POST['skip_survey'])) {
        $head_url = "Location: ".$DOMAIN_URL.$PAGE_RATE_VIDEO;
    } else if (isset($_POST['get_survey'])) {
        $head_url = "Location: ".$DOMAIN_URL.$PAGE_SURVEY;
    } else {
    }   
    # redirect
    header($head_url); 
    exit();
        

?>