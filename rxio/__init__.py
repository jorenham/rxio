from importlib import metadata as _metadata


__version__ = _metadata.version(__package__ or __file__.split('/')[-1])
