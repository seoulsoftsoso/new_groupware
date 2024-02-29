from django.http import JsonResponse, HttpResponse
from django.views import View

from api.models import ProMaster, UserMaster, ProMembers, CodeMaster, ProTask, ProTaskSub
from msgs import msg_error, msg_create_fail
import json
from django.shortcuts import get_object_or_404


class projectmgmtadd(View):

    def get(self, request, *args, **kwargs):
        context = {}
        return JsonResponse(context, safe=False)

    def post(self, request, *args, **kwargs):
        pjcode = request.POST.get('pjcode')
        pjname = request.POST.get('pjname')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        pjtype = request.POST.get('pj_type')
        pj_customer = request.POST.get('pj_customer')
        pj_note = request.POST.get('pj_note')

        # 참가자
        tagList = request.POST.get('TagifyUserList')
        if tagList is not None:
            tagList = json.loads(tagList)
        else:
            tagList = []

        pj_master = request.user.id

        context = {}

        try:
            pjtypecode = get_object_or_404(CodeMaster, id=pjtype)
            pjmasterInstance = get_object_or_404(UserMaster, id=pj_master)
            pro = ProMaster.objects.create(
                pjcode=pjcode,
                pjname=pjname,
                start_date=start_date,
                end_date=end_date,
                pj_type=pjtypecode,
                pj_customer=pj_customer,
                pj_note=pj_note,
                pj_master=pjmasterInstance,
                created_by=pjmasterInstance
            )

            if pro:
                context = {'error': False, 'message': 'success'}

                promember = ProMembers(
                    position='PM',
                    created_by=pjmasterInstance,
                    member_id=pjmasterInstance.id,
                    promaster=pro
                )

                promember.save()

            else:
                msg = msg_create_fail
                return JsonResponse({'error': True, 'message': msg})

            for tag in tagList:
                user_id = tag['value']
                user = get_object_or_404(UserMaster, id=user_id)
                try:
                    promember = ProMembers(
                        position='PE',
                        created_by=pjmasterInstance,
                        member_id=user.id,
                        promaster=pro
                    )

                    promember.save()

                    if promember:
                        context = {'error': False, 'message': 'success'}
                    else:
                        msg = msg_create_fail
                        return JsonResponse({'error': True, 'message': msg})

                except Exception as e:
                    print(e)
                    msg = msg_error

                    return JsonResponse({'error': True, 'message': msg})

        except Exception as e:
            print(e)
            msg = msg_error

            return JsonResponse({'error': True, 'message': msg})

        return JsonResponse({'message': 'success'})


class projectmgmtedit(View):
    def post(self, request, *args, **kwargs):
        type = request.POST.get('type')
        proid = request.POST.get('proid')

        project = get_object_or_404(ProMaster, pk=proid, delete_flag='N')

        if project:
            # 삭제시
            if type == 'D':
                try:
                    project.delete_flag = 'Y'
                    project.save()
                except Exception as e:
                    print(e)
            #수정
            else:
                print()

        return JsonResponse({'message': 'success'})


class taskmgmt(View):

    def get(self, request, *args, **kwargs):
        context = {}
        return JsonResponse(context, safe=False)

    def post(self, requset, *args, **kwargs):
        task_name = requset.POST.get('task_name')
        task_start = requset.POST.get('task_start')
        task_end = requset.POST.get('task_end')
        promaster = requset.POST.get('promasterid')
        userid = requset.user.id

        # 참가자
        tagList = requset.POST.get('TagifyUserList', None)
        if tagList is not None:
            tagList = json.loads(tagList)
        else:
            tagList = []

        context = {'message': 'success'}

        userIns = get_object_or_404(UserMaster, id=userid)
        proIns = get_object_or_404(ProMaster, id=promaster, delete_flag='N')

        try:
            task = ProTask.objects.create(
                task_name=task_name,
                task_start=task_start,
                task_end=task_end,
                created_by=userIns,
                pro_parent=proIns
            )

            task.save()

            if task:
                context = {'error': False, 'message': 'success'}
            else:
                msg = msg_create_fail
                return JsonResponse({'error': True, 'message': msg})

            for tag in tagList:
                user_id = tag['value']
                user = get_object_or_404(UserMaster, id=user_id)
                try:
                    promember = ProMembers(
                        position='PE',
                        created_by=userIns,
                        member_id=user.id,
                        promaster=proIns,
                        task=task
                    )

                    promember.save()

                    if promember:
                        context = {'error': False, 'message': 'success'}
                    else:
                        msg = msg_create_fail
                        return JsonResponse({'error': True, 'message': msg})

                except Exception as e:
                    print(e)
                    msg = msg_error

                    return JsonResponse({'error': True, 'message': msg})

        except Exception as e:
            print(e)
            msg = msg_error

            return JsonResponse({'error': True, 'message': msg})

        return JsonResponse({'error': False, 'message': 'success'})


class getSubData(View):
    def get(self, request, *args, **kwargs):

        taskId = request.GET.get('taskid')
        tasksub = ProTaskSub.objects.filter(task_parent=taskId, delete_flag='N').values(
            'id', 'sub_etc', 'sub_content', 'sub_title', 'sub_status', 'due_date', 'issue'
        ).order_by('-id')
        context = {'results': list(tasksub)}
        return JsonResponse(context, safe=False)

    def post(self, requset, *args, **kwargs):

        subtitle = requset.POST.get('sub_title')
        subcontent = requset.POST.get('sub_content')
        duedate = requset.POST.get('due_date')
        issue = requset.POST.get('issue')
        subetc = requset.POST.get('sub_etc')
        taskparent = requset.POST.get('selected_task_id')

        taskIns = get_object_or_404(ProTask, id=taskparent, delete_flag='N')

        try:
            sub = ProTaskSub.objects.create(
                sub_title=subtitle,
                sub_content=subcontent,
                due_date=duedate,
                issue=issue,
                sub_etc=subetc,
                task_parent=taskIns
            )

        except Exception as e:
            print(e)
            msg = msg_error

            return JsonResponse({'error': True, 'message': msg})

        return JsonResponse({'error': False, 'message': 'success'})
