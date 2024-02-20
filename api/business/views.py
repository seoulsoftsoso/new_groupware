from datetime import datetime, timedelta, date
from django.db.models.functions import TruncDate
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.views import View
from django.views.generic import ListView
from Pagenation import PaginatorManager
from api.models import UserMaster, EventMaster


class business_main_page(ListView):
    template_name = 'admins/business/business_main.html'
    paginate_by = 15

    def get_queryset(self):
        self.today = timezone.now().date()
        search_title = self.request.GET.get('search-title', None)
        search_content = self.request.GET.get('search-content', None)
        search_to = self.request.GET.get('search-to', None)
        search_from = self.request.GET.get('search-from', None)

        qs = EventMaster.objects.filter(event_type="Business", delete_flag="N").prefetch_related('participant_set').order_by('-id')
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
                event_qs = event_qs.filter(employee__employee_number__contains=str(search_content))

        self.original_qs = qs
        return event_qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event_qs'] = context['object_list']

        return context


class BusinessEditModal(View):
    def get(self, request, *args, **kwargs):
        id = request.GET.get('id')

        qs = EventMaster.objects.prefetch_related('participant_set').get(id=id)

        participants = [{
            'cuser_id': participant.cuser.id,
            'cuser_department': participant.cuser.department_position.name,
            'cuser_username': participant.cuser.username,
            'cuser_position': participant.cuser.job_position.name
        } for participant in qs.participant_set.all()]

        data = {
            'start_date': qs.start_date.strftime('%Y-%m-%d %H:%M'),
            'end_date': qs.end_date.strftime('%Y-%m-%d %H:%M'),
            'allDay': qs.allDay,
            'participants': participants,
            'location': qs.location,
            'description': qs.description,
            'etc': qs.etc,
            'vehicle': qs.vehicle.code if qs.vehicle else None,
            'business_pair': qs.business_pair
        }

        return JsonResponse(data)
