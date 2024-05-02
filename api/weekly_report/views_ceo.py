import json
from datetime import datetime, timedelta

from django.utils import timezone
from django.utils.timezone import make_aware
from django.views import View
from django.http import JsonResponse

from api.models import ProMaster, ProTask, ProTaskSub, WeeklyMember, WeeklySub, WeeklyMaster, Weekly, GradeMaster
from django.db.models import Prefetch, ExpressionWrapper, F, fields, Subquery, OuterRef


class PmSelect(View):
    def get(self, request, *args, **kwargs):
        pm_id = request.GET.get('pm_id')

        result = Weekly.objects.filter(owner_id=pm_id).values(
            'id', 'week_cnt', 'week_name', 'report_flag', 'create_at', 'owner_id'
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


class WeeklyTaskSubView_CEO(View):
    def get(self, request, *args, **kwargs):
        week_id = request.GET.get('week_id')
        weekly_master = WeeklyMaster.objects.get(weekly_no_id=week_id, delete_flag='N')

        grade_score_subquery = Subquery(GradeMaster.objects.filter(
            weekly_sub_id=OuterRef('pk'), delete_flag='N'
        ).values('grade_score')[:1])

        grade_opinion_subquery = Subquery(GradeMaster.objects.filter(
            weekly_sub_id=OuterRef('pk'), delete_flag='N'
        ).values('grade_opinion')[:1])

        result = WeeklySub.objects.filter(weekly_id=weekly_master.id, delete_flag='N').annotate(
            grade_score=grade_score_subquery,
            grade_opinion=grade_opinion_subquery
        ).values(
            'id', 'r_date', 'p_name', 't_name', 'perform', 'w_status', 'w_start', 'w_close', 'required_date', 'w_note',
            'create_at', 'created_by', 'charge', 'charge__username', 'delete_flag',
            'charge__username', 'charge_id', 'r_man_id', 'r_man__username', 'weekly', 'weekly_id', 'grade_score',
            'grade_opinion'
        )
        return JsonResponse({'data': list(result)})


class GetWeeklyMaster_CEO(View):
    def get(self, request, *args, **kwargs):
        weekly_id = request.GET.get('week_id')

        result = WeeklyMaster.objects.filter(weekly_no_id=weekly_id, delete_flag='N', weekly_no__report_flag='Y').values(
            'id', 'p_working', 'p_finish', 'p_stay', 'p_fail', 'p_etc', 'delete_flag', 'create_at', 'created_by_id',
            'weekly_no_id', 'weekly_no__owner__username', 'weekly_no__owner__department_position__name',
            'weekly_no__owner__job_position__name'
        )

        return JsonResponse({'data': list(result)})


class CeoGrade(View):
    def post(self, request, *args, **kwargs):
        type = request.POST.get('type')
        if type == 'A':
            data = request.POST
            print('data', data)

            g_master = GradeMaster.objects.create(
                grade_score=data.get('grade_score'),
                grade_opinion=data.get('grade_opinion'),
                created_by_id=request.user.id,
                weekly_sub_id=data.get('sub_id')
            )

            g_master.save()

            return JsonResponse({'success': True})

        elif type == 'E':
            data = request.POST

            g_master = GradeMaster.objects.get(weekly_sub_id=data.get('sub_id'), delete_flag='N')

            g_master.grade_score = data.get('grade_score')
            g_master.grade_opinion = data.get('grade_opinion')
            g_master.updated_by_id = request.user.id

            g_master.save()

            return JsonResponse({'success': True})

