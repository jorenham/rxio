# ruff: noqa: PLW3201
"""
Elementary interfaces for special "dunder" attributes.
"""
import typing as _tp
import weakref as _weakref

# special attributes

@_tp.runtime_checkable
class HasDict[V](_tp.Protocol):
    __dict__: dict[str, V]

@_tp.runtime_checkable
class _HasDocAttr(_tp.Protocol):
    __doc__: str | None

@_tp.runtime_checkable
class _HasDocProp(_tp.Protocol):
    @property
    def __doc__(self) -> str | None: ...  # type: ignore[override]

type HasDoc = _HasDocAttr | _HasDocProp
"""Note that with (c)python's `-OO` flag, any generated `__doc__` is `None`."""


@_tp.runtime_checkable
class _HasNameAttr(_tp.Protocol):
    __name__: str

@_tp.runtime_checkable
class _HasNameProp(_tp.Protocol):
    @property
    def __name__(self) -> str: ...

type HasName = _HasNameAttr | _HasNameProp

@_tp.runtime_checkable
class _HasQualnameAttr(_tp.Protocol):
    __qualname__: str

@_tp.runtime_checkable
class _HasQualnameProp(_tp.Protocol):
    @property
    def __qualname__(self) -> str: ...  # type: ignore[override]

type HasQualname = _HasQualnameAttr | _HasQualnameProp


@_tp.runtime_checkable
class _HasModuleAttr(_tp.Protocol):
    __module__: str

class _HasModuleProp(_tp.Protocol):
    @property
    def __module__(self) -> str: ...  # type: ignore[override]

type HasModule = _HasModuleAttr | _HasModuleProp


@_tp.runtime_checkable
class _HasAnnotationsAttr[V](_tp.Protocol):
    # `Mapping` is not allowed by pyright; imho unnecessarily restrictive
    __annotations__: dict[str, V]

@_tp.runtime_checkable
class _HasAnnotationsProp[V](_tp.Protocol):
    @property
    def __annotations__(self) -> dict[str, V]: ...  # type: ignore[override]

type HasAnnotations[V] = _HasAnnotationsAttr[V] | _HasAnnotationsProp[V]
"""Note that the `V` type is hard to accurately define; blame PEP 563."""


@_tp.runtime_checkable
class HasWeakReference(_tp.Protocol):
    """An object referenced by a `weakref.ReferenceType[Self]`."""
    __weakref__: _weakref.ReferenceType[_tp.Self]

@_tp.runtime_checkable
class HasWeakCallableProxy[**Xs, Y](_tp.Protocol):
    """A callable referenced by a `weakref.CallableProxyType[Self]`."""
    __weakref__: _weakref.CallableProxyType[_tp.Self]
    def __call__(self, *__args: Xs.args, **__kwargs: Xs.kwargs) -> Y: ...

@_tp.runtime_checkable
class _HasWeakProxy(_tp.Protocol):
    __weakref__: _weakref.ProxyType[_tp.Self]

type HasWeakProxy = HasWeakCallableProxy[..., _tp.Any] | _HasWeakProxy
"""An object referenced by a `weakref.proxy` (not the proxy itself)."""




# Unary operators
# TODO: type-cast metods, e.g. `__int__`
# TODO: strict int methods: `__len__`, `__index__`, `__hash__`
# TODO: strint str methods: `__repr__`



# Binary operators
# TODO; `__contains__`
# TODO: `class Cannot*: ...` variants that return `NotImplementedType`





# TODO: __getitem__ and __missing__
# TODO: __getattr__

# TODO: __init_subclass__ ?
# TODO: __class_getitem__ ?
