from datetime import datetime, timedelta, date
from django.db import models
from django.db.models.expressions import RawSQL
from django.utils import timezone
from django.views.generic import ListView
from django.db.models import Sum, Case, When, FloatField, F, Value, ExpressionWrapper, fields, Q, Func, Subquery, \
    OuterRef, IntegerField, DateField, DurationField, DateTimeField, Window
from django.db.models.functions import Floor, Coalesce, ExtractYear, Now, Cast, ExtractDay, Round
from Pagenation import PaginatorManager
from api.models import EventMaster, UserMaster, Holiday, AdjustHoliday


class DateDiff(Func):
    function = 'DATEDIFF'
    template = "%(function)s(%(expressions)s)"
    output_field = IntegerField()


class Days(Func):
    function = 'DATEDIFF'
    arity = 2  # number of arguments
    output_field = fields.FloatField()


class HolidayCheckView(ListView):
    template_name = 'admins/holiday/holiday_check.html'

    def get_queryset(self):
        # 근속연수 계산
        current_date = datetime.now().date()
        search_title = self.request.GET.get('search-title', None)
        search_content = self.request.GET.get('search-content', None)
        standard_year = self.request.GET.get('YEAR', datetime.today().year)
        standard_month = self.request.GET.get('MONTH', datetime.today().month)

        adjust_sum_subquery = AdjustHoliday.objects.filter(employee_id=OuterRef('create_by_id')).values(
            'employee_id').annotate(
            adjust_sum=Sum('adjust_count')).values('adjust_sum')[:1]

        result = (
            EventMaster.objects.annotate(
                user_workYear=Floor(  # 근속년수
                    DateDiff(current_date, F('create_by__created_at')) / 365
                ),
                law_holiday=Subquery(  # 법정근속년수별 연차
                    Holiday.objects.filter(
                        workYear=OuterRef('user_workYear')
                    ).values('law_holiday')[:1]
                ),
                adjust_sum=Coalesce(Subquery(adjust_sum_subquery, output_field=IntegerField()),  # 추가연차
                                    Value(0, output_field=IntegerField())),
                total_days=Case(  # 사용 연차
                    When(event_type='Holiday', then=Days('end_date', 'start_date') + Value(1.0)),
                    When(event_type='Family', then=Value(0.5)),
                    default=Value(1.0),
                    output_field=fields.FloatField(),
                ),
            ).annotate(
                total_holiday=F('law_holiday') + F('adjust_sum'),  # 총연차
                cumulative_total_days=Window(
                    expression=Sum('total_days'),
                    partition_by=F('create_by_id'),
                    order_by=F('id').asc(),
                    output_field=FloatField()
                ),
            ).annotate(
                residual_holiday=ExpressionWrapper(F('total_holiday') - F('cumulative_total_days'),
                                                   output_field=FloatField())  # 잔여연차
            )
            .filter(create_at__lte=timezone.now(), create_by__is_master=False, event_type__in=['Holiday', 'Family'])
            .values(
                'create_by__username', 'create_by__department_position__name', 'create_by__job_position__name',
                'create_by__created_at', 'cumulative_total_days',
                'start_date', 'end_date', 'description', 'user_workYear',
                'event_type', 'law_holiday', 'adjust_sum',
                'total_days', 'total_holiday', 'residual_holiday',
            ).order_by('-id')
        )

        # 일반 직원일 경우 자신의 연차 기록만 필터링
        if self.request.COOKIES['is_superuser'] == 'false':
            result = result.filter(create_by_id=self.request.COOKIES['user_id'])

        if search_title == 'name' or search_title == None:
            if search_content is not None and search_content != "":
                result = result.filter(create_by__username__contains=str(search_content))

        if standard_month == '-1':
            result = result.filter(start_date__year=int(standard_year)).all().order_by('-start_date')
        else:
            result = result.filter(start_date__year=int(standard_year),
                                   start_date__month=int(standard_month)).all().order_by('-start_date')

        for itme in result:
            print(itme)

        return result

    def get_user_holiday(self):
        user_id = self.request.COOKIES['user_id']
        return self.get_queryset().filter(create_by_id=user_id).order_by('-id')[:1]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['result'] = context['object_list']
        context['user_holiday'] = self.get_user_holiday()
        context['standard_year'] = self.request.GET.get('YEAR', datetime.today().year)
        context['standard_month'] = self.request.GET.get('MONTH', datetime.today().month)
        context['page_range'], context['contacts'] = PaginatorManager(self.request, context['object_list'])
        return context


class HolidayAdjustmentView(ListView):
    template_name = 'admins/holiday/holiday_adjustment.html'

    def get_queryset(self):
        current_date = datetime.now().date()

        adjust_sum_subquery = AdjustHoliday.objects.filter(employee_id=OuterRef('id')).values(
            'employee_id').annotate(
            adjust_sum=Sum('adjust_count')).values('adjust_sum')[:1]

        result = UserMaster.objects.annotate(
            user_workYear=Floor(  # 근속년수
                DateDiff(current_date, F('created_at')) / 365
            ),
            law_holiday=Subquery(  # 법정근속년수별 연차
                Holiday.objects.filter(
                    workYear=OuterRef('user_workYear')
                ).values('law_holiday')[:1]
            ),
            adjust_sum=Coalesce(Subquery(adjust_sum_subquery, output_field=IntegerField()),  # 추가연차
                                Value(0, output_field=IntegerField())),
        ).annotate(
            total_holiday=F('law_holiday') + F('adjust_sum'),  # 총연차
            total_days=Coalesce(Subquery(  # 사용 연차
                EventMaster.objects.filter(create_by=OuterRef('pk')).annotate(
                    days_diff=Case(
                        When(event_type='Holiday', then=Days('end_date', 'start_date') + Value(1.0)),
                        When(event_type='Family', then=Value(0.5)),
                        default=Value(1.0),
                        output_field=FloatField(),
                    )
                ).values('days_diff')[:1]
            ), Value(0)),
            cumulative_total_days=Window(
                expression=Sum('total_days'),
                partition_by=F('id'),
                order_by=F('id').asc(),
                output_field=FloatField()
            ),
        ).annotate(
            residual_holiday=ExpressionWrapper(F('total_holiday') - F('cumulative_total_days'),
                                               output_field=FloatField())  # 잔여연차
        ).filter(is_master=False, is_active=True, is_staff=True).values(
            'username', 'department_position__name', 'job_position__name', 'created_at',
            'user_workYear', 'law_holiday', 'adjust_sum', 'total_days', 'total_holiday',
            'residual_holiday',
        ).order_by('job_position')

        for obj in result:
            print('obj:', obj)

        return result

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['result'] = self.get_queryset()
        context['page_range'], context['contacts'] = PaginatorManager(self.request, context['result'])
        return context
