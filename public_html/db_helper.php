<?php
    
    include_once('config.inc.php'); 
    function insert_user($con, $email, $explv){
        global $TABLE_USERS;
        $sql_insert = "INSERT INTO $TABLE_USERS (Email, experienceLevel) VALUES ('$email', '$explv')";
        $result_insert = mysqli_query($con, $sql_insert);
        if(!$result_insert){  # if error happens when inserting
            die("<h3>error happens in creating your account, click <a href='/user_info.html'>HERE</a> to enter your email again</h3>");
        }
        # get the auto-id
        $user_id = mysqli_insert_id($con);
        return $user_id;
    }
    
    function select_user_by_email($con, $email){
        global $TABLE_USERS;
        $sql="SELECT * FROM $TABLE_USERS WHERE email= '$email'";
        $result=mysqli_query($con, $sql);
        $count=mysqli_num_rows($result);
        $row = mysqli_fetch_row($result);
        return $row;
    }
    
    function get_user_id_insert_if_not_exist($con, $email, $explv){
        $row = select_user_by_email($con, $email);
        if(!$row){
            $user_id = insert_user($con, $email, $explv);
        }else{
            $user_id = $row[0];
        }
        return $user_id;
    }
    
    function update_user_explv($con, $email, $explv){
        global $TABLE_USERS;
        $sql_update = "UPDATE $TABLE_USERS SET experienceLevel = '$explv' WHERE email='$email'";
        mysqli_query($con, $sql_update);
    }
    
    function insert_rate($con, $uid, $vid, $score, $comment, $tags){
        global $TABLE_RATING;
        $sql = "INSERT $TABLE_RATING (uid, vid, score, comment, tags) VALUES ($uid, $vid, $score, '$comment', '$tags')";
        $result = mysqli_query($con, $sql);
        if(!$result){  # if error happens when inserting
            echo mysqli_error($con)."<br>";
            die("<h3>error</h3>");
        }
        $rid = mysqli_insert_id($con);
        return $rid;
    }
    
    function select_rate_cnt_by_uid($con, $uid){
        global $TABLE_RATING;
        $sql = "SELECT count(1) from $TABLE_RATING WHERE uid=$uid";
        $result=mysqli_query($con, $sql);
        $row = mysqli_fetch_row($result);
        return $row[0];
    }
    
    function update_user_survey($con, $user_id, $dict_survey){
        global $TABLE_USERS;
        if($dict_survey){
            $sql = "UPDATE $TABLE_USERS SET ";
            # for key, value in $dict_survey:
            #   $sql = "$sql $key = '$value' AND"
            # $sql.remove(last and)
            # $sql+="WHERE user_id=$user_id"
            mysqli_query($con, $sql_update);
        }
    }
    
    function insert_seg($con, $streetsegid, $geometry_wkb){
        global $TABLE_SEG;
        $sql = "INSERT $TABLE_SEG (streetsegid_dc, geometry) VALUES ('$streetsegid', '$geometry_wkb')";
        $result = mysqli_query($con, $sql);
        $sid = mysqli_insert_id($con);
        return $sid;        
    }
    
    function insert_video($con, $url, $vfile, $gpx, $v2segs){
        global $TABLE_VIDEO;
        $sql = "INSERT $TABLE_VIDEO(url, vfile, gpx) VALUES ('$url', '$vfile', '$gpx')";
        $result = mysqli_query($con, $sql);
        $vid = mysqli_insert_id($con);
#        foreach($v2segs as $v2s){
#            $sid, $start_pt, $end_pt, $prcnt = $v2s;
#            insert_v2s($con, $vid, $sid, $start_pt, $end_pt, $prcnt);
#        }
        return $vid;
    }   
    
    function insert_v2s($con, $vid, $sid, $start_pt, $end_pt, $prcnt){
        global $TABLE_VIDEO2SEGS;
        $sql = "INSERT $TABLE_VIDEO2SEGS (vid, sid, start_pt, end_pt, prcnt) VALUES ($vid, $sid, $start_pt, $end_pt, $prcnt)";
        $result = mysqli_query($con, $sql);
        $vsid = mysqli_insert_id($con);
        return $vsid;
    }
?>