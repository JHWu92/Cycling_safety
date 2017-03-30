<?php
    session_start();    //Start session
    include_once('config.inc.php');  //$db_name, $host, $db_user, $db_pwd, $PAGE_RATE_VIDEO, $DOMAIN_URL
    
?>    

<!DOCTYPE html>
<html lang="en">
<head>
  <title>Survey of Demographics</title>
  <meta charset="utf-8">
  
  <script src="js/jquery-3.1.1.min.js"></script>
  <link href="css/bootstrap.min.css" rel="stylesheet" media="screen">
  <script src="js/bootstrap.min.js"></script>
  <link href="css/main.css" rel="stylesheet" media="screen">
  <style type="text/css">
    #fixedbutton {
        position: fixed;
        bottom: 20%;
        right: 3%; 
        font-size:20px;
    }
  </style>
</head>

<body>

<form method="post" action="<?=$PAGE_SURVEY_SAVE?>">

    <button id='fixedbutton' class="btn btn-primary center-block" type="submit">Submit and <br> Start Rating!</button>
    <div class="container" width="70%">
        <div class="row">
            <div class="col-sm-12">
        
    <h2>Survey (optional)</h2>
   <h4>It is of great help for the project to understand how cycling safety perceptions are affected by demographic and socioeconomic factors.</h4>
  <h4>There are 11 questions in this survey. None of these questions are required. If a question is uncomfortable for you to answer, just skip it.</h4> 
  <h4>if you prefer not to provide this information, please click <a href="<?=$PAGE_RATE_VIDEO?>" class="btn btn-default">No, thank you</a></h4>
        </div></div>
        <div class="spacer20"></div>   
        <div class="row">
            <div class="col-sm-12">
                <h3>(0) Which one of the following best describes your type of biking?</h3>
                <div class="radio"><label><input type="radio" value="1" name="<?=$TB_U_COL_BK_PURPOSE?>">Mainly utility biking – traveling from one location to another</label></div>
                <div class="radio"><label><input type="radio" value="2" name="<?=$TB_U_COL_BK_PURPOSE?>">Mainly recreational biking – biking for recreation, leisure, and health</label></div>
                <div class="radio"><label><input type="radio" value="3" name="<?=$TB_U_COL_BK_PURPOSE?>">About 50 : 50 between 1 and 2 above.</label></div>
            </div>
        </div>
        <br>
        <div class="row">
            <div class="col-sm-12">
                <h3>(1) How old are you?</h3>
                <div class="radio"><label><input type="radio" value="1" name="<?=$TB_U_COL_AGE?>">Under 18 years old</label></div>
                <div class="radio"><label><input type="radio" value="2" name="<?=$TB_U_COL_AGE?>">18-24 years old</label></div>
                <div class="radio"><label><input type="radio" value="3" name="<?=$TB_U_COL_AGE?>">25-34 years old</label></div>
                <div class="radio"><label><input type="radio" value="4" name="<?=$TB_U_COL_AGE?>">35-44 years old</label></div>
                <div class="radio"><label><input type="radio" value="5" name="<?=$TB_U_COL_AGE?>">45-54 years old</label></div>
                <div class="radio"><label><input type="radio" value="6" name="<?=$TB_U_COL_AGE?>">55-64 years old</label></div>
                <div class="radio"><label><input type="radio" value="7" name="<?=$TB_U_COL_AGE?>">65-74 years old</label></div>
                <div class="radio"><label><input type="radio" value="8" name="<?=$TB_U_COL_AGE?>">75 years or older</label></div>
            </div>
        </div>
        <br>
        <div class="row">
            <div class="col-sm-12">
            <h3>(2) Ethnicity origin (or Race): Please specify your ethnicity.</h3>
                <div class="radio"><label><input type="radio" value="1" name="<?=$TB_U_COL_ETHNICITY?>">White</label></div>
                <div class="radio"><label><input type="radio" value="2" name="<?=$TB_U_COL_ETHNICITY?>">Hispanic or Latino</label></div>
                <div class="radio"><label><input type="radio" value="3" name="<?=$TB_U_COL_ETHNICITY?>">Black or African American</label></div>
                <div class="radio"><label><input type="radio" value="4" name="<?=$TB_U_COL_ETHNICITY?>">Native American or American Indian</label></div>
                <div class="radio"><label><input type="radio" value="5" name="<?=$TB_U_COL_ETHNICITY?>">Asian / Pacific Islander</label></div>
                <div class="radio"><label><input type="radio" value="6" name="<?=$TB_U_COL_ETHNICITY?>">Other</label></div>
            </div>
        </div>
        <br>
        <div class="row">
            <div class="col-sm-12">
                <h3>(3) Education: What is the highest degree or level of school you have completed? If currently enrolled, highest degree received.</h3>
                <div class="radio"><label><input type="radio" value="1" name="<?=$TB_U_COL_EDU?>"></label>Nursery school to some high school, no diploma</div>
                <div class="radio"><label><input type="radio" value="2" name="<?=$TB_U_COL_EDU?>">High school graduate, diploma or the equivalent (for example: GED)</label></div>
                <div class="radio"><label><input type="radio" value="3" name="<?=$TB_U_COL_EDU?>">Some college credit, no degree</label></div>
                <div class="radio"><label><input type="radio" value="4" name="<?=$TB_U_COL_EDU?>">Associate degree</label></div>
                <div class="radio"><label><input type="radio" value="5" name="<?=$TB_U_COL_EDU?>">Bachelor’s degree</label></div>
                <div class="radio"><label><input type="radio" value="6" name="<?=$TB_U_COL_EDU?>">Master’s degree</label></div>
                <div class="radio"><label><input type="radio" value="7" name="<?=$TB_U_COL_EDU?>">Doctorate degree</label></div>
                
            </div>
        </div>
        <br>
        <div class="row">
            <div class="col-sm-12">
                <h3>(4) Marital Status: What is your marital status?</h3>
                <div class="radio"><label><input type="radio" value="1" name="<?=$TB_U_COL_MARITAL?>">Single, never married</label></div>
                <div class="radio"><label><input type="radio" value="2" name="<?=$TB_U_COL_MARITAL?>">Married or domestic partnership</label></div>
                <div class="radio"><label><input type="radio" value="3" name="<?=$TB_U_COL_MARITAL?>">Widowed</label></div>
                <div class="radio"><label><input type="radio" value="4" name="<?=$TB_U_COL_MARITAL?>">Divorced</label></div>
                <div class="radio"><label><input type="radio" value="5" name="<?=$TB_U_COL_MARITAL?>">Separated</label></div>
            </div>
        </div>
        <br>
        <div class="row">
            <div class="col-sm-12">
                <h3>(5) Gender: to which gender identity do you most identify?</h3>
                <div class="radio"><label><input type="radio" value="1" name="<?=$TB_U_COL_GENDER?>">Female</label></div>
                <div class="radio"><label><input type="radio" value="2" name="<?=$TB_U_COL_GENDER?>">Male</label></div>
                <div class="radio"><label><input type="radio" value="3" name="<?=$TB_U_COL_GENDER?>">Transgender – Female</label></div>
                <div class="radio"><label><input type="radio" value="4" name="<?=$TB_U_COL_GENDER?>">Transgender – Male</label></div>
                <div class="radio"><label><input type="radio" value="5" name="<?=$TB_U_COL_GENDER?>">Gender-variant / Non-conforming</label></div>
                <div class="radio"><label><input type="radio" value="6" name="<?=$TB_U_COL_GENDER?>">Not listed</label></div>
            </div>
        </div>
        <br>
        <div class="row">
            <div class="col-sm-12">
                <h3>(6) Driver's license: Do you currently have a valid driver's license?</h3>
                <div class="radio"><label><input type="radio" value="1" name="<?=$TB_U_COL_DRIVER?>">Yes</label></div>
                <div class="radio"><label><input type="radio" value="0" name="<?=$TB_U_COL_DRIVER?>">No</label></div>
            </div>
        </div>
        <br>
        <div class="row">
            <div class="col-sm-12">
                <h3>(7) Private car: Do you currently have an easy access to a car, including a Zip car, a Car2Go, etc.?</h3>
                <div class="radio"><label><input type="radio" value="1" name="<?=$TB_U_COL_CAR?>">Yes</label></div>
                <div class="radio"><label><input type="radio" value="0" name="<?=$TB_U_COL_CAR?>">No</label></div>
            </div>
        </div>
        <br>
        <div class="row">
            <div class="col-sm-12">
                <h3>(8) Household Income: What is your total household income?</h3>
                <div class="radio"><label><input type="radio" value="1" name="<?=$TB_U_COL_HHINCOME?>">Less than $24,999</label></div>
                <div class="radio"><label><input type="radio" value="2" name="<?=$TB_U_COL_HHINCOME?>">$25,000 to $39,999</label></div>
                <div class="radio"><label><input type="radio" value="3" name="<?=$TB_U_COL_HHINCOME?>">$40,000 to $54,999</label></div>
                <div class="radio"><label><input type="radio" value="4" name="<?=$TB_U_COL_HHINCOME?>">$55,000 to $69,999</label></div>
                <div class="radio"><label><input type="radio" value="5" name="<?=$TB_U_COL_HHINCOME?>">$70,000 to $84,999</label></div>
                <div class="radio"><label><input type="radio" value="6" name="<?=$TB_U_COL_HHINCOME?>">$85,000 to $99,999</label></div>
                <div class="radio"><label><input type="radio" value="7" name="<?=$TB_U_COL_HHINCOME?>">$100,000 to $149,999</label></div>
                <div class="radio"><label><input type="radio" value="8" name="<?=$TB_U_COL_HHINCOME?>">$150,000 or more</label></div>
            </div>
        </div>
        <br>
        <div class="row">
            <div class="col-sm-12">
                <h3>(9) Time of Residence: How long have you lived in the DC region?</h3>
                <div class="radio"><label><input type="radio" value="1" name="<?=$TB_U_COL_RESIDENCE?>">Never</label></div>
                <div class="radio"><label><input type="radio" value="2" name="<?=$TB_U_COL_RESIDENCE?>">Less than 3 months</label></div>
                <div class="radio"><label><input type="radio" value="3" name="<?=$TB_U_COL_RESIDENCE?>">3 to 6 months</label></div>
                <div class="radio"><label><input type="radio" value="4" name="<?=$TB_U_COL_RESIDENCE?>">6 months to 12 months</label></div>
                <div class="radio"><label><input type="radio" value="5" name="<?=$TB_U_COL_RESIDENCE?>">1 to 3 years</label></div>
                <div class="radio"><label><input type="radio" value="6" name="<?=$TB_U_COL_RESIDENCE?>">3 years or longer</label></div>
            </div>
        </div>
        <br>
        <div class="row">
            <div class="col-sm-12">
                <h3>(10) Types of bicycle : What type of bicycle do you usually ride?</h3>
                <div class="radio"><label><input type="radio" value="1" name="<?=$TB_U_COL_BK_TYPE?>">CaBi Bike (Shared bike in the DC region)</label></div>
                <div class="radio"><label><input type="radio" value="2" name="<?=$TB_U_COL_BK_TYPE?>">Road Bike</label></div>
                <div class="radio"><label><input type="radio" value="3" name="<?=$TB_U_COL_BK_TYPE?>">Mountain Bike</label></div>
                <div class="radio"><label><input type="radio" value="4" name="<?=$TB_U_COL_BK_TYPE?>">Hybrid Bike</label></div>
                <div class="radio"><label><input type="radio" value="5" name="<?=$TB_U_COL_BK_TYPE?>">Cruiser Bike</label></div>
                <div class="radio"><label><input type="radio" value="6" name="<?=$TB_U_COL_BK_TYPE?>">BMX Bike</label></div>
                <div class="radio"><label><input type="radio" value="7" name="<?=$TB_U_COL_BK_TYPE?>">Folding Bike</label></div>
                <div class="radio"><label><input type="radio" value="8" name="<?=$TB_U_COL_BK_TYPE?>">Recumbent Bike</label></div>
                <div class="radio"><label><input type="radio" value="9" name="<?=$TB_U_COL_BK_TYPE?>">Tandem Bike</label></div>
                <div class="radio"><label><input type="radio" value="10" name="<?=$TB_U_COL_BK_TYPE?>">Do not ride a bike</label></div>
            </div>
        </div>
    </div>
    


</form>
</body>




</html>