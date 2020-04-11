from django.db import models

class MFAUser(models.Model):
    """Model definition for user."""
    email = models.EmailField(max_length=254, verbose_name='User Email Address', unique=True)
    password = models.CharField(max_length=254, verbose_name='Hashed User Password')
    hotp_secret = models.CharField(max_length=254, verbose_name='Hashed HOTP Secret')
    hotp_count = models.IntegerField(verbose_name='Current HOTP Counter Value', default=0)
    register_dttm = models.DateTimeField(auto_now_add=True, verbose_name='Timestamp of Registration')
    is_confirmed = models.BooleanField(verbose_name="Whether Account is Confirmed", default=False)

    class Meta:
        """Meta definition for user."""
        db_table = 'mfa_users'
        verbose_name = 'Registered User'
        verbose_name_plural = 'Registered Users'

    def __str__(self):
        """Unicode representation of user."""
        return '{}'.format(self.email)
