<?php

function compare($a,$b)
{
	if ($a===$b)
  	{
  		return 0;
  	}
  return ($a > $b) ? 1 : -1;
}

function toArr($res){
	$arr = array();

	while($row = $res->fetch_assoc()){
		arr.array_push($arr, $row["vid"]);
	}
	return $arr;
}

session_start();    //Start session

# Connect to MySQL database
require_once 'config.inc.php';  //$db_name, $host, $db_user, $db_pwd 
$con=mysqli_connect($host, $db_user, $db_pwd, $db_name);
    
if(mysqli_connect_errno())
{
	echo"failed to connect to mysql:".mysqli_connect_error();
}

$sql = "SELECT vid FROM Video";
$all_vids = $con->query($sql);
$vids_arr = toArr($all_vids);
$num_vids = count($vids_arr);

if( $all_vids->num_rows == 0){
	echo "ERROR: Missing videos";
}

$sql = "SELECT vid FROM Rating WHERE uid =$_SESSION[$SESS_USER_ID]";
$rated_vids = $con->query($sql);
$rated_arr = toArr($rated_vids);

$valid_vids = array();

for($x=0; $x<$num_vids; $x++){
	if(!in_array($vids_arr[$x], $rated_arr)){
		array_push($valid_vids, $vids_arr[$x]);
	}
}
$rand = 0;


if(count($valid_vids) == 0){
	$rand = rand(0, $num_vids-1);
        $vid = $vids_arr[$rand];
}

else{
	$rand = rand(0, count($valid_vids)-1);
        $vid = $valid_vids[$rand];
}

$sql = "SELECT URL FROM Video WHERE vid=$vid";
$_SESSION[$SESS_VIDEO_ID] = $vid;
$url = $con->query($sql);
$res = $url->fetch_assoc();
echo($res[$TABL_VIDEO_FIELD_URL]);

?>

