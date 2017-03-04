
$(document).ready(function(){
    var obj = jQuery.ajax({
        url: '/check-login-jq.php',
        async: false,
    }).responseText;
       
    if(obj!="True") {
        window.location.href = "/login-first.html";
    }

});