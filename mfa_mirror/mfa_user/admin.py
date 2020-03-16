from django.contrib import admin
from .models import mfa_user

# Register your models here.
@admin.register(mfa_user)
class MFAUserAdmin(admin.ModelAdmin):
    '''Admin View for mfa_user'''

    list_display = ('email',)
    # list_filter = ('password',)