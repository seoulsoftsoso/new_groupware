from datetime import datetime, timedelta

from django.utils import timezone
from django.views.generic import ListView
from django.db.models import Sum, Case, When, FloatField, F, Value, ExpressionWrapper, fields, Q, Func, Subquery, \
    OuterRef, IntegerField, DateField
from django.db.models.functions import Floor, Coalesce, ExtractYear, Now
from Pagenation import PaginatorManager
from api.models import EventMaster, UserMaster, Holiday, AdjustHoliday


class HolidayCheckView(ListView):
    template_name = 'admins/holiday/holiday_check.html'
    model = UserMaster

    def get_queryset(self):
        # Calculate workYear for each User
        users = UserMaster.objects.annotate(
            workYear=ExtractYear(Now()) - ExtractYear(F('created_at'))
        )
        print('users : ', list(users))  # Print QuerySet Results

        # Get total adjust holiday for each User
        adjust_holidays = AdjustHoliday.objects.values('employee').annotate(adjust_sum=Sum('adjust_count')).order_by()
        print('adjust_holidays : ', list(adjust_holidays))  # Print QuerySet Results

        # Get total days for each User
        event_days = EventMaster.objects.values('create_by').annotate(
            total_days=Coalesce(Sum(
                Case(
                    When(event_type='Holiday', then=(F('end_date') - F('start_date') + Value(1))),
                    When(event_type='Family', then=((F('end_date') - F('start_date') + Value(1)) * 0.5)),
                    default=Value(0),
                    output_field=IntegerField(),
                )
            ), 0)
        ).filter(delete_flag='N').order_by()
        print('event_days : ', list(event_days))  # Print QuerySet Results
        print(event_days.query)

        # Main query
        users = users.filter(
            workYear__gte=0, event_creat__event_type__in=['Holiday', 'Family'], event_creat__delete_flag='N'
        ).annotate(
            law_holiday=Coalesce(F('holidayCreated_by__law_holiday'), 0),
            event_type=F('event_creat__event_type'),
            delete_flag=F('event_creat__delete_flag'),
            adjust_sum=Coalesce(Subquery(adjust_holidays.values('adjust_sum')), 0),
            total_days=Coalesce(Subquery(event_days.values('total_days')[:1]), 0)
        ).annotate(
            residul_Holiday=F('law_holiday') + F('adjust_sum') - F('total_days'),
            total_Holiday=F('law_holiday') + F('adjust_sum')
        )
        print('users : ', list(users))  # Print QuerySet Results

        return users

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_range'], context['contacts'] = PaginatorManager(self.request, context['object_list'])
        return context


class HolidayAdjustmentView(ListView):
    template_name = 'admins/holiday/holiday_adjustment.html'

    def get_queryset(self):
        return Holiday.objects.all()
