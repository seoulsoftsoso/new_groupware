$(document).ready(function() {
    $('.menu-item').each(function(index) {
        if (sessionStorage.getItem('menuOpen' + (index + 1)) === 'true') {
            $(this).find('.menu-sub').show();
            $(this).find('.menu-toggle').addClass('menu-opened');
            // $('.menu-toggle').css('transform', 'rotate(90deg)')
        } else {
            $(this).find('.menu-sub').hide();
            $(this).find('.menu-toggle').removeClass('menu-opened');
        }
    });

    var path = window.location.pathname;
    $('.menu-inner a').each(function () {
        var href = $(this).attr('href');
        if (path === href) {
            $(this).closest('li').addClass('selected');
        }
    });
});

// 드롭다운 메뉴를 토글할 때 상태 저장
$('.menu-toggle').click(function() {
    var menu = $(this).closest('.menu-item');
    var index = $('.menu-item').index(menu) + 1;

    // 클릭한 메뉴 외의 모든 메뉴 닫기
    $('.menu-item').not(menu).find('.menu-sub').hide();
    $('.menu-item').not(menu).each(function(ind) {
        sessionStorage.setItem('menuOpen' + (ind + 1), false);
    });

    // 클릭한 메뉴의 상태 토글
    menu.find('.menu-sub').toggle();
    sessionStorage.setItem('menuOpen' + index, menu.find('.menu-sub').is(':visible'));
    menu.find('.menu-toggle').toggleClass('menu-opened', menu.find('.menu-sub').is(':visible'));
});

$('.normal-menu, .main-page').click(function() {
    $('.menu-item').find('.menu-sub').hide();
    $('.menu-item').each(function(index) {
        sessionStorage.setItem('menuOpen' + (index + 1), false);
    });
});

