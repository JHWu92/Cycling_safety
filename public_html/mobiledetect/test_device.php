<?php
    $useragent=$_SERVER['HTTP_USER_AGENT'];
    echo $useragent;
    echo '<br>';
    require_once './Mobile_Detect.php';
    $detect = new Mobile_Detect;


    if( $detect->isMobile()){  echo 'mobile';    }else{ echo 'not mobile';    }
    echo '<br>';
    if( $detect->isTablet()){  echo 'isTablet';    }else{ echo 'not isTablet';    }
    echo '<br>';
    if( $detect->isiOS()){  echo 'isiOS';    }else{ echo 'not isiOS';    }
    echo '<br>';
    if( $detect->isAndroidOS()){  echo 'isAndroidOS';    }else{ echo 'not isAndroidOS';    }
    echo '<br>';
    if( $detect->is('Chrome')){  echo 'Chrome';    }else{ echo 'not Chrome';    }
?>