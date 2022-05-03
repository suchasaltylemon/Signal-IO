class Event:
    def __init__(self):
        self._callbacks = []

    def _fire(self, *args):
        for callback in self._callbacks:
            callback(*args)

    def connect(self, fn):
        self._callbacks.append(fn)
