<?php
require_once 'emailExpSurveyDBandRedirect.php';

$dbhost = "dbcyclesafety.c3pqizrexqbl.us-east-2.rds.amazonaws.com";
$dbport = 3306;
$dbname = "cyclings_vid1";

$dsn = "mysql:host={$dbhost};port={$dbport};dbname={$dbname}";
$username = 'cycling';
$password = '@2n54a=@]ZQ4';

try{
$pdo = new PDO($dsn, $username, $password, array(PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION));
}catch (PDOException $e) {
error_log('PDO Exception: '.$e);
die('Connection failed: ' . $e->getMessage());
}
$res = handle_input_email($pdo, 'asdf@sdf');

echo 'hello world----';
echo print_r($res);
echo '<<<<<<<';
echo '>>>';

?>
