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



