from django.shortcuts import get_object_or_404
from django.views import View
from django.http import JsonResponse
from api.models import ProMaster, ProTask, ProTaskSub
from django.db.models import Prefetch, ExpressionWrapper, F, fields


class AllProjectInfo(View):
    def get(self, request, *args, **kwargs):
        param = request.GET.get('param')
        if not param:
            return JsonResponse({'error': 'param이 필요합니다.'}, status=400)

        project = get_object_or_404(ProMaster, pk=param)

        # pro_task_sub_prefetch = Prefetch(
        #     'taskparent',
        #     queryset=ProTaskSub.objects.filter(delete_flag='N'),
        #     to_attr='fetched_sub_tasks'
        # )

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

