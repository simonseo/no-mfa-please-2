from django.contrib import admin
from mfa_user.models import MFAUser

# Register your models here.
@admin.register(MFAUser)
class MFAUserAdmin(admin.ModelAdmin):
    '''Admin View for MFAUser'''

    list_display = (
        'email',
        'is_confirmed',
        'hotp_count', 
        'register_dttm', 
        'password',
        'hotp_secret',
        )
    # list_filter = ('password',)