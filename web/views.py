from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
import os
from django.conf import settings
from django.contrib import auth
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView
import logging
from rest_framework.exceptions import ValidationError
from api.board import SignUpForm, QuestionForm
from api.models import UserMaster, EnterpriseMaster, BoardMaster, CodeMaster, FileBoardMaster, ReplyMaster


def index(request):
    return render(request, 'index.html', {})


def admin_index_page(request):
    context = {}
    context['block'] = ''
    return render(request, 'admins/index.html', context)


def admin_work_schedule_page(request):
    context = {}
    context['block'] = ''
    return render(request, 'admins/work_schedule.html')


def admin_notice_page(request):
    items_per_page = 10

    notices = BoardMaster.objects.all()

    for notice in notices:
        # 이 부분에서 notice 객체에 'comment_count' 속성을 추가하고 댓글 수를 계산하여 할당합니다.
        notice.comment_count = ReplyMaster.objects.filter(parent=notice).count()
        user_id = notice.created_by_id
        user = UserMaster.objects.get(id=user_id)
        notice.username = user.username

    # 상단 공지로 표시할 글 최대 2개 가져오기
    fixed_notices = BoardMaster.objects.filter(fixed_flag=True).order_by('-created_at')[:2]
    fixed_count = fixed_notices.count()

    for fixed_notice in fixed_notices:
        fixed_notice.comment_count = ReplyMaster.objects.filter(parent=notice).count()
        user_id = fixed_notice.created_by_id
        user = UserMaster.objects.get(id=user_id)
        fixed_notice.username = user.username

    # 페이징기능
    paginator = Paginator(notices[2:], items_per_page)
    page = request.GET.get('page')

    try:
        normal_notices = paginator.page(page)
    except PageNotAnInteger:
        # 페이지가 정수가 아닌 경우 첫 페이지로 설정
        normal_notices = paginator.page(1)
    except EmptyPage:
        # 페이지 범위를 초과하는 경우 마지막 페이지로 설정
        normal_notices = paginator.page(paginator.num_pages)

    context = {
        'fixed_notices': fixed_notices,
        'fixed_count': fixed_count,
        'normal_notices': normal_notices,
    }

    return render(request, 'admins/notice/notice.html', context)


def amdin_noticedetail_page(request, notice_id):
    notice = get_object_or_404(BoardMaster, pk=notice_id)

    # 조회수 증가
    notice.click_cnt += 1
    notice.save()

    # 게시글에 첨부된 파일 가져오기
    files = FileBoardMaster.objects.filter(parent_id=notice)

    # 게시글에 달린 댓글 가져오기
    comments = ReplyMaster.objects.filter(parent_id=notice)

    context = {
        'notice': notice,
        'files': files,
        'comments': comments,
    }

    return render(request, 'admins/notice/notice_detail.html', context)


def amdin_board_page(request):
    context = {}
    context['block'] = ''
    return render(request, 'admins/board/board.html')


def admin_boardwrite_page(request):
    context = {}
    context['block'] = ''
    return render(request, 'admins/board/board_write.html')


def admin_boardList_page(request):
    context = {}
    context['block'] = ''
    return render(request, 'admins/board/board_list.html')


def admin_boardDetail_page(request):
    context = {}
    context['block'] = ''
    return render(request, 'admins/board/board_detail.html')


def login_page(request):
    return render(request, 'login.html', {})


def logout_view(request):
    auth.logout(request)
    return redirect('index')


def signup_page(request):
    return render(request, 'registration/signup.html', {})


def UserCreate(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)  # UserCreationForm 객체를 생성하도록 수정
        if form.is_valid():
            form.save()
            print('데이터 통신 성공')
        else:
            raise ValidationError('관리자에게 문의 바랍니다.')

    return render(request, 'index.html')


@csrf_exempt
def check_duplicate(request):
    if request.method == "POST":
        user_id = request.POST.get("user_id", None)
        print('아이디', user_id)

        id_check = UserMaster.objects.filter(user_id=user_id).count()
        print('매칭 레코드 수:', id_check)

        is_duplicate = id_check > 0
        return JsonResponse({"is_duplicate": is_duplicate})

    return JsonResponse({"error": "Invalid request method"})


def register_page(request):
    return render(request, 'register.html', {})


def register_ok(request):
    return render(request, 'register_ok.html', {})


def SubView(request, menu_num):
    menucode1 = menu_num[:2]
    menucode2 = menu_num[2:]
    filename = 'sub/menu' + menucode1 + '/menu' + menucode1 + '_' + menucode2 + '.html'
    # filename = 'sub/menu01/menu01_01.html'
    print(filename)
    return render(request, filename, {'menucode1': menucode1, 'menucode2': menucode2})


def submit_question(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            form.save()
            print('데이터 통신 성공')
        else:
            raise ValidationError('관리자에게 문의 바랍니다.')

    return render(request, 'sub/menu01/menu01_06.html')


def amdin_noticewrite_page(request):
    context = {}
    context['block'] = ''
    return render(request, 'admins/notice/notice_write.html')


def admin_notice_write(request):
    if request.method == 'POST':
        formdata = request.POST
        title = formdata.get('title')
        content = formdata.get('content')
        fixed_flag = formdata.get('fixed_flag')
        files = request.FILES.getlist('file')
        created_by_id = request.COOKIES.get('user_id')

        if fixed_flag == 'true':
            fixed_flag = True
        else:
            fixed_flag = False

        board_instance = BoardMaster.objects.create(
            title=title, content=content, boardcode=CodeMaster.objects.get(code='3'), fixed_flag=fixed_flag,
            file_flag=bool(files), created_by_id=created_by_id
        )

        if files:
            for file in files:
                file_path = os.path.join(settings.MEDIA_ROOT, file.name)

                with open(file_path, 'wb') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)

                FileBoardMaster.objects.create(
                    parent=board_instance, file_path=file_path, created_by_id=created_by_id
                )

    else:
        raise ValidationError('관리자에게 문의 바랍니다.')

    return render(request, 'admins/index.html')
