from django.contrib import admin
from mfa_user.models import mfa_user

# Register your models here.
@admin.register(mfa_user)
class MFAUserAdmin(admin.ModelAdmin):
    '''Admin View for mfa_user'''

    list_display = ('email','password','hotp_secret', 'register_dttm')
    # list_filter = ('password',)