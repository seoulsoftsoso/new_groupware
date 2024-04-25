from django.shortcuts import get_object_or_404
from django.views import View
from django.http import JsonResponse
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
            'create_at', 'created_by', 'charge', 'division', 'division_name', 'weekly_no'
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
            formdata = request.POST
            print('수정', formdata)

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




