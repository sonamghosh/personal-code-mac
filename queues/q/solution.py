import queue
import codecs
import hashlib
import json

# Testing Transformations first
s1 = "Qadium, Inc."

if "Qadium" in s1:
    print('yes')
    s2 = s1[::-1]  # reverses the string
print(s2)

num = 512
print(~512)  # bitwise not

s2 = "Hello uwu"
s2 = codecs.encode(s2, encoding='utf-8')
s2h = hashlib.sha256(s2).hexdigest()  # hash
print(s2h)
