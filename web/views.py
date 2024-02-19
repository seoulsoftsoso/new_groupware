from datetime import date
from django.db.models import Count, Q, Case, When, IntegerField, F
from django.db.models.functions import TruncDate
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework.exceptions import ValidationError
from api.form import SignUpForm, QuestionForm
from api.models import UserMaster, BoardMaster, FileBoardMaster, CodeMaster, GroupCodeMaster, EventMaster
from api.views import *

def index(request):
    return render(request, 'index.html', {})


def admin_index_page(request):
    today = timezone.now()

    events = EventMaster.objects.select_related('vehicle').prefetch_related('participant_set', ).filter(
        start_date__lte=today, end_date__gte=today, event_type__in=["Business", "Holiday"], delete_flag="N")

    fixed_notice = BoardMaster.objects.filter(fixed_flag=True, delete_flag="N", boardcode_id=9).annotate(
        reply_count=Count('reply_board')).order_by("-updated_at").first()
    notice = BoardMaster.objects.filter(delete_flag="N", boardcode_id=9, fixed_flag=False).annotate(
        reply_count=Count('reply_board')).order_by("-updated_at")[:3]
    fixed_board = BoardMaster.objects.filter(boardcode__code="RSA", delete_flag="N", fixed_flag=True).annotate(
        reply_count=Count('reply_board')).order_by("-updated_at").first()
    board = BoardMaster.objects.filter(boardcode__code="RSA", delete_flag="N").annotate(
        reply_count=Count('reply_board')).order_by("-updated_at")[:3]

    context = {
        'events': events,
        'fixed_notice': fixed_notice,
        'notice': notice,
        'fixed_board': fixed_board,
        'board': board
    }

    return render(request, 'admins/index.html', context)


def check_vehicle_availability(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    print('sta', start_date)
    print('end', end_date)
    vehicle_list = []
    for vehicle in CodeMaster.objects.filter(code__in=["CQM3", "CSPO", "CETC"]):
        if vehicle.code == "CETC":
            is_available = True
        else:
            is_available = not EventMaster.objects.filter( # 참이면 is_available을 true로 변경 후 리스트에 들어감
                vehicle=vehicle,
                start_date__lt=end_date,
                end_date__gt=start_date,
                delete_flag='N'
            ).exists()
        vehicle_list.append({
            'code': vehicle.code,
            'name': vehicle.name,
            'is_available': is_available,
        })
    return JsonResponse({'vehicle_list': vehicle_list})


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
        print(request.POST)
        form = SignUpForm(request.POST)  # UserCreationForm 객체를 생성하도록 수정
        if form.is_valid():
            form.save()
        else:
            print(form.errors)
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


def organization_page(request):
    depart = CodeMaster.objects.filter(group_id=1).values('id', 'code', 'name')

    users = UserMaster.objects.filter(
        is_active=True, department_position_id__isnull=False
    ).prefetch_related('job_position').order_by(
        F('department_position_id').asc(nulls_last=True),
        F('job_position_id').asc(nulls_last=True)
    ).values('id', 'username', 'department_position_id', 'job_position__explain')
    context = {
        'departs': depart,
        'users': users
    }

    return render(request, 'admins/organization.html', context)


def project_main_page(request):
    context = {}
    return render(request, 'admins/project_mgmt/project_main.html', context)


def project_mgmt_page(request):
    context = {}
    return render(request, 'admins/project_mgmt/project_mgmt.html', context)


def weekly_report_main_page(request):
    context = {}
    return render(request, 'admins/weekly_report/weekly_report_main.html', context)


def weekly_report_mgmt_page(request):
    context = {}
    return render(request, 'admins/weekly_report/weekly_report_mgmt.html', context)


def holiday_info_page(request):

    qs = CodeMaster.objects.filter(group_id=6)

    context = {
        'holiday': qs
    }

    return render(request, 'admins/holiday/holiday_info.html', context)


def user_authority_page(request):
    context = get_member_info()
    return render(request, 'admins/administrator/user_authority.html', context)


def pay_question_page(request):
    context = {}
    return render(request, 'admins/administrator/pay_question.html', context)


def user_settings_page(request):
    context = {}
    return  render(request, 'admins/administrator/user_setting.html', context)

