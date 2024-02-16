from datetime import date
from django.db.models import Count, Q, Case, When, IntegerField, F
from django.db.models.functions import TruncDate
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework.exceptions import ValidationError
from api.form import SignUpForm, QuestionForm
from api.models import UserMaster, BoardMaster, FileBoardMaster, CodeMaster, GroupCodeMaster, EventMaster
from api.views import get_member_info


def user_approval(request):

    user_id = request.GET.get('id')
    print(user_id)

    usermaster = UserMaster.objects.get(id=user_id)

    usermaster.is_staff = True
    usermaster.is_active = True

    return

