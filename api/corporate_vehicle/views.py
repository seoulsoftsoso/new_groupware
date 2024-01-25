from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
import os
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, CreateView
from rest_framework.exceptions import ValidationError

from Pagenation import PaginatorManager
from api.corporate_vehicle.froms import CorporateMgmtForm
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
        #         print('사용확인', corporate_mgm.event_mgm)

        self.original_qs = qs
        return event_qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event_qs'] = context['object_list']
        context['today_qs'] = self.original_qs.filter(start_date__date__lte=self.today, end_date__date__gte=self.today)
        context['page_range'], context['contacts'] = PaginatorManager(self.request, self.get_queryset())

        return context


class CorporateMgmtCreateView(View):

    def get(self, request, *args, **kwargs):
        eventId = request.GET.get('eventId')
        corporate_mgmt = CorporateMgmt.objects.get(event_mgm_id=eventId)

        mgmt_qs = serializers.serialize('json', [corporate_mgmt])

        return JsonResponse(mgmt_qs, safe=False)

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            data = request.POST
            print('data', data)

            event_mgm = get_object_or_404(EventMaster, id=data['eventId'])

            mgmt_add, created = CorporateMgmt.objects.update_or_create(
                event_mgm=event_mgm,
                defaults={
                    'oiling': data['oiling'] == 'true',
                    'distance': int(data['distance']),
                    'maintenance': data['maintenance'],
                    'etc': data['etc'],
                }
            )

            if created:
                print("New CorporateMgmt created.")
            else:
                print("Existing CorporateMgmt updated.")

            return JsonResponse({"success": True}, status=200)
        else:
            return JsonResponse({"success": False}, status=400)


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
