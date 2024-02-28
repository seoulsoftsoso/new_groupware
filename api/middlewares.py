from django.db.models import ProtectedError
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect


class ProtectedErrorTo4xx:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        if type(exception) is ProtectedError:
            return HttpResponseBadRequest('["사용중입니다. 세부 혹은 하위 항목들을 먼저 삭제하시기 바랍니다."]')

        return None


class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admins/'):
            if not request.user.is_staff:
                return redirect('/login/')

            # 휴가관리/연차조정
            if request.path == '/admins/holiday_adjustment':
                if not request.user.is_superuser:
                    return redirect('/admins/index')

            # ADMINS/가입승인/탈퇴
            if request.path == '/admins/approval_delete_page':
                if not request.user.is_superuser:
                    return redirect('/admins/index')

            # ADMINS/견적문의
            if request.path == '/admins/pay_question_page':
                if not request.user.is_superuser:
                    return redirect('/admins/index')

        response = self.get_response(request)
        return response
