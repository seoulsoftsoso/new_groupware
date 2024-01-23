from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
import os
from django.utils import timezone
from django.views.generic import ListView
from rest_framework.exceptions import ValidationError
from api.models import UserMaster, CodeMaster, CorporateMgmt, EventMaster


class CorporateMgmtListView(ListView):
    model = CorporateMgmt
    template_name = 'admins/corporate_vehicle/vehicle_main.html'

    def get_queryset(self):
        self.today = timezone.now().date()

        event_qs = EventMaster.objects.filter(
            delete_flag="N",
            business_pair__isnull=False
        ).prefetch_related('participant_set', 'corporatemgmt_set')

        return event_qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event_qs'] = context['object_list']
        context['today_qs'] = context['object_list'].filter(start_date__lte=self.today, end_date__gte=self.today, business_pair__isnull=False)

        return context


