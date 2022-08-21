import hashlib
from base64 import b64encode, b64decode

from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

SESSION_KEY_SIZE = 128
AES_MODE = AES.MODE_CBC


class AESCipher:
    def __init__(self, key: bytes = None):
        self.block_size = AES.block_size

        self.key = None
        self.raw_key = None
        if key is not None:
            self.set_key(key)

    def set_key(self, key: bytes):
        self.key = hashlib.sha256(key).digest()
        self.raw_key = key

    def encrypt(self, data: bytes):
        padded_data = pad(data, self.block_size)

        iv = Random.new().read(self.block_size)
        cipher = AES.new(self.key, AES_MODE, iv)

        encrypted_data = cipher.encrypt(padded_data)

        return b64encode(iv + encrypted_data)

    def decrypt(self, encrypted_data: bytes):
        decoded_encryption = b64decode(encrypted_data)

        iv = decoded_encryption[:self.block_size]
        cipher = AES.new(self.key, AES_MODE, iv)

        decrypted_data = cipher.decrypt(decoded_encryption[self.block_size:])
        return unpad(decrypted_data, self.block_size)

    @staticmethod
    def generate_key():
        key = Random.new().read(SESSION_KEY_SIZE)

        return key
