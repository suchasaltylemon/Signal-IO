from socket import gethostname, gethostbyname

from .client import Client
from .connection import Connection
from .server import Server
from .signal import Signal


def get_host():
    return gethostbyname(gethostname())
