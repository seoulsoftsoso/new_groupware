from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta, SU
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.functions import TruncDate
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView
from django.db.models import Sum, Value, OuterRef, Subquery, Prefetch
from django.db.models.expressions import RawSQL, Exists
from api.attendance.common import DayOfTheWeek, cal_workTime_holiday, cal_workTime, cal_earlyleaveTime, cal_extendTime, \
    cal_workTime_check, PaginatorManager
from api.models import Attendance, CodeMaster, UserMaster, EventMaster


def last_attendance(request):
    user_id = request.GET.get('user_id')
    end_date = datetime.now().replace(microsecond=0)
    start_date = (end_date + relativedelta(weekday=SU(-1))).replace(hour=0, minute=0, second=0, microsecond=0)
    next_sunday = (end_date + relativedelta(weekday=SU(+1))).replace(hour=0, minute=0, second=0, microsecond=0)
    # print('endDate : ', end_date)
    # print('startDate : ', start_date)
    # print('nextSunday : ', next_sunday)

    if user_id is None:
        return JsonResponse({'error': 'user_id is required'}, status=400)

    try:
        attendance = Attendance.objects.filter(employee_id=user_id)
        # 일일 초기화 로직
        last_attendance = attendance.latest('date')
        if last_attendance.is_offwork == False and (last_attendance.date < date.today()):  # 이전 출근날 퇴근을 하지 않은 경우
            last_attendance.offwork_ip = last_attendance.attendance_ip
            if last_attendance.date + timedelta(days=1) == date.today():  # 출근이 전날인 경우 days=1 : 시간간격
                init_time = datetime.now().time().replace(hour=6, minute=0, second=0, microsecond=0)
                if datetime.now().time() < init_time:  # 오전 6시 이전
                    last_attendance.offworkTime = datetime.now().replace(second=0, microsecond=0)
                    CalculationDayAttendance(last_attendance)
                    cal_workTime_check(last_attendance)
                    last_attendance.save()
                else:
                    last_attendance.is_offwork = True
                    t_time = last_attendance.date.strftime('%Y-%m-%d') + ' 18:30:00'
                    last_attendance.offworkTime = datetime.strptime(t_time, '%Y-%m-%d %H:%M:%S')
                    CalculationDayAttendance(last_attendance)
                    cal_workTime_check(last_attendance)
                    last_attendance.save()
            else:
                last_attendance.is_offwork = True
                t_time = last_attendance.date.strftime('%Y-%m-%d') + ' 18:30:00'
                last_attendance.offworkTime = datetime.strptime(t_time, '%Y-%m-%d %H:%M:%S')
                CalculationDayAttendance(last_attendance)
                cal_workTime_check(last_attendance)
                last_attendance.save()

        # 주간 근무 시간 계산 로직
        weekly_work_time = attendance.filter(
            date__range=[start_date, end_date]
        ).annotate(
            workTime_in_seconds=RawSQL("TIME_TO_SEC(workTime)", [])
        ).aggregate(
            weekly_work_time=Sum('workTime_in_seconds')
        )['weekly_work_time']
        last_attendance.weekly_work_time = weekly_work_time

        # print('attendance: ', last_attendance)
        # print('weekly_work_time: ', last_attendance.weekly_work_time)

    except ObjectDoesNotExist:
        return JsonResponse({'error': 'No attendance record for the user'}, status=404)

    if last_attendance is not None:
        # 일요일 누적 시간 초기화
        if next_sunday.date() == end_date.date():
            last_attendance.weekly_work_time = 0

        return JsonResponse({
            'is_offwork': last_attendance.is_offwork,
            'attendanceTime': last_attendance.attendanceTime.strftime("%H:%M:%S"),
            'date': last_attendance.date,
            'weeklyWorkTime': last_attendance.weekly_work_time if last_attendance.weekly_work_time is not None else 0,
            'endDate': end_date,
            'startDate': start_date,
        })
    else:
        return JsonResponse({'error': 'No attendance record for the user'}, status=404)


def CalculationDayAttendance(last_attendance):
    if DayOfTheWeek(last_attendance.date.year, last_attendance.date.month, last_attendance.date.day) >= 5:
        last_attendance.earlyleaveTime = None
        last_attendance.extendTime = None
        last_attendance.workTime = cal_workTime_holiday(last_attendance)
        last_attendance.workTime_holiday = cal_workTime_holiday(last_attendance)
    else:
        last_attendance.workTime = cal_workTime(last_attendance)
        last_attendance.earlyleaveTime = cal_earlyleaveTime(last_attendance)
        last_attendance.extendTime = cal_extendTime(last_attendance)
        last_attendance.workTime_holiday = None
    return last_attendance


