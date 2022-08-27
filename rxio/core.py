from __future__ import annotations

__all__ = (
    'RxVar',
)

import asyncio
import collections
import sys
from typing import AsyncGenerator, Final, Generic, TypeVar, overload
import warnings

from .utils import pause

if sys.version_info >= (3, 10):
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias

_T = TypeVar('_T')
_D = TypeVar('_D')


_RxState: TypeAlias = collections.deque[tuple[int, asyncio.Future[_T]]]


class RxVar(Generic[_T]):
    __slots__ = '_name', '_state', '__weakref__'

    _name: Final[str]
    _state: _RxState[_T]

    def __init__(self, name: str, *, _state: _RxState[_T] | None = None):
        super().__init__()

        self._name = name

        if _state is None:
            future = asyncio.get_running_loop().create_future()
            self._state = collections.deque([(0, future)], maxlen=2)
        else:
            self._state = _state

    def __repr__(self) -> str:
        name = self.tickname

        notset = object()
        value = self.get_nowait(notset)
        if value is notset:
            return name

        return f'{name} = {value!r}'

    __str__ = __repr__
    __hash__ = None  # type: ignore[assignment]

    @property
    def is_set(self) -> bool:
        """True if a value is available."""
        return self._state[0][1].done()

    @property
    def tick(self) -> int:
        """The tick count, starting at 0, incrementing each time a new value
        is set.
        Internally used for tracking the cache state of the dependency grap.
        """
        return self._state[-1][0]

    @property
    def name(self) -> str:
        """The name of this variable."""
        return self._name

    @property
    def tickname(self) -> str:
        """The name and the tick of this variable, e.g. ``'spam@42'``."""
        return f'{self._name}@{self.tick}'

    async def get(self) -> _T:
        """Wait until a value is assigned and return it.
        """
        return await self._state[0][1]

    @overload
    def get_nowait(self) -> _T: ...
    @overload
    def get_nowait(self, __default: _T | _D, /) -> _T | _D: ...

    def get_nowait(self, *args: _T | _D) -> _T | _D:
        """Return the current value if set, otherwise, return the default, or
        raise LookupError.
        """
        if len(args) > 1:
            raise TypeError(
                f'get_nowait() expected at most 1 argument, got {len(args)}'
            )

        if (future := self._state[0][1]).done():
            return future.result()
        if args:
            return args[0]
        raise LookupError(self.tickname)

    async def wait(self) -> _T:
        """Wait until a new value is assigned and return it.
        """
        return await self._state[-1][1]

    async def watch(
        self,
        immediate: bool = False
    ) -> AsyncGenerator[_T, None]:
        """Return an async iterator that produces values once they are set.

        Args:
            immediate: When set to True, and a value is currently set, it will
            be yielded immediately.

        Returns:
            An async iterator of values.
        """
        t0, future = self._state[0 if immediate else -1]
        yield await future

        while True:
            ti, future = self._state[-1]
            dt = ti - t0
            assert dt > 0

            if dt > 1:
                tj, present = self._state[0]
                assert tj + 1 == ti

                if dt > 2:
                    if dt == 3:
                        value_fmt = 'value'
                    else:
                        value_fmt = f'{dt-2} values'
                    warnings.warn(
                        f"can't keep up: {value_fmt} missed in {self}.watch()"
                    )

                yield await present

            yield await future
            t0 = ti

    async def set(self, value: _T) -> bool:
        """Assign a new value to this variable.

        If the value equals the current value, it is ignored.
        Otherwise, the value is assigned, ``__tick__`` increments by one, and
        waits until the waiters and watchers are notified.
        """
        await pause()

        if was_set := self.set_nowait(value):
            value_current = await self.get()
            assert value_current is value

            await pause()

        return was_set

    def set_nowait(self, value: _T) -> bool:
        """Assign a new value to this variable without waiting.

        If the value equals the current value, it is ignored.
        Otherwise, the value is assigned, ``__tick__`` increments by one, and
        the waiters and watchers will soon be notified.

        Note:
            Calling this method multiple times without passing control back to
            the event loop (e.g. with ``asyncio.sleep(0)``) overwrites earlier
            values, "hiding" them from the current waiting and watching tasks.
        """
        present: asyncio.Future[_T]

        present = self._state[0][1]
        if present.done():
            current = present.result()

            if value is current or value == current:
                return False

        t, present = self._state[-1]
        if present.done():
            _ = present.result()  # raises if cancelled
            raise RuntimeError(
                "The future is already set...? If you're assigning from "
                "different threads: don't. Otherwise, this is probably a bug."
            )

        # prepare the next future
        self._state.append((t + 1, present.get_loop().create_future()))

        present.set_result(value)
        return True
