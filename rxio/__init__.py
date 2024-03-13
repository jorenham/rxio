__all__ = (
    '__version__',
    'rx',
)

from importlib import metadata as _metadata

from .rx import rx


__version__ = _metadata.version(__package__ or __file__.split('/')[-1])
