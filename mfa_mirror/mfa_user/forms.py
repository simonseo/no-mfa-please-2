from django import forms
from django.contrib.auth.hashers import make_password, check_password
from django.conf import settings
from mfa_user.models import MFAUser
from mfa_user import duo
# import activate, generate_hotp, encrypt


class RegisterForm(forms.Form):
    """RegisterForm definition."""
    email = forms.EmailField(label="Email address", required=True,
                             error_messages={
                                 'required': 'Better give me your email!'},
                             help_text={'placeholder': 'example@company.com'})
    password = forms.CharField(label="Password", required=True, widget=forms.PasswordInput,
                               help_text={
                                   'message': 'Password should be at least 6 characters long.',
                               }, min_length=6)
    re_password = forms.CharField(
        label="Re-enter Password", required=True, widget=forms.PasswordInput)
    qr_url = forms.URLField(label='Duo MFA QR Code Image URL', required=False, help_text={
                            'placeholder': 'api-1234.duosecurity.com/frame/qr?value=SomeValue123',
                            'message': 'Right-click or long press the QR code. Choose "Copy Image Address"',
                            'url': '#'
                            })
    qr_content = forms.CharField(label='Decoded Content of QR Code', required=False, help_text={
        'placeholder': 'VeryLongText-MoreLongText',
        'message': 'Click "Email me an activation link instead." OR scan the QR code with your smartphone camera app.',
        'url': '#'
    })
    # qr_image = forms.FileField(label='QR Code Image', allow_empty_file=False, required=False)
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
            if settings.DEBUG:
                print("Email already exists!")
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
        if password != re_password and not self.errors.get('password'):
            raise forms.ValidationError('Passwords don\'t match!')

        return re_password

    def clean_qr_url(self):
        qr_url = self.cleaned_data.get('qr_url')
        if not qr_url:
            # raise forms.ValidationError('Could not read URL of QR code image.')
            print(type(qr_url))
            return qr_url

        # Make sure hotp registration worked
        try:
            self.hotp_secret = duo.activate(qr_url=qr_url)
        except Exception as e:
            if settings.DEBUG:
                print(e)
                raise forms.ValidationError('Failed to activate Duo MFA from the QR code URL. {}'.format(e))
            raise forms.ValidationError('Failed to activate Duo MFA from the QR code URL.')
        return qr_url

    def clean_qr_content(self):
        qr_content = self.cleaned_data.get('qr_content')
        if not qr_content:
            return qr_content

        # Make sure hotp registration worked
        try:
            self.hotp_secret = duo.activate(payload=qr_content)
        except Exception as e:
            if settings.DEBUG:
                print(e)
                raise forms.ValidationError('Failed to activate Duo MFA using the given value. {}'.format(e))
            raise forms.ValidationError('Failed to activate Duo MFA using the given value.')
        return qr_content

    def clean(self):
        '''Validate RegisterForm'''
        super().clean()
        # TODO Allow three types of input: QR URL, Content of QR Code, QR Code image (which might be downloaded or photographed)
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        re_password = self.cleaned_data.get('re_password')
        qr_url = self.cleaned_data.get('qr_url')
        qr_content = self.cleaned_data.get('qr_content')

        if not qr_url and not qr_content:
            for field in 'qr_url', 'qr_content':
                self.add_error(field, forms.ValidationError('Either provide a proper URL of QR code or Activation Code.'))
            return

        if self.errors:
            return

        # TODO Move the below functionality to a separate module
        encrypted_secret = duo.encrypt(
            self.hotp_secret, password, settings.SECRET_KEY)

        new_user = MFAUser(email=email, password=make_password(
            password), hotp_secret=encrypted_secret) #, is_confirmed=False)
        if settings.DEBUG:
            print(email, password, re_password, qr_url, qr_content)
        new_user.save()
        self.user = new_user


class LoginForm(forms.Form):
    """LoginForm definition."""

    email = forms.EmailField(label="Email address", required=True, error_messages={
                             'required': 'Better give me your email!',
                             })
    password = forms.CharField(label="Password", required=True, widget=forms.PasswordInput,
                               help_text={
                                   'message': 'Password should be at least 6 characters long.',
                               })
    # password.help_url = 'https://naver.com'  # this attribute cannot be read from
    submit_button_label = 'Log in'

    # def clean_email(self):
    #     email = self.cleaned_data.get('email')
    #     if not email:
    #         raise forms.ValidationError('Could not read email address.')
    #     return email

    # def clean_password(self):
    #     password = self.cleaned_data.get('password')
    #     if not password:
    #         raise forms.ValidationError('Could not read password.')
    #     return password

    def clean(self):
        '''Validate LoginForm'''
        super().clean()

        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if not email or not password:
            return

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
            # elif :
                # TODO Check if account has been confirmed

            else:
                self.user_id = mfa_user.id


class GenerateOtpForm(forms.Form):
    """GenerateOtpForm definition."""

    email = forms.EmailField(label="Email address", required=True, error_messages={
                             'required': 'Better give me your email!',
                             })
    password = forms.CharField(label="Password", required=True, widget=forms.PasswordInput,
                               help_text={
                                   'message': 'Password should be at least 6 characters long.',
                               })
    submit_button_label = 'Generate'

    def clean(self):
        '''Validate LoginForm'''
        super().clean()

        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if not email or not password:
            return

        # Existence validation
        try:
            mfa_user = MFAUser.objects.get(email=email)
        except MFAUser.DoesNotExist:
            if settings.DEBUG:
                print('Email does not exist on system.')
            self.add_error('email', forms.ValidationError(
                'Email does not exist on system.'))
            return
        except Exception as e:
            if settings.DEBUG:
                print(f'Unknown error while retrieving user information. {e}')
            raise forms.ValidationError(
                'Unknown error while retrieving user information.')
            return

        # Password validation
        if not check_password(password, mfa_user.password):
            if settings.DEBUG:
                print('Wrong password Entered.')
            self.add_error('password', forms.ValidationError(
                'Wrong password Entered.'))
        
        # Confirmation check
        if not mfa_user.is_confirmed:
            raise forms.ValidationError('Account is not confirmed yet. Check your inbox first.')
        
        if self.errors:
            return

        # TODO Move following functionality to separate module
        # decrypt otp key using user password and server secret key
        # generate otp and increment counter
        hotp_secret = duo.decrypt(mfa_user.hotp_secret, password, settings.SECRET_KEY)
        n = 1
        otp_list = duo.generate_hotp(hotp_secret, current_at=mfa_user.hotp_count, n=n)
        mfa_user.hotp_count += n
        mfa_user.save()
        self.user = mfa_user
        self.otp_list = otp_list

        if settings.DEBUG:
            print(f'otp_list={otp_list}')
