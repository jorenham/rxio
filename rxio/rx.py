from __future__ import annotations

import contextlib
import math
import operator
from itertools import chain, starmap
from typing import (
    TYPE_CHECKING,
    Any,
    Concatenate,
    Final,
    Generic,
    Self,
    TypeVar,
    cast,
    final,
    overload,
    override,
)
from weakref import WeakValueDictionary

import optype as ot

from ._state import StateConst, StateVar


if TYPE_CHECKING:
    from collections.abc import Generator
    from types import EllipsisType, NotImplementedType

    from ._state import State


type CanRx[X] = Rx[X] | X

# because automatic variance inference isn't always possible; hence D.O.A.
Y_co = TypeVar('Y_co', covariant=True)


class Rx(Generic[Y_co]):  # noqa: PLR0904
    __slots__ = ('__rx_bases__', '__rx_out__', '__rx_state__', '__weakref__')

    __rx_bases__: tuple[State[Any], ...]
    __rx_state__: StateVar[EllipsisType | Y_co]
    # __rx_out__: WeakKeyDictionary[Rx[Any], int]
    __rx_out__: dict[Rx[Any], int]

    def __init__(self, value: Y_co, /) -> None:
        self.__rx_bases__ = ()
        self.__rx_state__ = StateVar(value)
        self.__rx_out__ = {}

    def __rx_get__(self) -> Y_co:
        return cast(Y_co, self.__rx_state__.get())

    def __rx_invalidate__(self, base_index: int, value: Any = ..., /) -> None:
        """
        Invalidate the caches w.r.t. the given base index, and propagate to
        children (if needed).
        """
        assert base_index >= 0

        rx_base = self.__rx_bases__[base_index]
        if not rx_base.set(value)[1] or not self.__rx_state__.set(...)[1]:
            # did not invalidate; no need to propagate
            return

        # invalidate the children
        for child, child_index in self.__rx_out__.items():
            child.__rx_invalidate__(child_index)

    # type conversions (non-reactive)

    @override
    def __str__(self) -> str:
        return str(self.__rx_get__())

    def __bytes__(self: Rx[ot.CanBytes[Any]]) -> bytes:
        return bytes(self.__rx_get__())

    def __complex__(self: Rx[ot.CanComplex]) -> complex:
        return complex(self.__rx_get__())

    def __float__(self: Rx[ot.CanFloat]) -> float:
        return float(self.__rx_get__())

    def __int__(self: Rx[ot.CanInt]) -> int:
        return int(self.__rx_get__())

    def __bool__(self) -> bool:
        return bool(self.__rx_get__())

    # representation (non-reactive)

    @override
    def __repr__(self) -> str:
        # TODO: custom rx_repr() function
        return f'rx({self.__rx_state__.item()[1]!r})'

    # TODO: format(CanFormat[Y: str]) -> RxFormat (`str & RxMap[str]`)

    @override
    def __hash__(self) -> int:
        # TODO: custom rx_hash() function
        return hash((type(self), self.__rx_bases__, self.__rx_state__))

    def __index__(self: Rx[ot.CanIndex]) -> int:
        return self.__rx_get__().__index__()

    def __len__(self: Rx[ot.CanLen]) -> int:
        # TODO: custom rx_len() function
        return len(self.__rx_get__())

    # rich comparison ops

    def __lt__[X, Y](self: Rx[ot.CanLt[X, Y]], other: X) -> RxOp2[Y]:
        return RxOp2(10, ' < ', operator.lt, self, other)  # type: ignore[arg]

    def __le__[X, Y](self: Rx[ot.CanLt[X, Y]], other: X) -> RxOp2[Y]:
        return RxOp2(10, ' <= ', operator.le, self, other)  # type: ignore[arg]

    @override
    def __eq__[X, Y](self: Rx[ot.CanEq[X, Y]], other: X) -> RxOp2[Y]:  # type: ignore[override]
        return RxOp2(10, ' == ', operator.eq, self, other)

    @override
    def __ne__[X, Y](self: Rx[ot.CanNe[X, Y]], other: X) -> RxOp2[Y]:  # type: ignore[override]
        return RxOp2(10, ' != ', operator.ne, self, other)

    def __gt__[X, Y](self: Rx[ot.CanGt[X, Y]], other: X) -> RxOp2[Y]:
        return RxOp2(10, ' > ', operator.gt, self, other)  # type: ignore[arg]

    def __ge__[X, Y](self: Rx[ot.CanGe[X, Y]], other: X) -> RxOp2[Y]:
        return RxOp2(10, ' >= ', operator.ge, self, other)  # type: ignore[arg]

    # binary arithmetic ops

    def __add__[X, Y](self: Rx[ot.CanAdd[X, Y]], x: CanRx[X]) -> RxOp2[Y]:
        return RxOp2(60, ' + ', operator.add, self, x)

    def __sub__[X, Y](self: Rx[ot.CanSub[X, Y]], x: CanRx[X]) -> RxOp2[Y]:
        return RxOp2(60, ' - ', operator.sub, self, x)

    def __mul__[X, Y](self: Rx[ot.CanMul[X, Y]], x: CanRx[X]) -> RxOp2[Y]:
        return RxOp2(70, ' * ', operator.mul, self, x)

    def __matmul__[X, Y](
        self: Rx[ot.CanMatmul[X, Y]],
        x: CanRx[X],
    ) -> RxOp2[Y]:
        return RxOp2(70, ' @ ', operator.matmul, self, x)

    def __truediv__[X, Y](
        self: Rx[ot.CanTruediv[X, Y]],
        x: CanRx[X],
    ) -> RxOp2[Y]:
        return RxOp2(70, ' / ', operator.truediv, self, x)

    def __floordiv__[X, Y](
        self: Rx[ot.CanFloordiv[X, Y]],
        x: CanRx[X],
    ) -> RxOp2[Y]:
        return RxOp2(70, ' // ', operator.floordiv, self, x)

    def __mod__[X, Y](self: Rx[ot.CanMod[X, Y]], x: CanRx[X]) -> RxOp2[Y]:
        return RxOp2(70, ' % ', operator.mod, self, x)

    @overload
    def __pow__(self, x: CanRx[ot.CanRPow[Y_co, Y_co]]) -> RxOp2[Y_co]: ...
    @overload
    def __pow__[X, Y](self: Rx[ot.CanPow2[X, Y]], x: CanRx[X]) -> RxOp2[Y]: ...
    @overload
    def __pow__[X, M, Y](
        self: Rx[ot.CanPow3[X, M, Y]],
        x: CanRx[X],
        m: CanRx[M],
    ) -> RxMap[Y]: ...

    def __pow__(
        self,
        x: CanRx[Any],
        m: CanRx[Any] | None = None,
    ) -> RxMap[Any]:
        if m is not None:
            return RxMap(pow, self, x, m)
        return RxOp2(90, '**', pow, self, x)

    def __lshift__[X, Y](
        self: Rx[ot.CanLshift[X, Y]],
        x: CanRx[X],
    ) -> RxOp2[Y]:
        return RxOp2(50, ' << ', operator.lshift, self, x)

    def __rshift__[X, Y](
        self: Rx[ot.CanRshift[X, Y]],
        x: CanRx[X],
    ) -> RxOp2[Y]:
        return RxOp2(50, ' >> ', operator.rshift, self, x)

    def __and__[X, Y](self: Rx[ot.CanAnd[X, Y]], x: CanRx[X]) -> RxOp2[Y]:
        return RxOp2(40, ' & ', operator.and_, self, x)

    def __xor__[X, Y](self: Rx[ot.CanXor[X, Y]], x: CanRx[X]) -> RxOp2[Y]:
        return RxOp2(30, ' ^ ', operator.xor, self, x)

    def __or__[X, Y](self: Rx[ot.CanOr[X, Y]], x: CanRx[X]) -> RxOp2[Y]:
        return RxOp2(20, ' | ', operator.or_, self, x)

    # reflected arithmetic ops

    def __radd__[X, Y](self: Rx[ot.CanRAdd[X, Y]], x: X) -> RxOp2[Y]:
        return RxOp2(60, ' + ', operator.add, x, self)

    def __rsub__[X, Y](self: Rx[ot.CanRSub[X, Y]], x: X) -> RxOp2[Y]:
        return RxOp2(60, ' - ', operator.sub, x, self)

    def __rmul__[X, Y](self: Rx[ot.CanRMul[X, Y]], x: X) -> RxOp2[Y]:
        return RxOp2(70, ' * ', operator.mul, x, self)

    def __rmatmul__[X, Y](self: Rx[ot.CanRMatmul[X, Y]], x: X) -> RxOp2[Y]:
        return RxOp2(70, ' @ ', operator.matmul, x, self)

    def __rtruediv__[X, Y](self: Rx[ot.CanRTruediv[X, Y]], x: X) -> RxOp2[Y]:
        return RxOp2(70, ' / ', operator.truediv, x, self)

    def __rfloordiv__[X, Y](self: Rx[ot.CanRTruediv[X, Y]], x: X) -> RxOp2[Y]:
        return RxOp2(70, ' // ', operator.floordiv, x, self)

    def __rmod__[X, Y](self: Rx[ot.CanRMod[X, Y]], x: X) -> RxOp2[Y]:
        return RxOp2(70, ' % ', operator.mod, x, self)

    def __rpow__[X, Y](self: Rx[ot.CanRPow[X, Y]], x: X, /) -> RxOp2[Y]:
        return RxOp2(90, '**', operator.pow, x, self)

    def __rlshift__[X, Y](self: Rx[ot.CanRLshift[X, Y]], x: X, /) -> RxOp2[Y]:
        return RxOp2(50, ' << ', operator.lshift, x, self)

    def __rrshift__[X, Y](self: Rx[ot.CanRRshift[X, Y]], x: X, /) -> RxOp2[Y]:
        return RxOp2(50, ' >> ', operator.rshift, x, self)

    def __rand__[X, Y](self: Rx[ot.CanRAnd[X, Y]], x: X) -> RxOp2[Y]:
        return RxOp2(40, ' & ', operator.and_, x, self)

    def __rxor__[X, Y](self: Rx[ot.CanRXor[X, Y]], x: X) -> RxOp2[Y]:
        return RxOp2(30, ' ^ ', operator.xor, x, self)

    def __ror__[X, Y](self: Rx[ot.CanROr[X, Y]], x: X) -> RxOp2[Y]:
        return RxOp2(20, ' | ', operator.or_, x, self)

    # arithmetic operators (unary)

    def __neg__[Y](self: Rx[ot.CanNeg[Y]]) -> RxOp1[Y]:
        return RxOp1(80, '-', operator.neg, self)

    def __pos__[Y](self: Rx[ot.CanPos[Y]]) -> RxOp1[Y]:
        return RxOp1(80, '+', operator.pos, self)

    def __invert__[Y](self: Rx[ot.CanInvert[Y]]) -> RxOp1[Y]:
        return RxOp1(80, '~', operator.invert, self)

    def __abs__[Y](self: Rx[ot.CanAbs[Y]]) -> RxMap[Y]:
        return RxMap(cast(ot.CanCall[[ot.CanAbs[Y]], Y], abs), self)

    # rounding

    @overload
    def __round__[Y](self: Rx[ot.CanRound1[Y]], /) -> RxMap[Y]:  ...
    @overload
    def __round__[Y](self: Rx[ot.CanRound1[Y]], n: None = ...) -> RxMap[Y]: ...
    @overload
    def __round__[N, Y](self: Rx[ot.CanRound2[N, Y]], n: CanRx[N]) -> RxMap[Y]:
        ...

    def __round__[N, Y1, Y2](
        self: Rx[ot.CanRound1[Y1] | ot.CanRound2[N, Y2]],
        n: CanRx[N] | None = None,
    ) -> RxMap[Y1] | RxMap[Y2]:
        if n is None:
            round1 = cast(ot.CanCall[[ot.CanRound1[Y1]], Y1], round)
            return RxMap(round1, self)

        round2 = cast(ot.CanCall[[ot.CanRound2[N, Y2], N], Y2], round)
        return RxMap(round2, self, n)

    def __trunc__[Y](self: Rx[ot.CanTrunc[Y]]) -> RxMap[Y]:
        return RxMap(cast(ot.CanCall[[ot.CanTrunc[Y]], Y], math.trunc), self)

    def __floor__[Y](self: Rx[ot.CanFloor[Y]]) -> RxMap[Y]:
        return RxMap(cast(ot.CanCall[[ot.CanFloor[Y]], Y], math.floor), self)

    def __ceil__[Y](self: Rx[ot.CanCeil[Y]]) -> RxMap[Y]:
        return RxMap(cast(ot.CanCall[[ot.CanCeil[Y]], Y], math.ceil), self)

    # callable emulation

    def __call__[**Xs, Y](
        self: Rx[ot.CanCall[Xs, Y]],
        *args: CanRx[Any],
        **kwargs: CanRx[Any],
    ) -> RxMap[Y]:
        """
        Returns the result, given reactive or constants args and kwargs.
        The function itself is also reactive, so setting this function to
        another (with the same signature) will invalidate the returned
        reactive result cache, too.
        """
        # TODO: map directly if constant
        def apply(
            func: ot.CanCall[Xs, Y],
            /,
            *args: Xs.args,
            **kwargs: Xs.kwargs,
        ) -> Y:
            return func(*args, **kwargs)

        # TODO: have RxMap also listen to rx callables
        return RxMap(apply, self, *args, **kwargs)


