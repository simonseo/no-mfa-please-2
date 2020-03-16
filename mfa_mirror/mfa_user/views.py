from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.hashers import make_password, check_password
from . import models
from collections import defaultdict

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

        # TODO Check duplicate email
        
        if not (email and password and re_password and qr_url):
            context['error']['message'] = 'Fill in all fields!'
        elif password != re_password:
            context['error']['message'] = 'Passwords don\'t match!'
        else:
            new_user = models.mfa_user(email=email, password=make_password(
                password), hotp_secret='somethinglikethis123')
            new_user.save()
            context['success']['message'] = 'Registration Successful.'

            # TODO When salting hotp_secret, it should be both encrypted and decryptable.
            # Option 1. Use a secret key in server that is not exposed to anything
            # Option 2. Use the user's password as key
            # Option 3. Use both 1 and 2

        return render(request, 'register.html', context)
