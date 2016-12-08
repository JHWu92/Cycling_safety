<?php
    session_start();

    $email = $_POST["Email"];
    $pwd = $_POST["Password"];
    $username = $_POST["userName"];

    $experience = $_POST["experienceLevel"];
          //echo 'email: '.$email.'<br/>';
          //echo 'pwd: '.$pwd.'<br/>';
          //echo 'option: '.$experience.'<br/>';
    $db_name = "cyclings_vid1";
    $con=mysqli_connect("localhost","cyclings_jiahui","@2n54a=@]ZQ4", $db_name);
    $crypt_pwd = crypt($pwd, "st");

    if(mysqli_connect_errno())
    {
      echo"failed to connect to mysql:".mysqli_connect_error();
    }
    else
      //            echo "connected!";
      $table_name = "Users";
      $sql="INSERT INTO ".$table_name." (Email, Password, experienceLevel, userName) VALUES ('".$email."', '".$crypt_pwd."', '".$experience."', '".$username."')";
    //    echo "<br>sql=".$sql;
    if (mysqli_query($con,$sql))
    {

      $_SESSION["username"] = $username;  //Store the username and user_id in session variable
      $sql="SELECT * FROM Users WHERE userName= '$username' AND password= '$crypt_pwd'";
      $result = $con->query($sql);
      $row = $result->fetch_assoc();
      $_SESSION["user_id"] = $row["userid"];


      header("Location: http://cyclingsafety.umd.edu/rate-vid.html"); /* Redirect browser */
      exit();
    }
    else
    {
      echo "Error creating table: " . mysqli_error($con);
    }
?>