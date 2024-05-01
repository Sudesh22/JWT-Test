import hashlib

a_string = 'The quick brown dog'

hashed_string = hashlib.hmac(a_string.encode('utf-8')).hexdigest()
print(hashed_string)