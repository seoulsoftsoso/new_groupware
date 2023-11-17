
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
    