class RxVar[Y](Rx[Y]):
    @contextlib.contextmanager
    def __rx_atomic__(self, /) -> Generator[None, None, None]:
        # TODO: implement this (like a re-entry lock) (backend-specific)
        yield

    def __rx_set__(self, value: Y, /) -> bool:
        """
        Sets the value of this variable (if changed), and notify the listeners.
        Returns True if the value changed, False if it didn't.
        """
        assert value is not Ellipsis

        with self.__rx_atomic__():
            _, changed = self.__rx_state__.set(value)
            if not changed:
                return False

            # propagate to children
            for child, base_index in self.__rx_out__.items():
                child.__rx_invalidate__(base_index, value)

        return True

    def __rx_update__[**Xs](
        self,
        func: ot.CanCall[Concatenate[Y, Xs], Y],
        /,
        *args: Xs.args,
        **kwargs: Xs.kwargs,
    ) -> Self | NotImplementedType:
        if any(isinstance(arg, Rx) for arg in chain(args, kwargs.values())):
            msg = 'cannot in-place update an rx variable with rx args'
            raise TypeError(msg)

        with self.__rx_atomic__():
            value = self.__rx_get__()
            value_new = func(value, *args, **kwargs)

            if value_new is NotImplemented:
                return NotImplemented

            self.__rx_set__(value_new)

        return self

    # augmented arithmetic ops

    def __iadd__[X](self: RxVar[ot.CanIAdd[X, Y]], x: X) -> RxVar[Y]:
        return self.__rx_update__(operator.__iadd__, x)

    def __isub__[X](self: RxVar[ot.CanISub[X, Y]], x: X) -> RxVar[Y]:
        return self.__rx_update__(operator.__isub__, x)

    def __imul__[X](self: RxVar[ot.CanIMul[X, Y]], x: X) -> RxVar[Y]:
        return self.__rx_update__(operator.__imul__, x)

    def __imatmul__[X](self: RxVar[ot.CanIMatmul[X, Y]], x: X) -> RxVar[Y]:
        return self.__rx_update__(operator.__imatmul__, x)

    def __itruediv__[X](self: RxVar[ot.CanITruediv[X, Y]], x: X) -> RxVar[Y]:
        return self.__rx_update__(operator.__itruediv__, x)

    def __ifloordiv__[X](self: RxVar[ot.CanIFloordiv[X, Y]], x: X) -> RxVar[Y]:
        return self.__rx_update__(operator.__ifloordiv__, x)

    def __imod__[X](self: RxVar[ot.CanIMod[X, Y]], x: X) -> RxVar[Y]:
        return self.__rx_update__(operator.__imod__, x)

    def __ipow__[X](self: RxVar[ot.CanIPow[X, Y]], x: X) -> RxVar[Y]:
        return self.__rx_update__(operator.__ipow__, x)

    def __ilshift__[X](self: RxVar[ot.CanILshift[X, Y]], x: X) -> RxVar[Y]:
        return self.__rx_update__(operator.__ilshift__, x)

    def __irshift__[X](self: RxVar[ot.CanIRshift[X, Y]], x: X) -> RxVar[Y]:
        return self.__rx_update__(operator.__irshift__, x)

    def __iand__[X](self: RxVar[ot.CanIAnd[X, Y]], x: X) -> RxVar[Y]:
        return self.__rx_update__(operator.__iand__, x)

    def __ixor__[X](self: RxVar[ot.CanIXor[X, Y]], x: X) -> RxVar[Y]:
        return self.__rx_update__(operator.__ixor__, x)

    def __ior__[X](self: RxVar[ot.CanIOr[X, Y]], x: X) -> RxVar[Y]:
        return self.__rx_update__(operator.__ior__, x)


