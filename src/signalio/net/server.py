import socket
from typing import List, Any, Optional

from .connection import Connection
from ..utils.event import Event
from ..utils.parallel import Parallel


class Server:
    BACKLOG = 7

    def __init__(self, host_name, port):
        self.IP = socket.gethostbyname(host_name)
        self.Port = port

        self.Connected = Event()
        self.Disconnected = Event()
        self.Stopped = Event()
        self.Started = Event()

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._connections: List[Connection] = []

        self._event_loop = Parallel(self._loop)

        self.running = True

    def send_to_all(self, signal):
        for conn in self._connections:
            if conn.connected is False:
                return

            conn.send(signal)

    def send_to_all_except(self, signal, excluded):
        for conn in self._connections:
            if conn.connected is False or conn is excluded:
                return

            conn.send(signal)

    def start(self):
        self._socket.bind((self.IP, self.Port))
        self._socket.listen()

        self._event_loop.start()
        self.Started.fire()

    def stop(self):
        self.running = False

        for conn in self._connections:
            if conn.connected is True:
                conn.disconnect()

        self._event_loop.cancel()

        self._socket.shutdown(socket.SHUT_RDWR)
        self._socket.close()

    def _handle_socket(self, sock: socket.socket, info: Any) -> Optional[Connection]:
        connection = Connection(sock)
        connection.listen()
        self._connections.append(connection)

        connection.Disconnected.connect(lambda: self.Disconnected.fire(connection))

        return connection

    def _loop(self):
        while self.running is True:
            try:
                sock, info = self._socket.accept()
                connection = self._handle_socket(sock, info)

                if connection is not None:
                    self.Connected.fire(connection)

            except ConnectionResetError:
                continue
