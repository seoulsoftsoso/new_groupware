import json
from datetime import datetime

from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from api.models import ProMaster, ProTask, ProTaskSub, WeeklyMember
from django.db.models import Prefetch, ExpressionWrapper, F, fields


class AllProjectInfo(View):
    def get(self, request, *args, **kwargs):
        param = request.GET.get('param')
        if not param:
            return JsonResponse({'error': 'param이 필요합니다.'}, status=400)

        project = get_object_or_404(ProMaster, pk=param)

        pro_task_sub_prefetch = Prefetch(
            'taskparent',
            queryset=ProTaskSub.objects.filter(delete_flag='N').annotate(
                duration_days=ExpressionWrapper(
                    F('due_date') - F('sub_start_date'),
                    output_field=fields.DurationField()
                )
            ),
            to_attr='fetched_sub_tasks'
        )

        pro_tasks = ProTask.objects.filter(
            pro_parent=project,
            delete_flag='N'
        ).prefetch_related(
            pro_task_sub_prefetch
        )

        result = []
        for task in pro_tasks:
            task_info = {
                'task_id': task.id,
                'task_name': task.task_name,
                'task_start': task.task_start,
                'task_end': task.task_end,
                'task_parent': task.pro_parent.pjname,
                'sub_tasks': [{
                    'sub_task_id': sub_task.id,
                    'sub_title': sub_task.sub_title,
                    'sub_content': sub_task.sub_content,
                    'sub_status': sub_task.sub_status,
                    'sub_start_date': sub_task.sub_start_date,
                    'sub_due_date': sub_task.due_date,
                    'sub_issue': sub_task.issue,
                    'sub_ect': sub_task.sub_etc,
                    'duration_days': sub_task.duration_days.days + 1,
                } for sub_task in getattr(task, 'fetched_sub_tasks', [])]
            }
            result.append(task_info)

        return JsonResponse({'data': result})


class WeeklyTaskSubView(View):
    def get(self, request, *args, **kwargs):
        week_id = request.GET.get('week_id')
        result = WeeklyMember.objects.filter(weekly_no_id=week_id, delete_flag='N').annotate(
            division_name=F('division__name')
        ).values(
            'id', 'r_date', 'p_name', 't_name', 'perform', 'w_status', 'w_start', 'w_close', 'required_date', 'w_note',
            'create_at', 'created_by', 'charge', 'charge__username', 'division', 'division_name', 'weekly_no'
        )
        return JsonResponse({'data': list(result)})

    def post(self, request, *args, **kwargs):
        type = request.POST.get('type')

        if type == 'A':
            w_member = WeeklyMember.objects.create(
                r_date=request.POST.get('r_date'),
                division_id=request.POST.get('division'),
                p_name=request.POST.get('p_name'),
                t_name=request.POST.get('t_name'),
                perform=request.POST.get('perform'),
                w_status=request.POST.get('w_status'),
                w_start=request.POST.get('w_start'),
                w_close=request.POST.get('w_close'),
                required_date=request.POST.get('required_date'),
                w_note=request.POST.get('w_note'),
                weekly_no_id=request.POST.get('weekly_no'),
                created_by_id=request.user.id
            )

            w_member.save()

            return JsonResponse({'message': 'success'})

        elif type == 'E':

            week_id = request.POST.get('subtask_id')
            w_member = WeeklyMember.objects.get(id=week_id)

            w_member.r_date = request.POST.get('r_date')
            w_member.division_id = request.POST.get('division')
            w_member.p_name = request.POST.get('p_name')
            w_member.t_name = request.POST.get('t_name')
            w_member.perform = request.POST.get('perform')
            w_member.w_status = request.POST.get('w_status')
            w_member.w_start = request.POST.get('w_start')
            w_member.w_close = request.POST.get('w_close')
            w_member.required_date = request.POST.get("required_date")
            w_member.w_note = request.POST.get('w_note')
            w_member.weekly_no_id = request.POST.get('weekly_no')

            w_member.save()

            return JsonResponse({'message': 'success'})

        return JsonResponse({'message': 'success'})


class WeeklySubPost(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        print('data', data)
        data_list = data.get('dataToSend')

        for item in data_list:
            r_date = datetime.strptime(item['r_date'], "%Y-%m-%dT%H:%M:%S.%fZ").date()
            w_start = datetime.strptime(item['w_start'], "%Y-%m-%dT%H:%M:%S").date()
            w_close = datetime.strptime(item['w_close'], "%Y-%m-%dT%H:%M:%S").date()

            WeeklyMember.objects.create(
                r_date=r_date,
                w_start=w_start,
                w_close=w_close,
                p_name=item['p_name'],
                t_name=item['t_name'],
                perform=item['perform'],
                w_status=item['w_status'],
                required_date=item['required_date'],
                w_note=item['w_note'],
                weekly_no_id=item['weekly_no'],
            )

        return JsonResponse({"success": True})


def WeeklyTaskSub_delete(request):
    data = json.loads(request.body)

    if data.get('type') == 'D':

        try:
            task_id = json.loads(request.body).get('ids')
            print('task_id', task_id)

            for obj_id in task_id:
                try:
                    w_member = WeeklyMember.objects.get(id=obj_id)

                    w_member.delete_flag = 'Y'
                    w_member.save()
                except ProTaskSub.DoesNotExist:
                    pass

            return JsonResponse({'del': True})
        except json.JSONDecodeError:

            return JsonResponse({'error': 'Invalid JSON'}, status=400)

    return JsonResponse({"success": True})


def do_report_pe(request):
    data = json.loads(request.body)
    task_ids = data.get('ids', [])
    pm_id = data.get('pm_id')

    WeeklyMember.objects.filter(id__in=task_ids).update(charge_id=pm_id)

    return JsonResponse({"success": True})
