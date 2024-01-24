from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
import os
from django.utils import timezone
from django.views.generic import ListView
from rest_framework.exceptions import ValidationError

from Pagenation import PaginatorManager
from api.models import UserMaster, CodeMaster, CorporateMgmt, EventMaster


class CorporateMgmtListView(ListView):
    template_name = 'admins/corporate_vehicle/vehicle_main.html'

    def get_queryset(self):
        self.today = timezone.now().date()
        search_title = self.request.GET.get('search-title', None)
        search_content = self.request.GET.get('search-content', None)
        search_to = self.request.GET.get('search-to', None)
        search_from = self.request.GET.get('search-from', None)

        qs = EventMaster.objects.select_related('vehicle').prefetch_related('participant_set', 'corporatemgmt_set')
        qs = qs.filter(delete_flag='N').filter(business_pair__isnull=False).order_by('-id')
        event_qs = qs

        if search_to != "" and search_to != None:
            event_qs = event_qs.filter(start_date__date__gte=search_to)
        if search_from != "" and search_from != None:
            event_qs = event_qs.filter(start_date__date__lte=search_from)

        if search_title == 'name' or search_title == None:
            if search_content is not None and search_content != "":
                event_qs = event_qs.filter(create_by__username=str(search_content))
        elif search_title == 'number':
            if search_content is not None and search_content != "":
                event_qs = event_qs.filter(
                    employee__employee_number__contains=str(search_content))

        # for event in event_qs:
        #     print(event.title)
        #     print(event.vehicle)
        #     for participant in event.participant_set.all():
        #         print(participant.cuser)
        #     for corporate_mgm in event.corporatemgmt_set.all():
        #         print(corporate_mgm.distance)

        self.original_qs = qs
        return event_qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event_qs'] = context['object_list']
        context['today_qs'] = self.original_qs.filter(start_date__date__lte=self.today, end_date__date__gte=self.today)
        context['page_range'], context['contacts'] = PaginatorManager(self.request, self.get_queryset())

        return context


def corporate_edit_data(request):
    if request.method == 'GET':
        id = request.GET.get('id')
        event = EventMaster.objects.select_related('vehicle').prefetch_related('participant_set', 'corporatemgmt_set').get(id=id)

        for participant in event.participant_set.all():
            print(participant)

        participants = [{
            'cuser_id': participant.cuser.id,
            'cuser_department': participant.cuser.department_position.name,
            'cuser_username': participant.cuser.username,
            'cuser_position': participant.cuser.job_position.name
        } for participant in event.participant_set.all()]

        data = {
            'id': event.id,
            'start_date': event.start_date.strftime('%Y-%m-%d %H:%M'),
            'end_date': event.end_date.strftime('%Y-%m-%d %H:%M'),
            'allDay': event.allDay,
            'guests': participants,
            'description': event.description,
            'location': event.location,
            'vehicleSelect': event.vehicle.code
        }

        return JsonResponse(data)