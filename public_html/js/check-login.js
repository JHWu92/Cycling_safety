
$(document).ready(function(){
    var obj = jQuery.ajax({
        url: '/check-login.php',
        async: false,
    }).responseText;
       
    if(obj!="True") {
        //$('#player').remove();
        $('.container').html("<h2>Please sign in before rating.</h2><h4>Redirecting to sign in page in 5 seconds. if it didn't refresh, click here <a href='/user_info.html'>sign in</a></h4>");
        setTimeout("location.href = '/user_info.html';",5000);
    }

});