from django import forms
from django.contrib.auth.hashers import make_password, check_password
from django.conf import settings
from mfa_user.models import MFAUser
from mfa_user import duo
# import activate, generate_hotp, encrypt


class RegisterForm(forms.Form):
    """RegisterForm definition."""
    email = forms.EmailField(label="Email address", required=True, 
                                error_messages={'required': 'Better give me your email!'}, 
                                help_text={'placeholder': 'example@company.com'})
    password = forms.CharField(label="Password", required=True, widget=forms.PasswordInput,
                               help_text={
                                   'message': 'Password should be at least 6 characters long.',
                               }, min_length=6)
    re_password = forms.CharField(
        label="Re-enter Password", required=True, widget=forms.PasswordInput)
    qr_url = forms.URLField(label='Duo MFA QR Code Image URL', required=False, help_text={
                            'placeholder': 'api-1234.duosecurity.com/frame/qr?value=SomeValue123',
                            'message': 'How to get this information', 
                            'url': '#'})
    # qr_content = forms.CharField(label='Decoded Content of QR Code', required=False)
    # qr_image = forms.FileField(label='QR Code Image', allow_empty_file=True, required=False)
    submit_button_label = 'Register'

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError('Could not read email address.')
        try:
            MFAUser.objects.get(email=email)
        except MFAUser.DoesNotExist:
            return email
        else:
            raise forms.ValidationError('Email address already exists!')

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not password:
            raise forms.ValidationError('Could not read password.')
        return password

    def clean_re_password(self):
        password = self.cleaned_data.get('password')
        re_password = self.cleaned_data.get('re_password')
        if not re_password:
            raise forms.ValidationError(
                'Could not read re-entered password.')
        if password != re_password:
            raise forms.ValidationError('Passwords don\'t match!')

        return re_password

    def clean_qr_url(self):
        qr_url = self.cleaned_data.get('qr_url')
        if not qr_url:
            raise forms.ValidationError('Could not read URL of QR code image.')

        # Make sure hotp registration worked
        try:
            self.hotp_secret = duo.activate(qr_url)
        except Exception as e:
            if settings.DEBUG:
                print(e)
            raise forms.ValidationError(
                'Failed to activate Duo MFA from the QR code URL. {}'.format(e))
        return qr_url

    def clean(self):
        '''Validate RegisterForm'''
        return super().clean()
        # TODO Allow three types of input: QR URL, Content of QR Code, QR Code image (which might be downloaded or photographed)
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        re_password = self.cleaned_data.get('re_password')
        qr_url = self.cleaned_data.get('qr_url')

        encrypted_secret = duo.encrypt(
            self.hotp_secret, password, settings.SECRET_KEY)

        new_user = MFAUser(email=email, password=make_password(
            password), hotp_secret=encrypted_secret)
        new_user.save()


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
