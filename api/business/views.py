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
        context['page_range'], context['contacts'] = PaginatorManager(self.request, context['object_list'])

        return context

