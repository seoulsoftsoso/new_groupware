import json
from datetime import datetime, timedelta, date

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views.generic import ListView

from api.attendance.common import DayOfTheWeek, cal_workTime_holiday, cal_workTime, cal_earlyleaveTime, cal_extendTime, cal_workTime_check, PaginatorManager
from api.models import Attendance, CodeMaster, UserMaster


def last_attendance(request):
    user_id = request.GET.get('user_id')

    if user_id is None:
        return JsonResponse({'error': 'user_id is required'}, status=400)
    try:
        attendance = Attendance.objects.filter(employee_id=user_id).order_by('-date', '-attendanceTime').first()
        print('attendance : ', attendance)
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'No attendance record for the user'}, status=404)

    if attendance is not None:
        return JsonResponse({'is_offwork': attendance.is_offwork})
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


def check_in(request):
    if request.method == "POST":
        user_id = request.COOKIES.get('user_id')
        user = UserMaster.objects.get(id=user_id)
        department_id = user.department_position.id
        jobposition_id = user.job_position.id

        data = request.POST
        attendance_ip = data.get('ip')

        current_date = datetime.now().date()
        current_time = datetime.now().time().replace(second=0, microsecond=0)

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
        print('기록', last_attendance)

        if last_attendance.date == datetime.today().date():  # 오늘 날짜랑 마지막 출근일이랑 같은 경우
            last_attendance.offwork_ip = request.POST['offwork_ip']
            last_attendance.offworkTime = datetime.now().replace(second=0, microsecond=0)
            last_attendance.is_offwork = True
            CalculationDayAttendance(last_attendance)
            cal_workTime_check(last_attendance)
            last_attendance.save()
            response = {'status': 1, 'message': '퇴근이 완료 되었습니다.'}

        elif last_attendance.offwork_ip == None and (last_attendance.date < date.today()):  # 이전 출근날 퇴근을 하지 않은 경우
            last_attendance.offwork_ip = last_attendance.attendance_ip
            if last_attendance.date + timedelta(days=1) == date.today():  # 출근이 전날인 경우
                init_time = datetime.now().time().replace(hour=6, minute=0, second=0, microsecond=0)
                if datetime.now().time() < init_time:  # 오전 6시 이전
                    last_attendance.offworkTime = datetime.now().replace(second=0, microsecond=0)
                    CalculationDayAttendance(last_attendance)
                    cal_workTime_check(last_attendance)
                    last_attendance.save()
                else:
                    last_attendance.is_offwork = 1
                    t_time = last_attendance.date.strftime('%Y-%m-%d') + ' 18:30:00'
                    last_attendance.offworkTime = datetime.strptime(t_time, '%Y-%m-%d %H:%M:%S')
                    CalculationDayAttendance(last_attendance)
                    cal_workTime_check(last_attendance)
                    last_attendance.save()
            else:
                t_time = last_attendance.date.strftime('%Y-%m-%d') + ' 18:30:00'
                last_attendance.offworkTime = datetime.strptime(t_time, '%Y-%m-%d %H:%M:%S')
                CalculationDayAttendance(last_attendance)
                cal_workTime_check(last_attendance)
                last_attendance.save()

            response = {'status': 1, 'message': '퇴근이 완료 되었습니다.'}

        response = {'status': 1, 'message': '퇴근이 완료 되었습니다.'}

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
        context['search_title'] = self.request.GET.get('search-title', "")
        context['search_content'] = search_content = self.request.GET.get('search-content', "")
        context['search_to'] = self.request.GET.get('search-to', "")
        context['search_from'] = self.request.GET.get('search-from', "")
        # paging
        context['page_range'], context['contacts'] = PaginatorManager(self.request, self.get_queryset())

        return context