from django import forms
from django.contrib.auth.hashers import check_password
from mfa_user.models import MFAUser


class RegisterForm(forms.Form):
    """RegisterForm definition."""
    email = forms.EmailField(label="Email address", required=True, error_messages={
                             'required': 'Better give me your email!',
                             })
    password = forms.CharField(label="Password", required=True, widget=forms.PasswordInput,
                               help_text={
                                   'message': 'Password should be at least 6 characters long.',
                               }, min_length=6)
    re_password = forms.CharField(
        label="Re-enter Password", required=True, widget=forms.PasswordInput)
    qr_url = forms.URLField(label='Duo MFA QR Code Image URL', required=False, help_text={
                            'message': 'How to get this information', 'url': '#'})
    # qr_content = forms.CharField(label='Decoded Content of QR Code', required=False)
    # qr_image = forms.FileField(label='QR Code Image', allow_empty_file=True, required=False)
    submit_button_label = 'Register'

    def clean(self):
        '''Validate RegisterForm'''
        return super().clean()


class LoginForm(forms.Form):
    """LoginForm definition."""

    email = forms.EmailField(label="Email address", required=True, error_messages={
                             'required': 'Better give me your email!',
                             })
    password = forms.CharField(label="Password", required=True, widget=forms.PasswordInput,
                               help_text={
                                   'message': 'the best way to construct a good password!',
                                   'url': 'https://naver.com',
                               })
    password.help_url = 'https://naver.com'  # this attribute cannot be read from
    submit_button_label = 'Log in'

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError('Could not read email address.')
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not password:
            raise forms.ValidationError('Could not read password.')
        return password

    def clean(self):
        '''Validate LoginForm'''
        super().clean()

        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        # Email registered validation
        try:
            mfa_user = MFAUser.objects.get(email=email)
        except MFAUser.DoesNotExist:
            print('Email does not exist on system.')
            self.add_error('email', forms.ValidationError(
                'Email does not exist on system.'))
        except Exception as e:
            print('Unknown error while retrieving user information.')
            raise forms.ValidationError(
                'Unknown error while retrieving user information.')
        else:
            # Password validation
            if not check_password(password, mfa_user.password):
                print('Wrong password Entered.')
                self.add_error('password', forms.ValidationError(
                    'Wrong password Entered.'))
            else:
                self.user_id = mfa_user.id
