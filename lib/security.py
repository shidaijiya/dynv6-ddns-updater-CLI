# 警告此依赖仅可以运行在windows
import os
import sys
os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
import json
import win32crypt
from lib.log_utils import log_print



def encrypt_token(secrets,secrets_file_path):
    try:
        data = json.dumps(secrets).encode("utf-8")
        encrypted = win32crypt.CryptProtectData(data, None, None, None, None, 0)
        with open(secrets_file_path, "wb") as f:
            f.write(encrypted)
        return True
    except Exception as e:
        log_print(e,"WARNING")
        return False



def decrypt_token(secrets_file_path):
    try:
        with open(secrets_file_path, "rb") as f:
            encrypted = f.read()
        decrypted = win32crypt.CryptUnprotectData(encrypted, None, None, None, 0)[1]
        secrets = json.loads(decrypted.decode("utf-8"))

        return secrets

    except FileNotFoundError:
        log_print("Can't found secrets file.","WARNING")
        return False
