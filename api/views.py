import time
import json
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.core import serializers
from .models import UserMaster, CodeMaster
from api import views


# Create your views here.


@csrf_exempt
def checkIn(request):
    context = '<xml>'
    context += '<root>'
    context += '<ack>ok</ack>'
    context += '<timestamp>' + str(int(time.time())) + '</timestamp>'
    context += '<offset-ch1>' + '0.0' + '</offset-ch1>'
    context += '<offset-ch2>' + '0.0' + '</offset-ch2>'
    context += '<sample-mode>' + '0.0' + '</sample-mode>'
    context += '</root>'
    context += '</xml>'

    return HttpResponse(context)


def get_member_info(type):
    if type:
        qs = UserMaster.objects.select_related('member').filter(
            member__promaster_id=type
        ).distinct().values(
            'id',
            'username',
            'department_position__name',
            'job_position__name',
        ).order_by('department_position', 'job_position')
    else:
        qs = UserMaster.objects.filter(is_master=False, is_active=True, is_staff=True).values(
            'id', 'user_id', 'code', 'username', 'email', 'is_master', 'is_active', 'is_staff',
            'created_at', 'department_position__name', 'job_position__name'
        ).order_by('department_position', 'job_position')
    context = {}
    context['result'] = list(qs)
    return context


def get_department_info():
    qs = CodeMaster.objects.filter(group_id=1).values(
        'id', 'code', 'name', 'created_at', 'updated_at', 'group_id'
    )

    context = {
        'department_info': list(qs)
    }
    return context


def get_job_info():
    qs = CodeMaster.objects.filter(group_id=2).values(
        'id', 'code', 'name', 'created_at', 'updated_at', 'group_id'
    )

    context = {
        'job_info': list(qs)
    }

    return context


def get_pow_info():
    qs = CodeMaster.objects.filter(group_id__code="POW").values(
        'id', 'code', 'name', 'created_at', 'updated_at', 'group_id'
    )

    context = {
        'pow_info': list(qs)
    }

    return context


class GetMemberInfo(View):
    def get(self, request, *args, **kwargs):
        type = request.GET.get('param', None)
        context = get_member_info(type)
        return JsonResponse(context, safe=False)


class GetNodeInfo(View):
    def get(self, request, *args, **kwargs):
        user_data = UserMaster.objects.filter(is_staff=True, is_active=True, is_master=False)
        user_data_json = serializers.serialize('json', user_data)
        user_result = json.loads(user_data_json)

        code_data = CodeMaster.objects.all()
        code_data_json = serializers.serialize('json', code_data)
        code_result = json.loads(code_data_json)

        result = {
            'user_data': user_result,
            'code_data': code_result
        }

        return JsonResponse(result, safe=False)
