from .base import *

DEBUG = False
ALLOWED_HOSTS = [
    '*'
]
TIME_ZONE = 'Asia/Dubai'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static/')
]
# Use in production if you want to use `./manage.py collectstatic`
STATIC_ROOT = os.path.join(BASE_DIR, 'static_generated')
