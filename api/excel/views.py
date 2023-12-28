import io
import csv
from django.http import HttpResponse, JsonResponse
from api.models import Attendance, CodeMaster, UserMaster


def excel_download(request):
    if request.method == "POST":
        search_to = request.POST.get('search_to')
        search_from = request.POST.get('search_from')
        search_title = request.POST.get('search_title')
        search_content = request.POST.get('search_content')
        print('search_content', search_content)

        if search_title == 'name':
            attendance_records = Attendance.objects.filter(employee__username=search_content, date__range=[search_to, search_from])
            if search_content == '':
                attendance_records = Attendance.objects.filter(date__range=[search_to, search_from])

        elif search_title == 'department':
            attendance_records = Attendance.objects.filter(department=search_content, date__range=[search_to, search_from])

        print('attendance_records: ', attendance_records)

        buffer = io.StringIO()
        writer = csv.writer(buffer)

        buffer.write('\ufeff')

        writer.writerow(['근무일자', '성명', '직급', '부서', '출근시간', '퇴근시간', '근무시간', '연장근로', '지각시간', '조퇴시간', '출근IP', '퇴근IP'])

        for record in attendance_records:
            # 각 레코드를 입력
            writer.writerow([
                record.date,
                record.employee.username,
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
            ])

        response = HttpResponse(buffer.getvalue().encode('utf-8-sig'), content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="출퇴근기록.csv"'

        return response
