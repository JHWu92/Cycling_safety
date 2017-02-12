<? php
    
    function insert_user($con, $email, $explv){
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
        $sql_update = "UPDATE $TABLE_USERS SET experienceLevel = '$explv' WHERE email='$email'";
        mysqli_query($con, $sql_update);
    }
    
    function insert_rate($con, $user_id, $video_id, $score, $comment, $tags){
        $sql = "INSERT $TABLE_RATING (user_id, vid, score, comment) VALUES ($user_id, $video_id, $score, '$comment')";
        $result = mysqli_query($con, $sql);
        $rid = mysqli_insert_id($con);
        return $rid;
    }
    
    function update_user_survey($con, $user_id, $dict_survey){
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
        $sql = "INSERT $TABLE_SEG (streetsegid_dc, geometry) VALUES ('$streetsegid', '$geometry_wkb')";
        $result = mysqli_query($con, $sql);
        $sid = mysqli_insert_id($con);
        return $sid;        
    }
    
    function insert_video($con, $url, $vfile, $gpx, $v2segs){
        $sql = "INSERT $TABLE_VIDEO(url, vfile, gpx) VALUES ('$url', '$vfile', '$gpx')";
        $result = mysqli_query($con, $sql);
        $vid = mysqli_insert_id($con);
        for $v2s: $v2segs{
            $sid, $start_pt, $end_pt, $prcnt = $v2s;
            insert_v2s($con, $vid, $sid, $start_pt, $end_pt, $prcnt);
        }
        return $vid;
    }
    
    function insert_v2s($con, $vid, $sid, $start_pt, $end_pt, $prcnt){
        $sql = "INSERT $TABLE_VIDEO2SEGS (vid, sid, start_pt, end_pt, prcnt) VALUES ($vid, $sid, $start_pt, $end_pt, $prcnt)";
        $result = mysqli_query($con, $sql);
        $vsid = mysqli_insert_id($con);
        return $vsid;
    }
?>