from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
import os
from django.conf import settings
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from api.models import BoardMaster, ReplyMaster, UserMaster, FileBoardMaster, CodeMaster


def vehicle_main_page(request):

    context ={}

    return render(request, 'admins/corporate_vehicle/vehicle_main.html', context)