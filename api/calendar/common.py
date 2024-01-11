from datetime import datetime, timedelta

from django.db import transaction
from django.shortcuts import render
from django.utils.dateparse import parse_datetime

from api.models import EventMaster
from django.views import View
from django.http import JsonResponse, HttpResponse
import json


class get_eventDataAll(View):
    def get(self, request, *args, **kwargs):
        qs = EventMaster.objects.filter(delete_flag='N').values(
            'id', 'url', 'title', 'start_date', 'end_date', 'allDay',
            'event_type', 'create_by__username', 'description', 'location'
        )
        context = {}
        context['result'] = list(qs)
        return JsonResponse(context, safe=False)

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            created_by_id = request.COOKIES.get('user_id')

            # 날짜,시간 파싱
            startDate_str = request.POST.get('eventStartDate')
            endDate_str = request.POST.get('eventEndDate')

            allDay_str = request.POST.get('allDay')
            allDay = True if allDay_str.lower() == 'true' else False

            start_date = parse_datetime(startDate_str) or datetime.strptime(startDate_str, '%Y-%m-%d')
            end_date = parse_datetime(endDate_str) or datetime.strptime(endDate_str, '%Y-%m-%d')

            if allDay:
                start_date = start_date.replace(hour=9, minute=0)
                end_date = end_date.replace(hour=18, minute=0)

            event_add = EventMaster(
                url=request.POST.get('eventURL'),
                title=request.POST.get('eventTitle'),
                start_date=start_date,
                end_date=end_date,
                allDay=allDay,
                event_type=request.POST.get('eventLabel'),
                create_by_id=created_by_id,
                updated_by_id=created_by_id,
                description=request.POST.get('eventDescription'),
                location=request.POST.get('eventLocation')
            )

            event_add.save()

            return JsonResponse({'message': 'success'})

        return HttpResponse("Invalid Request")

    @transaction.atomic
    def patch(self, request, *args, **kwargs):
        if request.method == 'PATCH':
            body_unicode = request.body.decode('utf-8')
            body_data = json.loads(body_unicode)
            eventData = body_data
            updateEventId = eventData.get('updateEventId')
            event = EventMaster.objects.get(id=updateEventId)

            if event:
                allDay = eventData.get('allDay', False)

                # 날짜,시간 파싱
                startDate_str = eventData.get('eventStartDate')
                endDate_str = eventData.get('eventEndDate')
                start_date = parse_datetime(startDate_str) or datetime.strptime(startDate_str, '%Y-%m-%d')
                end_date = parse_datetime(endDate_str) or datetime.strptime(endDate_str, '%Y-%m-%d')

                if allDay:
                    start_date = start_date.replace(hour=9, minute=0)
                    end_date = end_date.replace(hour=18, minute=0)

                event.start_date = start_date
                event.end_date = end_date
                event.url = eventData.get('eventURL')
                event.title = eventData.get('eventTitle')
                event.allDay = allDay
                event.event_type = eventData.get('eventLabel')
                event.create_by_id = request.COOKIES.get('user_id')
                event.updated_by_id = request.COOKIES.get('user_id')
                event.description = eventData.get('eventDescription')
                event.location = eventData.get('eventLocation')

                event.save()

            return HttpResponse()

    def delete(self, request, *args, **kwargs):
        if request.method == "DELETE":
            body_unicode = request.body.decode('utf-8')
            body_data = json.loads(body_unicode)
            eventId = body_data.get('eventId')

            event = EventMaster.objects.get(id=eventId)

            event.delete_flag = "Y"

            event.save()

        return HttpResponse()
