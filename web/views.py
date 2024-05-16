from datetime import date, datetime, timedelta
from django.contrib.auth.hashers import make_password
from django.db import models
from django.db.models import Count, Q, Case, When, IntegerField, F, Func, CharField, Value, BooleanField
from django.db.models.functions import TruncDate, Floor
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework.exceptions import ValidationError
from api.form import QuestionForm
from api.models import UserMaster, BoardMaster, FileBoardMaster, CodeMaster, GroupCodeMaster, EventMaster, ProMaster, \
    ProTask, ProMembers, Weekly
from api.views import *


class DateDiff(Func):
    function = 'DATEDIFF'
    template = "%(function)s(%(expressions)s)"
    output_field = IntegerField()


class MondayDate(Func):
    function = 'DATE_ADD'
    template = "%(function)s(%(expressions)s, INTERVAL -WEEKDAY(%(expressions)s) DAY)"


class FridayDate(Func):
    function = 'DATE_ADD'
    template = "%(function)s(%(expressions)s, INTERVAL (4-WEEKDAY(%(expressions)s)) DAY)"


def index(request):
    return render(request, 'index.html', {})


def admin_index_page(request):
    today = timezone.now()

    events = EventMaster.objects.select_related('vehicle').prefetch_related('participant_set').filter(
        start_date__lte=today, end_date__gte=today, event_type__in=["Business", "Holiday"], delete_flag="N")

    # 공지사항
    fixed_notice = BoardMaster.objects.filter(boardcode_id=9, delete_flag="N").annotate(
        is_fixed=Case(
            When(fixed_flag=True, then=Value(True)),
            default=Value(False),
            output_field=BooleanField()
        ),
        reply_count=Count('reply_board')
    ).order_by('-is_fixed', '-id')[:4]

    # fixed_notice = next((n for n in notices if n.fixed_flag), None)
    # notice = [n for n in notices if not n.fixed_flag][:3]

    # 전사게시판
    fixed_board = BoardMaster.objects.filter(boardcode__code="RSA", delete_flag="N").annotate(
        is_fixed=Case(
            When(fixed_flag=True, then=Value(True)),
            default=Value(False),
            output_field=BooleanField()
        ),
        reply_count=Count('reply_board')
    ).order_by('-is_fixed', '-id')[:4]
    print('fixed_board', fixed_board)

    # fixed_board = next((b for b in boards if b.fixed_flag), None)
    # board = [b for b in boards if not b.fixed_flag][:3]

    # 오늘의 이야기
    today_about = BoardMaster.objects.filter(boardcode__code="G02", delete_flag='N').last()

    type = request.GET.get('param', None)
    employee_list = get_member_info(type)

    context = {
        'events': events,
        'fixed_notice': fixed_notice,
        'fixed_board': fixed_board,
        'employee_list': employee_list['result'],
        'today_about': today_about
    }

    return render(request, 'admins/index.html', context)


def calendar_page(request):
    today = timezone.now()

    events = EventMaster.objects.select_related('vehicle').prefetch_related('participant_set', ).filter(
        start_date__lte=today, end_date__gte=today, event_type__in=["Business", "Holiday"], delete_flag="N")

    type = request.GET.get('param', None)
    employee_list = get_member_info(type)

    context = {
        'events': events,
        'employee_list': employee_list['result']
    }

    return render(request, 'admins/index_calendar.html', context)


