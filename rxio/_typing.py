from __future__ import annotations

__all__ = (
    "Async",
    "AsyncCallable",
    "AwaitResult",
    "Coro",
    "CoroCallable",
)

from asyncio import Future
import sys
from typing import (
    Any,
    Awaitable,
    Callable,
    Coroutine,
    Generator,
    TypeVar,
    Union,
)

from typing_extensions import ParamSpec

if sys.version_info >= (3, 10):
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias

_T = TypeVar("_T")
_V = TypeVar("_V")
_Ps = ParamSpec("_Ps")

AwaitResult: TypeAlias = Generator[Any, None, _T]

Async: TypeAlias = Union[Future[_T], AwaitResult[_T], Awaitable[_T]]
AsyncCallable: TypeAlias = Callable[_Ps, Async[_T]]

Coro: TypeAlias = Coroutine[Any, None, _T]
CoroCallable: TypeAlias = Callable[_Ps, Coro[_T]]
