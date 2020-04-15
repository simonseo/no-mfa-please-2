from django.conf import settings
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
import requests
import html2text

from mfa_user.tokens import account_confirmation_token

h = html2text.HTML2Text()

def send_simple_message(mail_subject:str, message:str, from_email:str, to_emails:list):
    '''
    Send an email via mailgun.
    mail_subject is plaintext string.
    message is either html or plaintext.
    from_email is either an email address or f'{ NAME } <{ EMAIL_ADDRESS }>'.
    to_emails is a list of emails.
    '''
    return requests.post(
        f"https://api.mailgun.net/v3/{settings.EMAIL_DOMAIN_NAME}/messages",
        auth=("api", settings.MAILGUN_API_KEY),
        data={"from": from_email,
              "to": to_emails,
              "subject": mail_subject,
              "html": message,
              "text": h.handle(message)})

def send_confirmation_email(domain, user):
    mail_subject = 'Confirm your account on Duo MFA Online Mirror.'
    message = render_to_string('emails/account-confirmation-email.html', {
        'domain': domain,
        'uid': urlsafe_base64_encode(force_bytes(user.email)),
        'token': account_confirmation_token.make_token(user),
    })
    from_email = f'no-reply@{domain}'
    if settings.DEBUG:
        from_email = 'no-reply@mfa.com'
    to_email = user.email

    return send_simple_message(mail_subject, message, from_email, [to_email])


def send_otp_generation_email(domain, user, otp_list):
    mail_subject = 'Your MFA Passcodes'
    message = render_to_string('emails/otp-generation-email.html', {
        'otp_list': otp_list,
    })
    from_email = f'no-reply@{domain}'
    if settings.DEBUG:
        from_email = 'no-reply@mfa.com'
    to_email = user.email

    return send_simple_message(mail_subject, message, from_email, [to_email])