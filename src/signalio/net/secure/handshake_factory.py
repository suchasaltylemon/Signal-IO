import abc

from .secure_connection import SecureConnection
from .. import Signal
from ...utils.encoding import bstring


class HandshakeFactory(abc.ABC):
    @property
    @abc.abstractmethod
    def path(self) -> str:
        pass

    @classmethod
    @abc.abstractmethod
    def create_handshake(cls, session_key: bytes) -> Signal:
        pass


# Client to server, initialise handshake
class HandshakeInitRequest(HandshakeFactory):
    path = "__handshake/init"

    @classmethod
    def create_handshake(cls, _: bytes):
        return Signal(cls.path, {})


# Server to client, send public key
class HandshakePublicKeyRequest(HandshakeFactory):
    path = "__handshake/public_key"

    @classmethod
    def create_handshake(cls, key: bytes):
        data = {
            "public_key": bstring(key)
        }

        return Signal(cls.path, data)


# Client to server, send session key
class HandshakeSessionKeyExchange(HandshakeFactory):
    path = "__handshake/session_key"

    @classmethod
    def create_handshake(cls, key: bytes):
        data = {
            "session_key": bstring(key)
        }

        return Signal(cls.path, data)


# Server to client, finish handshake, send hash of session key
class HandshakeResolve(HandshakeFactory):
    path = "__handshake/resolve"

    @classmethod
    def create_handshake(cls, key: bytes) -> Signal:
        data = {
            "hash": bstring(SecureConnection.hash(key))
        }

        return Signal(cls.path, data)
