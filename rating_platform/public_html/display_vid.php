<?php

    if (!isset($_SESSION))
    {
        session_start();
    }
#require_once 'check-login.php';
#redirect_if_not_login($_SESSION);

require_once 'config.inc.php';  //$db_name, $host, $db_user, $db_pwd 
$_SESSION[$SESS_VIDEO_ID] = null;
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

	while($row = $res->fetch(PDO::FETCH_ASSOC)){
		array_push($arr, $row["vid"]);
	}
	return $arr;
}


# Connect to MySQL database

try{
    $pdo = new PDO($GLOBALS['DB_DSN'], $GLOBALS['DB_USER'], $GLOBALS['DB_PASSWD'], array(PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION));
}catch (PDOException $e) {
    error_log('display_vid, PDO Exception: '.$e);
    die('Connection failed: ' . $e->getMessage());
}

$sql = "SELECT vid FROM Video";
$select = $pdo->prepare($sql);
$select->execute();
$num_vids=$select->rowCount();
$vids_arr = toArr($select);

if( $num_vids == 0){
	echo "ERROR: Missing videos";
}


$sql = "SELECT vid FROM Rating WHERE uid = ?";
$select = $pdo->prepare($sql);
$select->execute(array($_SESSION[$SESS_USER_ID]));
$rated_arr = toArr($select);

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

$_SESSION[$SESS_VIDEO_ID] = $vid;

$sql = "SELECT URL FROM Video WHERE vid=?";
$select = $pdo->prepare($sql);
$select->execute(array($vid));
$res = $select->fetch(PDO::FETCH_ASSOC);
    
# clear pdo connection
$pdo = null;

echo($res[$TABL_VIDEO_FIELD_URL]);


?>