
from django.shortcuts import render



def index(request):
    return render(request, 'index.html', {})


def login_page(request):
    return render(request, 'login.html', {})


def register_page(request):
    return render(request, 'register.html', {})


def register_ok(request):
    return render(request, 'register_ok.html', {})


# 작성자 : 홍재성
def menu0101(request):
    return render(request, 'sub/menu01/menu01_01.html', {})


def menu0102(request):
    return render(request, 'sub/menu01/menu01_02.html', {})


def menu0103(request):
    return render(request, 'sub/menu01/menu01_03.html', {})


def menu0104(request):
    return render(request, 'sub/menu01/menu01_04.html', {})


def menu010402(request):
    return render(request, 'sbu/menu01/menu01_0402.html', {})
