<?php
	session_start();	//resume the session

    # Connect to MySQL database
    include_once('config.inc.php');  //$db_name, $host, $db_user, $db_pwd 
    $con=mysqli_connect($host, $db_user, $db_pwd, $db_name);

	$rating = $_POST["inlineRadioOptions"];
	$comment = $_POST["Description"];
	$vid_id = 3;

	$experience = $_POST["experienceLevel"];
	$db_name = "cyclings_vid1";
	$con=mysqli_connect("localhost","cyclings_jiahui","@2n54a=@]ZQ4", $db_name);

	if(mysqli_connect_errno())
	{
		echo"failed to connect to mysql:".mysqli_connect_error();
	}
	else
		$table_name = "Rating";
		$sql="INSERT INTO ".$table_name." (comment, ratingScore, userid, email, videoid) VALUES ('".$comment."', '".$rating."', '".$_SESSION["user_id"]."', '".$_SESSION["email"]."', '".$_SESSION["videoid"]."')";
		if (mysqli_query($con,$sql))
		{
			header("Location: http://cyclingsafety.umd.edu/rate-vid.html"); /* Redirect browser */
			exit();
		}
		else
		{
			echo "Error creating table: " . mysqli_error($con);
		}
?>