@csrf_exempt
def check_in(request):
    if request.method == "POST":
        print(request.POST)
        user_id = request.COOKIES.get('user_id')
        user = UserMaster.objects.get(id=user_id)
        department_id = user.department_position.id
        jobposition_id = user.job_position.id

        data = request.POST
        attendance_ip = data.get('ip')

        current_date = datetime.now().date()
        current_time = datetime.now().time().replace(microsecond=0)

        # 지각시간
        latenessTime = None
        if current_time.hour >= 10 and current_time.minute >= 1:
            latenessTime = current_time

        Attendance.objects.create(
            date=current_date,
            attendanceTime=current_time,
            latenessTime=latenessTime,
            employee_id=user_id,
            attendance_ip=attendance_ip,
            department_id=department_id,
            jobTitle_id=jobposition_id,
            create_by_id=user_id,
            updated_by_id=user_id
        )

        return HttpResponse()


def check_out(request):
    if request.method == "POST":
        user_id = request.COOKIES.get('user_id')
        last_attendance = Attendance.objects.filter(employee_id=user_id).order_by('-date', '-attendanceTime').first()

        if last_attendance.date == datetime.today().date():  # 오늘 날짜랑 마지막 출근일이랑 같은 경우
            last_attendance.offwork_ip = request.POST['offwork_ip']
            last_attendance.offworkTime = datetime.now().replace(second=0, microsecond=0)
            last_attendance.is_offwork = True
            CalculationDayAttendance(last_attendance)
            cal_workTime_check(last_attendance)
            last_attendance.save()

    return HttpResponse()


class admin_work_schedule_page(ListView):
    template_name = 'admins/attendance/work_schedule.html'

    def get_queryset(self):
        search_title = self.request.GET.get('search-title', None)
        search_content = self.request.GET.get('search-content', None)
        search_to = self.request.GET.get('search-to', None)
        search_from = self.request.GET.get('search-from', None)
        attendance_queryset = Attendance.objects.all().order_by('-date', 'employee__username')

        if search_to != "" and search_to != None:
            attendance_queryset = attendance_queryset.filter(date__gte=search_to)
        if search_from != "" and search_from != None:
            attendance_queryset = attendance_queryset.filter(date__lte=search_from)

        if search_title == 'name' or search_title == None:
            if search_content is not None and search_content != "":
                attendance_queryset = attendance_queryset.filter(employee__username__contains=str(search_content))
        elif search_title == 'number':
            if search_content is not None and search_content != "":
                attendance_queryset = attendance_queryset.filter(
                    employee__employee_number__contains=str(search_content))
        elif search_title == 'department':
            if search_content is not None and search_content != "":
                try:
                    department_id = CodeMaster.objects.get(department__contains=str(search_content)).id
                    attendance_queryset = attendance_queryset.filter(department_id=department_id)
                except ObjectDoesNotExist:
                    print("존재하지 않는 부서를 검색!")
                    return None

        return attendance_queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(admin_work_schedule_page, self).get_context_data(**kwargs)
        context['USER'] = self.request.user.id
        # paging
        context['page_range'], context['contacts'] = PaginatorManager(self.request, self.get_queryset())

        print('context : ', context)

        return context


