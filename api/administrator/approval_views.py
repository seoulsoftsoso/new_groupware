from django.http import JsonResponse
from django.views.generic import ListView

from Pagenation import PaginatorManager
from api.models import UserMaster
from api.views import get_department_info, get_job_info, get_pow_info


class ApprovalDeletePageView(ListView):
    template_name = 'admins/administrator/approval_delete.html'
    paginate_by = 15

    def get_queryset(self):
        result = UserMaster.objects.filter(is_master=False).values(
            'id', 'user_id', 'code', 'username', 'email', 'is_master', 'is_active', 'is_staff',
            'created_at', 'department_position__name', 'job_position__name'
        ).order_by('-id')

        return result

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        department_info = get_department_info()
        job_info = get_job_info()
        pow_info = get_pow_info()
        context['department_info'] = department_info['department_info']
        context['job_info'] = job_info['job_info']
        context['pow_info'] = pow_info['pow_info']
        context['result'] = context['object_list']
        context['page_range'], context['contacts'] = PaginatorManager(self.request, self.get_queryset())
        return context


def user_approval(request):
    if request.method == 'POST':
        user_id = request.POST.get('id')
        employment_date = request.POST.get('employment_date')
        department_select = request.POST.get('department_select')
        job_select = request.POST.get('job_select')
        phone_num = request.POST.get('phone_num')
        research_num = request.POST.get('research_num')
        update_user_id = request.COOKIES['user_id']
        user = UserMaster.objects.get(id=update_user_id)

        usermaster = UserMaster.objects.get(id=user_id)

        usermaster.employment_date = employment_date
        usermaster.department_position_id = department_select
        usermaster.job_position_id = job_select
        usermaster.tel = phone_num
        usermaster.is_staff = True
        usermaster.is_active = True
        usermaster.created_by_id = user

        usermaster.save()

        return JsonResponse({'status': 'success'})


def user_resignation(request):

    user_id = request.GET.get('id')
    update_user_id = request.COOKIES['user_id']
    user = UserMaster.objects.get(id=update_user_id)

    usermaster = UserMaster.objects.get(id=user_id)
    usermaster.is_staff = False
    usermaster.created_by_id = user

    usermaster.save()

    return JsonResponse({'status': 'success'})

