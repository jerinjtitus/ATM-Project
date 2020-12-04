import hashlib

def sha_encode(password):
    hashed_pass = hashlib.sha512(password.encode())
    return hashed_pass.hexdigest()
