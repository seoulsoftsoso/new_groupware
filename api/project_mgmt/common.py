from django.http import JsonResponse, HttpResponse
from django.utils import timezone
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
            # 수정
            else:
                try:
                    # promember - 구성원 (수정,삭제)
                    tagList = json.loads(request.POST.get('TagifyUserList', '[]'))
                    ProMembers.objects.filter(promaster_id=proid).delete()
                    for tag in tagList:
                        user_id = tag['value']
                        user = get_object_or_404(UserMaster, id=user_id)
                        participant = ProMembers(
                            position='PE',
                            promaster=project,
                            member=user,
                            created_by_id=request.user.id,
                            updated_by_id=request.user.id
                        )
                        participant.save()

                    project.pjcode = request.POST.get('pjcode')
                    project.pjname = request.POST.get('pjname')
                    project.start_date = request.POST.get('start_date')
                    project.end_date = request.POST.get('end_date')
                    project.pj_customer = request.POST.get('pj_customer')
                    project.pj_note = request.POST.get('pj_note')
                    project.update_at = timezone.now()
                    project.updated_by_id = request.user.id

                    project.save()

                    return JsonResponse({'message': 'success'})
                except Exception as e:
                    print(e)

        return JsonResponse({'message': 'success'})


class ProMemberListGet(View):
    def get(self, request, *args, **kwargs):
        pro_type = request.GET.get('pro_type')
        pro_id = request.GET.get('pro_id')
        print(pro_id)
        promaster_id = request.GET.get('promaster_id')
        print(promaster_id)

        if pro_type == 'pt_get':
            result = ProMembers.objects.filter(promaster_id=promaster_id, task_id=pro_id)

            memberlist = [{
                'cuser_id': participant.member.id,
                'cuser_department': participant.member.department_position.name,
                'cuser_username': participant.member.username,
                'cuser_position': participant.member.job_position.name
            } for participant in result]

            context = {'memberlist': memberlist}
            return JsonResponse(context)

        else:
            result = ProMembers.objects.filter(promaster_id=pro_id)

            memberlist = [{
                'cuser_id': participant.member.id,
                'cuser_department': participant.member.department_position.name,
                'cuser_username': participant.member.username,
                'cuser_position': participant.member.job_position.name
            } for participant in result]

            context = {'memberlist': memberlist}
            return JsonResponse(context)


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

    def patch(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            print(data)

            return JsonResponse({'success': True})

        except Exception as e:
            print(e)
            return JsonResponse({'error': 'Invalid JSON'}, status=400)


class GetSubDataEdit(View):
    def post(self, request, *args, **kwargs):
        type = request.POST.get('type')

        if type == 'edit':
            try:
                data = request.POST

                tasksub_id = request.POST.get('selected_task_id')
                print(tasksub_id)

                pro_task_sub = ProTaskSub.objects.get(id=tasksub_id)

                pro_task_sub.sub_title = data.get('sub_title')
                pro_task_sub.sub_content = data.get('sub_content')
                pro_task_sub.due_date = data.get('due_date')
                pro_task_sub.issue = data.get('issue')
                pro_task_sub.sub_etc = data.get('sub_etc')
                pro_task_sub.update_at = timezone.now()
                pro_task_sub.updated_by_id = request.user.id

                pro_task_sub.save()

                return JsonResponse({'success': True})

            except Exception as e:
                print(e)
                return JsonResponse({'error': 'Invalid JSON'}, status=400)

        elif type == 'cng_status':
            proTaskSub_id = request.POST.get('proTaskSub_id')
            code = request.POST.get('code')

            proTaskSub = ProTaskSub.objects.get(id=proTaskSub_id)

            proTaskSub.sub_status = code
            proTaskSub.save()

            return JsonResponse({'success': True})

        else:
            try:
                task_id = json.loads(request.body)

                for obj_id in task_id:
                    try:
                        pro_task_sub = ProTaskSub.objects.get(id=obj_id)

                        pro_task_sub.delete_flag = 'Y'
                        pro_task_sub.save()
                    except ProTaskSub.DoesNotExist:
                        pass

                return JsonResponse({'del': True})
            except json.JSONDecodeError:

                return JsonResponse({'error': 'Invalid JSON'}, status=400)


class ProTaskEdit(View):
    def post(self, request, *args, **kwargs):
        type = request.POST.get('type')

        if type == 'E':
            try:
                protask_id = request.POST.get('proid')
                promaster_id = request.POST.get('promaster_id')

                # 멤버 수정할 때 객체를 완전삭제 후 다시 생성
                ProMembers.objects.filter(task_id=protask_id, promaster_id=promaster_id).delete()

                protask = ProTask.objects.get(id=protask_id)

                protask.task_name = request.POST.get('task_name')
                protask.task_start = request.POST.get('task_start')
                protask.task_end = request.POST.get('task_end')
                protask.save()

                tagList = json.loads(request.POST.get('TagifyUserList', '[]'))
                tagUserIds = [tag['value'] for tag in tagList]

                ProMembers.objects.filter(promaster_id=promaster_id, task_id=protask_id).exclude(member_id__in=tagUserIds).update(task_id=None, update_at=timezone.now())

                for tag in tagList:
                    user_id = tag['value']

                    # ProMembers 객체가 존재하지 않을 경우에만 생성
                    if not ProMembers.objects.filter(member_id=user_id, promaster_id=promaster_id, task_id=protask_id).exists():
                        participant = ProMembers.objects.create(
                            position='PE',
                            member_id=user_id,
                            promaster_id=promaster_id,
                            task_id=protask_id,
                            update_at=timezone.now(),
                            created_by_id=request.user.id
                        )
                        participant.save()

                return JsonResponse({'success': True})
            except Exception as e:
                print(e)
                return JsonResponse({'error': 'fail'}, status=400)

        elif type == 'del':
            try:
                protask_id = request.POST.get('protask_id')
                proTask = ProTask.objects.get(id=protask_id)

                proTask.delete_flag = "Y"
                proTask.save()

                return JsonResponse({'success': True})
            except Exception as e:
                print(e)
                return JsonResponse({'error': 'fail'}, status=400)

