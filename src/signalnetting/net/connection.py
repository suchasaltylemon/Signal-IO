import json
import socket
from base64 import b64encode, b64decode
from typing import Union

from .signal import Signal
from ..utils.event import Event, ConditionalEvent
from ..utils.parallel import Parallel

EXPECTS_RESPONSE_SUFFIX = "<EXPECTS_RESPONSE>"
RESPONSE_SUFFIX = "<RESPONSE>"


class Connection:
    TERMINATOR = b"\0"
    CHUNK_SIZE = 1024

    def __init__(self, sock: socket.socket):
        self.ip, self.port = sock.getpeername()
        self._socket = sock

        self.Signalled = ConditionalEvent(lambda signal: [signal.path], default="*")
        self.Disconnected = Event()

        self.connected = False
        self._event_loop = Parallel(self._listen)

    def listen(self):
        self.connected = True

        self._event_loop.start()

    def disconnect(self):
        self.send(Signal("/__disconnect"))
        self._close()

    def _close(self):
        self.connected = False
        self.Disconnected.fire()

        self._socket.shutdown(socket.SHUT_RDWR)
        self._socket.close()
        self._event_loop.cancel()

    def _signal_transformer(self, signal: Signal) -> Signal:
        decoded_data = self._decode_data(signal.data)

        return Signal(signal.path, decoded_data)

    def _listen(self):
        while self.connected:
            stream = b""

            while Connection.TERMINATOR not in stream:
                stream += self._socket.recv(Connection.CHUNK_SIZE)

            signal = Signal.decode(stream.split(Connection.TERMINATOR)[0])

            if signal.path == "/__disconnect":
                self._close()

            else:
                try:
                    transformed_signal = self._signal_transformer(signal)
                    self.Signalled.fire(transformed_signal)

                except BaseException as e:
                    print(e)

    @staticmethod
    def _encode_data(data: dict):
        return b64encode(json.dumps(data).encode("utf-8")).decode("utf-8")

    @staticmethod
    def _decode_data(encoded: Union[str, bytes]):
        return json.loads(b64decode(encoded))

    def send(self, signal: Signal):
        encoded_data = self._encode_data(signal.data)

        final_signal = Signal(signal.path, encoded_data)
        terminated_signal = bytes(final_signal) + Connection.TERMINATOR

        size = len(terminated_signal)
        current_chunks = 0
        while current_chunks < size:
            chunked_data = terminated_signal[current_chunks:current_chunks + Connection.CHUNK_SIZE]
            self._socket.send(chunked_data)
            current_chunks += Connection.CHUNK_SIZE
