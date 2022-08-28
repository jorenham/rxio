from __future__ import annotations

__all__ = ("RxVar",)

import asyncio
import collections
import enum
import sys
from typing import (
    AsyncGenerator,
    ClassVar,
    Final,
    Generic,
    Literal,
    TypeVar,
    Union,
    overload,
)

from ._typing import AwaitResult
from .utils import pause

if sys.version_info >= (3, 10):
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias

_T = TypeVar("_T")
_D = TypeVar("_D")


class _Marker(enum.Enum):
    """Marker sentinel, for internal use.

    The usage of an enum makes it compatible with type checkers, since
    enum values are allowed to be used in typing.Literal, whereas e.g.
    ``empty = object()`` and ``class empty: ...`` aren't.
    """

    empty = object()


_EmptyT: TypeAlias = Literal[_Marker.empty]

_RxState: TypeAlias = collections.deque[
    tuple[int, Union[_EmptyT, _T], asyncio.Future[Union[_EmptyT, _T]]]
]


class RxBase(Generic[_T]):
    __slots__ = ("_name", "_state", "__weakref__")

    empty: ClassVar[_EmptyT] = _Marker.empty

    _name: Final[str]
    _state: _RxState[_T]

    def __init__(self, name: str, *, _state: _RxState[_T] | None = None):
        super().__init__()

        self._name = name

        if _state is None:
            future = asyncio.get_running_loop().create_future()
            self._state = collections.deque([(0, self.empty, future)], maxlen=1)
        else:
            self._state = _state

    __hash__ = None  # type: ignore[assignment]

    def __repr__(self) -> str:
        name = f'{self.name}@{self.tick}"'

        if self.is_empty:
            return name

        return f"{name} = {self.value!r}"

    __str__ = __repr__

    @property
    def name(self) -> str:
        """The name of this variable."""
        return self._name

    @property
    def tick(self) -> int:
        """The tick count, starting at 0, incrementing each time a new value
        is set.
        Internally used for tracking the cache state of the dependency grap.
        """
        return self._state[0][0]

    @property
    def value(self) -> _T | _EmptyT:
        return self._state[0][1]

    @property
    def is_empty(self) -> bool:
        """True if a non-empty value is set.."""
        return self.value is RxBase.empty

    @property
    def _future(self) -> asyncio.Future[_T | _EmptyT]:
        future = self._state[0][2]
        if future.done():
            # potentially raises asyncio.CancelledError
            _ = future.result()

            raise RuntimeError(
                "The future is already set...? If you're assigning from "
                "different threads: don't. Otherwise, this is probably a bug."
            )
        return future

    async def get_tick(self) -> int:
        """Get the current tick.

        This method is basically the same as .tick, but mainly exists for
        interface consistency with the other async getter method.

        Returns:
            The current tick.
        """
        await pause()
        return self.tick

    async def get_value(self) -> _T:
        """Get the current value, or wait until there is one.

        Returns:
            The first available non-empty value.
        """
        value = self.value
        if value is RxBase.empty:
            return await self.next_value()

        await pause()
        return value

    async def next_tick(self) -> int:
        """Wait on the next tick and return it.

        Returns:
            The next tick.
        """
        await self._future
        return self.tick

    @overload
    async def next_value(self) -> _T:
        ...

    @overload
    async def next_value(self, skip_empty: Literal[True]) -> _T:
        ...

    @overload
    async def next_value(self, skip_empty: Literal[False]) -> _T | _EmptyT:
        ...

    async def next_value(self, skip_empty: bool = True) -> _T | _EmptyT:
        """Wait until a value is assigned and return it.

        Args:
            skip_empty: If True (default), waits for a non-empty value.
        Returns:
            The next value, or ``RxBase.empty`` if ``skip_empty=False`` and
            it's empty.
        """
        future = self._future
        value = await future

        if not skip_empty:
            return value

        while value is RxBase.empty:
            _future = self._future
            assert _future is not future

            await pause()

            future = _future
            value = await future

        return value

    async def iter_ticks(
        self,
        current: bool = True,
    ) -> AsyncGenerator[int, None]:
        """Waits for the next tick and yields it, ad infinitum.

        Args:
            current: If True (default), start with the current value.
        Returns:
            An async generator over future ticks.
        """
        future = self._future

        if current:
            yield self.tick
            await pause()

        while True:
            await future

            _future = self._future
            assert _future is not future
            future = _future

            yield self.tick

            await pause()

    @overload
    async def iter_values(
        self, current: bool = ...
    ) -> AsyncGenerator[_T, None]:
        ...

    @overload
    async def iter_values(
        self,
        current: bool = ...,
        skip_empty: Literal[True] = ...,
    ) -> AsyncGenerator[_T, None]:
        ...

    @overload
    async def iter_values(
        self,
        current: bool = ...,
        skip_empty: Literal[False] = ...,
    ) -> AsyncGenerator[_T | _EmptyT, None]:
        ...

    async def iter_values(
        self,
        current: bool = True,
        skip_empty: bool = True,
    ) -> AsyncGenerator[_T | _EmptyT, None]:
        """Iterates over the values once they change.

        Args:
            current: If True (default), start with the current value.
            skip_empty: If True (default), waits for a non-empty value.
        Returns:
            An async generator over future ticks.
        """
        future = self._future

        if current:
            value = self.value
            if not skip_empty or value is not RxBase.empty:
                yield value

            await pause()

        while True:
            value = await future

            _future = self._future
            assert _future is not future
            future = _future

            if not skip_empty or value is not RxBase.empty:
                yield value

            await pause()


