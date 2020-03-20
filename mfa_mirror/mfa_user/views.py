from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from collections import defaultdict
from mfa_user.models import MFAUser
from mfa_user.forms import LoginForm, RegisterForm

recursive_defaultdict = lambda: defaultdict(recursive_defaultdict)

def home(request: HttpRequest):
    user_id = request.session.get('user_id')
    if user_id:
        mfa_user = MFAUser.objects.get(id=user_id)
        return HttpResponse(mfa_user.email) 
    return HttpResponse("home page")


def register(request: HttpRequest):
    context = recursive_defaultdict()

    if request.method == 'GET':
        form = RegisterForm()
        return render(request, 'register.html', {'form':form})
    elif request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            return redirect(request, 'login.html', {'form': LoginForm()})
        # TODO Allow three types of input: QR URL, Content of QR Code, QR Code image (which might be downloaded or photographed)
        return render(request, 'register.html', {'form':form})



def login(request: HttpRequest):
    context = recursive_defaultdict()
    if request.method == 'GET':
        user_id = request.session.get('user_id')
        if user_id:
            return redirect('/')
        else:
            form = LoginForm()
            return render(request, 'login.html', {'form':form})

    elif request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            # TODO it's kinda weird that the form gives user_id. change it.
            request.session['user_id'] = form.user_id 
            return redirect('/')
        else:
            return render(request, 'login.html', {'form':form})

def logout(request: HttpRequest):
    del request.session['user_id']
    return redirect('/')

def generate(request: HttpRequest):
    return HttpResponse('hotp generation page coming soon!')