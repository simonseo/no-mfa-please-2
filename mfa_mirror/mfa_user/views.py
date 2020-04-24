from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect, reverse
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.views import View
from django.views.generic.edit import FormView
from django.views.generic.base import TemplateView


from collections import defaultdict

from mfa_user.emails import send_confirmation_email, send_otp_generation_email
from mfa_user.forms import LoginForm, RegisterForm, OtpGenerationForm
from mfa_user.models import MFAUser
from mfa_user.tokens import account_confirmation_token


def recursive_defaultdict(): return defaultdict(recursive_defaultdict)


class Home(View):
    def get(self, request: HttpRequest):
        return redirect(reverse('get-started'))
        # user_id = request.session.get('user_id')
        # if user_id:
        #     mfa_user = MFAUser.objects.get(pk=user_id)
        #     return HttpResponse(mfa_user.email)
        # return HttpResponse("home page")


class GetStarted(TemplateView):
    template_name = 'pages/get-started.html'


class Login(FormView):
    form_class = LoginForm
    template_name = 'pages/login.html'
    success_url = '/'

    def get(self, request: HttpRequest):
        user_id = request.session.get('user_id')
        if user_id:
            return redirect('/')
        else:
            return super().get(request)

    def form_valid(self, form: LoginForm):
        # TODO it's kinda weird that the form gives user_id. change it.
        request.session['user_id'] = form.user_id
        return super().form_valid(form)


class Logout(View):
    def get(self, request: HttpRequest):
        del request.session['user_id']
        return redirect('/')


class Register(FormView):
    form_class = RegisterForm
    template_name = 'pages/register.html'

    # TODO Allow three types of input: QR URL, Content of QR Code, QR Code image (which might be downloaded or photographed)

    def form_invalid(self, form):
        # seems to be equivalent to `return render(self.request, self.template_name, {'form': form})`
        return super().form_invalid(form)

    def form_valid(self, form: RegisterForm):
        domain: str = get_current_site(self.request).domain
        new_user = form.user

        try:
            email = send_confirmation_email(domain, new_user)
        except Exception as e:
            if settings.DEBUG:
                print('Exception while sending confirmation email', e)
            modal = {
                'title': 'Oops! A Problem!',
                'body': 'There was a problem while singing you up. Please check your details and try again. You will need to create a new QR code to register again.',
                'fade': False,
            }
        else:
            modal = {
                'title': 'Registration Almost Complete!',
                'body': 'We sent a confirmation email to your email address. Follow the instructions in the email to complete the registration. Make sure to check the spam folder if the email doesn\'t arrive within a few minutes.',
                'fade': False,
            }

        # return super().form_valid(form) # this just redirects to success_url
        return self.render_to_response(self.get_context_data(form=form, modal=modal))


class Generate(FormView):
    form_class = OtpGenerationForm
    template_name = 'pages/generate.html'

    def form_valid(self, form):
        # send email with otp
        domain = get_current_site(self.request).domain
        try:
            email = send_otp_generation_email(
                domain, form.user, form.otp_list)
        except Exception as e:
            if settings.DEBUG:
                print('Exception while sending otp generation email', e)
            modal = {
                'title': 'Oops! A Problem!',
                'body': 'There was a problem while generating your passcodes. Please check your details and try again.',
                'fade': False,
            }
        else:
            modal = {
                'title': 'Passcodes Generated',
                'body': 'Check your inbox! We sent the passcodes to your email. \
                        Make sure to check the spam folder if the email doesn\'t arrive within a few minutes.',
                'fade': False,
            }
        
        # return super().form_valid(form) # this only redirects to self.success_url
        # return render(self.request, self.template_name, {'form': self.form_class(), 'modal': modal}) # equivalent to below
        return self.render_to_response(self.get_context_data(form=form, modal=modal))


class Confirm(View):
    def get(self, request: HttpRequest, uidb64, token):
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
