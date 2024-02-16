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


def get_member_info():
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


class GetMemberInfo(View):
    def get(self, request, *args, **kwargs):
        context = get_member_info()
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




'''
    mac : 장치의 mac 어드레스를 의미합니다.
    sig :  WIFI 신호 세기로 RSSI값입니다. (dbm) : 0 번부터 -150까지 가능하고 -70이상이면 좋은 상태입니다.
    bat : RN400의 배터리 상태 정보입니다.  0~255 값이 가능하고, 5가 되면 배터리 교체가 필요합니다.
          값이 -1 인경우는 DC 전원을 공급하고 있는 경우 입니다.
    volt : 현재 배터리 정보를 전달합니다. <battery type>|<current voltage>
           <Battery Type> 0: 1.5V X 2EA , 1: 3.6V X 1 EA |  <Current Voltage> 2.95
    SMODEL: RN400의 상세 모델 번호를 전달합니다. RN400H2EX
    Cxxx :  센서의 정보를 보내줍니다. 
            C000 = 타임스탬프 | Ch.1(온도) | Ch.2 | Ch.3 | Ch.4
    Pxxx  :  센서의 정보를 보내줍니다. <timestamp>|<ch1센서값>|<ch2센서값|<ch3센서값>|......
    * 센서값: NULL : 센서없음.
'''

