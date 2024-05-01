import json
from datetime import datetime, timedelta
from django.utils.timezone import make_aware
from django.views import View
from django.http import JsonResponse

from api.models import ProMaster, ProTask, ProTaskSub, WeeklyMember, WeeklySub, WeeklyMaster, Weekly
from django.db.models import Prefetch, ExpressionWrapper, F, fields


class PmSelect(View):
    def get(self, request, *args, **kwargs):
        pm_id = request.GET.get('pm_id')

        result = Weekly.objects.filter(owner_id=pm_id).values(
            'id', 'week_cnt', 'week_name', 'report_flag', 'create_at','owner_id'
        ).order_by('-id')

        data = []
        for item in result:
            tuesday = item['create_at']
            monday = tuesday - timedelta(days=1)
            friday = tuesday + timedelta(days=3)
            week_range = f"{monday.strftime('%Y-%m-%d')} ~ {friday.strftime('%Y-%m-%d')}"

            item_data = {
                'id': item['id'],
                'week_name': f"{item['week_name']} ({week_range})"
            }
            data.append(item_data)

        return JsonResponse({'data': data})


class GetWeeklyMaster_CEO(View):
    def get(self, request, *args, **kwargs):
        weekly_id = request.GET.get('week_id')

        result = WeeklyMaster.objects.filter(weekly_no_id=weekly_id).values(
            'id', 'p_working', 'p_finish', 'p_stay', 'p_fail', 'p_etc', 'delete_flag', 'create_at', 'created_by_id',
            'weekly_no_id', 'weekly_no__owner__username', 'weekly_no__owner__department_position__name',
            'weekly_no__owner__job_position__name'
        )

        return JsonResponse({'data': list(result)})

