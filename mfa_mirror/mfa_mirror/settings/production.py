from .base import *

DEBUG = False
ALLOWED_HOSTS = [
    'http://ec2-34-219-167-204.us-west-2.compute.amazonaws.com/', # remove this later
    'http://duo-mfa.online',
    'https://duo-mfa.online',
    ]

TIME_ZONE = 'Asia/Dubai'

# Use in production if you want to use `./manage.py collectstatic`
STATIC_ROOT = os.path.join(BASE_DIR, 'static_generated') 

# Session protection from man-in-the-middle or XSS attacks
# explanation: https://stackoverflow.com/a/28072319/6501783
# CSRF_COOKIE_SECURE = True
# SESSION_COOKIE_SECURE = True
# SESSION_COOKIE_HTTPONLY = True
# SECURE_SSL_REDIRECT = True
