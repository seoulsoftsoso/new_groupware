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


class DateDiff(Func):
    function = 'DATEDIFF'
    template = "%(function)s(%(expressions)s)"


class HolidayCheckView(ListView):
    template_name = 'admins/holiday/holiday_check.html'

    def get_queryset(self):


        # 근속연수 계산
        current_date = datetime.now().date()

        user_work_year =  ExpressionWrapper(
    DateDiff(current_date, F('created_at')) / 365,
    output_field=IntegerField()
    )

        # 법정연차 계산
        law_holiday_subquery = Holiday.objects.filter(
            workYear=user_work_year
        ).values('law_holiday')

        adjust_sum_subquery = AdjustHoliday.objects.filter(employee_id=OuterRef('id')).values('employee_id').annotate(
            adjust_sum=Sum('adjust_count')).values('adjust_sum')[:1]

        total_days = Sum(
            ExpressionWrapper(
                Case(
                    When(event_creat__event_type='Holiday',
                         then=F('event_creat__end_date') - F('event_creat__start_date') + 1),
                    When(event_creat__event_type='Family',
                         then=(F('event_creat__end_date') - F('event_creat__start_date') + 1) * 0.5),
                    default=Value(0),
                    output_field=DurationField()
                ),
                output_field=DurationField()
            )
        )

        result = (
            UserMaster.objects.annotate(
                user_workYear=user_work_year,
                law_holiday=law_holiday_subquery,
                total_days=total_days,
                adjust_sum=Coalesce(Subquery(adjust_sum_subquery, output_field=IntegerField()),
                                    Value(0, output_field=IntegerField())),
            )
            .filter(created_at__lte=timezone.now(), is_master=False)
            .values(
                'id', 'username', 'user_workYear',
                'law_holiday', 'adjust_sum',
                'total_days',
            )
        )



        # user_work_year = ExpressionWrapper(
        #     F('created_at') - F('created_at'),
        #     output_field=IntegerField()
        # )
        #
        # total_days = Sum(
        #     Case(
        #         When(event_creat__event_type='Holiday',
        #              then=ExpressionWrapper(F('event_creat__end_date') - F('event_creat__start_date') + 1,
        #                                     output_field=IntegerField())),
        #         When(event_creat__event_type='Family',
        #              then=ExpressionWrapper((F('event_creat__end_date') - F('event_creat__start_date') + 1) * 0.5,
        #                                     output_field=IntegerField())),
        #         default=Value(0),
        #         output_field=IntegerField()
        #     )
        # )
        #
        # adjust_sum_subquery = Coalesce(
        #     AdjustHoliday.objects.filter(employee_id=F('id')).aggregate(adjust_sum=Sum('adjust_count'))['adjust_sum'],
        #     Value(0, output_field=IntegerField())
        # )
        #
        # # 조정연차 계산
        # adjust_holiday_subquery = AdjustHoliday.objects.filter(
        #     employee_id=OuterRef('usermaster_id')).values('adjust_count')
        #
        # result = UserMaster.objects.annotate(
        #     user_work_year=user_work_year,
        #     total_days=total_days,
        #     adjust_sum=adjust_sum_subquery,
        #     law_holiday=OuterRef('holidayCreated_by__law_holiday'),
        #     total_use_holiday=F('total_days') + F('adjust_sum'),
        #     remain_holiday=F('law_holiday') + F('adjust_sum') - F('total_days'),
        # ).select_related('law_holiday').values('remain_holiday')

        for itme in result:
            print(itme)
            total_days_days_only = itme['total_days'].days
            print(total_days_days_only)

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
