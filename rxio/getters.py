from __future__ import annotations

__all__ = ('Self', 'Attr', 'Item')

from abc import ABCMeta, abstractmethod
from types import NotImplementedType
from typing import (
    Any,
    ClassVar,
    Final,
    Generic,
    Hashable,
    Literal,
    Mapping,
    Self as _TSelf,
    TypeAlias,
    TypeVar,
    cast,
    final,
    overload,
)

_T = TypeVar('_T')
_KT = TypeVar("_KT", bound=Hashable, contravariant=True)
_GT = TypeVar("_GT", bound='Getter[Any, Any]')


_Context: TypeAlias = dict[str, Any]


class Getter(Generic[_GT, _KT], metaclass=ABCMeta):
    __slots__ = ('_root', '_arg',)
    __match_args__ = ('_root', '_arg',)

    _root: _GT
    _arg: _KT

    @overload
    def __init__(self: Getter[_GT, SelfType], arg: _KT, /) -> None: ...
    @overload
    def __init__(self: Getter[_GT, _KT], arg: _KT, root: _GT, /) -> None: ...
    @overload
    def __init__(self: Getter[_GT, SelfType], arg: _KT, root: None = ..., /) -> None: ...

    def __init__(self, arg: _KT, root: _GT | None = None, /) -> None:
        self._arg = arg

        if root is None:
            self._root = cast(_GT, Self)
        else:
            self._root = root

        super().__init__()

    def __repr__(self) -> str:
        return f'<{type(self).__name__}: {self._arg}>'

    def __eq__(self, other: Any) -> bool:
        return bool(
            type(self) is type(other)
            and self._arg == other._arg  # noqa
            and self._root == other._root  # noqa
        )

    def __ne__(self, other: Any) -> bool:
        return not self == other

    @overload
    def __ge__(self, other: Getter[Any, Any]) -> bool: ...
    @overload
    def __ge__(self, other: Any) -> bool | NotImplementedType: ...

    def __ge__(self, other: Any) -> bool | NotImplementedType:
        if not isinstance(other, Getter):
            return NotImplemented
        return self == other or self._root >= other

    def __gt__(self, other: Any) -> bool:
        return self != other and self._root >= other

    def __lt__(self, other: Getter[Any, Any]) -> bool:
        return not self >= other

    def __le__(self, other: Getter[Any, Any]) -> bool:
        return not self > other

    def __getattr__(self, arg: str) -> Attr[_TSelf]:
        return Attr(arg, self)

    def __getitem__(self, arg: _T) -> Item[_TSelf, _T]:
        return Item(arg, self)

    @abstractmethod
    def __call__(self, obj: Any) -> Any: ...


@final
class SelfType(Getter['SelfType', Any]):
    """Represents the identity / root / self of an object."""

    __slots__ = ()
    __match_args__ = ()

    _instance: ClassVar[SelfType | None] = None

    _root: SelfType
    _arg: None

    def __new__(cls, *args: Any, **kwargs: Any) -> SelfType:
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance

    # noinspection PyUnusedLocal
    def __init__(self, arg: None = None, root: None = None, /):
        # noinspection PyTypeChecker
        super().__init__(None, self)

    def __repr__(self) -> str:
        return '<Self>'

    def __str__(self) -> str:
        return '_'

    def __eq__(self, other: Any) -> bool:
        return self is other

    def __ge__(self, other: Any) -> bool | NotImplementedType:
        if not isinstance(other, Getter):
            return NotImplemented
        return self == other

    @overload
    def __gt__(self, other: Getter[Any, Any]) -> Literal[False]: ...
    @overload
    def __gt__(self, other: Any) -> Literal[False] | NotImplementedType: ...

    def __gt__(self, other: Any) -> Literal[False] | NotImplementedType:
        if not isinstance(other, Getter):
            return NotImplemented
        return False

    def __call__(self, obj: _T) -> _T:
        """Returns the object."""
        return obj


Self: Final[Getter[SelfType, Any]] = SelfType()


@final
class Attr(Getter[_GT, str]):
    __slots__ = ()

    _root: _GT
    _arg: str

    def __init__(self, arg: str, root: _GT | None = None, /) -> None:
        super().__init__(arg, root)

    def __str__(self) -> str:
        return f"{self._root}.{self._arg}"

    def __call__(self, obj: Any) -> Any:
        """Gets this attribute of the object, or raises AttributeError."""
        return getattr(self._root(obj), self._arg)


@final
class Item(Getter[_GT, _KT]):
    __slots__ = ()

    _root: _GT
    _arg: _KT

    def __init__(self, arg: _KT, root: _GT | None = None) -> None:
        super().__init__(arg, root)

    def __hash__(self) -> int:
        return hash(self._arg)

    def __str__(self) -> str:
        return f"{self._root}[{self._format_arg()}]"

    def __call__(self, obj: Mapping[_KT, _T]) -> _T:
        """Returns this item of the object, or raises KeyError."""
        return self._root(obj)[self._arg]

    def _format_arg(self) -> str:
        def __format_arg(arg: slice | tuple[Any, ...] | str | Any) -> str:
            if isinstance(arg, slice):
                parts = arg.start, arg.stop, arg.step
                if parts[:-1] is None:
                    parts = parts[:-1]

                return ":".join(
                    "" if part is None else __format_arg(part)
                    for part in parts
                )

            if isinstance(arg, tuple):
                return ", ".join(map(__format_arg, arg))

            if isinstance(arg, str):
                return repr(arg)

            return str(arg)

        return __format_arg(self._arg)
