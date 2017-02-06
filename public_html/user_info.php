<?php
session_start();    //Start session

# Connect to MySQL database
include_once('config.inc.php');  //$db_name, $host, $db_user, $db_pwd 
$con=mysqli_connect($host, $db_user, $db_pwd, $db_name);

if(mysqli_connect_errno())
{
    echo"failed to connect to mysql:".mysqli_connect_error();
}
else{
    // parse data from form and which button is clicked
    // check whether the email exist
    //      if exist: retrieve user id into SESSION; update experience level
    //      else insert email, retrieve user id into SESSION
    // if survey btn is clicked:
    //      redirect to survey.html
    // else: redirect to rate-vid.html
    $email=$_POST['Email'];
    $explv = $_POST['experienceLevel'];
    $_SESSION["Email"] = $email;  //Store the username and user_id in session variable
    
    $sql="SELECT * FROM Users WHERE email= '$email'";
    $result=mysqli_query($con, $sql);

    $count=mysqli_num_rows($result);
    if($count >= 1){
        $row = mysqli_fetch_row($result);
        $_SESSION["user_id"] = $row[0];
            header("Location: http://cyclingsafety.umd.edu/rate-vid.html"); 
            return true;
        }
        else{      
            $table_name = "Users";
            $sql="INSERT INTO ".$table_name." (Email, experienceLevel) VALUES ('".$email."', '".$explv."')";
            $result=mysqli_query($con, $sql);
            if(mysqli_connect_errno())
            {
              echo"failed to connect to mysql:".mysqli_connect_error();
            }
            else{
                header("Location: http://cyclingsafety.umd.edu/survey.html"); 
                return true;
            }
        }
    
    echo "unknown error";
    return false;    
}
?>