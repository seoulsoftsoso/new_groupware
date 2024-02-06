from datetime import datetime, timedelta, date
from django.db import models
from django.db.models.expressions import RawSQL
from django.utils import timezone
from django.views.generic import ListView
from django.db.models import Sum, Case, When, FloatField, F, Value, ExpressionWrapper, fields, Q, Func, Subquery, \
    OuterRef, IntegerField, DateField, DurationField, DateTimeField
from django.db.models.functions import Floor, Coalesce, ExtractYear, Now, Cast, ExtractDay
from Pagenation import PaginatorManager
from api.models import EventMaster, UserMaster, Holiday, AdjustHoliday


class HolidayCheckView(ListView):
    template_name = 'admins/holiday/holiday_check.html'

    def get_queryset(self):
        now_date = datetime.now().date()
        print('now : ', now_date)

        law_holiday_subquery = Holiday.objects.filter(
            workYear=OuterRef('user_workYear')
        ).values('law_holiday')

        # 조정 휴가 합계 계산
        adjust_sum = AdjustHoliday.objects.values('employee_id').annotate(
            adjust_sum=Sum('adjust_count')
        )

        result = UserMaster.objects.annotate(
            user_workYear=ExpressionWrapper(
                (now_date - F('created_at')),
                output_field=FloatField()
            ),
            user_lawHoliday=Subquery(law_holiday_subquery[:1]),
            residul_Holiday=ExpressionWrapper(
                F('holidayCreated_by__law_holiday')
                + Coalesce(Sum('adjustCreated_by__adjust_count'), 0)
                - Coalesce(Sum(
                    Case(
                        When(event_creat__event_type='Holiday',
                             then=F('event_creat__end_date') - F('event_creat__start_date')),
                        When(event_creat__event_type='Family',
                             then=((F('event_creat__end_date') - F('event_creat__start_date')) + 1) * 0.5),
                        default=0,
                    )
                ), 0),
                output_field=FloatField()
            ),
            total_Holiday=ExpressionWrapper(
                F('holidayCreated_by__law_holiday') + Coalesce(Sum('adjustCreated_by__adjust_count'), 0),
                output_field=FloatField()
            )
        ).filter(
            Q(event_creat__event_type__in=['Holiday', 'Family']) & Q(event_creat__delete_flag='N')
        )

        # result = UserMaster.objects.raw(
        #     """
        #     SELECT a.*,
        #             FLOOR(DATEDIFF(CURDATE(), a.created_at) / 365) AS 'user_workYear',
        #             b.law_holiday AS 'user_lawHoliday',
        #             c.event_type, c.delete_flag,
        #             (b.law_holiday + IFNULL(d.adjust_sum, 0) - IFNULL(e.total_days, 0)) AS 'residul_Holiday',
        #             (b.law_holiday + IFNULL(d.adjust_sum, 0)) AS 'total_Holiday'
        #     FROM api_usermaster a
        #     JOIN api_holiday b ON FLOOR(DATEDIFF(CURDATE(), a.created_at) / 365) = b.workYear
        #     LEFT JOIN api_eventmaster c ON a.id = c.create_by_id
        #     LEFT JOIN (
        #         SELECT employee_id, SUM(adjust_count) AS adjust_sum
        #         FROM api_adjustholiday
        #         GROUP BY employee_id
        #     ) d ON a.id = d.employee_id
        #     LEFT JOIN (
        #         SELECT create_by_id,
        #                SUM(CASE
        #                     WHEN event_type = 'Holiday' THEN DATEDIFF(end_date, start_date) + 1
        #                     WHEN event_type = 'Family' THEN (DATEDIFF(end_date, start_date) + 1) * 0.5
        #                     ELSE 0
        #                 END) AS total_days
        #         FROM api_eventmaster
        #         WHERE delete_flag = 'N'
        #         GROUP BY create_by_id
        #     ) e ON a.id = e.create_by_id
        #     WHERE DATEDIFF(CURDATE(), a.created_at) >= 0
        #         AND ((c.event_type = 'Holiday' OR c.event_type = 'Family') AND c.delete_flag = 'N');
        #     """
        # )

        return result

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['result'] = self.get_queryset()
        # context['page_range'], context['contacts'] = PaginatorManager(self.request, context['result'])
        return context


class HolidayAdjustmentView(ListView):
    template_name = 'admins/holiday/holiday_adjustment.html'

    def get_queryset(self):
        return Holiday.objects.all()
