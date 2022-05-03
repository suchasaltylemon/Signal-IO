import socket

from event import Event


class Connection:
    TERMINATOR = b"\0"
    CHUNK_SIZE = 1024

    def __init__(self, sock: socket.socket):
        self.ip = sock.getpeername()
        self._socket = sock
        self.Signalled = Event()
        self._Closed = Event()

        while True:
            pass

    def send(self, data):
        encoded = bytes(data) + Connection.TERMINATOR

        size = len(bytes)
        current_chunks = 0
        while current_chunks < size:
            self._socket.send(encoded[current_chunks:current_chunks + Connection.CHUNK_SIZE])
            current_chunks += Connection.CHUNK_SIZE
