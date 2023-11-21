
$(".menu li").mouseover(function(){
    $(".submenu", this).stop().fadeIn(300);

});

$(".menu li").mouseleave(function(){
    $(".submenu", this).stop().fadeOut(300);
});


window.addEventListener('load', function(event){
    AOS.init();
});

const toggleBtn = document.querySelector('.nav_popup');
const menu = document.querySelector('.menu');

toggleBtn.addEventListener('click', () => {
    menu.classList.toggle('active');
});

$(".close").click(function(){
    $(".thankyou_message").css("display", "none");
});


$("input[name='answer']:checked").each(function(){
    console.log($(this).val())
});

$("input[name='chk']:checked").each(function(){
    console.log($(this).val())
});


$(function(){
    $(window).scroll(function(){
        if ($(this).scrollTop() > 250){
            $('#topBtn').fadeIn();
        }else{
            $('#topBtn').fadeOut();
        }
    });

    $('#topBtn').click(function(){
        $('html, body').animate({
            scrollTop : 0
        }, 400);
        return false;
    });
});


var text = document.getElementById('text')
var shadow = '';
for(var i = 0; i < 20; i++){
  shadow +=(shadow? ',':'')+ -i*1+'px ' + i*1+'px 0 #d9d9d9';
}
text.style. textShadow = shadow;


$(document).ready(function(){
    $('.more').click(function(){
        $('.back').addClass('active')
        $('.front').removeClass('active')
    })
    $('.go-back').click(function(){
        $('.back').removeClass('active')
        $('.front').addClass('active')
    })
})

