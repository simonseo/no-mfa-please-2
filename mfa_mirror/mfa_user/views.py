from django.shortcuts import render, redirect, reverse
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpRequest, HttpResponse
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from collections import defaultdict

from mfa_user.models import MFAUser
from mfa_user.forms import LoginForm, RegisterForm, GenerateOtpForm
from mfa_user.emails import create_confirmation_email, create_otp_generation_email
from mfa_user.tokens import account_confirmation_token

recursive_defaultdict = lambda: defaultdict(recursive_defaultdict)

def home(request: HttpRequest):
    user_id = request.session.get('user_id')
    if user_id:
        mfa_user = MFAUser.objects.get(pk=user_id)
        return HttpResponse(mfa_user.email) 
    return HttpResponse("home page")


def register(request: HttpRequest):
    context = recursive_defaultdict()

    if request.method == 'GET':
        form = RegisterForm()
        # TODO Allow three types of input: QR URL, Content of QR Code, QR Code image (which might be downloaded or photographed)
        return render(request, 'pages/register.html', {'form': form})
    elif request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            domain = get_current_site(request).domain
            new_user = form.user
            email = create_confirmation_email(domain, new_user)
            email.send()
            modal = {
                'title': 'Registration Almost Complete!',
                'body': 'We sent a confirmation email to your email address. Click the link in the email to complete the registration.',
                'fade': False,
            }
            return render(request, 'pages/register.html', {'form': form, 'modal': modal})
        return render(request, 'pages/register.html', {'form': form})



def login(request: HttpRequest):
    context = recursive_defaultdict()
    if request.method == 'GET':
        user_id = request.session.get('user_id')
        if user_id:
            return redirect('/')
        else:
            form = LoginForm()
            return render(request, 'pages/login.html', {'form':form})

    elif request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            # TODO it's kinda weird that the form gives user_id. change it.
            request.session['user_id'] = form.user_id 
            return redirect('/')
        else:
            return render(request, 'pages/login.html', {'form':form})

def logout(request: HttpRequest):
    del request.session['user_id']
    return redirect('/')

def generate(request: HttpRequest):
    context = recursive_defaultdict()
    if request.method == 'GET':
        form = GenerateOtpForm()
        return render(request, 'pages/generate.html', {'form':form})

    elif request.method == 'POST':
        form = GenerateOtpForm(request.POST)
        if form.is_valid():
            # send email with otp
            domain = get_current_site(request).domain
            email = create_otp_generation_email(domain, form.user, form.otp_list)
            email.content_subtype = "html"
            email.send()
            # TODO show popup saying otp was sent to email

            modal = {
                'title': 'Passcodes Generated',
                'body': 'Check your inbox! We sent the passcodes to your email. \
                        Make sure to check the spam folder if the email doesn\'t arrive within a few minutes.',
                'fade': False,
            }
            return render(request, 'pages/generate.html', {'form':GenerateOtpForm(), 'modal':modal})
        else:
            return render(request, 'pages/generate.html', {'form':form})

def confirm(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = MFAUser.objects.get(email=uid)
    except(TypeError, ValueError, OverflowError, MFAUser.DoesNotExist):
        user = None
    if user is None:
        return HttpResponse('User account does not exist. Try registering again.')
    elif account_confirmation_token.check_token(user, token):
        user.is_confirmed = True
        user.save()
        # login(request, user)
        # return redirect('/')
        return HttpResponse('Thank you for your email confirmation. Now you can safely closet this tab and generate OTPs on our website.')
    else:
        return HttpResponse('Confirmation link is invalid!')
