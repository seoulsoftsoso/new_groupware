from django.contrib import auth
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView
import logging

from rest_framework.exceptions import ValidationError

from api.board import SignUpForm, QuestionForm
from api.models import UserMaster


def index(request):
    return render(request, 'index.html', {})


def admin_index_page(request):
    context = {}
    context['block'] = ''
    return render(request, 'admins/index.html', context)


def login_page(request):
    return render(request, 'login.html', {})


def logout_view(request):
    auth.logout(request)
    return redirect('index')


def signup_page(request):
    return render(request, 'registration/signup.html', {})


def UserCreate(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)  # UserCreationForm 객체를 생성하도록 수정
        if form.is_valid():
            form.save()
            print('데이터 통신 성공')
        else:
            raise ValidationError('관리자에게 문의 바랍니다.')

    return render(request, 'index.html')


@csrf_exempt
def check_duplicate(request):
    if request.method == "POST":
        user_id = request.POST.get("user_id", None)
        print('아이디', user_id)

        id_check = UserMaster.objects.filter(user_id=user_id).count()
        print('매칭 레코드 수:', id_check)

        is_duplicate = id_check > 0
        return JsonResponse({"is_duplicate": is_duplicate})

    return JsonResponse({"error": "Invalid request method"})


def register_page(request):
    return render(request, 'register.html', {})


def register_ok(request):
    return render(request, 'register_ok.html', {})


def SubView(request, menu_num):
    menucode1 = menu_num[:2]
    menucode2 = menu_num[2:]
    filename = 'sub/menu' + menucode1 + '/menu' + menucode1 + '_' + menucode2 + '.html'
    # filename = 'sub/menu01/menu01_01.html'
    print(filename)
    return render(request, filename, {'menucode1': menucode1, 'menucode2': menucode2})


def submit_question(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            form.save()
            print('데이터 통신 성공')
        else:
            raise ValidationError('관리자에게 문의 바랍니다.')

    return render(request, 'sub/menu01/menu01_06.html')
