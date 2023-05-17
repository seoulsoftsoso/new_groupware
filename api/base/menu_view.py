import json

from django.core import serializers
from django.db import transaction
from django.http import JsonResponse
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.views import View

from api.models import Menu_Auth, MenuMaster, UserMaster


def getLmenuList(request):
    user_id = request.GET.get('user_id')
    client = request.GET.get('client')
    qs = MenuMaster.objects.filter(menuauth__enterprise=client
                                   , menuauth__user=user_id
                                   , menuauth__use_flag='Y'
                                   , menuauth__del_flag='N'
                                   , menuauth__parent_id=0).order_by('menuauth__order')
    qs_json = serializers.serialize('json', qs)
    qs_json = qs_json.encode('utf-8').decode('unicode_escape')
    qs_json = json.dumps(json.loads(qs_json), ensure_ascii=False)

    context = {}
    context['results'] = qs_json
    return JsonResponse(context)


def getSubMenuList(request):
    menutype = ['S']
    try:
        userId = request.GET.get('user_id')

        enterpriseId = request.GET.get('client')
        parent_id = request.GET.get('parent_id')
    except KeyError:
        userId = None

    if userId:
        user = UserMaster.objects.get(id=userId)

    if userId == 1:
        menutype.append('M')

    if enterpriseId:
        enterprise = enterpriseId
    else:
        enterprise = request.COOKIES['enterprise_id']

    if parent_id:
        parent = parent_id
    else:
        parent = 0

    qs = MenuMaster.objects.filter(menuauth__enterprise=enterprise
                                   , menuauth__user=user
                                   , menuauth__parent_id=parent
                                   , menuauth__del_flag='N'
                                   , type__in=menutype
                                   ).order_by('menuauth__order').distinct()

    ql = MenuMaster.objects.filter(type__in=menutype)

    # 직렬화된 JSON 문자열로 변환 (인코딩 설정-한글깨짐방지)
    qs_json = serializers.serialize('json', qs)
    qs_json = qs_json.encode('utf-8').decode('unicode_escape')
    qs_json = json.dumps(json.loads(qs_json), ensure_ascii=False)
    ql_json = serializers.serialize('json', ql)
    ql_json = ql_json.encode('utf-8').decode('unicode_escape')
    ql_json = json.dumps(json.loads(ql_json), ensure_ascii=False)
    context = {}
    context['usesubmenu'] = qs_json
    context['allsubmenu'] = ql_json

    return JsonResponse(context)


class Menuauth(View):
    queryset = Menu_Auth.objects.all()
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        qs = Menu_Auth.objects.all()
        return qs

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @transaction.atomic
    def post(self, request, *args, **kwargs):

        menulist = request.POST.getlist('menuid[]', '')
        userId = request.POST.get('user_id', '')
        client = request.POST.get('client', '')
        parentId = request.POST.get('parent_id', '')

        user = UserMaster.objects.get(id=request.COOKIES['user_id'])

        if not parentId:
            parentId = 0  # 대메뉴이기 때문에 0으로 고정
            cnt = 100
            auto = 100
        else:
            orders = self.get_queryset().filter(menu_id=parentId, user_id=userId).values('order').first()
            if orders:
                cnt = orders['order'] + 5

            auto = 5

        for unit in menulist:

            menuobj = self.get_queryset().filter(menu_id=unit, use_flag='Y', parent_id=parentId,
                                                 enterprise_id=client, user_id=userId).first()
            if menuobj:
                menuobj.delete()

            authObj = Menu_Auth.objects.create(
                menu_id=unit,
                enterprise_id=client,
                user_id=userId,
                order=cnt,
                parent_id=parentId,
                use_flag='Y',
                del_flag='N',
                created_by=user,
                created_at=user,
                updated_by=user,
                updated_at=user
            )

            cnt += auto

        return JsonResponse({'success': True}, status=status.HTTP_200_OK)
