from __future__ import annotations

import functools
from types import NotImplementedType
from typing import TYPE_CHECKING, final, override


if TYPE_CHECKING:
    import optype as opt


def _ensure_rx[X](x: RX[X] | X) -> RX[X]:
    rx_x: RX[X] = x if isinstance(x, RX) else RX(x)
    return rx_x


type _DoesOp2[Xa, Xb, Y] = opt.CanCall[[RX[Xa], RX[Xb] | Xb], RX[Y]]


def _binop[Xa, Xb, Y](do_op2: _DoesOp2[Xa, Xb, Y], /) -> _DoesOp2[Xa, Xb, Y]:
    fname = getattr(do_op2, '__name__', '')
    assert fname[:2] == fname[-2:] == '__', fname

    @functools.wraps(do_op2)
    def _method(self: RX[Xa], other: RX[Xb] | Xb, /) -> RX[Y]:
        try:
            rx_y = do_op2(self, other)
        except AttributeError as e:
            if e.name == fname:
                return NotImplemented
            raise

        # let potential wrapped `NotImplemented` pass through
        match rx_y:
            case RX(NotImplementedType()):
                return NotImplemented
            case _:
                return rx_y

    return _method


@final
class RX[V]:
    # TODO: let NotImplemented pass through in __new__, instead of @_binop
    # TODO: have `RX(v: RX[V])` return `v.map(lambda v: v)`, not `RX[RX[V]]`
    # TODO: return NotImplemented in .map when a.__{}__ raises AttributeError
    # TODO: lazy evaluation
    # TODO: in-place `imap` and `iapply` methods for "revisioned mutability"
    # TODO: augmented `__i{}__` binops using `imap` and `iapply`
    # TODO: reactivity; notify listeners on mutation
    # TODO: weakref parents, and "absorb"/"inline" their values when finalized

    __slots__ = ('__weakref__', '_value')
    __match_args__ = ('_value',)

    _value: V

    def __init__(self, value: V, /) -> None:
        self._value = value

    @override
    def __str__(self) -> str:
        return f'RX({self._value!r})'

    __repr__ = __str__

    def map[Y](self, f: opt.CanCall[[V], Y], /) -> RX[Y]:
        return RX(f(self._value))

    def apply[Y](self, rx_f: RX[opt.CanCall[[V], Y]], /) -> RX[Y]:
        match rx_f:
            case RX(f) if callable(f):
                return RX(f(self._value))
            case _:
                raise TypeError(type(rx_f))

    # TODO: dry-er (bin)ops

    @_binop
    def __add__[X, Y](self: RX[opt.CanAdd[X, Y]], x: RX[X] | X, /) -> RX[Y]:
        # TODO: map directly when x is not RX[X]
        return _ensure_rx(x).apply(self.map(lambda v: lambda x: v + x))

    @_binop
    def __radd__[X, Y](self: RX[opt.CanRAdd[X, Y]], x: RX[X] | X, /) -> RX[Y]:
        # TODO: map directly when x is not RX[X]
        return _ensure_rx(x).apply(self.map(lambda v: lambda x: x + v))
