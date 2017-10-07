<?php
    session_start();    //Start session
    require_once 'config.inc.php'; 
    #require_once 'check-login.php';
    #redirect_if_not_login($_SESSION);
    error_log('landed on exp-lvl.php, Session array: '.json_encode($_SESSION).', _POST: '.json_encode($_POST));

?>

<!DOCTYPE html>
<html>
<head>
    <title>Cycling Safety Project</title>
    <script src="js/jquery-3.1.1.min.js"></script>
    <script src="js/bootstrap.min.js"></script>
    <link href="css/bootstrap.min.css" rel="stylesheet" media="screen">
    <link href="css/main.css" rel="stylesheet" >
    <link href="css/img-button.css" rel="stylesheet" >
    
    <style type="text/css">
        li {font-size: 18px;}
    </style>
    <script>
        
$(document).ready(function(){
        if (navigator.userAgent.indexOf('MSIE') !== -1 || navigator.appVersion.indexOf('Trident/') > 0) {
            $("#ie").html('This website is not compatible with IE. If you have trouble while using IE, please try other browsers. Thank you.');
        }
});
     </script>
</head>

<body>
<div class="spacer20"></div>   <!-- add space -->
<form id="myform" method="post" action="<?=$PAGE_SAVE_EXP?>">
    <div class="container"> 
        <div class="row">
                <h1>Welcome! <?=$_SESSION[$SESS_EMAIL]?></h1>
                <p>Before you start, we would like to know your cycling experience level, please choose the type of experience that best fits you.</p>
                <p id="ie"></p>
        </div>    
        <div class="spacer20"></div>   <!-- add space -->
    
        <!-- row of experience level -->
        <div class="row">
            <div class="btn-group">
                <!-- exp lvl Fearless -->
                <div class="col-md-3 text-center">
                        <label>
                          <input type="radio" name="<?=$SESS_EXPLV?>" id='e1' value="fearless" class="sr-only" required/>
                          <img src="cyclingsafety_files/c1.png" /> 
                        </label>
                        <ul class="text-align-left">
                            <h2>Fearless</h2>
                            <li>Cycling is strong part of your identity</li>
                            <li>You are generally undeterred by motor vehicles</li>
                            <li>You will consider cycling even in the absence of any visible bike facility</li>
                        </ul>
                </div><!-- /exp lvl Fearless -->
                
                <!-- exp lvl confident -->
                <div class="col-md-3 text-center">
                        <label>
                          <input type="radio" name="<?=$SESS_EXPLV?>" id='e2'  value="confident" class="sr-only" required/>
                          <img src="cyclingsafety_files/c2.png" /> 
                        </label>
                        <ul class="text-align-left">
                            <h2>Confident</h2>
                            <li>Cycling is a part of your identity</li>
                            <li>You are slightly or moderately comfortable sharing the road with motor vehicles</li>
                            <li>You will consider cycling if the route is mostly on a bike facility</li>
                        </ul>
                </div><!-- /exp lvl confident -->
                
                <!-- exp lvl interested -->
                <div class="col-md-3 text-center">
                        <label>
                          <input type="radio" name="<?=$SESS_EXPLV?>" id='e3'  value="interested" class="sr-only" required/>
                          <img src="cyclingsafety_files/c3.png"/> 
                        </label>
                        <ul class="text-align-left">
                            <h2>Interested</h2>
                            <li>You do not identify yourself as a regular cyclist</li>
                            <li>You are not very comfortable sharing the road with motor vehicles without a visible bike facility</li>
                            <li>You are Interested in cycling if the route is on a bike facility</li>
                        </ul>
                </div><!-- /exp lvl interested -->
                
                <!-- exp lvl reluctant -->
                <div class="col-md-3 text-center">
                        <label>
                          <input type="radio" name="<?=$SESS_EXPLV?>" id='e4'  value="reluctant" class="sr-only" required/>
                          <img src="cyclingsafety_files/c4.png"/> 
                        </label>
                        <ul class="text-align-left">
                            <h2>Reluctant</h2>
                            <li>You do not identify yourself as a cyclist</li>
                            <li>You are not comfortable sharing the road with motor vehicles without a visible bike facility</li>
                            <li>You are not interested in cycling</li>
                        </ul>
                </div><!-- /exp lvl reluctant -->
                
            </div> <!-- /btn-group-->
        </div><!-- /experience Level -->
        
        <div class="spacer20"></div>   <!-- add space -->
        <div class="row text-center">
            <div class="col-md-4"></div>
            <div class="col-md-4"><button class="btn btn-lg btn-primary" type="submit" style='width:60%; padding: 20px; font-size:20px'><big><b>Submit</b></big></button></div>
            <div class="col-md-4"></div>
        </div>
    </div>
</form>
            
        <div class="spacer20"></div>   <!-- add space -->
        <div class="spacer20"></div>   <!-- add space -->
<footer class="footer">
        <div class="container">
            <p class="text-muted footer-text">
   Cycling Safety project is designed and lead by the <a href="http://www.urbancomputinglab.org">Urban Computing Lab</a> at the <a href="http://www.umd.edu/">University of Maryland</a> with support from the <a href="http://www.nsf.gov">National Science Foundation. </a>  If you have any suggestion or question, contact us at <a href="mailto:umdcyclingsafety@gmail.com">umdcyclingsafety@gmail.com</a>
            </p>
        </div>
    </footer>
</body>

