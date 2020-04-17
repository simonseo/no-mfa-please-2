from .base import *

DEBUG = False
ALLOWED_HOSTS = [
        '.compute.amazonaws.com',
        '.duo-mfa.online',
    ]
TIME_ZONE = 'Asia/Dubai'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static/')
]
# Use in production if you want to use `./manage.py collectstatic`
STATIC_ROOT = os.path.join(BASE_DIR, 'static_generated') 

# Session protection from man-in-the-middle or XSS attacks
# explanation: https://stackoverflow.com/a/28072319/6501783
# CSRF_COOKIE_SECURE = True
# SESSION_COOKIE_SECURE = True
# SESSION_COOKIE_HTTPONLY = True
# SECURE_SSL_REDIRECT = True
