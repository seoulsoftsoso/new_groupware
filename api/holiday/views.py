from copy import deepcopy
from datetime import datetime, timedelta, date

from dateutil.relativedelta import relativedelta
from django.db.models.expressions import RawSQL
from django.http import JsonResponse
from django.utils import timezone
from django.views.generic import ListView
from django.db.models import Sum, Case, When, FloatField, F, Value, ExpressionWrapper, fields, Q, Func, Subquery, \
    OuterRef, IntegerField, Window
from django.db.models.functions import Floor, Coalesce, ExtractYear, Now, Cast, ExtractDay, Round, Extract, Substr, \
    Concat
from api.models import EventMaster, UserMaster, Holiday, AdjustHoliday


class DateDiff(Func):
    function = 'DATEDIFF'
    template = "%(function)s(%(expressions)s)"
    output_field = IntegerField()


class Days(Func):
    function = 'DATEDIFF'
    arity = 2  # number of arguments
    output_field = fields.FloatField()


class DateAdd(Func):
    function = 'DATE_ADD'
    template = "%(function)s(%(expressions)s, INTERVAL %(days)s DAY)"


class HolidayCheckView(ListView):
    template_name = 'admins/holiday/holiday_check.html'
    paginate_by = 15

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.now_employ_year_raw_sql = RawSQL(
            """
            DATE_ADD(DATE_ADD(employment_date, INTERVAL FLOOR(DATEDIFF(CURDATE(), employment_date) / 365) YEAR), INTERVAL 1 DAY)
            """,
            []
        )
        self.next_employ_year_raw_sql = RawSQL(
            """
            DATE_ADD(DATE_ADD(employment_date, INTERVAL FLOOR(DATEDIFF(CURDATE(), employment_date) / 365) YEAR), INTERVAL 1 YEAR)
            """,
            []
        )

    def get_original_queryset(self):
        current_date = datetime.now().date()
        search_title = self.request.GET.get('search-title', None)
        search_content = self.request.GET.get('search-content', None)
        standard_year = self.request.GET.get('YEAR', datetime.today().year)
        standard_month = self.request.GET.get('MONTH', datetime.today().month)

        adjust_sum_subquery = AdjustHoliday.objects.filter(
            employee_id=OuterRef('create_by_id'),
            delete_flag="N",
            create_at__gt=self.now_employ_year_raw_sql,
            create_at__lte=self.next_employ_year_raw_sql,
        ).values(
            'employee_id'
        ).annotate(
            adjust_sum=Sum('adjust_count')
        ).values('adjust_sum')[:1]

        result = (
            EventMaster.objects.annotate(
                user_workYear=Floor(DateDiff(current_date, F('create_by__employment_date')) / 365),
                law_holiday=Subquery(
                    Holiday.objects.filter(
                        workYear=OuterRef('user_workYear')
                    ).values('law_holiday')[:1]
                ),
                adjust_sum=Coalesce(Subquery(adjust_sum_subquery, output_field=IntegerField()), Value(0, output_field=IntegerField())),
                total_days=Case(
                    When(event_type='Holiday', then=Days('end_date', 'start_date') + Value(1.0)),
                    When(event_type='Family', then=Value(0.5)),
                    default=Value(1.0),
                    output_field=fields.FloatField(),
                ),
            )
            .annotate(
                total_holiday=F('law_holiday') + F('adjust_sum'),
                cumulative_total_days=Window(
                    expression=Sum('total_days'),
                    partition_by=F('create_by_id'),
                    order_by=F('id').asc(),
                    output_field=FloatField()
                ),
                residual_holiday=ExpressionWrapper(F('total_holiday') - F('cumulative_total_days'),
                                                  output_field=FloatField())
            )
            .filter(
                create_by__is_master=False,
                event_type__in=['Holiday', 'Family'],
            )
            .values(
                'create_by__username', 'create_by__department_position__name', 'create_by__job_position__name',
                'create_by__employment_date', 'cumulative_total_days',
                'start_date', 'end_date', 'description', 'user_workYear',
                'event_type', 'law_holiday', 'adjust_sum',
                'total_days', 'total_holiday', 'residual_holiday', 'create_by_id'
            )
            .order_by('-id')
        )

        original_result = deepcopy(result)

        if not self.request.user.is_superuser:
            result = result.filter(create_by_id=self.request.user.id)

        if search_title == 'name' or search_title == None:
            if search_content is not None and search_content != "":
                result = result.filter(create_by__username__contains=str(search_content))

        if standard_month == '-1':
            result = result.filter(start_date__year=int(standard_year)).all().order_by('-start_date')
        else:
            result = result.filter(start_date__year=int(standard_year),
                                   start_date__month=int(standard_month)).all().order_by('-start_date')

        return result, original_result

    def get_queryset(self):
        # 새로운 get_queryset 메소드에서는 result만 반환
        result, original_result = self.get_original_queryset()
        return result

    def get_user_holiday(self):
        user_id = self.request.user.id
        _, original_result = self.get_original_queryset()
        return original_result.filter(
            create_by_id=user_id,
            create_at__gt=self.now_employ_year_raw_sql,
            create_at__lte=self.next_employ_year_raw_sql,
        ).order_by('-id')[:1]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # get_original_queryset 메소드에서 original_result만 가져옴
        _, original_result = self.get_original_queryset()
        context['original_result'] = original_result
        context['user_holiday'] = self.get_user_holiday()
        context['standard_year'] = self.request.GET.get('YEAR', datetime.today().year)
        context['standard_month'] = self.request.GET.get('MONTH', datetime.today().month)
        return context


