from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.hashers import make_password, check_password
from django.conf import settings
from mfa_user.models import MFAUser
from collections import defaultdict
from mfa_user.duo import activate, generate_hotp, encrypt

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
        return render(request, 'register.html')
    elif request.method == 'POST':
        email = request.POST.get('user-email', None)
        password = request.POST.get('user-password', None)
        re_password = request.POST.get('user-re-password', None)
        qr_url = request.POST.get('user-qr-url', None)

        # TODO Allow three types of input: QR URL, Content of QR Code, QR Code image (which might be downloaded or photographed)
        # TODO Use form validation
        if not (email and password and re_password and qr_url):
            context['error']['message'] = 'Fill in all fields!'
        elif password != re_password:
            context['error']['message'] = 'Passwords don\'t match!'
        else:
            hotp_secret = activate(qr_url)
            encrypted_secret = encrypt(hotp_secret, password, settings.SECRET_KEY)

            new_user = MFAUser(email=email, password=make_password(
                password), hotp_secret=encrypted_secret)
            # TODO Make sure hotp registration worked
            # TODO Check duplicate email without erasing all fields (possibly that's default Django behaviour)
            new_user.save()
            context['success']['message'] = 'Registration Successful.'


        return render(request, 'register.html', context)

def login(request: HttpRequest):
    context = recursive_defaultdict()
    if request.method == 'GET':
        user_id = request.session.get('user_id')
        if user_id:
            return redirect('/')
        else:
            return render(request, 'login.html')
    elif request.method == 'POST':
        email = request.POST.get('user-email')
        password = request.POST.get('user-password')

        if not (email and password):
            context['error']['message'] = "Fill in all fields!"
        else:
            try:
                mfa_user = MFAUser.objects.get(email=email)
            except MFAUser.DoesNotExist:
                context['error']['message'] = "Email does not exist"
            else:
                if not check_password(password, mfa_user.password):
                    context['error']['message'] = "Password is incorrect"

        if context['error']:
            return render(request, 'login.html', context)
        else:
            request.session['user_id'] = mfa_user.id
            return redirect('/')

def logout(request: HttpRequest):
    del request.session['user_id']
    return redirect('/')

def generate(request: HttpRequest):
    return HttpResponse('hotp generation page coming soon!')