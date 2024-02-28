from django.contrib.auth import logout
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.views import LogoutView
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from api.models import UserMaster, FileBoardMaster, sign_upload_path


class UserSettingsPage(View):
    template_name = 'admins/administrator/user_setting/user_setting.html'

    def get(self, request, *args, **kwargs):
        user_id = request.user.id

        user = UserMaster.objects.get(id=user_id)

        context = {
            'result': user,
        }

        return render(request, self.template_name, context)


def change_password(request):
    if request.method == 'POST':
        user_id = request.user.id
        now_password = request.POST.get('now_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirmPassword')

        userMaster = UserMaster.objects.get(id=user_id)

        if not check_password(now_password, userMaster.password):
            return JsonResponse({'status': 'fail', 'msg': '현재 패스워드가 맞지 않습니다.'})

        userMaster.password = make_password(new_password)
        userMaster.save()
        LogoutView.as_view()

        return JsonResponse({'status': 'success'})


def signature_img_upload(request):
    if request.method == 'POST':
        file_obj = request.FILES['signature']
        employee = UserMaster.objects.get(id=request.user.id)
        employee.signature_file_path = file_obj
        employee.save()
        return JsonResponse({'message': 'success'}, status=200)

    return JsonResponse({'error': 'fail'}, status=400)

