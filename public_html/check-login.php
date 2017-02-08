<?php
    session_start();
    if (isset($_SESSION['Email'])) {
        echo 'True';
    } else {
        echo 'False';
 //       echo "Please log in first to see this page. Redirecting to log in page in 2 seconds. if it didn't refresh, click here <a href='user_info.html'>login</a>";
 //       echo "<script>setTimeout(\"location.href = 'user_info.html';\",1000);</script>";
        
    }     
    
?>