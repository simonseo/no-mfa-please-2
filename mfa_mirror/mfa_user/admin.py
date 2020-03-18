from django.contrib import admin
from mfa_user.models import MFAUser

# Register your models here.
@admin.register(MFAUser)
class MFAUserAdmin(admin.ModelAdmin):
    '''Admin View for MFAUser'''

    list_display = ('email','password','hotp_secret', 'register_dttm')
    # list_filter = ('password',)