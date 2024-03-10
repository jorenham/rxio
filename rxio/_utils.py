__all__ = ('has_refs',)

import gc
import sys
import weakref
from typing import Any


def has_refs(obj: Any, /, stacklevel: int = 1) -> bool:
    """
    Checks if the object has any references to it.

    A `ReferenceError` is raised for primitives
    (e.g. strings, tuples, dicts, direct `object` instances) and any other
    objects that aren't tracked by the garbage collector.

    Unlike `weakref` refs or proxies, `has_refs()` doesn't require objects with
    `__slots__` to have a  `__weakref__` slot.

    Any `weakref.referenceType` or one of the `weakref.ProxyTypes` objects
    are automatically "unwrapped", i.e. checked whether its referent is alive.

    Examples:
        Basic usage:

        >>> class Spam: ...
        >>> spam = Spam()
        >>> has_refs(spam)
        True
        >>> has_refs(Spam())
        False

        Weak references:

        >>> import weakref
        >>> spam = Spam()
        >>> spam_ref = weakref.ref(spam)
        >>> has_refs(spam_ref)
        True
        >>> del spam
        >>> has_refs(spam_ref)
        False

        Weakref proxies:

        >>> import weakref
        >>> spam = Spam()
        >>> spam_proxy = weakref.proxy(spam)
        >>> has_refs(spam_proxy)
        True
        >>> del spam
        >>> has_refs(spam_proxy)
        False

    """
    # J: This works perfectly fine in pyscript==2024.1.3 (pyodide==0.25.0)
    if stacklevel < 1:
        raise ValueError('stacklevel must be >=1')

    # handle weakref types
    if isinstance(obj, weakref.ProxyTypes):
        try:
            # this either raises, or is always true
            cls = obj.__class__
        except ReferenceError:
            return False
        else:
            if cls is not type(obj):
                return True
            # otherwise not a proxy after all
    if isinstance(obj, weakref.ReferenceType):
        return obj() is not None

    if not gc.is_tracked(obj):
        raise ReferenceError(f'{obj!r} is untracked')

    # the -1 corrects for the `sys.getrefcount` call
    refs = sys.getrefcount(obj) - 1 - stacklevel
    assert refs >= 0 or stacklevel > 1
    if refs < 0:
        raise ValueError('stacklevel is too big')
    return bool(refs)
