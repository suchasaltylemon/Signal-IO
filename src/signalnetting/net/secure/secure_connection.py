import socket

from Crypto.Hash import SHA3_256
from .. import Signal
from ..connection import Connection
from ...ciphers.aes import AESCipher
from ...utils.encoding import bstring, sbytes
from ...utils.event import Event

ENCODING = "utf-8"


class SecureConnection(Connection):
    SECURE_PREFIX = "<SECURE>"

    def __init__(self, sock: socket.socket, aes: AESCipher):
        super().__init__(sock)

        self.aes = aes
        self.secure = False
        self.Secured = Event()

    @staticmethod
    def hash(data: bytes):
        return SHA3_256.new(data).digest()

    def _signal_transformer(self, signal: Signal) -> Signal:
        decoded_signal = super()._signal_transformer(signal)

        if decoded_signal.path.startswith(self.SECURE_PREFIX):
            assert self.secure, "SecureSocket has not completed handshake. Cannot send secure packets!"

            decrypted_encoded_data = self.aes.decrypt(sbytes(decoded_signal.data["data"]))
            path = decoded_signal.path.lstrip(self.SECURE_PREFIX)

            decoded_data = bstring(decrypted_encoded_data)
            data = self._decode_data(decoded_data)

        else:
            path = decoded_signal.path
            data = decoded_signal.data

        return Signal(path, data)

    def send(self, signal: Signal, /, use_secure=True):
        path = signal.path

        if use_secure and not self.secure:
            return False

        if use_secure:
            path = self.SECURE_PREFIX + path

            encoded_internal_data = sbytes(self._encode_data(signal.data))
            encrypted_data = self.aes.encrypt(encoded_internal_data)
            encoded_external_data = bstring(encrypted_data)

            data = {"data": encoded_external_data}

        else:
            data = signal.data

        encrypted_signal = Signal(path, data)
        super().send(encrypted_signal)
