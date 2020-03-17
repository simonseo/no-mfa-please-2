import pyotp
import requests
import base64
import json
import sys
import inspect
from os.path import dirname, join, abspath
from os import getenv
from urllib import parse
from django.conf import settings


def _get_payload(qr_url):
	# URL originally looks like https://api-e4c9863e.duosecurity.com/frame/qr?value=UQ1zdmSrJ9RTjuAGOymc-YXBpLWU0Yzk4NjNlLmR1b3NlY3VyaXR5LmNvbQ
	# get ?value=XXX; this is the payload represented by the QR Code
	try:
		payload = parse.unquote(qr_url.split('?value=')[1]) 
	except IndexError:
		raise RuntimeError("QR URL is not in proper format.")
	except Exception as e:
		raise e
	else:
		return payload

def _get_activation_url(payload):
	"""Interpret QR Code URL to get activation URL"""
	# --- Create request URL
	try:
		code, hostb64 = payload.split('-')
		code = code.replace('duo://', '') # first half of value is the activation code
		host = base64.b64decode(hostb64 + '='*(-len(hostb64) % 4)).decode("utf-8") # second half of value is the hostname in base64. Same as "api-e4c9863e.duosecurity.com"
		activation_url = 'https://{host}/push/v2/activation/{code}'.format(host=host, code=code) # this api is not publicly known
	except IndexError:
		raise RuntimeError("QR code payload is not in proper format.")
	except Exception as e:
		raise e
	else:
		return activation_url

def _request_activate(activation_url):
	'''Activates through activation url and returns HOTP key '''
	# --- Get response which will be a JSON of secret keys, customer names, etc.
	# --- Expected Response: {'response': {'hotp_secret': 'blahblah123', ...}, 'stat': 'OK'}
	# --- Expected Error: {'code': 40403, 'message': 'Unknown activation code', 'stat': 'FAIL'}
	try:
		response = requests.post(activation_url)
		response_dict = json.loads(response.text)
		if settings.DEBUG:
			print(response_dict)
		if response_dict['stat'] == 'FAIL':
			raise Exception("The given URL is invalid. Try a new QR/Activation URL")
		hotp_secret = response_dict['response']['hotp_secret']
	except ConnectionError as e:
		raise e
	except KeyError:
		raise Exception("Response is in unexpected format: {}".format(response.text))
	except Exception as e:
		raise e
	else:
		return hotp_secret

def activate(qr_url: str) -> str:
	'''Activates a new HOTP Key'''
	payload = _get_payload(qr_url) # getting payload can be done in other ways
	activation_url = _get_activation_url(payload)
	if settings.DEBUG:
		print(activation_url)
	hotp_secret = _request_activate(activation_url)
	return hotp_secret

def _encode(hotp_secret):
	encoded_secret = base64.b32encode(hotp_secret.encode("utf-8"))
	return encoded_secret

def generate_hotp(hotp_secret, current_at=0, n=1):
	'''Generate `n` number of HOTPs starting at the `current_at` count
	using `hotp_secret` that looks like `7e1c0372fec015ac976765ef4bb5c3f3`'''
	# --- Create HOTP object
	encoded_secret = _encode(hotp_secret)
	hotp = pyotp.HOTP(encoded_secret)   # As long as the secret key is the same, the HOTP object is the same

	# --- Generate new passcodes
	passcode_list = [hotp.at(current_at + i) for i in range(n)]
	return passcode_list

def encrypt(plain_message: str, key1: str, key2: str) -> str:
	'''Symmetric encryption of message using two keys. 
	These keys should be stored in different ways.
	For example, key1 could be a user\'s unhashed password which is only available to the server for a brief moment
	while key2 could be a random string stored in the server but not version-controlled'''
	# TODO Use real encryption
	return plain_message + key1 + key2


def decrypt(encrypted_message: str, key1: str, key2: str) -> str:
	'''Symmetric decryption of an encrypted message using two keys.
	See also: encrypt'''
	# TODO Use real encryption
	return encrypted_message.replace(key1, '').replace(key2, '')

	