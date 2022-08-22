from threading import Event as Waiter
from typing import TypeVar, Callable, Generic, Optional, Any, TypeAlias

T = TypeVar("T")
F: TypeAlias = Callable[[T], None]


class Event(Generic[T]):
    def __init__(self) -> None:
        self._callbacks = []
        self._waiters = []
        self._waiter_return = None

    def __call__(self, fn: Optional[F] = None) -> Callable[[F], F]:
        return self.connect(fn)

    def fire(self, *args: T):
        for callback in self._callbacks:
            callback(*args)

        for w in self._waiters:
            self._waiter_return = args
            w.set()

        self._waiters = []

    def connect(self, fn: Optional[Callable[[T], None]] = None) -> Callable[[F], F]:
        if fn is None:
            def decorator(fnx: F) -> F:
                self._callbacks.append(fnx)
                return fnx

            return decorator

        else:
            self._callbacks.append(fn)
            return fn

    def wait(self):
        w = Waiter()

        self._waiters.append(w)

        w.wait()

        return self._waiter_return


class ConditionalEvent(Event, Generic[T]):
    def __init__(self, checker, default=None):
        super().__init__()

        self._default = default
        self._callbacks = {}
        self._waiters = {}
        self._conditioner = checker

    def __call__(self, condition=None) -> Callable[[T], None]:
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

    def connect(self, condition: Optional[Callable[[Any], bool]] = None) -> Callable[
        [Callable[[T], None]], Callable[[T], None]]:
        if condition is None:
            condition = self._default

        def _handle_connect(fn: Callable[[T], Callable[[T], None]]):
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
