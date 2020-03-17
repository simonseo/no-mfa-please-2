from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.hashers import make_password, check_password
from django.conf import settings
from mfa_user import models
from collections import defaultdict
from mfa_user.duo import activate, generate_hotp, encrypt

def register(request: HttpRequest):
    recursive_defaultdict = lambda: defaultdict(recursive_defaultdict)
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

            new_user = models.mfa_user(email=email, password=make_password(
                password), hotp_secret=encrypted_secret)
            # TODO Make sure hotp registration worked
            # TODO Check duplicate email without erasing all fields (possibly that's default Django behaviour)
            new_user.save()
            context['success']['message'] = 'Registration Successful.'


        return render(request, 'register.html', context)
