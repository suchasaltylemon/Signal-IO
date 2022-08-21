from time import sleep as wait

from .handshake_factory import HandshakeInitRequest, HandshakePublicKeyRequest, HandshakeSessionKeyExchange, \
    HandshakeResolve
from .secure_connection import SecureConnection
from .. import Client
from ..client import WAIT_TIME
from ...ciphers.aes import AESCipher
from ...ciphers.rsa import RSACipher
from ...utils.encoding import sbytes


class SecureClient(Client):
    def __init__(self, ip: str, port: int):
        super().__init__(ip, port)

        self.aes = AESCipher(AESCipher.generate_key())

    def _handshake(self):
        @self._connection.Signalled(HandshakePublicKeyRequest.path)
        def handle_public_key(signal):
            public_key = sbytes(signal.data["public_key"])

            rsa_cipher = RSACipher(public_key)

            encrypted_session_key = rsa_cipher.encrypt(self.aes.raw_key)
            self._connection.send(HandshakeSessionKeyExchange.create_handshake(encrypted_session_key), use_secure=False)

        @self._connection.Signalled(HandshakeResolve.path)
        def resolve(signal):
            server_hash = sbytes(signal.data["hash"])
            client_hash = SecureConnection.hash(self.aes.raw_key)

            if server_hash == client_hash:
                self._connection.secure = True
                self._connection.Secured.fire()

        self._connection.send(HandshakeInitRequest.create_handshake(self.aes.key), use_secure=False)

    def connect(self):
        self._socket.connect((self.IP, self.Port))
        self._connection = SecureConnection(self._socket, self.aes)
        self._connection.listen()

        wait(WAIT_TIME)

        self._handshake()

        self.Connected.fire(self._connection)

        self._connection.Disconnected.connect(lambda: self.Disconnected.fire())
