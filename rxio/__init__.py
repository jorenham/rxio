__all__ = (
    'RX',
    '__version__',
)

from importlib import metadata as _metadata

from .rx import RX


__version__ = _metadata.version(__package__ or __file__.split('/')[-1])
