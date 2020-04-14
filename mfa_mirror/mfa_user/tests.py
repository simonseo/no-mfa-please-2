from django.test import TestCase
from django.core import mail

from mfa_user.models import MFAUser
from mfa_user.emails import create_confirmation_email 

class EmailTestCase(TestCase):
    def setUp(self):
        pass

    def test_confirmation_email_content(self):
        """Confirmation email is correctly drafted"""
        user = MFAUser(email='simonseo.doubles@gmail.com', password='asdf')
        message = create_confirmation_email('naver.com', user)
        expected = '\nWelcome,\n\nPlease click on the link below to confirm your registration.\n\nhttps://naver.com/user/confirm/Tm9uZQ/5fk-fc7556eee5a36359ec16/\n\n'
        
        self.assertEqual(expected[:103], message.body[:103])
        self.assertNotEqual(expected[103:], message.body[103:])

    def test_send_email(self):
        mail.send_mail('Subject here', 'Here is the message.',
            'from@example.com', ['to@example.com'],
            fail_silently=False)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Subject here')

# Create your tests here.
# from django.contrib.auth.models import AnonymousUser, User
# from django.test import TestCase, RequestFactory

# from .views import index

# class SimpleTest(TestCase):
#     def setUp(self):
#         # Every test needs access to the request factory.
#         self.factory = RequestFactory()

#     def test_details(self):
#         # Create an instance of a GET request.
#         request = self.factory.get('/')
#         request.user = AnonymousUser()

#         # Test my_view() as if it were deployed at /customer/details
#         response = index(request)
#         self.assertEqual(response.status_code, 200)