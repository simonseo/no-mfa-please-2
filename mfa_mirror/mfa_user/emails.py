from django.conf import settings
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

from mfa_user.tokens import account_confirmation_token


def create_confirmation_email(domain, user):
    mail_subject = 'Confirm your account on Duo MFA Online Mirror.'
    message = render_to_string('account-confirmation-email.html', {
        'domain': domain,
        'uid': urlsafe_base64_encode(force_bytes(user.email)),
        'token': account_confirmation_token.make_token(user),
    })
    from_email = f'no-reply@{domain}'
    if settings.DEBUG:
        from_email = 'no-reply@mfa.com'
    to_email = user.email

    email = EmailMessage(
        mail_subject, message, from_email=from_email, to=[to_email]
    )
    if settings.DEBUG:
        print(f'email.body={email.body}')
    return email

def create_otp_generation_email(domain, user, otp_list):
    mail_subject = 'Your MFA Passcodes'
    message = render_to_string('otp-generation-email.html', {
        'otp_list': otp_list,
    })
    from_email = f'no-reply@{domain}'
    if settings.DEBUG:
        from_email = 'no-reply@mfa.com'
    to_email = user.email

    email = EmailMessage(
        mail_subject, message, from_email=from_email, to=[to_email]
    )
    if settings.DEBUG:
        print(f'email.body={email.body}')
    return email