class RxMap[Y](RxVar[Y]):
    __slots__ = ('__func__', '_rx_parents')

    __func__: ot.CanCall[..., Y]
    _rx_parents: WeakValueDictionary[int, Rx[Any]]

    @override
    def __init__(
        self,
        func: ot.CanCall[..., Y],
        /,
        *rx_args: Rx[Any] | Any,
    ) -> None:
        # TODO: constant if all args are constant

        self.__func__ = func

        self._rx_parents = WeakValueDictionary()
        rx_parent_ix: dict[int, int] = {}
        rx_bases: list[State[Any]] = []
        for i, arg in enumerate(rx_args):
            if isinstance(arg, Rx):
                if id(arg) in rx_parent_ix:
                    # share the arg state of the same parent
                    base_state = rx_bases[rx_parent_ix[id(arg)]]
                else:
                    rx_parent_ix[id(arg)] = i
                    base_state = StateVar(arg.__rx_get__())
                    # make sure we can find the parent
                    self._rx_parents[i] = arg
            else:
                base_state = StateConst(arg)

            rx_bases.append(base_state)

        self.__rx_bases__ = tuple(rx_bases)
        self.__rx_state__ = StateVar(func(*self._get_args()))
        self.__rx_out__ = {}

        # make sure that our parents know about us
        for i, parent in self._rx_parents.items():
            parent.__rx_out__[self] = i

    def _get_args(self, /) -> list[Any]:
        # TODO: exception groups + exception notes
        args: list[Any] = []
        for i, base_state in enumerate(self.__rx_bases__):
            value = base_state.get()
            if value is Ellipsis:
                value = self._rx_parents[i].__rx_get__()
                assert not base_state.set(value)[1]

            args.append(value)

        return args

    def _get_params(self, /) -> starmap[Rx[Any] | Any]:
        parents = self._rx_parents
        return starmap(parents.get, enumerate(self.__rx_bases__))

    @override
    def __repr__(self) -> str:
        fname = cast(str, self.__func__.__name__)  # type: ignore[asdasd]
        return f'{fname}({', '.join(map(repr, self._get_params()))})'

    @override
    def __rx_get__(self, /) -> Y:
        """Maximally lazy evaluation."""
        if (res := self.__rx_state__.get()) is not Ellipsis:
            assert not any(b.get() is Ellipsis for b in self.__rx_bases__)
            return cast(Y, res)

        args = self._get_args()
        try:
            res = self.__func__(*args)
        except Exception as e:
            e.add_note(repr(self))
            raise

        super().__rx_set__(res)

        return res

    @override
    def __rx_set__(self, value: Y, /) -> bool:
        raise RuntimeError('RxResult is immutable')


