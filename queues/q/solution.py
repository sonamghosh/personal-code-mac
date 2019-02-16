import queue
import codecs
import hashlib
import json
import base64
from collections import OrderedDict
from operator import itemgetter

# Testing Transformations first
s1 = "Qadium, Inc."

if "Qadium" in s1:
    print('yes')
    s2 = s1[::-1]  # reverses the string
print(s2)

num = 512
print(~512)  # bitwise not

s2 = "Hello uwu"
#s2 = codecs.encode(s2, encoding='utf-8')
s2 = s2.encode('utf-8')
s2 = base64.encodebytes(s2)
s2h = hashlib.sha256(s2).hexdigest()  # hash
print(s2h)
# Transformation rules ignore values of private fields ones with _


# Dispatch Rules
# _special -> queue 0
# _hash -> 1
# value with muidaQ -> 2
# int val -> 3
# Else 4
# Ignore private field values with underscore _

class MessageService:
    def __init__(self):
        continue

    def encode_str(val):
        utf8_base64_encoded = base64.encodebytes(val.encode('utf-8'))
        hashed_str = hashlib.sha256(utf8_base64_encoded).hexdigest()

    def transform(msg):
        for field, val in msg.items():
            if not field.startswith('_'):
                if isinstance(val, str) and 'Qadium' in val:
                    msg[field] = val[::-1]
                elif isinstance(val, int):
                    msg[field] = ~val
            if '_hash' in field:
                msg['hash'] = encode_str(val)

        return msg

    def dispatch(msg):
        continue
