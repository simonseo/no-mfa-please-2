from django.contrib.auth.tokens import PasswordResetTokenGenerator

class _TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return str(user.email) + str(timestamp) + str(user.is_confirmed)
account_confirmation_token = _TokenGenerator()