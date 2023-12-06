from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from api.models import Attendance, CodeMaster


def check_in(request):
    if request.method == "POST":
        # 나중에 코드마스터 보고 변경해야 함
        codemaster = CodeMaster.objects.all()

        user = request.user
        current_date = timezone.now().date()
        current_time = timezone.now().time()

        attendance = Attendance.objects.create(
            date=current_date,
            attendanceTime=current_time,
        )

        # 근무 시간 계산
        if attendance.attendanceTime:
            # 출근 시간이 기록되어 있을 때만 근무 시간 계산
            work_duration = timezone.now() - timezone.datetime.combine(current_date, attendance.attendanceTime)
            attendance.workTime = work_duration



        context = {
            'attendance': attendance,
        }

        return JsonResponse(context)


def check_out(request):
    print('퇴근')
    return