class RxOp[Y](RxMap[Y]):
    __slots__ = ('_precedence',)
    _precedence: Final[int]

    @override
    def __init__(
        self,
        precedence: int,
        func: ot.CanCall[..., Y],
        /,
        *rx_args: Rx[Any] | Any,
    ) -> None:
        self._precedence = precedence
        super().__init__(func, *rx_args)

    @property
    def precedence(self) -> int:
        return self._precedence

    def _format_params(self) -> Generator[str, None, None]:
        for x in self._get_params():
            if isinstance(x, RxOp) and self._precedence > x.precedence:
                yield f'({x!r})'
            else:
                yield repr(x)


@final
class RxOp1[Y](RxOp[Y]):
    """Unary prefix operators."""

    __slots__ = ('_symbol',)
    _symbol: Final[str]

    @override
    def __init__[X](
        self,
        precedence: int,
        symbol: str,
        func: ot.CanCall[[X], Y],
        x: CanRx[X],
        /,
    ) -> None:
        self._symbol = symbol
        super().__init__(precedence, func, x)

    @override
    def __repr__(self) -> str:
        s, = self._format_params()
        return f'{self._symbol}{s}'


@final
class RxOp2[Y](RxOp[Y]):
    """Binary infix operators."""

    __slots__ = ('_symbol',)
    _symbol: Final[str]

    @override
    def __init__[X0, X1](
        self,
        precedence: int,
        symbol: str,
        func: ot.CanCall[[X0, X1], Y],
        x0: CanRx[X0],
        x1: CanRx[X1],
        /,
    ) -> None:
        self._symbol = symbol
        super().__init__(precedence, func, x0, x1)

    @override
    def __repr__(self) -> str:
        s0, s1 = self._format_params()
        return f'{s0}{self._symbol}{s1}'


def rx[Y: object](obj: Y) -> RxVar[Y]:
    if obj is None or obj is NotImplemented:
        raise ValueError(f'`{obj}` is ')
    if obj is Ellipsis:
        raise TypeError('`...` is not supported')

    if isinstance(obj, dict | list | set | bytearray):
        raise TypeError('mutable container types are not supported (yet)')
    try:
        hash(obj)
    except TypeError as e:
        raise TypeError('mutable types are not supported (yet)') from e

    return RxVar(obj)