class HolidayAdjustmentView(ListView):
    template_name = 'admins/holiday/holiday_adjustment.html'
    paginate_by = 15

    def get_queryset(self):
        current_date = datetime.now().date()
        search_title = self.request.GET.get('search_title', None)
        search_content = self.request.GET.get('search_content', None)

        now_employ_year_raw_sql = RawSQL("""
            DATE_ADD(DATE_ADD(employment_date, INTERVAL FLOOR(DATEDIFF(CURDATE(), employment_date) / 365) YEAR), INTERVAL 1 DAY)
        """, [])

        next_employ_year_raw_sql = RawSQL("""
            DATE_ADD(DATE_ADD(employment_date, INTERVAL FLOOR(DATEDIFF(CURDATE(), employment_date) / 365) YEAR), INTERVAL 1 YEAR)
        """, [])

        adjust_sum_subquery = AdjustHoliday.objects.filter(
            employee_id=OuterRef('id'),
            delete_flag="N",
            create_at__gt=now_employ_year_raw_sql,
            create_at__lte=next_employ_year_raw_sql
        ).values(
            'employee_id').annotate(
            adjust_sum=Sum('adjust_count')).values('adjust_sum')[:1]

        total_days_subquery = EventMaster.objects.filter(
            create_by_id=OuterRef('id'),
            event_type__in=["Holiday", "Family"],
            start_date__gt=now_employ_year_raw_sql,
            start_date__lte=next_employ_year_raw_sql
        ).annotate(
            days_diff=Case(
                When(event_type='Holiday', then=Days('end_date', 'start_date') + Value(1.0)),
                When(event_type='Family', then=Value(0.5)),
                default=Value(1.0),
                output_field=fields.FloatField(),
            )
        ).values('create_by_id').annotate(total=Sum('days_diff')).values('total')

        result = UserMaster.objects.annotate(
            user_workYear=Floor(  # 근속년수
                DateDiff(current_date, F('employment_date')) / 365
            ),
            law_holiday=Subquery(  # 법정근속년수별 연차
                Holiday.objects.filter(
                    workYear=OuterRef('user_workYear')
                ).values('law_holiday')[:1]
            ),
            adjust_sum=Coalesce(Subquery(adjust_sum_subquery, output_field=FloatField()),  # 추가연차
                                Value(0, output_field=FloatField())),
        ).annotate(
            total_holiday=ExpressionWrapper(F('law_holiday') + F('adjust_sum'), output_field=FloatField()),  # 총연차
            total_days=Coalesce(Subquery(total_days_subquery), Value(0)),  # 사용연차
            cumulative_total_days=Window(
                expression=Sum('total_days'),
                partition_by=F('id'),
                order_by=F('id').asc(),
                output_field=FloatField()
            ),
        ).annotate(
            residual_holiday=ExpressionWrapper(F('total_holiday') - F('cumulative_total_days'),
                                               output_field=FloatField())  # 잔여연차
        ).filter(
            is_master=False,
            is_active=True,
            is_staff=True,
        ).values(
            'id', 'username', 'department_position__name', 'job_position__name', 'employment_date',
            'user_workYear', 'law_holiday', 'adjust_sum', 'total_days', 'total_holiday',
            'residual_holiday', 'cumulative_total_days'
        ).order_by('department_position_id', 'job_position_id')

        if search_title == 'name' and search_content:
            result = result.filter(username__icontains=search_content)
        elif search_title == 'department' and search_content:
            result = result.filter(department_position__name__icontains=search_content)

        # for obj in result:
        #     print('obj:', obj)

        return result

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['result'] = context['object_list']
        # context['page_range'], context['contacts'] = PaginatorManager(self.request, context['result'])
        return context


def get_adjust_holiday(request):

    user_id = request.GET.get('user_id')

    res = AdjustHoliday.objects.filter(delete_flag="N", employee_id=user_id).values(
        'id', 'adjust_count', 'adjust_reason', 'create_at', 'employee_id', 'created_by_id', 'updated_at', 'updated_by_id'
    )

    res_list = list(res)

    return JsonResponse(res_list, safe=False)


def create_adjust_holiday(request):
    current_date = datetime.now().date()

    adjust_num = request.GET.get('adjust_num')
    adjust_reason = request.GET.get('adjust_reason')
    employee = request.GET.get('id')
    # print('id : ', employee)

    user_id = request.user.id
    user = UserMaster.objects.get(id=user_id)

    adjust_add = AdjustHoliday(
        adjust_count=adjust_num,
        adjust_reason=adjust_reason,
        create_at=current_date,
        employee_id=employee,
        created_by=user,
        updated_at=current_date,
        updated_by=user,
    )
    adjust_add.save()

    return JsonResponse({"success": "success"})


def update_adjust_holiday(request):
    adjust_id = request.GET.get('id')
    adjust_count = request.GET.get('adjust_count')
    adjust_reason = request.GET.get('adjust_reason')

    adjust_holiday = AdjustHoliday.objects.get(id=adjust_id)

    user_id = request.user.id
    user = UserMaster.objects.get(id=user_id)

    adjust_holiday.adjust_count = adjust_count
    adjust_holiday.adjust_reason = adjust_reason
    adjust_holiday.updated_by = user
    adjust_holiday.save()

    return JsonResponse({"success": "success"})


def delete_adjust_holiday(request):
    adjust_id = request.GET.get('id')
    adjust_holiday = AdjustHoliday.objects.get(id=adjust_id)
    adjust_holiday.delete_flag = 'Y'
    adjust_holiday.save()

    return JsonResponse({"success": "success"})

