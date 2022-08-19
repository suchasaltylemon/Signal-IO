import socket
from socket import gethostbyname
from time import sleep as wait

from .connection import Connection as Connection
from ..utils.event import Event

WAIT_TIME = 0.2


class Client:
    def __init__(self, ip, port):
        self.IP = gethostbyname(ip)
        self.Port = port

        self.Connected = Event[Connection]()
        self.Disconnected = Event()
        self.Signalled = Event()

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._connection = None

    def connect(self):
        self._socket.connect((self.IP, self.Port))
        self._connection = Connection(self._socket)
        self._connection.listen()

        wait(WAIT_TIME)
        self.Connected.fire(self._connection)

        self._connection.Disconnected.connect(lambda: self.Disconnected.fire())

    def disconnect(self):
        self._connection.disconnect()
