
from django.shortcuts import render



def index(request):
    return render(request, 'index.html', {})


def login_page(request):
    return render(request, 'registration/login.html', {})


def register_page(request):
    return render(request, 'register.html', {})


def register_ok(request):
    return render(request, 'register_ok.html', {})

def SubView(request, menu_num):
    menucode1 = menu_num[:2]
    menucode2 = menu_num[2:]
    filename = 'sub/menu' + menucode1 + '/menu' + menucode1 + '_' + menucode2 + '.html'
    #filename = 'sub/menu01/menu01_01.html'
    print(filename)
    return render(request, filename, {'menucode1': menucode1, 'menucode2': menucode2})


