from api.models import EventMaster
from django.views import View
from django.http import JsonResponse


class get_eventDataAll(View):
    def get(self, request, *args, **kwargs):
        qs = EventMaster.objects.filter(delete_flag='N').values(
            'id', 'url', 'title', 'start_date', 'end_date', 'allDay',
            'event_type', 'create_by', 'description', 'location'
        )
        context ={}
        context['result'] = list(qs)
        return JsonResponse(context, safe=False)