def check_vehicle_availability(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    # print('sta', start_date)
    # print('end', end_date)
    vehicle_list = []
    for vehicle in CodeMaster.objects.filter(code__in=["CQM3", "CSPO", "CETC"]):
        if vehicle.code == "CETC":
            is_available = True
        else:
            is_available = not EventMaster.objects.filter(  # 참이면 is_available을 true로 변경 후 리스트에 들어감
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
    print(request.POST)

    email = request.POST.get('email')
    allowed_domains = ['seoul-soft.com', 'solic.kr']
    # 도메인 추출
    email_domain = email.split('@')[-1]
    if email_domain not in allowed_domains:
        return JsonResponse(
            {"success": False, "errors": "해당 도메인으로 가입할 수 없습니다. @seoul-soft.com 또는 @solic.kr 도메인을 사용해주세요."}, status=400)

    password = request.POST.get('password')
    clean_password = make_password(password)

    useremailreceive = request.POST.get('useremailreceive') == 'on'

    userMaster = UserMaster(
        password=clean_password,
        last_login=timezone.now(),
        username=request.POST.get('username'),
        user_id=request.POST.get('user_id'),
        email=email,
        useremailreceive=useremailreceive,
        userintro=request.POST.get('userintro')
    )

    userMaster.save()

    return JsonResponse({"success": 'true', "message": "회원가입이 완료되었습니다."}, status=200)


@csrf_exempt
def check_duplicate(request):
    if request.method == "GET":
        user_id = request.GET.get("user_id", None)

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


# def cost_page(request):
#
#     return render(request,'sub/menu01/me')


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
        is_staff=True, department_position_id__isnull=False
    ).prefetch_related('job_position').order_by(
        F('department_position_id').asc(nulls_last=True),
        F('job_position_id').asc(nulls_last=True),
        F('id').asc(nulls_last=True),
    ).values('id', 'username', 'department_position_id', 'job_position__explain')
    context = {
        'departs': depart,
        'users': users
    }

    return render(request, 'admins/organization.html', context)


def get_project_data(userid):
    project_data = ProMaster.objects.filter(delete_flag='N') \
        .select_related('pj_master', 'pj_type') \
        .values('id', 'pjcode', 'pjname', 'start_date', 'end_date', 'pj_customer', 'pj_note',
                'pj_master__username', 'pj_type__name', 'created_by_id', 'pj_master_id') \
        .distinct() \
        .filter(Q(pj_master_id=userid) | Q(promaster__member_id=userid))

    formatted_projects = []
    for project in project_data:
        formatted_project = project
        formatted_project['start_date'] = project['start_date'].strftime('%Y-%m-%d')
        formatted_project['end_date'] = project['end_date'].strftime('%Y-%m-%d')
        formatted_projects.append(formatted_project)

    return formatted_projects


def project_main_page(request):
    userid = request.user.id
    userinfo = UserMaster.objects.filter(id=userid).annotate(
        cnt=Count('member__id', filter=models.Q(member__task_id__isnull=True))
    ).select_related('department_position').values(
        'department_position__name', 'cnt', 'id', 'username').first()

    projects = get_project_data(userid)

    userlist = ProMembers.objects.filter(
        task_id__isnull=True, position='PE'
        ).select_related('member').values('id', 'promaster_id', 'member__username')

    project_type_select = CodeMaster.objects.filter(group_id=8).values(
        'id', 'code', 'name'
    )

    context = {'project': projects, 'userinfo': userinfo, 'userlist': userlist, 'project_type_select': project_type_select}

    return render(request, 'admins/project_mgmt/project_main.html', context)


def project_mgmt_page(request):
    context = {}
    return render(request, 'admins/project_mgmt/project_mgmt.html', context)


def task_mgmt_page(request):
    pro = request.GET.get('param', None)
    project_name = None
    task = None
    formatted_projects = []
    if pro:
        task = ProTask.objects.filter(pro_parent=pro, delete_flag="N").annotate(
            task_remain=Floor(DateDiff(F('task_end'), datetime.now().date()))
        ).select_related(
            'pro_parent'
        ).values(
            'id', 'task_name', 'task_start', 'task_end', 'pro_parent_id', 'task_remain', 'pro_parent__pjcode', 'pro_parent__pjname'
        ).order_by('-id')

        for task in task:
            formatted_project = task
            formatted_project['task_start'] = task['task_start'].strftime('%Y-%m-%d')
            formatted_project['task_end'] = task['task_end'].strftime('%Y-%m-%d')
            formatted_projects.append(formatted_project)

        #project_name = task.first()['pro_parent__pjname']
        project_name = get_object_or_404(ProMaster, pk=pro, delete_flag='N')

    userlist = ProMembers.objects.filter(
        promaster_id=pro,
        task_id__isnull=False
    ).select_related('member').values(
        'id',
        'position',
        'task_id',
        'member__username'
    )

    userid = request.user.id
    project = get_project_data(userid)

    context = {
        'task': formatted_projects,
        'userlist': userlist,
        'pjname': project_name,
        'projectlist': project
    }

    return render(request, 'admins/project_mgmt/task_mgmt.html', context)


def weekly_report_main_page(request):  # 주간업무보고 PE
    userid = request.user.id
    type = request.GET.get('param', None)
    projects = get_project_data(userid)

    weekly_list = Weekly.objects.all().annotate(
        monday_date=MondayDate('create_at', output_field=CharField()),
        friday_date=FridayDate('create_at', output_field=CharField())
    ).values(
        'id', 'week_cnt', 'week_name', 'report_flag', 'create_at', 'owner', 'monday_date', 'friday_date'
    ).order_by('-id')

    pro_types = CodeMaster.objects.filter(group__code="WTYPE")
    pm_list = UserMaster.objects.filter(report_auth="M")

    context = {
        'is_pe_page': True,
        'projects': projects,
        'weekly_list': weekly_list,
        'pro_type': pro_types,
        'pm_list': pm_list
    }

    return render(request, 'admins/weekly_report/weekly_report_pe.html', context)


def weekly_report_mgmt_page(request):  # 주간업무보고 PM
    userid = request.user.id
    type = request.GET.get('param', None)
    projects = get_project_data(userid)

    weekly_list = Weekly.objects.all().annotate(
        monday_date=MondayDate('create_at', output_field=CharField()),
        friday_date=FridayDate('create_at', output_field=CharField())
    ).values(
        'id', 'week_cnt', 'week_name', 'report_flag', 'create_at', 'owner', 'monday_date', 'friday_date'
    ).order_by('-id')

    pro_types = CodeMaster.objects.filter(group__code="WTYPE")

    context = {
        'is_pe_page': False,
        'projects': projects,
        'weekly_list': weekly_list,
        'pro_type': pro_types,
    }
    return render(request, 'admins/weekly_report/weekly_report_pm.html', context)


def weekly_report_ceo_page(request):  # 주간업무보고 CEO
    current_year = datetime.now().year
    year_range = range(current_year - 10, current_year + 11)

    pm_list = UserMaster.objects.filter(report_auth="M", is_staff=True)
    weekly_list = Weekly.objects.all()

    context = {
        'current_year': current_year,
        'year_range': year_range,
        'weekly_list': weekly_list,
        'pm_list': pm_list,
    }
    return render(request, 'admins/weekly_report/weekly_report_ceo.html', context)


def holiday_info_page(request):
    qs = CodeMaster.objects.filter(group_id=6)

    context = {
        'holiday': qs
    }

    return render(request, 'admins/holiday/holiday_info.html', context)


def user_authority_page(request):
    context = {}
    return render(request, 'admins/administrator/user_authority/user_authority.html', context)


def test_form(request):
    context = {}
    return render(request, 'admins/administrator/test_form.html', context)

