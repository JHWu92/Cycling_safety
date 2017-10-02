<?php
    session_start();    //Start session
    require_once 'config.inc.php';  //$db_name, $host, $db_user, $db_pwd, $PAGE_RATE_VIDEO, $DOMAIN_URL
   
    error_log('survey.php, Session array: '.json_encode($_SESSION).', _POST: '.json_encode($_POST));
    
?>    

<!DOCTYPE html>
<html lang="en">
<head>
  <title>Cycling Safety Project</title>
  <meta charset="utf-8">
  
  <script src="js/jquery-3.1.1.min.js"></script>
  <link href="css/bootstrap.min.css" rel="stylesheet" media="screen">
  <script src="js/bootstrap.min.js"></script>
  <link href="css/main.css" rel="stylesheet" media="screen">
  <style type="text/css">
    #fixedbutton {
        z-index: 99;
        position: fixed;
        bottom: 20%;
        right: 3%; 
        font-size:20px;
    }
    label {
        font-size:18px;
    }
  </style>
</head>

<body>

<form method="post" action="<?=$PAGE_SURVEY_SAVE?>">

    <button id='fixedbutton' class="btn btn-primary center-block" type="submit">Submit and <br> Start Rating!</button>
    <div class="container" width="70%">
        <div class="row">
            <div class="col-lg-12">
        
    <h2>Survey (optional)</h2>
   <h4>This survey is optional, but we would greatly appreciate if you could provide answers for some or all of the 11 questions. We will use this information to understand how cycling safety perceptions might be affected by personal demographic or socioeconomic factors. All your information is treated in a confidential manner. </h4>
  <h4>If you prefer not to provide this information, please click <a href="<?=$PAGE_RATE_VIDEO?>" class="btn btn-default">No,thank you</a></h4>
        </div></div>
        <div class="spacer20"></div>   
        <div class="row">
            <div class="col-lg-12">
                <h3>(1) Which one of the following best describes your type of biking?</h3>
                <div class="radio"><label><input type="radio" value="1" name="<?=$TB_U_COL_BK_PURPOSE?>">Mainly utility biking – traveling from one location to another</label></div>
                <div class="radio"><label><input type="radio" value="2" name="<?=$TB_U_COL_BK_PURPOSE?>">Mainly recreational biking – biking for recreation, leisure, and health</label></div>
                <div class="radio"><label><input type="radio" value="3" name="<?=$TB_U_COL_BK_PURPOSE?>">50% utility, 50% recreational</label></div>
            </div>
        </div>
        <br>
        <div class="row">
            <div class="col-lg-12">
                <h3>(2) How old are you?</h3>
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
            <div class="col-lg-12">
            <h3>(3) Ethnicity origin (or Race): Please specify your ethnicity.</h3>
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
            <div class="col-lg-12">
                <h3>(4) Education: What is the highest degree or level of school you have completed? If currently enrolled, highest degree received.</h3>
                <div class="radio"><label><input type="radio" value="1" name="<?=$TB_U_COL_EDU?>">Nursery school to some high school, no diploma</label></div>
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
            <div class="col-lg-12">
                <h3>(5) Marital Status: What is your marital status?</h3>
                <div class="radio"><label><input type="radio" value="1" name="<?=$TB_U_COL_MARITAL?>">Single, never married</label></div>
                <div class="radio"><label><input type="radio" value="2" name="<?=$TB_U_COL_MARITAL?>">Married or domestic partnership</label></div>
                <div class="radio"><label><input type="radio" value="3" name="<?=$TB_U_COL_MARITAL?>">Widowed</label></div>
                <div class="radio"><label><input type="radio" value="4" name="<?=$TB_U_COL_MARITAL?>">Divorced</label></div>
                <div class="radio"><label><input type="radio" value="5" name="<?=$TB_U_COL_MARITAL?>">Separated</label></div>
            </div>
        </div>
        <br>
        <div class="row">
            <div class="col-lg-12">
                <h3>(6) Gender: To which gender identity do you most identify?</h3>
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
            <div class="col-lg-12">
                <h3>(7) Driver's license: Do you currently have a valid driver's license?</h3>
                <div class="radio"><label><input type="radio" value="1" name="<?=$TB_U_COL_DRIVER?>">Yes</label></div>
                <div class="radio"><label><input type="radio" value="0" name="<?=$TB_U_COL_DRIVER?>">No</label></div>
            </div>
        </div>
        <br>
        <div class="row">
            <div class="col-lg-12">
                <h3>(8) Private car: Do you currently have easy access to a car, including a Zipcar, a Car2Go, etc.?</h3>
                <div class="radio"><label><input type="radio" value="1" name="<?=$TB_U_COL_CAR?>">Yes</label></div>
                <div class="radio"><label><input type="radio" value="0" name="<?=$TB_U_COL_CAR?>">No</label></div>
            </div>
        </div>
        <br>
        <div class="row">
            <div class="col-lg-12">
                <h3>(9) Household Income: What is your total household income?</h3>
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
            <div class="col-lg-12">
                <h3>(10) Time of Residence: How long have you lived in the DC region?</h3>
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
            <div class="col-lg-12">
                <h3>(11) Type of bicycle : What type of bicycle do you usually ride?</h3>
                <div class="radio"><label><input type="radio" value="1" name="<?=$TB_U_COL_BK_TYPE?>">CaBi Bike (Shared bike in the DC region)</label></div>
                <div class="radio"><label><input type="radio" value="2" name="<?=$TB_U_COL_BK_TYPE?>">Road Bike</label></div>
                <div class="radio"><label><input type="radio" value="3" name="<?=$TB_U_COL_BK_TYPE?>">Mountain Bike</label></div>
                <div class="radio"><label><input type="radio" value="4" name="<?=$TB_U_COL_BK_TYPE?>">Hybrid Bike</label></div>
                <div class="radio"><label><input type="radio" value="5" name="<?=$TB_U_COL_BK_TYPE?>">Cruiser Bike</label></div>
                <div class="radio"><label><input type="radio" value="6" name="<?=$TB_U_COL_BK_TYPE?>">BMX Bike</label></div>
                <div class="radio"><label><input type="radio" value="7" name="<?=$TB_U_COL_BK_TYPE?>">Folding Bike</label></div>
                <div class="radio"><label><input type="radio" value="8" name="<?=$TB_U_COL_BK_TYPE?>">Recumbent Bike</label></div>
                <div class="radio"><label><input type="radio" value="9" name="<?=$TB_U_COL_BK_TYPE?>">Tandem Bike</label></div>
                <div class="radio"><label>
                    <input type="radio" value="11" name="<?=$TB_U_COL_BK_TYPE?>">Other: </label>
                    <input type ="text" name="<?=$TB_U_COL_BK_TYPE_OTHER?>" id="other_text"/></label>
                </div>
                <div class="radio"><label><input type="radio" value="10" name="<?=$TB_U_COL_BK_TYPE?>">Do not ride a bike</label></div>
            </div>
        </div>
    </div>
    


</form>

<footer class="footer">
        <div class="container">
            <p class="text-muted footer-text">
   Cycling Safety project is designed and lead by the <a href="http://www.urbancomputinglab.org">Urban Computing Lab</a> at the <a href="http://www.umd.edu/">University of Maryland</a> with support from the <a href="http://www.nsf.gov">National Science Foundation. </a>  If you have any suggestion or question, contact us at <a href="mailto:umdcyclingsafety@gmail.com">umdcyclingsafety@gmail.com</a>
            </p>
        </div>
    </footer>

</body>




</html>
