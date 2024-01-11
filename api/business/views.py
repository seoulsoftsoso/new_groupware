from datetime import datetime, timedelta, date
from django.db.models.functions import TruncDate
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.views.generic import ListView
from api.models import UserMaster, EventMaster


class business_main_page(ListView):
    template_name = 'admins/business/business_main.html'

    def get_queryset(self):
        self.search_to = self.request.GET.get('search-to')

        return

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_to'] = self.search_to

        return context

