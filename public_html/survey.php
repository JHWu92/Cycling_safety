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
    $gender=$_POST['gender'];
    $email = $_SESSION["Email"];
    
    $sql="UPDATE Users SET gender='$gender' WHERE email= '$email'";
    $result=mysqli_query($con, $sql);

    if(mysqli_connect_errno())
    {
        echo"failed to connect to mysql:".mysqli_connect_error();
    }
    else{
        header("Location: http://cyclingsafety.umd.edu/rate-vid.html"); 
        return true;
    }
}
?>