class RxVar(RxBase[_T], Generic[_T]):
    __slots__ = ("_write_lock",)

    empty: ClassVar[_EmptyT] = _Marker.empty

    def __init__(self, name: str):
        super().__init__(name)

        self._write_lock = asyncio.Lock()

    def __await__(self) -> AwaitResult[_T]:
        """Alias for ``.get()``."""
        return self.get_value().__await__()

    def __aiter__(self) -> AsyncGenerator[_T, None]:
        """Alias for ``.iter_values()``."""
        # noinspection PyTypeChecker
        return self.iter_values()

    @property
    def value(self) -> _T | _EmptyT:
        return super().value

    @value.setter
    def value(self, value: _T):
        """Assign a new value to this value and increment the tick, or ignore
        if it equals the current value.

        If the value equals the current value, it is ignored.
        Otherwise, the value is assigned, ``tick`` increments by one, and
        the waiters and watchers will soon be notified.

        Note:
            Setting the value multiple times without passing control back to
            the event loop (e.g. with ``asyncio.sleep(0)``) overwrites earlier
            values, "hiding" them from the current async waiters and iterators.

        Raises:
            RuntimeError: if another task is already writing the value.
        """
        if self._write_lock.locked():
            raise RuntimeError("Another task is writing the value.")

        if self._set(value):
            assert self.value is value

    @value.deleter
    def value(self):
        """Delete the current value and increment the tick, or ignore if already
        empty.

        Raises:
            RuntimeError: if another task is already writing the value.
        """
        if self._write_lock.locked():
            raise RuntimeError("Another task is writing the value.")

        if self._set():
            assert self.is_empty

    async def set_value(self, value: _T) -> bool:
        """Assign a new value to this variable.

        If the value equals the current value, it is ignored.
        Otherwise, the value is assigned, ``__tick__`` increments by one, and
        waits until the waiters and watchers are notified.

        Returns:
            True if the value has been set, False if equal to the current.
        """
        # await pause()

        async with self._write_lock:
            if was_set := self._set(value):
                _value = await self.get_value()
                assert value is _value

                await pause()
                assert value is self.value

        return was_set

    async def del_value(self) -> bool:
        """Delete the current value if not empty and increment ``.tick``.

        Returns:
            True if a value was set, otherwise False.
        """
        await pause()

        async with self._write_lock:
            if was_deleted := self._set():
                await pause()
                assert self.is_empty

        return was_deleted

    def _set(self, value: _EmptyT | _T = empty) -> bool:
        t0, value0, future0 = self.tick, self.value, self._future
        if value is value0 or value == value0:
            return False

        t = t0 + 1
        future = future0.get_loop().create_future()
        self._state.append((t, value, future))
        future0.set_result(value)

        return True
