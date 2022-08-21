import socket
from typing import Any, Optional

from .handshake_factory import HandshakeInitRequest, HandshakePublicKeyRequest, HandshakeSessionKeyExchange, \
    HandshakeResolve
from .secure_connection import SecureConnection
from .. import Server
from ..connection import Connection
from ...ciphers.aes import AESCipher
from ...ciphers.rsa import RSACipher
from ...utils.encoding import sbytes


class SecureServer(Server):
    def __init__(self, host_name: str, port: int):
        super().__init__(host_name, port)

        self.rsa = RSACipher(*RSACipher.generate_key())

    def _handshake(self, connection: SecureConnection, aes: AESCipher):
        @connection.Signalled(HandshakeInitRequest.path)
        def handle_public_key_request(_):
            connection.send(HandshakePublicKeyRequest.create_handshake(self.rsa.public_key_bytes), use_secure=False)

        @connection.Signalled(HandshakeSessionKeyExchange.path)
        def handle_session_key(signal):
            encrypted_session_key = sbytes(signal.data["session_key"])

            decrypted_session_key = self.rsa.decrypt(encrypted_session_key)

            aes.set_key(decrypted_session_key)
            connection.secure = True
            connection.Secured.fire()

            connection.send(HandshakeResolve.create_handshake(decrypted_session_key), use_secure=False)

    def _handle_socket(self, sock: socket.socket, info: Any) -> Optional[Connection]:
        aes = AESCipher(None)

        connection = SecureConnection(sock, aes)
        connection.listen()

        self._handshake(connection, aes)
        self._connections.append(connection)

        connection.Disconnected.connect(lambda: self.Disconnected.fire(connection))

        return connection
