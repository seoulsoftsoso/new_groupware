import json
import csv
from django.http import HttpResponse, JsonResponse
from api.models import Attendance, CodeMaster, UserMaster


def excel_download(request):
    if request.method == "POST":
        search_to = request.POST.get('search_to')
        search_from = request.POST.get('search_from')
        search_title = request.POST.get('search_title')
        search_content = request.POST.get('search_content')
        print('search_content', search_from)

        # search_title 필터링
        if search_title == 'name':
            attendance_records = Attendance.objects.filter(employee__username=search_content, date__range=[search_to, search_from])
        elif search_title == 'number':
            attendance_records = Attendance.objects.filter(number=search_content, date__range=[search_to, search_from])
        elif search_title == 'department':
            attendance_records = Attendance.objects.filter(department=search_content, date__range=[search_to, search_from])

        print('attendancec_record : ', attendance_records)

        # CSV 파일 생성
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="attendance.csv"'
        writer = csv.writer(response)
        writer.writerow(['근무일자', '성명', '직급', '부서', '출근시간', '퇴근시간', '근무시간', '연장근로', '지각시간', '조퇴시간', '출근IP', '퇴근IP'])  # 컬럼명을 입력합니다.

        for record in attendance_records:
            writer.writerow([
                record.date,
                record.employee,
                record.jobTitle,
                record.department,
                record.attendanceTime,
                record.offworkTime,
                record.workTime,
                record.extendTime,
                record.latenessTime,
                record.earlyleaveTime,
                record.attendance_ip,
                record.offwork_ip
            ])  # 각 레코드를 입력합니다.

        return response