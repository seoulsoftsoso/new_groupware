from datetime import datetime, timedelta

from django.core import serializers
from django.db import transaction
from django.db.models import Prefetch
from django.shortcuts import render, get_object_or_404
from django.utils.dateparse import parse_datetime
from api.models import EventMaster, Participant, UserMaster, CodeMaster
from django.views import View
from django.http import JsonResponse, HttpResponse
import json


class get_eventDataAll(View):
    def get(self, request, *args, **kwargs):
        qs = EventMaster.objects.filter(delete_flag='N').select_related('create_by').prefetch_related(
            Prefetch('participant_set', queryset=Participant.objects.select_related('cuser'))).order_by('-id')
        data = []

        for event in qs:
            participants = event.participant_set.all()
            participants_data = [
                {
                    'id': p.id,
                    'cuser_id': p.cuser.id,
                    'cuser_username': p.cuser.username,
                    'cuser_department': p.cuser.department_position.name,
                    'cuser_position': p.cuser.job_position.name
                }
                for p in participants
            ]

            event_data = {
                'id': event.id,
                'url': event.url,
                'title': event.title,
                'start_date': event.start_date.isoformat(),
                'end_date': event.end_date.isoformat(),
                'allDay': event.allDay,
                'event_type': event.event_type,
                'create_by_id': event.create_by_id,
                'create_by__username': event.create_by.username,
                'description': event.description,
                'location': event.location,
                'participants': participants_data,
                'vehicleSelect': event.vehicle.code if event.vehicle else None,
                'vehicleName': event.vehicle.name if event.vehicle else None,
                'businessPair': event.business_pair,
            }
            data.append(event_data)

        context = {'result': data}
        return JsonResponse(context, safe=False)

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            created_by_id = request.user.id

            # 날짜,시간 파싱
            startDate_str = request.POST.get('eventStartDate')
            endDate_str = request.POST.get('eventEndDate')
            start_date = parse_datetime(startDate_str) or datetime.strptime(startDate_str, '%Y-%m-%d')
            end_date = parse_datetime(endDate_str) or datetime.strptime(endDate_str, '%Y-%m-%d')
            event_type = request.POST.get('eventLabel')
            employee_select = request.POST.get('employee_select')

            allDay_str = request.POST.get('allDay')
            allDay = True if allDay_str.lower() == 'true' else False
            if allDay:
                start_date = start_date.replace(hour=9, minute=0)
                end_date = end_date.replace(hour=18, minute=0)

            # 참가자
            tagList = request.POST.get('tagList')
            if tagList is not None:
                tagList = json.loads(tagList)
            else:
                tagList = []

            if any(tag['value'] == str(created_by_id) for tag in tagList):
                return JsonResponse({'error': '참석자란에 작성자는 등록될 수 없습니다.'}, status=400)

            # 법인차량
            vehicleCode = request.POST.get('vehicleSelect')
            selected_vehicle = None
            if vehicleCode:
                selected_vehicle = CodeMaster.objects.get(code=vehicleCode)

            if EventMaster.objects.filter(start_date=start_date, end_date=end_date, event_type=event_type, create_by_id=request.user.id, delete_flag='N').exists():
                return JsonResponse({'error': '중복된 일정이 있습니다.'}, status=400)

            # 작성자
            if employee_select:
                created_by_id = employee_select
                # print(created_by_id)

            event_add = EventMaster(
                url='',
                title=request.POST.get('eventTitle'),
                start_date=start_date,
                end_date=end_date,
                allDay=allDay,
                event_type=event_type,
                create_by_id=created_by_id,
                updated_by_id=created_by_id,
                description=request.POST.get('eventDescription'),
                location=request.POST.get('eventLocation'),
                vehicle=selected_vehicle
            )

            event_add.save()

            # 참가자
            for tag in tagList:
                user_id = tag['value']
                print('userID :', user_id)
                print('created_by_id :', created_by_id)
                user = get_object_or_404(UserMaster, id=user_id)
                participant = Participant(event=event_add, cuser=user)
                participant.save()

                # event에 등록된 참석자도 연차,반차 등록될 수 있게
                if event_type == 'Holiday' or event_type == 'Family':
                    participant_event = EventMaster(
                        url='',
                        title=request.POST.get('eventTitle'),
                        start_date=start_date,
                        end_date=end_date,
                        allDay=allDay,
                        event_type=event_type,
                        create_by_id=user_id,
                        updated_by_id=user_id,
                        description=request.POST.get('eventDescription'),
                        location=request.POST.get('eventLocation'),
                    )

                    participant_event.save()
                    Participant.objects.filter(event_id=event_add.id).delete()  # 참석자란에 태그 안되게 delete

            if vehicleCode:
                event_add.business_pair = event_add.id
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
            employee_select = eventData.get('employee_select')
            created_by_id = request.user.id

            tagList = json.loads(eventData.get('tagList', '[]'))
            if any(tag['value'] == str(created_by_id) for tag in tagList):
                return JsonResponse({'error': '참석자란에 작성자는 등록될 수 없습니다.'}, status=400)

            Participant.objects.filter(event=event).delete()

            for tag in tagList:
                Participant.objects.create(event=event, cuser_id=tag['value'])

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

                # 법인차량
                vehicleCode = json.loads(request.body).get('vehicleSelect')
                # print('vehicleCode', vehicleCode)
                selected_vehicle = None
                if vehicleCode:
                    selected_vehicle = CodeMaster.objects.get(code=vehicleCode)

                # 작성자
                if employee_select:
                    created_by_id = employee_select

                event.start_date = start_date
                event.end_date = end_date
                event.title = eventData.get('eventTitle')
                event.allDay = allDay
                event.event_type = eventData.get('eventLabel')
                event.create_by_id = created_by_id
                event.updated_by_id = created_by_id
                event.description = eventData.get('eventDescription')
                event.location = eventData.get('eventLocation')
                event.vehicle = selected_vehicle

                event.save()

                return JsonResponse({'message': 'success'})

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