class MonthAttendanceListView(ListView):
    template_name = 'admins/attendance/month_work_schedule.html'

    def get_queryset(self):
        search_title = self.request.GET.get('search-title', None)
        search_content = self.request.GET.get('search-content', None)
        attendance_queryset = Attendance.objects.all()
        standard_year = self.request.GET.get('YEAR', datetime.today().year)
        standard_month = self.request.GET.get('MONTH', datetime.today().month)

        if search_title == 'name' or search_title == None:
            if search_content is not None and search_content != "":
                attendance_queryset = attendance_queryset.filter(employee__username__contains=str(search_content))
        elif search_title == 'number':
            if search_content is not None and search_content != "":
                attendance_queryset = attendance_queryset.filter(
                    employee__employee_number__contains=str(search_content))
        elif search_title == 'department':
            if search_content is not None and search_content != "":
                try:
                    department_id = CodeMaster.objects.get(department__contains=str(search_content)).id
                    attendance_queryset = attendance_queryset.filter(department_id=department_id)
                except ObjectDoesNotExist:
                    print("존재하지 않는 부서를 검색!")
                    return None

        if standard_month == '-1':
            attendance_queryset = attendance_queryset.filter(date__year=int(standard_year)).all().order_by('-date')
        else:
            attendance_queryset = attendance_queryset.filter(date__year=int(standard_year),
                                                             date__month=int(standard_month)).all().order_by('-date')
            print('attendance_queryset', attendance_queryset)

        return attendance_queryset

    # def get_vacation(self):
    #     search_title = self.request.GET.get('search-title', None)
    #     search_content = self.request.GET.get('search-content', None)
    #     standard_year = self.request.GET.get('YEAR', datetime.today().year)
    #     standard_month = self.request.GET.get('MONTH', datetime.today().month)
    #     vacation_queryset = Vacation.objects.all()

    # if search_title == 'name' or search_title == None:
    #     if search_content is not None and search_content != "":
    #         vacation_queryset = vacation_queryset.filter(employee__name__contains=str(search_content))
    # elif search_title == 'number':
    #     if search_content is not None and search_content != "":
    #         vacation_queryset = vacation_queryset.filter(employee__employee_number__contains=str(search_content))
    # elif search_title == 'department':
    #     if search_content is not None and search_content != "":
    #         try:
    #             department_id = CodeMaster.objects.get(department__contains=str(search_content)).id
    #             # vacation_queryset = vacation_queryset.filter(department_id=department_id)
    #         except ObjectDoesNotExist:
    #             print("존재하지 않는 부서를 검색!")
    #             return None

    # if standard_month == '-1':
    #     vacation_queryset = vacation_queryset.filter(startDate__year=int(standard_year),
    #                                                  is_approval=True).all().order_by(
    #         '-startDate')
    # else:
    #     vacation_queryset = vacation_queryset.filter(startDate__year=int(standard_year),
    #                                                  startDate__month=int(standard_month),
    #                                                  is_approval=True).all().order_by('-startDate')
    # return vacation_queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(MonthAttendanceListView, self).get_context_data(**kwargs)
        context['contacts'] = self.get_queryset()
        # context['vacation_inquiry'] = self.get_vacation()
        context['standard_year'] = self.request.GET.get('YEAR', datetime.today().year)
        context['standard_month'] = self.request.GET.get('MONTH', datetime.today().month)
        context['search_title'] = self.request.GET.get('search-title', None)
        context['search_content'] = self.request.GET.get('search-content', None)

        return context


class work_history_search(ListView):
    template_name = 'admins/attendance/workHistory_search.html'

    def get(self, request, *args, **kwargs):
        self.today = timezone.now().date()
        self.search_to = self.request.GET.get('search-to', self.today)
        print('오늘 ', self.today)
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        search_to = self.request.GET.get('search-to', None)
        date_to_search = search_to if (search_to != "" and search_to is not None) else self.today
        print('date_to_search : ', date_to_search)

        attendance_prefetch = Prefetch('attend_user', queryset=Attendance.objects.filter(date=date_to_search).order_by('-date'), to_attr='attendance_rec')
        event_prefetch = Prefetch('event_creat', queryset=EventMaster.objects.annotate(truncated_date=TruncDate('create_at')).filter(truncated_date=date_to_search).order_by('-create_at'), to_attr='events')
        attendance_queryset = UserMaster.objects.select_related('department_position').prefetch_related(event_prefetch, attendance_prefetch).filter(is_active=True, is_staff=True, is_superuser=False).order_by('job_position_id', 'id')

        # for user in attendance_queryset:
        #     if user.attendance_rec:
        #         attendance_rec = user.attendance_rec[0]
        #     else:
        #         attendance_rec = None
        #
        #     print(
        #         attendance_rec.date if attendance_rec else 'N/A',
        #         user.username,
        #         attendance_rec.attendanceTime if attendance_rec else 'N/A',
        #         attendance_rec.is_offwork if attendance_rec else 'N/A',
        #     )
        #
        # for user in attendance_queryset:
        #     if user.event_creat and user.events:
        #         events = user.events[0]
        #     else:
        #         events = None
        #
        #     print(
        #         user.username,
        #         events.event_type if events else 'N/A',
        #     )

        return attendance_queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['today'] = self.today
        context['search_to'] = self.search_to
        context['attendance_queryset'] = context['object_list']
        context['codemaster'] = CodeMaster.objects.filter(group_id=1)
        context['eventmaster'] = EventMaster.objects.all()
        return context

