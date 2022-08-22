import time
from threading import Event as Waiter, Thread
from typing import TypeVar, Callable, Generic, Optional, Any

T = TypeVar("T")
F = Callable[[T], None]


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

    def _timeout(self, time_out: float, waiter: Waiter):
        time.sleep(time_out)

        if not waiter.is_set():
            waiter.set()

    def _wait_handler(self, waiter: Waiter, time_out: Optional[float]):
        started = time.time()
        if time_out is not None:
            Thread(target=self._timeout, args=(time_out, waiter)).start()

        waiter.wait()
        finished = time.time()

        if time_out is not None and finished - started > time_out:
            return self._waiter_return

        else:
            return None

    def wait(self, *, time_out: Optional[float] = None):
        w = Waiter()

        self._waiters.append(w)

        return self._wait_handler(w, time_out)


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

        for condition, waiter in self._waiters.items():
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

    def wait(self, condition, *, time_out: Optional[float] = None):
        w = Waiter()

        if condition in self._waiters:
            self._waiters[condition].append(w)

        else:
            self._waiters[condition] = [w]

        return self._wait_handler(w, time_out)
