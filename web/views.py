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
    ProTask, ProMembers, Weekly, ApvMaster
from api.views import *
from api.approval import *
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.conf.urls import handler403
from django.contrib import messages
import requests


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


def term_page(request):
    return render(request, 'term.html', {})


def admin_index_page(request):
    today = timezone.now()

    events = EventMaster.objects.select_related('vehicle').prefetch_related('participant_set').filter(
        start_date__lte=today, end_date__gte=today, event_type__in=["Business", "Holiday"], delete_flag="N")

    # 공지사항
    fixed_notice = BoardMaster.objects.filter(boardcode_id=9, delete_flag="N").order_by('-id')[:4]

    # 전사게시판
    fixed_board = BoardMaster.objects.filter(boardcode__code="RSA", delete_flag="N").order_by('-id')[:4]

    # 오늘의 이야기
    today_about = BoardMaster.objects.filter(boardcode__code="G02", delete_flag='N').last()

    # 나의 결재
    # user_id = request.COOKIES["user_id"]
    user = get_object_or_404(UserMaster, id=request.user.id)
    qs = ApvMaster.objects.filter()

    # 사용자의 권한에 따라 필터링
    if user.is_authenticated:
        if user.is_superuser:  # 슈퍼유저는 모든 게시물 조회 가능
            pass

        else:
            # 임시 상태의 문서를 해당 사용자만 볼 수 있도록 필터링, 삭제 상태의 문서를 목록에서 제외
            qs = qs.filter(
                Q(created_by=user) |
                ~Q(apv_status='임시')
            ).exclude(apv_status='삭제')

            # 사용자가 생성한 게시물, cc_list에 포함된 게시물, 승인자로 포함된 게시물만 필터링
            qs = qs.filter(
                Q(created_by=user) |
                Q(apv_docs_cc__user=user) |
                Q(apv_docs_approvers__approver1=user) |
                Q(apv_docs_approvers__approver2=user) |
                Q(apv_docs_approvers__approver3=user) |
                Q(apv_docs_approvers__approver4=user) |
                Q(apv_docs_approvers__approver5=user) |
                Q(apv_docs_approvers__approver6=user)
            ).distinct()

    else:  # 인증되지 않은 사용자는 아무 게시물도 조회할 수 없음
        qs = qs.none()

    waiting_docs = qs.filter(
        id__in=[apv.id for apv in qs if ApvDetail.get_next_approver(apv) == user]).count()

    read_status = ApvReadStatus.objects.filter(user=user).values_list('document_id', flat=True)
    read_documents = set(read_status)
    unread_docs = qs.exclude(id__in=read_documents).count()

    type = request.GET.get('param', None)
    employee_list = get_member_info(type)

    context = {
        'events': events,
        'fixed_notice': fixed_notice,
        'fixed_board': fixed_board,
        'employee_list': employee_list['result'],
        'today_about': today_about,
        'waiting_docs': waiting_docs,
        'unread_docs': unread_docs,
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
    # filename = 'sub/menu01/menu01_01.html' 서비스 - MES (리뉴얼)
    # filename = 'sub/menu01/menu01_02.html' 서비스 - MMS (리뉴얼)
    # filename = 'sub/menu01/menu01_03.html' 서비스 - IBT (리뉴얼)
    # filename = 'sub/menu01/menu01_06.html' 문의하기 (리뉴얼)
    # filename = 'sub/menu01/menu01_07.html' 기업정보 ESG경영 (리뉴얼)
    # filename = 'sub/menu01/menu01_08.html' 기업정보 사업영역 (리뉴얼)
    # filename = 'sub/menu01/menu01_09.html' 스토리 (리뉴얼)

    return render(request, filename, {'menucode1': menucode1, 'menucode2': menucode2})


# def submit_question(request):
#     if request.method == 'POST':
#         form = QuestionForm(request.POST)
#         if form.is_valid():
#             form.save()
#         else:
#             raise ValidationError('관리자에게 문의 바랍니다.')
#
#     return render(request, 'sub/menu01/menu01_06.html')


def submit_question(request):
    if request.method == 'POST':
        recaptcha_response = request.POST.get('g-recaptcha-response')
        secret_key = '6Lcz9v0pAAAAALzPy5BXnUQ5BalsNZQFL9rNB6nB'
        data = {
            'secret': secret_key,
            'response': recaptcha_response
        }
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result = r.json()

        if result['success']:
            # reCAPTCHA 검증 성공
            form = QuestionForm(request.POST)
            if form.is_valid():
                form.save()
                return render(request, 'sub/menu01/menu01_06.html')
            else:
                return HttpResponse('이용자 검증 실패. 관리자에게 문의 바랍니다.')
        else:
            # reCAPTCHA 검증 실패
            return HttpResponse('reCAPTCHA verification failed. Please try again.')

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

    context = {'project': projects, 'userinfo': userinfo, 'userlist': userlist,
               'project_type_select': project_type_select}

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
            'id', 'task_name', 'task_start', 'task_end', 'pro_parent_id', 'task_remain', 'pro_parent__pjcode',
            'pro_parent__pjname'
        ).order_by('-id')

        for task in task:
            formatted_project = task
            formatted_project['task_start'] = task['task_start'].strftime('%Y-%m-%d')
            formatted_project['task_end'] = task['task_end'].strftime('%Y-%m-%d')
            formatted_projects.append(formatted_project)

        # project_name = task.first()['pro_parent__pjname']
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


# def test_form(request):
#     context = {}
#     return render(request, 'admins/administrator/test_form.html', context)


def check_story_admin(user):
    if user.story_admin:
        return True
    raise PermissionDenied("접근 권한이 없습니다.")


@login_required
@user_passes_test(check_story_admin)
def story_create_page(request):
    context = {}
    return render(request, 'story/story_create.html', context)


def permission_denied_view(request, exception):
    return render(request, 'story/story_403.html', status=403)


handler403 = permission_denied_view


def apv_list(request):
    context = {}
    return render(request, 'approval/apv_list.html', context)


def apv_temp_update(request, document_id):
    context = {
        'document_id': document_id
    }
    return render(request, 'approval/apv_temp_update.html', context)


def apv_progress(request, document_id):
    context = {
        'document_id': document_id
    }
    return render(request, 'approval/apv_progress.html', context)


def apv_template_view(request, category_no):
    # user_id = request.COOKIES["user_id"]
    user = get_object_or_404(UserMaster, id=request.user.id)
    approver_list = (UserMaster.objects.filter(is_staff='1').exclude(id__in=[1, 2, 1111, user.id])
                     .order_by('department_position', 'username'))
    approver_choices = [(approver.department_position, approver.username, approver.id) for approver in approver_list]

    leave_choices = ApvMaster.LEAVE_CHOICES
    create_template = 'approval/template_' + category_no + '_create.html'
    context = {
        'category_no': category_no,
        'leave_choices': leave_choices,
        'approver_list': approver_choices,
    }
    return render(request, create_template, context)


def apv_template_detail(request, category_no):
    approver_list = (UserMaster.objects.filter(is_staff='1').exclude(id__in=[1, 2, 1111])
                     .order_by('department_position', 'username'))
    approver_choices = [(approver.department_position, approver.username, approver.id) for approver in approver_list]

    leave_choices = ApvMaster.LEAVE_CHOICES
    detail_template = 'approval/template_' + category_no + '_detail.html'
    context = {
        'category_no': category_no,
        'leave_choices': leave_choices,
        'approver_list': approver_choices,
    }
    return render(request, detail_template, context)
