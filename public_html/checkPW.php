<?php
session_start();    //Start session

$db_name = "cyclings_vid1";
$con=mysqli_connect("localhost","cyclings_jiahui","@2n54a=@]ZQ4", $db_name);

if(mysqli_connect_errno())
{
    echo"failed to connect to mysql:".mysqli_connect_error();
}
else{
    $username=$_POST['userName'];
    $pwd=$_POST['Password'];

    $sql="SELECT * FROM Users WHERE userName= '$username'";
    $result=mysqli_query($con, $sql);


    $count=mysqli_num_rows($result);
    if($count == 1){
        $row = mysqli_fetch_row($result);
        if (crypt($pwd, $row[2]) == $row[2]){
            $_SESSION["username"] = $username;  //Store the username and user_id in session variable
            $_SESSION["user_id"] = $row[0];
            header("Location: http://cyclingsafety.umd.edu/rate-vid.html"); 
            return true;
        }
        else{
            echo "Incorrect Username or Password";
            return false;
        }
    }
    echo "Incorrect Username or Password";
    return false;    
}
?>