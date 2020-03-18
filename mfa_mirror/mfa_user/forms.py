from django import forms
from django.contrib.auth.hashers import check_password
from mfa_user.models import MFAUser

class LoginForm(forms.Form):
    """LoginForm definition."""

    email = forms.EmailField(required=True, error_messages={'required':'Better give me your email!'})
    password = forms.CharField(required=True, widget=forms.PasswordInput)

    def clean(self):
        super().clean()

        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        # Sanity check
        if not (email and password):
            print('Could not read email address and/or password.')
            raise forms.ValidationError('Could not read email address and/or password.')
        
        # Email registered validation
        try:
            mfa_user = MFAUser.objects.get(email=email)
        except MFAUser.DoesNotExist:
            print('Email does not exist on system.')
            self.add_error('email', forms.ValidationError('Email does not exist on system.'))
        except Exception as e:
            print('Unknown error while retrieving user information.')
            raise forms.ValidationError('Unknown error while retrieving user information.')
        else:
            # Password validation
            if not check_password(password, mfa_user.password):
                print('Wrong password Entered.')
                self.add_error('password', forms.ValidationError('Wrong password Entered.'))
            else:
                self.user_id = mfa_user.id


    