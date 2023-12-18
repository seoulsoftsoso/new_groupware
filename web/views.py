from datetime import date

from django.contrib import auth
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from rest_framework.exceptions import ValidationError
from api.form import SignUpForm, QuestionForm
from api.models import UserMaster, BoardMaster, FileBoardMaster, CodeMaster, GroupCodeMaster, EventMaster


def index(request):
    return render(request, 'index.html', {})


def admin_index_page(request):
    today = date.today()

    event_holiday = EventMaster.objects.annotate(start_date_date=TruncDate('start_date')).filter(delete_flag="N", start_date_date=today, event_type="Holiday")
    event_business = EventMaster.objects.annotate(start_date_date=TruncDate('start_date')).filter(delete_flag="N", start_date_date=today, event_type="Business")
    event_qm3 = EventMaster.objects.annotate(start_date_date=TruncDate('start_date')).filter(delete_flag="N", start_date_date=today, event_type="ETC")
    event_spo = EventMaster.objects.annotate(start_date_date=TruncDate('start_date')).filter(delete_flag="N", start_date_date=today, event_type="Spotage")
    fixed_notice = BoardMaster.objects.filter(fixed_flag=True, delete_flag="N", boardcode_id=9).annotate(
        reply_count=Count('reply_board')).order_by("-updated_at").first()
    notice = BoardMaster.objects.filter(delete_flag="N", boardcode_id=9, fixed_flag=False).annotate(
        reply_count=Count('reply_board')).order_by("-updated_at")[:3]
    fixed_board = BoardMaster.objects.filter(boardcode__code="RSA", delete_flag="N", fixed_flag=True).annotate(
        reply_count=Count('reply_board')).order_by("-updated_at").first()
    board = BoardMaster.objects.filter(boardcode__code="RSA", delete_flag="N").annotate(
        reply_count=Count('reply_board')).order_by("-updated_at")[:3]

    context = {
        'event_holiday': event_holiday,
        'event_business': event_business,
        'event_qm3': event_qm3,
        'event_spo': event_spo,
        'fixed_notice': fixed_notice,
        'notice': notice,
        'fixed_board': fixed_board,
        'board': board
    }

    return render(request, 'admins/index.html', context)


def admin_boardwrite_page(request):
    codemaster = CodeMaster.objects.filter(group=3).exclude(code__in=['NOTICE', 'ASK'])

    context = {
        'codemaster': codemaster
    }
    return render(request, 'admins/board/board_write.html', context)


def login_page(request):
    return render(request, 'login.html', {})


def signup_page(request):
    return render(request, 'registration/signup.html', {})


def UserCreate(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)  # UserCreationForm 객체를 생성하도록 수정
        if form.is_valid():
            form.save()
        else:
            raise ValidationError('관리자에게 문의 바랍니다.')

    return render(request, 'index.html')


@csrf_exempt
def check_duplicate(request):
    if request.method == "POST":
        user_id = request.POST.get("user_id", None)

        id_check = UserMaster.objects.filter(user_id=user_id).count()

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
    return render(request, filename, {'menucode1': menucode1, 'menucode2': menucode2})


def submit_question(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            form.save()
        else:
            raise ValidationError('관리자에게 문의 바랍니다.')

    return render(request, 'sub/menu01/menu01_06.html')


def amdin_noticewrite_page(request):
    context = {}
    context['block'] = ''
    return render(request, 'admins/notice/notice_write.html')


def admin_noticeEdit_page(request, notice_id):
    notice = get_object_or_404(BoardMaster, pk=notice_id)
    files = FileBoardMaster.objects.filter(parent_id=notice_id, delete_flag="N")

    context = {
        'notice': notice,
        'files': files,
    }

    return render(request, 'admins/notice/edit.html', context)


def admin_boardEdit_page(request, board_id):
    board = get_object_or_404(BoardMaster, pk=board_id)
    files = FileBoardMaster.objects.filter(parent_id=board_id, delete_flag="N")
    codemaster = CodeMaster.objects.filter(group=3).exclude(code__in=['NOTICE', 'ASK'])

    context = {
        'board': board,
        'files': files,
        'codemaster': codemaster
    }

    return render(request, 'admins/board/edit.html', context)