from threading import Event as Waiter
from types import FunctionType
from typing import TypeVar, Callable, Generic

T = TypeVar("T")


class Event(Generic[T]):
    def __init__(self) -> None:
        self._callbacks = []
        self._waiters = []
        self._waiter_return = None

    def __call__(self, fn: Callable[[T], None] = None) -> Callable[[T], None]:
        return self.connect(fn)

    def fire(self, *args: T):
        for callback in self._callbacks:
            callback(*args)

        for w in self._waiters:
            self._waiter_return = args
            w.set()

        self._waiters = []

    def connect(self, fn=None):
        if fn is None:
            def decorator(fn: Callable[[T], None]):
                self._callbacks.append(fn)
                return fn

            return decorator

        else:
            self._callbacks.append(fn)
            return fn

    def wait(self):
        w = Waiter()

        self._waiters.append(w)

        w.wait()

        return self._waiter_return


class ConditionalEvent(Event):
    def __init__(self, checker, default=None):
        super().__init__()

        self._default = default
        self._callbacks = {}
        self._waiters = {}
        self._conditioner = checker

    def __call__(self, condition=None):
        if condition is None:
            condition = self._default

        return self.connect(condition)

    def fire(self, *args):
        target_condition = self._conditioner(*args)

        for condition, callback in self._callbacks.items():
            if condition in target_condition:
                callback(*args)

        for condition, waiter in self._waiters:
            if condition in target_condition:
                self._waiter_return = args
                waiter.set()
                self._waiter_return = None

    def connect(self, condition=None):
        if condition is None:
            condition = self._default

        def _handle_connect(fn: FunctionType):
            self._callbacks[condition] = fn

            return fn

        return _handle_connect

    def wait(self, condition):
        w = Waiter()

        if condition in self._waiters:
            self._waiters[condition].append(w)

        else:
            self._waiters[condition] = [w]

        w.wait()

        return self._waiter_return
