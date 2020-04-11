from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from collections import defaultdict

from mfa_user.models import MFAUser
from mfa_user.forms import LoginForm, RegisterForm, GenerateOtpForm
from mfa_user.emails import send_confirmation_email
from mfa_user.tokens import account_confirmation_token

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

            # user = form.save(commit=False)
            # user.is_active = False
            # user.save()
            # send_confirmation_email(request, user, form)
            return HttpResponse('Please confirm your email address to complete the registration')


            context['popup']['message'] = "Registration Successful! Check your email!"
            return redirect('/user/login', context)
            # return redirect(request, 'login.html', {'form': LoginForm()})
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
    context = recursive_defaultdict()
    if request.method == 'GET':
        form = GenerateOtpForm()
        return render(request, 'generate.html', {'form':form})

    elif request.method == 'POST':
        form = GenerateOtpForm(request.POST)
        if form.is_valid():
            pass
            # send email
            # show popup saying otp was sent to email
        else:
            return render(request, 'generate.html', {'form':form})
    return HttpResponse('hotp generation page coming soon!')

def confirm(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = MFAUser.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, MFAUser.DoesNotExist):
        user = None
    if user is None:
        return HttpResponse('User account does not exist. Try registering again.')
    # elif account_confirmation_token.check_token(user, token):
    #     return HttpResponse('Confirmation link is invalid!')
    else:
        user.is_active = True
        user.save()
        login(request, user)
        # return redirect('home')
        return HttpResponse('Thank you for your email confirmation. Now you can safely closet this tab and generate OTPs.')