from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA

RSA_KEY_SIZE = 2048


class RSACipher:
    def __init__(self, public_key, private_key=None):
        rsa_public_key = RSA.import_key(public_key)
        self.public_key = PKCS1_OAEP.new(rsa_public_key)

        self.public_key_bytes = public_key

        if private_key is not None:
            rsa_private_key = RSA.import_key(private_key)
            self.private_key = PKCS1_OAEP.new(rsa_private_key)

        else:
            self.private_key = None

    @staticmethod
    def generate_key():
        key = RSA.generate(RSA_KEY_SIZE)

        rsa_public_key = key.public_key().export_key("PEM")
        rsa_private_key = key.export_key("PEM")

        return [rsa_public_key, rsa_private_key]

    def encrypt(self, data: bytes):
        return self.public_key.encrypt(data)

    def decrypt(self, data: bytes):
        return self.private_key.decrypt(data)
