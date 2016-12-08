<html>
<body>
<?php   
$con=mysqli_connect("localhost","cyclings_jiahui","@2n54a=@]ZQ4","cyclings_vid1");
if(mysqli_connect_errno())
{
echo"failed to connect to mysql:".mysqli_connect_error();
}
else
        echo "connected!";
?>
Welcome <?php echo $_POST["cemail"]; ?>
<br>
Your pwd is: <?php echo $_POST["pwd"]; ?>

    </body>


</html>