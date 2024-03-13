import itertools
import time
from typing import ClassVar, Final, Literal, NoReturn, final, override

from optype import CanCall


class State[V]:
    __slots__ = ('__weakref__',)

    is_constant: ClassVar[bool]
    is_readonly: ClassVar[bool]

    def item(self) -> tuple[int, V]:
        raise NotImplementedError

    def get(self) -> V:
        return self.item()[1]

    def set(self, new_value: V, /) -> tuple[int, bool]:
        raise NotImplementedError

    @override
    def __repr__(self) -> str:
        value = self.get()
        value_repr = '...' if value is Ellipsis else repr(value)
        return f'{type(self).__name__}({value_repr})'

    @override
    def __str__(self) -> str:
        if (value := self.get()) is Ellipsis:
            return '...'
        return str(value)


@final
class StateConst[V](State[V]):
    __slots__ = ('_value',)
    __match_args__ = ('_value',)

    is_constant: ClassVar[bool] = True
    is_readonly: ClassVar[bool] = True

    _value: V

    def __init__(self, value: V, /) -> None:
        assert value is not Ellipsis
        self._value = value

    @override
    def item(self) -> tuple[Literal[-1], V]:
        return -1, self._value

    @override
    def set(self, _: V, /) -> NoReturn:
        raise RuntimeError('constant is immutable')

    @override
    def __repr__(self) -> str:
        return repr(self.get())


@final
class StateSignal[V](State[V]):
    __slots__ = ('_func', '_t0')
    __match_args__ = ()

    is_constant: ClassVar[bool] = False
    is_readonly: ClassVar[bool] = True

    _func: CanCall[[], V]
    _t0: Final[int]

    def __init__(self, func: CanCall[[], V], /) -> None:
        self._func = func
        self._t0 = time.perf_counter_ns()

    @override
    def item(self) -> tuple[int, V]:
        t0, value = self._t0, self._func()
        return time.perf_counter_ns() - t0, value

    @override
    def set(self, _: V, /) -> NoReturn:
        raise RuntimeError('signal is immutable')


@final
class StateVar[V](State[V]):
    __slots__ = ('__clock', '_item')
    __match_args__ = ('_value',)

    is_constant: ClassVar[bool] = False
    is_readonly: ClassVar[bool] = False

    __clock: CanCall[[], int]
    _item: tuple[int, V]

    def __init__(self, initial: V, /) -> None:
        self.__clock = itertools.count(0).__next__
        self._item = self.__clock(), initial

    @property
    def _value(self) -> V:
        return self._item[1]

    @override
    def item(self) -> tuple[int, V]:
        return self._item

    @override
    def set(self, new_value: V, /) -> tuple[int, bool]:
        tick, value = self._item
        if (
            value is not Ellipsis and new_value is not Ellipsis
            and (new_cls := type(new_value)) is not (cls := type(value))
        ):
            # value type must be invariant
            raise TypeError(f'expected {cls.__name__}, got {new_cls.__name__}')

        if new_value == value:
            # nothing needs to changed
            return tick, False

        # update and increment the tick
        self._item = self.__clock(), new_value

        # check for a race condition
        new_tick = self._item[0]
        assert new_tick == tick + 1, 'race condition encountered'

        # return the new tick and True (changed)
        return new_tick, True
