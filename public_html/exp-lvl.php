<?php
    session_start();    //Start session
    include_once('config.inc.php');  //$db_name, $host, $db_user, $db_pwd, $TABLE_USERS, $DOMAIN_URL, $PAGE_RATE_VIDEO, $PAGE_SURVEY
?>

<!DOCTYPE html>
<html>
<head>
    <title>Welcome to Cycling Safety Project</title>
    <script src="js/jquery-3.1.1.min.js"></script>
    <script src="js/bootstrap.min.js"></script>
    <script type="text/javascript" src="js/check-login.js"></script>
    <link href="css/bootstrap.min.css" rel="stylesheet" media="screen">
    <link href="css/main.css" rel="stylesheet" >
    <link href="css/img-button.css" rel="stylesheet" >
</head>

<body>
<div class="spacer20"></div>   <!-- add space -->
<form id="myform" method="post" action="<?=$PAGE_SAVE_EXP?>">
    <div class="container"> 
        <div class="row">
                <h1>Welcome! <?=$_SESSION[$SESS_EMAIL]?></h1>
                <p>Before you start, we would like to know your cycling experience level, please choose the type of experience that best fits you.</p>
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
                            <h3>Fearless</h3>
                            <li>Cycling is strong part of their identity</li>
                            <li>Generally undeterred by motor vehicles</li>
                            <li>Will consider cycling even in the absence of any visible bike facility</li>
                        </ul>
                </div><!-- /exp lvl Fearless -->
                
                <!-- exp lvl confident -->
                <div class="col-md-3 text-center">
                        <label>
                          <input type="radio" name="<?=$SESS_EXPLV?>" id='e2'  value="confident" class="sr-only" required/>
                          <img src="cyclingsafety_files/c2.png" /> 
                        </label>
                        <ul class="text-align-left">
                            <h3>Confident</h3>
                            <li>Cycling is a part of their identity</li>
                            <li>Slightly or moderately comfortable sharing the road with motor vehicles</li>
                            <li>Will consider cycling if the route is mostly on a bike facility</li>
                        </ul>
                </div><!-- /exp lvl confident -->
                
                <!-- exp lvl interested -->
                <div class="col-md-3 text-center">
                        <label>
                          <input type="radio" name="<?=$SESS_EXPLV?>" id='e3'  value="interested" class="sr-only" required/>
                          <img src="cyclingsafety_files/c3.png"/> 
                        </label>
                        <ul class="text-align-left">
                            <h3>Interested</h3>
                            <li>Do not identify as a cyclist</li>
                            <li>Not comfortable sharing the road with motor vehicles without a visible bike facility</li>
                            <li>Interested in cycling if the route is on a bike facility</li>
                        </ul>
                </div><!-- /exp lvl interested -->
                
                <!-- exp lvl reluctant -->
                <div class="col-md-3 text-center">
                        <label>
                          <input type="radio" name="<?=$SESS_EXPLV?>" id='e4'  value="reluctant" class="sr-only" required/>
                          <img src="cyclingsafety_files/c4.png"/> 
                        </label>
                        <ul class="text-align-left">
                            <h3>Reluctant</h3>
                            <li>Do not identify as a cyclist</li>
                            <li>Not comfortable sharing the road with motor vehicles without a visible bike facility</li>
                            <li>Not interested in cycling</li>
                        </ul>
                </div><!-- /exp lvl reluctant -->
                
            </div> <!-- /btn-group-->
        </div><!-- /experience Level -->
        
        <div class="spacer20"></div>   <!-- add space -->
        <div class="row text-center">
            <div class="col-md-4"></div>
            <div class="col-md-4"><button class="btn btn-lg btn-primary" type="submit" style='width:60%'>Submit</button></div>
            <div class="col-md-4"></div>
        </div>
    </div>
</form>
</body>

