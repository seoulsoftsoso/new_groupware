from datetime import datetime

from django.db import transaction

from api.models import EventMaster
from django.views import View
from django.http import JsonResponse, HttpResponse
import json


class get_eventDataAll(View):
    def get(self, request, *args, **kwargs):
        qs = EventMaster.objects.filter(delete_flag='N').values(
            'id', 'url', 'title', 'start_date', 'end_date', 'allDay',
            'event_type', 'create_by', 'description', 'location'
        )
        context = {}
        context['result'] = list(qs)
        return JsonResponse(context, safe=False)

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            created_by_id = request.COOKIES.get('user_id')

            print(request.POST.get('eventStartDate'))

            # 프론트에서 넘어오는 날짜 파싱
            def parse_date(date_str):
                date_str = date_str.replace("GMT+0900 (한국 표준시)", "+0900")
                date_obj = datetime.strptime(date_str, "%a %b %d %Y %H:%M:%S %z")
                date_obj = date_obj.replace(tzinfo=None)
                return date_obj.strftime("%Y-%m-%d %H:%M:%S.%f")

            date_str = request.POST.get('eventStartDate')
            end_date_str = request.POST.get('eventEndDate')

            formatted_date_str = parse_date(date_str)
            end_formatted_date_str = parse_date(end_date_str)

            allDay_str = request.POST.get('allDay')
            allDay = True if allDay_str.lower() == 'true' else False

            event_add = EventMaster(
                url=request.POST.get('eventURL'),
                title=request.POST.get('eventTitle'),
                start_date=formatted_date_str,
                end_date=end_formatted_date_str,
                allDay=allDay,
                event_type=request.POST.get('eventLabel'),
                create_by_id=created_by_id,
                updated_by_id=created_by_id,
                description=request.POST.get('eventDescription'),
                location=request.POST.get('eventLocation')
            )

            event_add.save()
            response_data = {'message': '성공'}
            return JsonResponse(response_data)

        else:
            print('db저장 실패')

        return HttpResponse("Invalid Request")

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        if request.method == 'PATCH':

            created_by_id = request.COOKIES.get('user_id')

            print(request.POST.get('eventStartDate'))

            # 프론트에서 넘어오는 날짜 파싱
            def parse_date(date_str):
                date_str = date_str.replace("GMT+0900 (한국 표준시)", "+0900")
                date_obj = datetime.strptime(date_str, "%a %b %d %Y %H:%M:%S %z")
                date_obj = date_obj.replace(tzinfo=None)
                return date_obj.strftime("%Y-%m-%d %H:%M:%S.%f")

            date_str = request.POST.get('eventStartDate')
            end_date_str = request.POST.get('eventEndDate')

            formatted_date_str = parse_date(date_str)
            end_formatted_date_str = parse_date(end_date_str)

            allDay_str = request.POST.get('allDay')
            allDay = True if allDay_str.lower() == 'true' else False

            event_add = EventMaster(
                updateEventId=request.POST.get('updateEventId'),
                url=request.POST.get('eventURL'),
                title=request.POST.get('eventTitle'),
                start_date=formatted_date_str,
                end_date=end_formatted_date_str,
                allDay=allDay,
                event_type=request.POST.get('eventLabel'),
                create_by_id=created_by_id,
                updated_by_id=created_by_id,
                description=request.POST.get('eventDescription'),
                location=request.POST.get('eventLocation')
            )

            event_add.save()
            response_data = {'message': '성공'}
            return JsonResponse(response_data)
