from __future__ import annotations

import weakref
from collections import defaultdict
from typing import TYPE_CHECKING, Any, Protocol, cast, final, override


if TYPE_CHECKING:
    from collections.abc import Mapping
    from types import EllipsisType

    import optype as opt


class CanCallPositional[*Xs, Y](Protocol):
    def __call__(self, *__args: *Xs) -> Y: ...


class Reactive[Y]:
    __slots__ = ('__func__', '__rx_children__', '__weakref__')

    __rx_children__: weakref.WeakKeyDictionary[_CanRxCache, set[int]]

    def __init__(self) -> None:
        self.__rx_children__ = weakref.WeakKeyDictionary()

    def __rx_get__(self) -> Y:
        raise NotImplementedError

    @final
    def __rx_adopt__(self, child: _CanRxCache, /, *edges: int) -> None:
        """
        Adopt a child node, that can reach this node via `edges`,
        which correspond to the child's args indices (this is a multi-graph).
        """
        assert edges

        self.__rx_children__.setdefault(child, set()).update(edges)

    @final
    def __rx_invalidate__(self, value: Y | EllipsisType = ..., /) -> None:
        """
        Invalidate or update the children's cache. Invalidation will propagate
        to all children (depth-first) if necessary.

        So can we stop reciting Phil Karlton now? Or did he change his name...?
        """
        # TODO: prevent overlap with __rx_set__() in self and (grand-)children
        if value is Ellipsis:
            for child, edges in self.__rx_children__.items():
                child.__rx_delcache__(*edges)
        else:
            for child, edges in self.__rx_children__.items():
                child.__rx_setcache__(value, *edges)

    def __bool__(self) -> bool:
        return bool(self.__rx_get__())

    @override
    def __str__(self) -> str:
        return str(self.__rx_get__())

    @override
    def __repr__(self) -> str:
        return f'rx({self.__rx_get__()!r})'


class RxValue[Y: opt.CanHash](Reactive[Y]):
    __slots__ = ('_value', '_watchers')
    __match_args__ = ('_value',)

    _value: Y

    def __init__(self, value: Y, /) -> None:
        self._value = value

    @override
    def __rx_get__(self) -> Y:
        return self._value

    def __rx_set__(self, value_new: Y, /) -> bool:
        # TODO: ensure type invariance (a type should never change)
        # TODO:

        # TODO: currently not threadsafe:
        #  - build extensible transaction system (with context manager)
        #  - default implementation: 1 writer, N readers, 1 machine

        # transaction start
        value = self._value
        if value == value_new:
            return False

        self._value = value_new
        # transaction stop

        # TODO: optionally run in (async) worker/pool
        self.__rx_invalidate__(value_new)

        return True


class _CanRxCache(Protocol):
    def __rx_delcache__(self, *__keys: int) -> None: ...
    def __rx_setcache__(self, __value: Any, *__keys: int) -> None: ...


class RxResult[*Xs, Y](Reactive[Y]):
    __slots__ = ('__defaults__', '__func__', '__rx_args__', '__rx_cache__')

    # TODO: support kwargs

    __func__: CanCallPositional[*Xs, Y]
    __defaults__: Mapping[int, Any]

    __rx_args__: dict[int, Reactive[Any]]
    __rx_cache__: dict[int | str, Any]

    @override
    def __init__(
        self,
        func: CanCallPositional[*Xs, Y],
        /,
        *args: Any,
    ) -> None:
        super().__init__()
        self.__func__ = func

        # distinguish between rx-args (parents) and non-rx args (defaults).
        self.__defaults__ = defaults = {}
        self.__rx_args__ = rx_args = {}
        # build the local multi-graph from the rx-args
        rx_edges: dict[Reactive[Any], list[int]] = defaultdict(list)

        for i, arg in enumerate(args):
            if isinstance(arg, Reactive):
                rx_arg: Reactive[Any] = arg
                rx_args[i] = rx_arg
                rx_edges[rx_arg].append(i)
            else:
                defaults[i] = arg

        # make the parents adopt this child, so that they'll manage the child's
        # cache in a push-based manner
        self.__rx_cache__ = {}
        for arg, edges in rx_edges.items():
            arg.__rx_adopt__(self, *edges)

    def _collect_args(self, /) -> tuple[*Xs]:
        defaults = self.__defaults__
        rx_args = self.__rx_args__
        nargs = len(defaults) + len(rx_args)

        rx_cache = self.__rx_cache__
        args: list[Any] = []

        for i in range(nargs):
            if i in rx_cache:
                # maybe check if stale?
                args.append(rx_cache[i])
            elif i in defaults:
                args.append(defaults[i])
            else:
                arg = rx_cache[i] = rx_args[i].__rx_get__()
                args.append(arg)

        return cast(tuple[*Xs], tuple(args))

    @override
    def __rx_get__(self, /) -> Y:
        """Maximally lazy evaluation."""
        # TODO: rare race-condition: parent change, child not invalidated yet?
        cache = self.__rx_cache__
        if 'return' in cache:
            return cache['return']

        args = self._collect_args()
        res = self.__func__(*args)
        cache['return'] = res

        self.__rx_invalidate__(res)

        return res

    @final
    def __rx_delcache__(self, *keys: int) -> None:
        """
        Called from a specific RXValue parent arg after it was invalidated.
        """
        # TODO: prevent overlap with __rx_get__()

        if not (cache := self.__rx_cache__):
            return

        invalidated = cache.pop('return', ...) is not Ellipsis
        for key in keys:
            cache.pop(key, None)

        if invalidated:
            self.__rx_invalidate__()

    @final
    def __rx_setcache__(self, value: Any, *keys: int) -> None:
        """
        Called from a specific RXValue parent arg after it changed.
        """
        # TODO: prevent overlap with __rx_get__()

        cache = self.__rx_cache__
        invalidated = cache.pop('return', ...) is not Ellipsis
        cache |= dict.fromkeys(keys, value)

        if invalidated:
            self.__rx_invalidate__()
