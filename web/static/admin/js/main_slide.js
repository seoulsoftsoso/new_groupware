
$(".menu li").mouseover(function(){
    $(".submenu", this).stop().fadeIn(300);

});

$(".menu li").mouseleave(function(){
    $(".submenu", this).stop().fadeOut(300);
});




var slides = document.querySelector('.slides'),
    slide = document.querySelectorAll('.slides li'),
    currentIdx = 0,
    slideCount = slide.length,
    slideWidth = 200,
    slideMargin = 30,
    preBtn = document.querySelector('.prev'),
    nextBtn = document.querySelector('.next'); 

    makeClone();

    function makeClone(){
        for(var i = 0; i<slideCount; i++){
            // a.cloneNode() 에이요소를 그대로 복사/ a.cloneNode(true) 에이의 자식까지 모두 복사
            var cloneSlide = slide[i].cloneNode(true);
            cloneSlide.classList.add('clone');
            slides.appendChild(cloneSlide);
        }

        for(var i = slideCount -1; i>=0; i--){
            var cloneSlide = slide[i].cloneNode(true);
            cloneSlide.classList.add('clone');
            slides.prepend(cloneSlide);
        }
        updateWidth();
        setInitiapos();
        setTimeout(function(){
        slides.classList.add('animated');
        },100);
    }

    function updateWidth(){
        var currentSlides = document.querySelectorAll('.slides li');
        var newSlideCount = currentSlides.length;

        var newWidth = (slideWidth + slideMargin)*newSlideCount - slideMargin +'px';
        slides.style.width = newWidth;
    }


    function setInitiapos(){
        var initialTranslateVlue = -(slideWidth + slideMargin)*slideCount;
        slides.style.transform = 'translateX('+ initialTranslateVlue+'px)';
    }

    nextBtn.addEventListener('click', function(){
        moneSlide(currentIdx + 1);
    });
    preBtn.addEventListener('click', function(){
        moveSlide(currentIdx -1);
    });

    function moveSlide(num){
        slides.style.left = -num * (slideWidth + slideMargin) + 'px';
        currentIdx = num;
        // console.log(currentIdx, slideCount);
        if(currentIdx == slideCount || currentIdx == -slideCount){
            setTimeout(function(){
                slides.classList.remove('animated');
                slides.style.left = '0px';
                currentIdx = 0;
            }, 500);
            setTimeout(function(){
                slides.classList.add('animated');
            }, 600);
        }
    }


    var timer = undefined;
    function autoSlide(){
        if(timer == undefined){
            timer = setInterval(function(){
                moveSlide(currentIdx + 1);
            },3000);
        }
    }
    autoSlide();


    const toggleBtn = document.querySelector('.nav_popup');
    const menu = document.querySelector('.menu');

    toggleBtn.addEventListener('click', () => {
        menu.classList.toggle('active');
    });


    window.addEventListener('load', function(event){
        AOS.init();
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
    