import json
from datetime import datetime
from django.utils.timezone import make_aware
from django.views import View
from django.http import JsonResponse

from api.models import ProMaster, ProTask, ProTaskSub, WeeklyMember, WeeklySub, WeeklyMaster, Weekly
from django.db.models import Prefetch, ExpressionWrapper, F, fields


class WeeklyTaskSubView_PM(View):
    def get(self, request, *args, **kwargs):
        week_id = request.GET.get('week_id')
        weekly_master = WeeklyMaster.objects.get(weekly_no_id=week_id)
        result = WeeklySub.objects.filter(weekly_id=weekly_master.id, delete_flag='N').values(
            'id', 'r_date', 'p_name', 't_name', 'perform', 'w_status', 'w_start', 'w_close', 'required_date', 'w_note',
            'create_at', 'created_by', 'charge', 'charge__username', 'delete_flag',
            'charge__username', 'charge_id', 'r_man_id', 'r_man__username', 'weekly', 'weekly_id'
        )
        return JsonResponse({'data': list(result)})

    def post(self, request, *args, **kwargs):
        type = request.POST.get('type')
        now = make_aware(datetime.now())
        today_date = now.date()
        weekly_no = request.POST.get('weekly_no')
        weekly_master = WeeklyMaster.objects.get(weekly_no_id=weekly_no)

        if type == 'A':
            w_sub = WeeklySub.objects.create(
                r_date=today_date,
                p_name=request.POST.get('p_name'),
                t_name=request.POST.get('t_name'),
                perform=request.POST.get('perform'),
                w_status=request.POST.get('w_status'),
                w_start=request.POST.get('w_start'),
                w_close=request.POST.get('w_close'),
                required_date=request.POST.get('required_date'),
                w_note=request.POST.get('w_note'),
                r_man_id=request.user.id,
                weekly_id=weekly_master.id,
                created_by_id=request.user.id
            )

            w_sub.save()

            return JsonResponse({'message': 'success'})

        elif type == 'E':
            week_id = request.POST.get('subtask_id')
            w_sub = WeeklySub.objects.get(id=week_id)

            w_sub.r_date = today_date
            w_sub.p_name = request.POST.get('p_name')
            w_sub.t_name = request.POST.get('t_name')
            w_sub.perform = request.POST.get('perform')
            w_sub.w_status = request.POST.get('w_status')
            w_sub.w_start = request.POST.get('w_start')
            w_sub.w_close = request.POST.get('w_close')
            w_sub.required_date = request.POST.get("required_date")
            w_sub.w_note = request.POST.get('w_note')
            w_sub.weekly_no_id = request.POST.get('weekly_no')

            w_sub.save()

            return JsonResponse({'message': 'success'})

        return JsonResponse({'message': 'success'})


class WeeklySubPost_PM(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        # print('data', data)
        data_list = data.get('dataToSend')

        for item in data_list:
            r_date = datetime.strptime(item['r_date'], "%Y-%m-%dT%H:%M:%S.%fZ").date()
            w_start = datetime.strptime(item['w_start'], "%Y-%m-%dT%H:%M:%S").date()
            w_close = datetime.strptime(item['w_close'], "%Y-%m-%dT%H:%M:%S").date()
            weekly_no = item['weekly_no']
            weekly_master = WeeklyMaster.objects.get(weekly_no_id=weekly_no)
            # print('weekly_master', weekly_master.id)

            WeeklySub.objects.create(
                r_date=r_date,
                w_start=w_start,
                w_close=w_close,
                p_name=item['p_name'],
                t_name=item['t_name'],
                r_man_id=request.user.id,
                perform=item['perform'],
                w_status=item['w_status'],
                required_date=item['required_date'],
                w_note=item['w_note'],
                weekly_id=weekly_master.id
            )

        return JsonResponse({"success": True})


def WeeklyTaskSub_pm_delete(request):
    data = json.loads(request.body)

    if data.get('type') == 'D':

        try:
            task_id = json.loads(request.body).get('ids')
            # print('task_id', task_id)

            for obj_id in task_id:
                try:
                    w_sub = WeeklySub.objects.get(id=obj_id)

                    w_sub.delete_flag = 'Y'
                    w_sub.save()
                except ProTaskSub.DoesNotExist:
                    pass

            return JsonResponse({'del': True})
        except json.JSONDecodeError:

            return JsonResponse({'error': 'Invalid JSON'}, status=400)

    return JsonResponse({"success": True})


def pm_do_report_pe(request):
    data = request.POST
    # print('data', data.get('p_working'))

    weekly_id = data.get('weekly_no')
    Weekly.objects.filter(id=weekly_id).update(report_flag='Y')

    w_master = WeeklyMaster.objects.get(weekly_no_id=weekly_id)

    w_master.p_working = data.get('p_working')
    w_master.p_finish = data.get('p_finish')
    w_master.p_stay = data.get('p_stay')
    w_master.p_fail = data.get('p_fail')
    w_master.p_etc = data.get('p_etc')

    w_master.save()

    return JsonResponse({"success": True})

