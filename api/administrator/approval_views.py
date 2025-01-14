from datetime import datetime

from django.http import JsonResponse
from django.views.generic import ListView
from api.models import UserMaster
from api.views import get_department_info, get_job_info, get_pow_info


class ApprovalDeletePageView(ListView):
    template_name = 'admins/administrator/approval/approval_delete.html'
    paginate_by = 15

    def get_queryset(self):
        status_filter = self.request.GET.get('statusFilter', None)
        name_filter = self.request.GET.get('search_content', None)

        queryset = UserMaster.objects.filter(is_master=False)

        if status_filter:
            if status_filter == 'resignation':  # 퇴사
                queryset = queryset.filter(is_staff=False, department_position__id__isnull=False)
            elif status_filter == 'working':  # 재직 중
                queryset = queryset.filter(is_active=True, is_staff=True)
            elif status_filter == 'standby':  # 승인 대기
                queryset = queryset.filter(is_staff=False, code__isnull=True)

        if name_filter:
            queryset = queryset.filter(username__icontains=name_filter)

        result = queryset.values(
            'id', 'user_id', 'code', 'username', 'email', 'is_master', 'is_active', 'is_staff',
            'created_at', 'department_position__name', 'job_position__name', 'employment_date', 'postal_code', 'address',
            'etc', 'tel', 'research_num', 'place_of_work__name', 'birthday',
        ).order_by('-id')

        return result

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_content'] = self.request.GET.get('search_content', '')
        context['status_filter'] = self.request.GET.get('statusFilter', '')
        department_info = get_department_info()
        job_info = get_job_info()
        pow_info = get_pow_info()
        context['department_info'] = department_info['department_info']
        context['job_info'] = job_info['job_info']
        context['pow_info'] = pow_info['pow_info']
        context['result'] = context['object_list']
        # context['page_range'], context['contacts'] = PaginatorManager(self.request, context['object_list'])
        return context


def user_approval(request):
    if request.method == 'POST':
        type = request.POST.get('type')
        if type == 'A':
            print(request.POST)
            user_id = request.POST.get('id')
            employment_date = request.POST.get('employment_date')
            department_select = request.POST.get('department_select')
            job_select = request.POST.get('job_select')
            phone_num = request.POST.get('phone_num')
            research_num = request.POST.get('research_num')
            place_of_work = request.POST.get('place_of_work')
            birthday = request.POST.get('birthday')
            update_user_id = request.user.id
            user = UserMaster.objects.get(id=update_user_id)

            # 사원번호 생성
            try:
                temp_year_month = employment_date.split('-')[0][2:] + employment_date.split('-')[1]

                if department_select == '38' or department_select == '39' or department_select == '41':
                    temp_depart = 'D'
                elif department_select == '42':
                    temp_depart = 'B'
                else:
                    temp_depart = 'P'

                temp_user_id = str(user_id).zfill(5)

                employee_code = temp_year_month + '-' + temp_depart + '-' + temp_user_id
                print('employee_code : ', employee_code)

            except Exception as e:
                print(e)
                return JsonResponse({'error': 'Data Error'}, status=400)

            usermaster = UserMaster.objects.get(id=user_id)

            usermaster.employment_date = employment_date
            usermaster.code = employee_code
            usermaster.department_position_id = department_select
            usermaster.job_position_id = job_select
            usermaster.tel = phone_num
            usermaster.research_num = research_num
            usermaster.place_of_work_id = place_of_work
            if birthday:
                usermaster.birthday = birthday
            usermaster.is_staff = True
            usermaster.is_active = True
            usermaster.created_by_id = user

            usermaster.save()

            return JsonResponse({'status': 'success'})

        elif type == 'E':
            print(request.POST)
            id = request.POST.get('id')
            usermaster = UserMaster.objects.get(id=id)

            usermaster.employment_date = datetime.strptime(request.POST.get('employment_date'), "%Y-%m-%d").date()
            usermaster.department_position_id = request.POST.get('department_select')
            usermaster.job_position_id = request.POST.get('job_select')
            usermaster.tel = request.POST.get('phone_num')
            usermaster.place_of_work_id = request.POST.get('place_of_work')
            usermaster.research_num = request.POST.get('research_num')
            birthday = request.POST.get('birthday')
            if birthday:
                usermaster.birthday = datetime.strptime(birthday, "%Y-%m-%d").date()
            usermaster.save()

            return JsonResponse({'status': 'success'})


def user_resignation(request):

    user_id = request.GET.get('id')
    update_user_id = request.user.id
    user = UserMaster.objects.get(id=update_user_id)

    usermaster = UserMaster.objects.get(id=user_id)
    usermaster.is_staff = False
    usermaster.created_by_id = user

    usermaster.save()

    return JsonResponse({'status': 'success'})

